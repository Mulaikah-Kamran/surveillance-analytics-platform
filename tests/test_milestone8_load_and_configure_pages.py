"""Milestone 8 tests: Load Dataset and Configure Roles pages (ADR-010).

Uses AppTest to simulate real interactions (uploading a file,
selecting dropdowns), not just "does it load without exception" --
verifying the actual resulting session state and displayed feedback.
"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).parent.parent
APP_PATH = str(REPO_ROOT / "app.py")

VALID_CSV = (
    b"adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
    b"Testland,2020-01-01,2020-01-31,10,Admin0\n"
    b"Testland,2020-02-01,2020-02-29,20,Admin0\n"
)

SUB_NATIONAL_CSV = (
    b"adm_0_name,calendar_start_date,calendar_end_date,dengue_total,S_res\n"
    b"Testland,2020-01-01,2020-01-31,10,Admin1\n"
)


def _at_on_page(page_name: str) -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page(f"src/surveillance_platform/ui/pages/{page_name}")
    at.run()
    return at


# --- Load Dataset ---------------------------------------------------------


def test_uploading_a_valid_csv_populates_the_session():
    at = _at_on_page("load_dataset.py")
    at.get("file_uploader")[0].upload("test.csv", VALID_CSV, "text/csv")
    at.run()
    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert session.dataset is not None
    assert len(session.dataset) == 2


def test_uploading_sub_national_data_shows_a_warning_not_a_block():
    at = _at_on_page("load_dataset.py")
    at.get("file_uploader")[0].upload("test.csv", SUB_NATIONAL_CSV, "text/csv")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0
    # Still loaded -- a warning, not a block.
    session = at.session_state["analysis_session"]
    assert session.dataset is not None


def test_no_upload_yet_shows_no_dataset():
    at = _at_on_page("load_dataset.py")
    session = at.session_state["analysis_session"]
    assert session.dataset is None


def test_sample_download_button_is_present():
    at = _at_on_page("load_dataset.py")
    assert len(at.get("download_button")) == 1


# --- Configure Roles -------------------------------------------------------


def test_configure_roles_without_dataset_shows_warning_and_stops():
    at = _at_on_page("configure_roles.py")
    assert at.exception == []
    assert len(at.warning) > 0


def test_selecting_valid_roles_shows_success():
    at = _at_on_page("load_dataset.py")
    at.get("file_uploader")[0].upload("test.csv", VALID_CSV, "text/csv")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/configure_roles.py")
    at.run()

    at.selectbox(key="role_time").select("calendar_start_date")
    at.selectbox(key="role_location").select("adm_0_name")
    at.selectbox(key="role_measure").select("dengue_total")
    at.run()

    assert at.exception == []
    assert len(at.success) > 0
    session = at.session_state["analysis_session"]
    assert session.status == "Configured"
    assert session.role_config.time == "calendar_start_date"


def test_selecting_the_same_column_for_two_roles_shows_error():
    at = _at_on_page("load_dataset.py")
    at.get("file_uploader")[0].upload("test.csv", VALID_CSV, "text/csv")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/configure_roles.py")
    at.run()

    at.selectbox(key="role_time").select("dengue_total")
    at.selectbox(key="role_location").select("adm_0_name")
    at.selectbox(key="role_measure").select("dengue_total")  # duplicate
    at.run()

    assert at.exception == []
    session = at.session_state["analysis_session"]
    assert session.status == "Failed"
    assert len(session.error_messages) > 0


def test_highlighting_suggestion_is_shown_but_not_preselected():
    at = _at_on_page("load_dataset.py")
    at.get("file_uploader")[0].upload("test.csv", VALID_CSV, "text/csv")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/configure_roles.py")
    at.run()

    # A suggestion caption should be shown for at least Time/Location...
    captions = [c.value for c in at.caption]
    assert any("calendar_start_date" in c for c in captions)
    # ...but the dropdown itself must still be unselected (None), per
    # ADR-004's "never pre-select" rule.
    assert at.selectbox(key="role_time").value is None
