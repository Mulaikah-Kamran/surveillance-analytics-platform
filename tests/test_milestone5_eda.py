"""Milestone 5 tests: Exploratory Data Analysis.

Exercises the frozen M5 contract: descriptive statistics and
distribution summary for the configured Surveillance Measure only,
post-cleaning missingness, the ``T_res`` / ``case_definition_standardised``
interpretation checks (overall distribution, country-level
distribution, generic — not hard-coded — country-year homogeneity
flagging), annual time-series summaries, country comparisons, and
optional population normalization. Uses a small, deterministic
synthetic dataframe shaped like Milestone 4's *output* (i.e. already
containing the derived ``time`` column) — no real OpenDengue data or
network access is required.
"""

import pandas as pd
import pytest

from surveillance_platform.eda import EDAResult, analyze
from surveillance_platform.eda.country_comparison import country_comparison
from surveillance_platform.eda.descriptive import (
    case_definition_summary,
    descriptive_statistics,
    distribution_summary,
    resolution_summary,
)
from surveillance_platform.eda.missingness import missingness_summary
from surveillance_platform.eda.population import population_normalized_summary
from surveillance_platform.eda.time_series import time_series_summary
from surveillance_platform.role_configuration import RoleConfiguration

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _synthetic_dataset() -> pd.DataFrame:
    """Shaped like M4's *output*: already has the derived ``time`` column.

    * Sri Lanka 2020 — 3 rows, homogeneous ``T_res`` ("Week") and
      homogeneous ``case_definition_standardised`` ("Total").
    * Sri Lanka 2021 — 2 rows, heterogeneous ``T_res`` ("Week"/"Month").
    * Bangladesh 2021 — 3 rows, heterogeneous ``case_definition_standardised``
      ("Confirmed"/"Confirmed"/"Total"); homogeneous ``T_res``.
    * Bangladesh 2022 — 2 rows, fully homogeneous.
    * Nepal 2019 and Nepal 2023 — 1 row each, a 4-year reporting gap.
    * Maldives 2020 — 2 rows, one with a missing Surveillance Measure value.
    """
    rows = [
        # country, year, dengue_total, T_res, case_definition
        ("Sri Lanka", "2020-01-01", 10, "Week", "Total"),
        ("Sri Lanka", "2020-01-08", 0, "Week", "Total"),
        ("Sri Lanka", "2020-01-15", 5, "Week", "Total"),
        ("Sri Lanka", "2021-01-01", 8, "Week", "Total"),
        ("Sri Lanka", "2021-02-01", 12, "Month", "Total"),
        ("Bangladesh", "2021-01-01", 3, "Month", "Confirmed"),
        ("Bangladesh", "2021-02-01", 4, "Month", "Confirmed"),
        ("Bangladesh", "2021-10-01", 6, "Month", "Total"),
        ("Bangladesh", "2022-01-01", 7, "Month", "Confirmed"),
        ("Bangladesh", "2022-02-01", 2, "Month", "Confirmed"),
        ("Nepal", "2019-06-01", 1, "Year", "Total"),
        ("Nepal", "2023-06-01", 9, "Year", "Total"),
        ("Maldives", "2020-01-01", 0, "Month", "Total"),
        ("Maldives", "2020-02-01", None, "Month", "Total"),
    ]
    data = pd.DataFrame(
        rows,
        columns=[
            "adm_0_name",
            "calendar_start_date",
            "dengue_total",
            "T_res",
            "case_definition_standardised",
        ],
    )
    data["time"] = pd.to_datetime(data["calendar_start_date"]).astype("datetime64[ns]")
    return data


def _population_dataset() -> pd.DataFrame:
    """Only covers a subset of country-years present in the fixture, to
    exercise graceful skipping of missing population figures."""
    return pd.DataFrame(
        {
            "country": ["Sri Lanka", "Sri Lanka", "Bangladesh"],
            "year": [2020, 2021, 2021],
            "population": [21_800_000, 22_000_000, 169_000_000],
        }
    )


# ---------------------------------------------------------------------
# Descriptive statistics / distribution summary
# ---------------------------------------------------------------------


def test_descriptive_statistics_normal_numeric_input():
    data = _synthetic_dataset()
    result = descriptive_statistics(data, ROLE_CONFIG)
    assert result.count == 13  # one row has a missing dengue_total
    assert result.minimum == 0
    assert result.maximum == 12


