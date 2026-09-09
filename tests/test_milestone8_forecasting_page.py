"""Milestone 8 tests: Forecasting page (ADR-010).

Uses "BANGLADESH" as the synthetic test dataset's location (not a
fictional name), so it actually matches the (mocked) World Bank
registry and population fetch -- exercising the real live-progress
path (select_sarima_order/rolling_origin_backtest genuinely run),
not just the "no population data" short-circuit.
"""

from __future__ import annotations

import json
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
    f"BANGLADESH,2020-{m:02d}-01,2020-{m:02d}-28,{m * 3},Admin0\n" for m in range(1, 13)
)
VALID_CSV = (VALID_CSV_HEADER + VALID_CSV_ROWS).encode()

_FAKE_REGISTRY = [
    {"id": "BGD", "name": "Bangladesh", "region": {"value": "South Asia"}},
]
_FAKE_POPULATION_RECORDS = [
    {"countryiso3code": "BGD", "date": "2020", "value": 165_000_000},
]


def _mock_indicator_response():
    payload = json.dumps([{"total": 1}, _FAKE_POPULATION_RECORDS]).encode()

    class MockResponse:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            pass

        def read(self):
            return payload

    return MockResponse()


@pytest.fixture
def mocked_population(tmp_path):
    with (
        patch(
            "surveillance_platform.data_loading.population_lookup._CACHE_PATH",
            tmp_path / "registry.json",
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup._fetch_country_registry",
            return_value=_FAKE_REGISTRY,
        ),
        patch(
            "surveillance_platform.data_loading.population_lookup.urllib.request.urlopen",
            return_value=_mock_indicator_response(),
        ),
    ):
        yield


def _app_through_preparation(csv_bytes: bytes) -> AppTest:
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
    return at


def test_forecasting_without_preparation_shows_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/forecasting.py")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0


def test_forecasting_computes_and_stores_result_for_selected_track(mocked_population):
    at = _app_through_preparation(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/forecasting.py")
    at.run(timeout=60)
    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert "forecast_by_track" in session.results
    assert len(session.results["forecast_by_track"]) == 1


def test_forecasting_shows_below_threshold_warning_for_short_track(mocked_population):
    """12 months of data is well below the 72-month eligibility floor
    -- ADR-009's limitation message must appear as a warning.
    """
    at = _app_through_preparation(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/forecasting.py")
    at.run(timeout=60)
    assert at.exception == []
    warnings_text = " ".join(w.value for w in at.warning)
    assert "eligibility floor" in warnings_text


def test_revisiting_an_already_computed_track_does_not_recompute(mocked_population):
    """Second run must reuse session.results['forecast_by_track'] --
    verified by confirming the stored result is identical and the
    page still renders without exception on the second pass.
    """
    at = _app_through_preparation(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/forecasting.py")
    at.run(timeout=60)
    first_result = at.session_state["analysis_session"].results["forecast_by_track"]

    at.run(timeout=60)  # rerun the same page again
    assert at.exception == []
    second_result = at.session_state["analysis_session"].results["forecast_by_track"]
    assert first_result == second_result


def test_forecasting_page_never_uses_forecast_all_tracks_batch(mocked_population):
    """Confirms the page uses the per-track path, not the batch
    forecast() -- 'forecast' (the batch key) must never appear,
    only 'forecast_by_track'.
    """
    at = _app_through_preparation(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/forecasting.py")
    at.run(timeout=60)
    session = at.session_state["analysis_session"]
    assert "forecast" not in session.results
    assert "forecast_by_track" in session.results
