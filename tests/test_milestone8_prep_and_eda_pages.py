"""Milestone 8 tests: Data Preparation and Exploratory Analysis pages (ADR-010)."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).parent.parent
APP_PATH = str(REPO_ROOT / "app.py")

# 20 months, well-formed -- enough for a meaningful preparation/EDA run
# without being large enough to slow the test suite down.
VALID_CSV_HEADER = "adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
VALID_CSV_ROWS = "".join(
    f"Testland,2020-{m:02d}-01,2020-{m:02d}-28,{m * 3},Admin0\n" for m in range(1, 13)
)
VALID_CSV = (VALID_CSV_HEADER + VALID_CSV_ROWS).encode()

# A dataset that fails Milestone 4's structural validation: the
# surveillance-measure column is entirely null.
INVALID_CSV = (
    b"adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
    b"Testland,2020-01-01,2020-01-31,,Admin0\n"
)


def _configured_session_app(csv_bytes: bytes) -> AppTest:
    """Upload csv_bytes and configure a valid role mapping, landing on
    Configure Roles with a Configured (or Failed, for invalid data)
    session ready for Data Preparation to consume.
    """
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
    return at


# --- Data Preparation ------------------------------------------------------


def test_data_preparation_without_dataset_shows_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/3_data_preparation.py")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0


def test_data_preparation_succeeds_with_valid_data():
    at = _configured_session_app(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/3_data_preparation.py")
    at.run()
    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert session.status == "Running"
    assert "preparation" in session.results
    assert len(at.success) > 0


def test_data_preparation_shows_only_diagnostics_on_failure():
    at = _configured_session_app(INVALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/3_data_preparation.py")
    at.run()
    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert session.status == "Failed"
    assert len(session.error_messages) > 0
    assert len(at.error) > 0
    # No downstream content (metrics) should render on failure.
    assert len(at.metric) == 0


# --- Exploratory Analysis ---------------------------------------------------


def test_exploratory_analysis_without_preparation_shows_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/4_exploratory_analysis.py")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0


def test_exploratory_analysis_succeeds_after_preparation():
    at = _configured_session_app(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/3_data_preparation.py")
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/4_exploratory_analysis.py")
    at.run()
    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert "eda" in session.results
    assert len(at.success) > 0


def test_exploratory_analysis_shows_population_unavailable_caption():
    """No population data is wired in yet (open question) -- must show
    the graceful 'not available' caption, never an error.
    """
    at = _configured_session_app(VALID_CSV)
    at.switch_page("src/surveillance_platform/ui/pages/3_data_preparation.py")
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/4_exploratory_analysis.py")
    at.run()
    assert at.exception == []
    captions = [c.value for c in at.caption]
    assert any("not available" in c for c in captions)