def test_descriptive_statistics_handles_missing_values():
    data = _synthetic_dataset()
    result = descriptive_statistics(data, ROLE_CONFIG)
    # 14 rows total, 1 missing -> count reflects only non-null values.
    assert result.count == len(data) - 1


def test_descriptive_statistics_uses_role_configuration_not_hardcoded_name():
    data = _synthetic_dataset().rename(columns={"dengue_total": "case_count"})
    renamed_config = RoleConfiguration(
        time="calendar_start_date",
        location="adm_0_name",
        surveillance_measure="case_count",
        identifier=None,
    )
    result = descriptive_statistics(data, renamed_config)
    assert result.count == 13


def test_distribution_summary_reports_zero_value_share():
    data = _synthetic_dataset()
    result = distribution_summary(data, ROLE_CONFIG)
    # 2 zero values out of 13 non-null values.
    assert result.zero_value_share == pytest.approx(2 / 13)


def test_resolution_summary_overall_distribution():
    data = _synthetic_dataset()
    result = resolution_summary(data)
    assert result.counts["Week"] == 4
    assert result.counts["Month"] == 8
    assert result.counts["Year"] == 2


def test_resolution_summary_degrades_gracefully_when_absent():
    data = _synthetic_dataset().drop(columns=["T_res"])
    assert resolution_summary(data) is None


def test_case_definition_summary_overall_distribution():
    data = _synthetic_dataset()
    result = case_definition_summary(data)
    assert result.counts["Total"] == 10
    assert result.counts["Confirmed"] == 4


def test_case_definition_summary_degrades_gracefully_when_absent():
    data = _synthetic_dataset().drop(columns=["case_definition_standardised"])
    assert case_definition_summary(data) is None


# ---------------------------------------------------------------------
# Missingness
# ---------------------------------------------------------------------


def test_missingness_summary_complete_data():
    data = _synthetic_dataset().drop(columns=["dengue_total"])
    result = missingness_summary(data)
    assert result.missing_counts["adm_0_name"] == 0
    assert result.missing_fractions["adm_0_name"] == 0.0


def test_missingness_summary_partial_missingness():
    data = _synthetic_dataset()
    result = missingness_summary(data)
    assert result.missing_counts["dengue_total"] == 1
    assert result.missing_fractions["dengue_total"] == pytest.approx(1 / 14)


def test_missingness_summary_does_not_mutate_input():
    data = _synthetic_dataset()
    original = data.copy()
    missingness_summary(data)
    pd.testing.assert_frame_equal(data, original)


# ---------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------


def test_time_series_groups_by_country_and_year():
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    keys = {(cy.country, cy.year) for cy in result.country_years}
    assert ("Sri Lanka", 2020) in keys
    assert ("Sri Lanka", 2021) in keys
    assert ("Bangladesh", 2021) in keys
    assert ("Nepal", 2019) in keys
    assert ("Nepal", 2023) in keys


def test_time_series_annual_aggregate_is_correct():
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    sri_lanka_2020 = next(
        cy
        for cy in result.country_years
        if cy.country == "Sri Lanka" and cy.year == 2020
    )
    assert sri_lanka_2020.reported_case_total == 15  # 10 + 0 + 5
    assert sri_lanka_2020.observation_count == 3


def test_time_series_flags_homogeneous_resolution():
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    sri_lanka_2020 = next(
        cy
        for cy in result.country_years
        if cy.country == "Sri Lanka" and cy.year == 2020
    )
    assert sri_lanka_2020.resolution_homogeneous is True


def test_time_series_flags_heterogeneous_resolution_generically():
    """The heterogeneous-resolution country-year is discovered by the
    generic homogeneity check, not hard-coded to a specific country/year."""
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    flagged = [cy for cy in result.country_years if cy.resolution_homogeneous is False]
    assert len(flagged) == 1
    assert (flagged[0].country, flagged[0].year) == ("Sri Lanka", 2021)
    # The aggregate is still produced, not discarded, for the flagged group.
    assert flagged[0].reported_case_total == 20  # 8 + 12


