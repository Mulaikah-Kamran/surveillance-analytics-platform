"""Milestone 7 tests: monthly aggregation and population-rate join (ADR-009)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from surveillance_platform.forecasting.aggregation import monthly_series, population_rate
from surveillance_platform.forecasting.report import Track
from surveillance_platform.role_configuration import RoleConfiguration

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _data(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["time"] = pd.to_datetime(df["time"])
    return df


def test_monthly_series_sums_multiple_rows_in_the_same_month():
    """Simulates weekly rows rolling up into one monthly total."""
    data = _data(
        [
            {"adm_0_name": "Testland", "time": "2020-01-05", "dengue_total": 3,
             "case_definition_standardised": "Confirmed"},
            {"adm_0_name": "Testland", "time": "2020-01-19", "dengue_total": 4,
             "case_definition_standardised": "Confirmed"},
            {"adm_0_name": "Testland", "time": "2020-02-02", "dengue_total": 5,
             "case_definition_standardised": "Confirmed"},
        ]
    )
    track = Track("Testland", "Confirmed", pd.Period("2020-01"), pd.Period("2020-02"), 2, 0, False)
    series = monthly_series(data, ROLE_CONFIG, track)
    assert series.loc[pd.Period("2020-01")] == 7
    assert series.loc[pd.Period("2020-02")] == 5


def test_monthly_series_reindexes_missing_months_as_nan():
    data = _data(
        [
            {"adm_0_name": "Testland", "time": "2020-01-01", "dengue_total": 1,
             "case_definition_standardised": "Confirmed"},
            {"adm_0_name": "Testland", "time": "2020-03-01", "dengue_total": 1,
             "case_definition_standardised": "Confirmed"},
        ]
    )
    track = Track("Testland", "Confirmed", pd.Period("2020-01"), pd.Period("2020-03"), 3, 1, False)
    series = monthly_series(data, ROLE_CONFIG, track)
    assert len(series) == 3
    assert pd.isna(series.loc[pd.Period("2020-02")])


def test_monthly_series_filters_by_country_and_case_definition():
    data = _data(
        [
            {"adm_0_name": "Testland", "time": "2020-01-01", "dengue_total": 100,
             "case_definition_standardised": "Total"},
            {"adm_0_name": "Testland", "time": "2020-01-01", "dengue_total": 5,
             "case_definition_standardised": "Confirmed"},
            {"adm_0_name": "Otherland", "time": "2020-01-01", "dengue_total": 999,
             "case_definition_standardised": "Confirmed"},
        ]
    )
    track = Track("Testland", "Confirmed", pd.Period("2020-01"), pd.Period("2020-01"), 1, 0, False)
    series = monthly_series(data, ROLE_CONFIG, track)
    assert series.loc[pd.Period("2020-01")] == 5


def test_monthly_series_case_definition_none_includes_all_rows():
    data = _data(
        [
            {"adm_0_name": "Testland", "time": "2020-01-01", "dengue_total": 3,
             "case_definition_standardised": "Total"},
            {"adm_0_name": "Testland", "time": "2020-01-05", "dengue_total": 4,
             "case_definition_standardised": "Confirmed"},
        ]
    )
    track = Track("Testland", None, pd.Period("2020-01"), pd.Period("2020-01"), 1, 0, False)
    series = monthly_series(data, ROLE_CONFIG, track)
    assert series.loc[pd.Period("2020-01")] == 7


def test_monthly_series_does_not_mutate_input():
    data = _data(
        [{"adm_0_name": "Testland", "time": "2020-01-01", "dengue_total": 1,
          "case_definition_standardised": "Confirmed"}]
    )
    original = data.copy(deep=True)
    track = Track("Testland", "Confirmed", pd.Period("2020-01"), pd.Period("2020-01"), 1, 0, False)
    monthly_series(data, ROLE_CONFIG, track)
    pd.testing.assert_frame_equal(data, original)


def test_population_rate_applies_annual_value_to_every_month_in_year():
    counts = pd.Series(
        [10, 20, 30],
        index=pd.period_range("2020-01", periods=3, freq="M"),
    )
    population = pd.Series({2020: 1_000_000})
    rate = population_rate(counts, population)
    assert rate.loc[pd.Period("2020-01")] == pytest.approx(1.0)
    assert rate.loc[pd.Period("2020-02")] == pytest.approx(2.0)
    assert rate.loc[pd.Period("2020-03")] == pytest.approx(3.0)


def test_population_rate_uses_correct_year_when_series_spans_years():
    counts = pd.Series(
        [10, 20],
        index=[pd.Period("2020-12"), pd.Period("2021-01")],
    )
    population = pd.Series({2020: 1_000_000, 2021: 2_000_000})
    rate = population_rate(counts, population)
    assert rate.loc[pd.Period("2020-12")] == pytest.approx(1.0)
    assert rate.loc[pd.Period("2021-01")] == pytest.approx(1.0)


def test_population_rate_missing_year_yields_nan_not_fabricated_value():
    counts = pd.Series([10], index=[pd.Period("2020-01")])
    population = pd.Series({2019: 1_000_000})  # 2020 absent
    rate = population_rate(counts, population)
    assert pd.isna(rate.loc[pd.Period("2020-01")])
