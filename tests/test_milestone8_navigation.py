"""Milestone 8 tests: navigation skeleton (ADR-010, Batch 1).

Confirms the st.navigation structure itself works -- initial page
resolution and switching between all seven pages without exception.
No real pipeline logic exists yet (that's Batches 2+); these tests
exist so the skeleton is verified before anything is built on top of
it, matching the project's "verify each batch before the next"
discipline.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).parent.parent
APP_PATH = str(REPO_ROOT / "app.py")

PAGES = [
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/1_load_dataset.py"),
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/2_configure_roles.py"),
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/3_data_preparation.py"),
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/4_exploratory_analysis.py"),
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/5_visualization.py"),
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/6_forecasting.py"),
    str(REPO_ROOT / "src/surveillance_platform/ui/pages/7_results_export.py"),
]


def test_app_loads_without_exception():
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert at.exception == []


def test_initial_page_is_load_dataset():
    at = AppTest.from_file(APP_PATH)
    at.run()
    assert [t.value for t in at.title] == ["Load Dataset"]


@pytest.mark.parametrize("page_path", PAGES)
def test_each_page_loads_without_exception(page_path):
    at = AppTest.from_file(APP_PATH)
    at.run()
    at.switch_page(page_path)
    at.run()
    assert at.exception == []