def test_time_series_flags_homogeneous_case_definition():
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    bangladesh_2022 = next(
        cy
        for cy in result.country_years
        if cy.country == "Bangladesh" and cy.year == 2022
    )
    assert bangladesh_2022.case_definition_homogeneous is True


def test_time_series_flags_heterogeneous_case_definition_generically():
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    flagged = [
        cy for cy in result.country_years if cy.case_definition_homogeneous is False
    ]
    assert len(flagged) == 1
    assert (flagged[0].country, flagged[0].year) == ("Bangladesh", 2021)
    # Still produced, not discarded or corrected.
    assert flagged[0].reported_case_total == 13  # 3 + 4 + 6


def test_time_series_homogeneity_flags_degrade_gracefully_when_columns_absent():
    data = _synthetic_dataset().drop(columns=["T_res", "case_definition_standardised"])
    result = time_series_summary(data, ROLE_CONFIG)
    assert all(cy.resolution_homogeneous is None for cy in result.country_years)
    assert all(cy.case_definition_homogeneous is None for cy in result.country_years)


def test_time_series_reports_max_year_gap():
    data = _synthetic_dataset()
    result = time_series_summary(data, ROLE_CONFIG)
    nepal_gap = next(g for g in result.gaps if g.country == "Nepal")
    assert nepal_gap.max_year_gap == 4  # 2023 - 2019
    sri_lanka_gap = next(g for g in result.gaps if g.country == "Sri Lanka")
    assert sri_lanka_gap.max_year_gap == 1  # consecutive years


def test_time_series_does_not_mutate_input():
    data = _synthetic_dataset()
    original = data.copy()
    time_series_summary(data, ROLE_CONFIG)
    pd.testing.assert_frame_equal(data, original)


# ---------------------------------------------------------------------
# Country comparison
# ---------------------------------------------------------------------


def test_country_comparison_covers_every_country_present():
    data = _synthetic_dataset()
    result = country_comparison(data, ROLE_CONFIG)
    countries = {entry.country for entry in result.countries}
    assert countries == {"Sri Lanka", "Bangladesh", "Nepal", "Maldives"}


def test_country_comparison_descriptive_statistics_per_country():
    data = _synthetic_dataset()
    result = country_comparison(data, ROLE_CONFIG)
    sri_lanka = next(e for e in result.countries if e.country == "Sri Lanka")
    assert sri_lanka.descriptive.count == 5
    assert sri_lanka.observation_count == 5


def test_country_comparison_temporal_coverage_per_country():
    data = _synthetic_dataset()
    result = country_comparison(data, ROLE_CONFIG)
    nepal = next(e for e in result.countries if e.country == "Nepal")
    assert nepal.first_date == pd.Timestamp("2019-06-01")
    assert nepal.last_date == pd.Timestamp("2023-06-01")


def test_country_comparison_missingness_per_country():
    data = _synthetic_dataset()
    result = country_comparison(data, ROLE_CONFIG)
    maldives = next(e for e in result.countries if e.country == "Maldives")
    assert maldives.missingness.missing_counts["dengue_total"] == 1


def test_country_comparison_categorical_distributions_per_country():
    data = _synthetic_dataset()
    result = country_comparison(data, ROLE_CONFIG)
    bangladesh = next(e for e in result.countries if e.country == "Bangladesh")
    assert bangladesh.case_definition_distribution.counts["Confirmed"] == 4
    assert bangladesh.case_definition_distribution.counts["Total"] == 1
    assert bangladesh.resolution_distribution.counts["Month"] == 5


def _invalid_population_dataset() -> pd.DataFrame:
    """One valid figure plus one each of zero, negative, and missing/NaN
    population, to exercise the invalid-population guard directly."""
    return pd.DataFrame(
        {
            "country": ["Sri Lanka", "Sri Lanka", "Bangladesh", "Bangladesh"],
            "year": [2020, 2021, 2021, 2022],
            "population": [21_800_000, 0, -169_000_000, float("nan")],
        }
    )


# ---------------------------------------------------------------------
# Population normalization
# ---------------------------------------------------------------------


def test_population_normalization_correct_annual_join_and_rate():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _population_dataset())
    sri_lanka_2020 = next(
        r for r in result.rates if r.country == "Sri Lanka" and r.year == 2020
    )
    # 15 reported cases / 21,800,000 population * 100,000
    assert sri_lanka_2020.reported_cases_per_100000 == pytest.approx(
        15 / 21_800_000 * 100_000
    )


