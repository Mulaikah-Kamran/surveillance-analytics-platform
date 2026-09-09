"""Milestone 8 tests: Results & Export page (ADR-010)."""

from __future__ import annotations

from pathlib import Path

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


def test_results_export_without_preparation_shows_warning():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/results_export.py")
    at.run()
    assert at.exception == []
    assert len(at.warning) > 0


def test_results_export_shows_download_button_after_preparation():
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page("src/surveillance_platform/ui/pages/load_dataset.py")
    at.run()
    at.get("file_uploader")[0].upload("test.csv", VALID_CSV, "text/csv")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/configure_roles.py")
    at.run()
    at.selectbox(key="role_time").select("calendar_start_date")
    at.selectbox(key="role_location").select("adm_0_name")
    at.selectbox(key="role_measure").select("dengue_total")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/data_preparation.py")
    at.run()

    at.switch_page("src/surveillance_platform/ui/pages/results_export.py")
    at.run()
    assert at.exception == []
    assert len(at.get("download_button")) == 1
