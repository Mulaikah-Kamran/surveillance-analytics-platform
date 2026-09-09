"""Milestone 8 tests: Visualization page (ADR-010)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).parent.parent
APP_PATH = str(REPO_ROOT / "app.py")

VALID_CSV_HEADER = "adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
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
    at.switch_page("src/surveillance_platform/ui/pages/1_load_dataset.py")
    at.run()
    at.get("file_uploader")[0].upload("test.csv", csv_bytes, "text/csv")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/2_configure_roles.py")
    at.run()
    at.selectbox(key="role_time").select("calendar_start_date")
    at.selectbox(key="role_location").select("adm_0_name")
    at.selectbox(key="role_measure").select("dengue_total")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/3_data_preparation.py")
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/4_exploratory_analysis.py")
    at.run()
    return at


def test_visualization_without_eda_shows_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/5_visualization.py")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0


def test_visualization_succeeds_after_eda(mocked_population_registry):
    at = _app_through_visualization(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/5_visualization.py")
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
    at.switch_page("src/surveillance_platform/ui/pages/5_visualization.py")
    at.run()
    assert at.exception == []
    captions = [c.value for c in at.caption]
    assert any("not available" in c for c in captions)