def test_population_normalization_omitted_input_returns_none():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    assert population_normalized_summary(time_series, None) is None


def test_population_normalization_handles_missing_country_year_gracefully():
    """Nepal/Maldives have no matching rows in the small population
    fixture — those (country, year) pairs are skipped, not an error."""
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _population_dataset())
    covered_keys = {(r.country, r.year) for r in result.rates}
    assert ("Nepal", 2019) not in covered_keys
    assert ("Maldives", 2020) not in covered_keys
    # But the country-years that ARE covered are still present.
    assert ("Bangladesh", 2021) in covered_keys


def test_population_normalization_does_not_mutate_population_data():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    population_data = _population_dataset()
    original = population_data.copy()
    population_normalized_summary(time_series, population_data)
    pd.testing.assert_frame_equal(population_data, original)


def test_population_normalization_valid_positive_population_produces_rate():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _invalid_population_dataset())
    covered = {(r.country, r.year): r for r in result.rates}
    assert ("Sri Lanka", 2020) in covered
    assert covered[("Sri Lanka", 2020)].reported_cases_per_100000 == pytest.approx(
        15 / 21_800_000 * 100_000
    )


def test_population_normalization_zero_population_is_skipped():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _invalid_population_dataset())
    covered = {(r.country, r.year) for r in result.rates}
    assert ("Sri Lanka", 2021) not in covered


def test_population_normalization_negative_population_is_skipped():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _invalid_population_dataset())
    covered = {(r.country, r.year) for r in result.rates}
    assert ("Bangladesh", 2021) not in covered


def test_population_normalization_missing_or_nan_population_is_skipped():
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _invalid_population_dataset())
    covered = {(r.country, r.year) for r in result.rates}
    assert ("Bangladesh", 2022) not in covered


def test_population_normalization_invalid_values_do_not_crash_pipeline():
    """The guard's whole point: an invalid external population value
    must not raise, only skip that one observation."""
    data = _synthetic_dataset()
    time_series = time_series_summary(data, ROLE_CONFIG)
    result = population_normalized_summary(time_series, _invalid_population_dataset())
    assert result is not None
    assert len(result.rates) == 1  # only the one valid figure produced a rate


# ---------------------------------------------------------------------
# API / orchestration
# ---------------------------------------------------------------------


def test_analyze_returns_eda_result():
    data = _synthetic_dataset()
    result = analyze(data, ROLE_CONFIG)
    assert isinstance(result, EDAResult)
    assert result.descriptive.count == 13
    assert result.population_normalized is None


def test_analyze_with_population_data_populates_population_normalized():
    data = _synthetic_dataset()
    result = analyze(data, ROLE_CONFIG, population_data=_population_dataset())
    assert result.population_normalized is not None
    assert len(result.population_normalized.rates) > 0


def test_analyze_uses_role_configuration_not_hardcoded_columns():
    data = _synthetic_dataset().rename(
        columns={"adm_0_name": "country_name", "dengue_total": "case_count"}
    )
    renamed_config = RoleConfiguration(
        time="calendar_start_date",
        location="country_name",
        surveillance_measure="case_count",
        identifier=None,
    )
    result = analyze(data, renamed_config)
    assert result.descriptive.count == 13
    countries = {entry.country for entry in result.country_comparison.countries}
    assert countries == {"Sri Lanka", "Bangladesh", "Nepal", "Maldives"}


def test_analyze_does_not_mutate_input_dataframe():
    data = _synthetic_dataset()
    original = data.copy()
    population_data = _population_dataset()
    population_original = population_data.copy()
    analyze(data, ROLE_CONFIG, population_data=population_data)
    pd.testing.assert_frame_equal(data, original)
    pd.testing.assert_frame_equal(population_data, population_original)


def test_analyze_is_deterministic():
    data = _synthetic_dataset()
    result_a = analyze(data, ROLE_CONFIG)
    result_b = analyze(data, ROLE_CONFIG)
    assert result_a.descriptive == result_b.descriptive
    assert len(result_a.time_series.country_years) == len(
        result_b.time_series.country_years
    )
