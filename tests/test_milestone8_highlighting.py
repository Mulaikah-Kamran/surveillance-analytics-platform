"""Milestone 8 tests: role-column highlighting heuristic (ADR-004/ADR-010).

Zero Streamlit imports -- plain pytest.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.ui.highlighting import suggest_roles


def test_suggests_correct_roles_for_typical_column_names():
    df = pd.DataFrame(
        {
            "report_date": pd.to_datetime(["2020-01-01"]),
            "country_name": ["Testland"],
            "case_count": [5],
            "record_id": ["abc123"],
        }
    )
    suggestions = suggest_roles(df)
    assert suggestions["time"] == "report_date"
    assert suggestions["location"] == "country_name"
    assert suggestions["surveillance_measure"] == "case_count"
    assert suggestions["identifier"] == "record_id"


def test_datetime_dtype_is_recognized_even_without_a_hinting_name():
    df = pd.DataFrame({"x": pd.to_datetime(["2020-01-01"]), "y": [1]})
    suggestions = suggest_roles(df)
    assert suggestions["time"] == "x"


def test_returns_none_for_roles_with_no_plausible_column():
    df = pd.DataFrame({"foo": [1], "bar": [2]})
    suggestions = suggest_roles(df)
    assert suggestions["location"] is None
    assert suggestions["identifier"] is None


def test_never_suggests_the_same_column_twice():
    """Each column can only fill the first role it matches -- a
    column named 'case_id' shouldn't simultaneously be suggested as
    both identifier and something else.
    """
    df = pd.DataFrame({"case_id": [1]})
    suggestions = suggest_roles(df)
    matched_columns = [v for v in suggestions.values() if v is not None]
    assert len(matched_columns) == len(set(matched_columns))


def test_does_not_mutate_input():
    df = pd.DataFrame({"date": pd.to_datetime(["2020-01-01"])})
    original = df.copy(deep=True)
    suggest_roles(df)
    pd.testing.assert_frame_equal(df, original)


def test_real_national_extract_columns_suggest_correctly():
    """Regression check against the actual real-data column names
    this heuristic was verified against during development. Includes
    one representative row so dtypes infer realistically -- an empty,
    columns-only DataFrame would give every column `object` dtype,
    which isn't how real loaded data behaves.
    """
    df = pd.DataFrame(
        {
            "adm_0_name": ["BANGLADESH"],
            "adm_1_name": [None],
            "adm_2_name": [None],
            "full_name": ["Bangladesh"],
            "calendar_start_date": pd.to_datetime(["2020-01-01"]),
            "calendar_end_date": pd.to_datetime(["2020-01-31"]),
            "dengue_total": [42],
            "case_definition_standardised": ["Confirmed"],
            "S_res": ["Admin0"],
            "T_res": ["Month"],
        }
    )
    suggestions = suggest_roles(df)
    assert suggestions["time"] == "calendar_start_date"
    assert suggestions["location"] == "adm_0_name"
    assert suggestions["surveillance_measure"] == "dengue_total"
