"""Milestone 8 tests: Visualization page (ADR-010)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).parent.parent
APP_PATH = str(REPO_ROOT / "app.py")

VALID_CSV_HEADER = (
    "adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
)
VALID_CSV_ROWS = "".join(
    f"Testland,2020-{m:02d}-01,2020-{m:02d}-28,{m * 3},Admin0\n" for m in range(1, 13)
)
VALID_CSV = (VALID_CSV_HEADER + VALID_CSV_ROWS).encode()


@pytest.fixture
def mocked_population_registry(tmp_path):
    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            tmp_path / "registry.json",
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=[
                {"id": "BGD", "name": "Bangladesh", "region": {"value": "South Asia"}},
            ],
        ),
    ):
        yield


def _app_through_visualization(csv_bytes: bytes) -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/load_dataset.py")
    at.run()
    at.get("file_uploader")[0].upload("test.csv", csv_bytes, "text/csv")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/configure_roles.py")
    at.run()
    at.selectbox(key="role_time").select("calendar_start_date")
    at.selectbox(key="role_location").select("adm_0_name")
    at.selectbox(key="role_measure").select("dengue_total")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/data_preparation.py")
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/exploratory_analysis.py")
    at.run()
    return at


def test_visualization_without_eda_shows_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/visualization.py")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0


def test_visualization_succeeds_after_eda(mocked_population_registry):
    at = _app_through_visualization(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/visualization.py")
    at.run()
    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert "visualization" in session.results
    assert len(at.success) > 0


def test_visualization_shows_unavailable_captions_when_optional_figures_absent(
    mocked_population_registry,
):
    """Testland's data has no T_res/case_definition_standardised and no
    matching population -- both optional figures should be absent,
    shown via captions, never an error.
    """
    at = _app_through_visualization(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/visualization.py")
    at.run()
    assert at.exception == []
    captions = [c.value for c in at.caption]
    assert any("not available" in c for c in captions)


def test_annual_trend_shows_a_country_selector_with_a_single_native_chart():
    """Redesign (2026-09-10): cramming many small per-country subplots
    into one scrollable box was replaced with a country selector
    showing one country at a time as a full-sized native
    st.plotly_chart -- the same pattern already used successfully on
    the Forecasting page. Confirms the selector offers both countries
    and defaults to rendering the first one without exception.
    """
    from unittest.mock import patch

    header = "adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
    rows = "".join(
        f"{country},2020-{m:02d}-01,2020-{m:02d}-28,{m * 3},Admin0\n"
        for country in ("Testland", "Otherland")
        for m in range(1, 13)
    )
    csv_bytes = (header + rows).encode()

    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            Path("/tmp/nonexistent_registry.json"),
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=[],
        ),
    ):
        at = _app_through_visualization(csv_bytes)
        at.switch_page("src/surveillance_platform/ui/pages/visualization.py")
        at.run()

    assert at.exception == []
    country_selector = at.selectbox(key="viz_trend_country")
    assert set(country_selector.options) == {"Otherland", "Testland"}
    # AppTest has no attribute for inspecting st.plotly_chart elements
    # directly -- the actual single-country chart rendering (correct
    # axis formatting, preserved diamond marker, legible at a normal
    # viewport) was verified separately with real screenshots.


def test_annual_trend_expander_still_offers_the_full_overview():
    """The full small-multiples grid is still available for anyone who
    wants to compare every country at once, now tucked into an
    expander rather than being the default view. AppTest cannot
    inspect an st.components.v1.html element's actual rendered
    HTML/iframe content -- the genuine bounded, scrollable rendering
    inside the expander was verified separately with real screenshots
    and a real horizontal-scroll interaction, against both a
    two-country case and the full 129-country dataset (confirmed
    directly: 320px per row of countries comes to over 20,000px
    without the height cap). What's verified here, at the level
    AppTest can actually check, is that the expander exists and the
    underlying figure was mutated with the width the fix depends on.
    """
    from unittest.mock import patch

    header = "adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
    rows = "".join(
        f"{country},2020-{m:02d}-01,2020-{m:02d}-28,{m * 3},Admin0\n"
        for country in ("Testland", "Otherland")
        for m in range(1, 13)
    )
    csv_bytes = (header + rows).encode()

    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            Path("/tmp/nonexistent_registry.json"),
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=[],
        ),
    ):
        at = _app_through_visualization(csv_bytes)
        at.switch_page("src/surveillance_platform/ui/pages/visualization.py")
        at.run()

    assert at.exception == []
    assert len(at.expander) > 0
    fig = at.session_state["analysis_session"].results["visualization"].annual_trend
    assert fig.layout.width == 780


def test_annual_trend_natural_height_exceeds_cap_for_many_countries():
    """Real bug, caught via a real browser reproduction against the full
    129-country dataset: the overview expander's embedded component
    height was set to the figure's own full natural height (320px per
    row of countries), which for that many countries came to over
    20,000px -- an iframe that tall stretches the whole page rather
    than giving a bounded, scrollable chart viewer.

    AppTest cannot inspect the actual rendered iframe height (same
    limitation noted above) -- what's verified here is that the
    underlying figure's own natural height genuinely exceeds the
    intended cap for a realistic many-country case, confirming the
    scenario is real. The capped, scrollable rendering itself was
    verified separately with real screenshots and a real
    horizontal-scroll interaction.
    """
    from unittest.mock import patch

    header = "adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
    rows = "".join(
        f"Country{country_index},2020-{m:02d}-01,2020-{m:02d}-28,{m * 3},Admin0\n"
        for country_index in range(20)
        for m in range(1, 13)
    )
    csv_bytes = (header + rows).encode()

    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            Path("/tmp/nonexistent_registry2.json"),
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=[],
        ),
    ):
        at = _app_through_visualization(csv_bytes)
        at.switch_page("src/surveillance_platform/ui/pages/visualization.py")
        at.run()

    assert at.exception == []
    fig = at.session_state["analysis_session"].results["visualization"].annual_trend
    # 20 countries at 2 per row is 10 rows * 320px -- comfortably past
    # any reasonable fixed viewport, confirming this scenario would
    # have hit the pre-fix bug.
    assert fig.layout.height > 600
