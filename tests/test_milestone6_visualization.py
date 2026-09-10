"""Milestone 6 tests: Visualization.

Exercises the frozen M6 contract: the five finalized visualizations
built purely from an ``EDAResult`` (never ``prepared_data``), small
multiples for the annual trend, propagation of M5's generic (never
hard-coded) heterogeneity flags, graceful omission of the optional
population-normalized visualization, non-mutation of the input
``EDAResult``, and graceful failure on empty analytical input. Reuses
the same small, deterministic synthetic dataframe fixture already
established in ``test_milestone5_eda.py`` so results are directly
comparable, and runs M6 on top of the real ``analyze()`` output rather
than hand-built ``EDAResult`` instances wherever practical.
"""

from __future__ import annotations

import copy
import dataclasses
import math

import pandas as pd
import plotly.graph_objects as go
import pytest

from surveillance_platform.eda import EDAResult, analyze
from surveillance_platform.eda.report import (
    CountryComparison,
    DescriptiveSummary,
    DistributionSummary,
    MissingnessSummary,
    PopulationNormalizedSummary,
    TimeSeriesSummary,
)
from surveillance_platform.role_configuration import RoleConfiguration
from surveillance_platform.visualization import (
    VisualizationResult,
    annual_distribution_by_country,
    annual_surveillance_trend,
    population_normalized_distribution,
    surveillance_measure_distribution,
    surveillance_resolution_profile,
    visualize,
)
from surveillance_platform.visualization._theme import EmptyVisualizationInputError

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _synthetic_dataset() -> pd.DataFrame:
    """Same fixture as ``test_milestone5_eda.py`` (see that module for the
    full per-row rationale): Sri Lanka 2021 has heterogeneous ``T_res``;
    Bangladesh 2021 has heterogeneous ``case_definition_standardised``;
    every other country-year is fully homogeneous.
    """
    rows = [
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
    return pd.DataFrame(
        {
            "country": ["Sri Lanka", "Sri Lanka", "Bangladesh"],
            "year": [2020, 2021, 2021],
            "population": [21_800_000, 22_000_000, 169_000_000],
        }
    )


@pytest.fixture
def eda_result() -> EDAResult:
    return analyze(_synthetic_dataset(), ROLE_CONFIG, population_data=None)


@pytest.fixture
def eda_result_with_population() -> EDAResult:
    return analyze(
        _synthetic_dataset(), ROLE_CONFIG, population_data=_population_dataset()
    )


def _empty_eda_result() -> EDAResult:
    """An EDAResult with genuinely no analytical content, for the
    graceful-failure tests. Not something ``analyze()`` would ever
    naturally produce from a non-empty dataset, but a legitimate shape
    for a caller to hand M6 directly.
    """
    return EDAResult(
        descriptive=DescriptiveSummary(
            count=0, mean=0.0, median=0.0, minimum=0.0, maximum=0.0, std=0.0
        ),
        distribution=DistributionSummary(
            q25=0.0, q50=0.0, q75=0.0, zero_value_share=0.0
        ),
        missingness=MissingnessSummary(row_count=0),
        resolution=None,
        case_definition=None,
        time_series=TimeSeriesSummary(country_years=[], gaps=[]),
        country_comparison=CountryComparison(countries=[]),
        population_normalized=None,
    )


# ---------------------------------------------------------------------
# Each required visualization can be generated from an EDAResult
# ---------------------------------------------------------------------


def test_annual_surveillance_trend_generates_figure(eda_result):
    figure = annual_surveillance_trend(eda_result)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) > 0


def test_annual_distribution_by_country_generates_figure(eda_result):
    figure = annual_distribution_by_country(eda_result)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) > 0


def test_surveillance_measure_distribution_generates_figure(eda_result):
    figure = surveillance_measure_distribution(eda_result)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


def test_surveillance_resolution_profile_generates_figure(eda_result):
    figure = surveillance_resolution_profile(eda_result)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 2  # T_res panel + case_definition panel


def test_population_normalized_distribution_generates_figure(
    eda_result_with_population,
):
    figure = population_normalized_distribution(eda_result_with_population)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) > 0


def test_visualize_orchestrator_produces_all_five(eda_result_with_population):
    result = visualize(eda_result_with_population)
    assert isinstance(result, VisualizationResult)
    assert isinstance(result.annual_trend, go.Figure)
    assert isinstance(result.annual_distribution_by_country, go.Figure)
    assert isinstance(result.surveillance_measure_distribution, go.Figure)
    assert isinstance(result.population_normalized_distribution, go.Figure)
    assert isinstance(result.surveillance_profile, go.Figure)


# ---------------------------------------------------------------------
# Correct analytical results are represented / country-year structure
# ---------------------------------------------------------------------


def test_annual_trend_uses_reported_case_totals_not_raw_rows(eda_result):
    figure = annual_surveillance_trend(eda_result)
    sri_lanka_trace = next(t for t in figure.data if t.name == "Sri Lanka")
    # Sri Lanka has two country-years: 2020 (10+0+5=15) and 2021 (8+12=20).
    assert list(sri_lanka_trace.x) == [2020, 2021]
    assert list(sri_lanka_trace.y) == [15.0, 20.0]


def test_annual_trend_preserves_all_countries(eda_result):
    figure = annual_surveillance_trend(eda_result)
    plotted_countries = {t.name for t in figure.data}
    expected_countries = {
        entry.country for entry in eda_result.time_series.country_years
    }
    assert plotted_countries == expected_countries


def test_annual_distribution_preserves_country_structure(eda_result):
    figure = annual_distribution_by_country(eda_result)
    plotted_countries = {t.name for t in figure.data}
    expected_countries = {
        entry.country for entry in eda_result.time_series.country_years
    }
    assert plotted_countries == expected_countries


def test_surveillance_measure_distribution_matches_m5_summary(eda_result):
    figure = surveillance_measure_distribution(eda_result)
    box = figure.data[0]
    assert box.q1[0] == eda_result.distribution.q25
    assert box.median[0] == eda_result.distribution.q50
    assert box.q3[0] == eda_result.distribution.q75
    assert box.lowerfence[0] == eda_result.descriptive.minimum
    assert box.upperfence[0] == eda_result.descriptive.maximum


def test_population_normalized_distribution_uses_rate_not_raw_total(
    eda_result_with_population,
):
    figure = population_normalized_distribution(eda_result_with_population)
    sri_lanka_trace = next(t for t in figure.data if t.name == "Sri Lanka")
    expected = [
        entry.reported_cases_per_100000
        for entry in eda_result_with_population.population_normalized.rates
        if entry.country == "Sri Lanka"
    ]
    assert sorted(sri_lanka_trace.y) == sorted(expected)


def test_surveillance_resolution_profile_reflects_m5_counts(eda_result):
    figure = surveillance_resolution_profile(eda_result)
    resolution_trace = figure.data[0]
    expected = eda_result.resolution.counts
    plotted = dict(zip(resolution_trace.x, resolution_trace.y))
    assert plotted == expected


# ---------------------------------------------------------------------
# Heterogeneity flags are propagated to the annual trend
# ---------------------------------------------------------------------


def test_heterogeneity_flags_are_visibly_distinguishable(eda_result):
    figure = annual_surveillance_trend(eda_result)

    sri_lanka_trace = next(t for t in figure.data if t.name == "Sri Lanka")
    # Sri Lanka 2021 has heterogeneous T_res -> flagged (index 1).
    assert sri_lanka_trace.marker.symbol[0] == "circle"
    assert sri_lanka_trace.marker.symbol[1] == "diamond"
    assert "⚠" in sri_lanka_trace.hovertext[1]
    assert "⚠" not in sri_lanka_trace.hovertext[0]

    bangladesh_trace = next(t for t in figure.data if t.name == "Bangladesh")
    # Bangladesh 2021 has heterogeneous case_definition_standardised
    # (index 0); 2022 is homogeneous (index 1).
    assert bangladesh_trace.marker.symbol[0] == "diamond"
    assert bangladesh_trace.marker.symbol[1] == "circle"
    assert "⚠" in bangladesh_trace.hovertext[0]


def test_heterogeneity_flags_are_generic_not_hardcoded():
    """A dataset where a *different* country-year is heterogeneous should
    flag that one instead — proving the flag is read from M5's generic
    per-country-year output, not hard-coded to Bangladesh 2021.
    """
    rows = [
        ("Nepal", "2020-01-01", 5, "Week", "Confirmed"),
        ("Nepal", "2020-06-01", 5, "Month", "Total"),  # heterogeneous T_res
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
    result = analyze(data, ROLE_CONFIG, population_data=None)
    figure = annual_surveillance_trend(result)
    nepal_trace = next(t for t in figure.data if t.name == "Nepal")
    assert "⚠" in nepal_trace.hovertext[0]
    assert "reporting resolution changed mid-year" in nepal_trace.hovertext[0]


def test_homogeneous_dataset_has_no_heterogeneity_markers():
    rows = [
        ("Nepal", "2020-01-01", 5, "Week", "Confirmed"),
        ("Nepal", "2020-01-08", 5, "Week", "Confirmed"),
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
    result = analyze(data, ROLE_CONFIG, population_data=None)
    figure = annual_surveillance_trend(result)
    for trace in figure.data:
        assert all("⚠" not in text for text in trace.hovertext)


# ---------------------------------------------------------------------
# Population-normalized visualization is omitted when unavailable
# ---------------------------------------------------------------------


def test_population_normalized_distribution_omitted_when_none(eda_result):
    # eda_result fixture was built with population_data=None.
    assert eda_result.population_normalized is None
    assert population_normalized_distribution(eda_result) is None


def test_population_normalized_distribution_omitted_when_rates_empty(eda_result):
    result_with_empty_rates = EDAResult(
        descriptive=eda_result.descriptive,
        distribution=eda_result.distribution,
        missingness=eda_result.missingness,
        resolution=eda_result.resolution,
        case_definition=eda_result.case_definition,
        time_series=eda_result.time_series,
        country_comparison=eda_result.country_comparison,
        population_normalized=PopulationNormalizedSummary(rates=[]),
    )
    assert population_normalized_distribution(result_with_empty_rates) is None


def test_visualize_orchestrator_omits_population_visualization(eda_result):
    result = visualize(eda_result)
    assert result.population_normalized_distribution is None
    # Every other visualization is still produced normally.
    assert isinstance(result.annual_trend, go.Figure)
    assert isinstance(result.annual_distribution_by_country, go.Figure)
    assert isinstance(result.surveillance_measure_distribution, go.Figure)


def test_surveillance_resolution_profile_omitted_when_both_columns_absent(
    eda_result,
):
    result_without_metadata = EDAResult(
        descriptive=eda_result.descriptive,
        distribution=eda_result.distribution,
        missingness=eda_result.missingness,
        resolution=None,
        case_definition=None,
        time_series=eda_result.time_series,
        country_comparison=eda_result.country_comparison,
        population_normalized=None,
    )
    assert surveillance_resolution_profile(result_without_metadata) is None


def test_surveillance_resolution_profile_renders_partial_metadata(eda_result):
    result_resolution_only = EDAResult(
        descriptive=eda_result.descriptive,
        distribution=eda_result.distribution,
        missingness=eda_result.missingness,
        resolution=eda_result.resolution,
        case_definition=None,
        time_series=eda_result.time_series,
        country_comparison=eda_result.country_comparison,
        population_normalized=None,
    )
    figure = surveillance_resolution_profile(result_resolution_only)
    assert isinstance(figure, go.Figure)
    assert len(figure.data) == 1


# ---------------------------------------------------------------------
# Visualization functions do not mutate EDAResult
# ---------------------------------------------------------------------


def _nan_safe_equal(left: object, right: object) -> bool:
    """Structural equality that treats ``NaN == NaN`` as equal.

    Plain Python/dataclass ``==`` follows IEEE 754 (``NaN != NaN``), so
    a straight ``eda_result == before`` comparison can spuriously fail
    an immutability check even when nothing was mutated, whenever a
    field is genuinely ``NaN`` in both objects (e.g. a per-country
    standard deviation computed from a single observation, as in the
    Maldives 2020 fixture row). This recurses through dataclasses,
    dicts, lists, and tuples, and only special-cases ``float`` NaN —
    every other field still uses ordinary ``==``, so a real mutation
    is still caught.
    """
    if dataclasses.is_dataclass(left) and dataclasses.is_dataclass(right):
        if type(left) is not type(right):
            return False
        return all(
            _nan_safe_equal(getattr(left, field.name), getattr(right, field.name))
            for field in dataclasses.fields(left)
        )
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _nan_safe_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(
            _nan_safe_equal(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, float) and isinstance(right, float):
        if math.isnan(left) and math.isnan(right):
            return True
        return left == right
    return left == right


def test_visualize_does_not_mutate_eda_result(eda_result_with_population):
    before = copy.deepcopy(eda_result_with_population)
    visualize(eda_result_with_population)
    assert _nan_safe_equal(eda_result_with_population, before)


def test_individual_functions_do_not_mutate_eda_result(eda_result_with_population):
    before = copy.deepcopy(eda_result_with_population)
    annual_surveillance_trend(eda_result_with_population)
    annual_distribution_by_country(eda_result_with_population)
    surveillance_measure_distribution(eda_result_with_population)
    population_normalized_distribution(eda_result_with_population)
    surveillance_resolution_profile(eda_result_with_population)
    assert _nan_safe_equal(eda_result_with_population, before)


# ---------------------------------------------------------------------
# Empty/partial analytical results fail gracefully where appropriate
# ---------------------------------------------------------------------


def test_annual_trend_raises_clear_error_on_empty_time_series():
    with pytest.raises(EmptyVisualizationInputError):
        annual_surveillance_trend(_empty_eda_result())


def test_annual_distribution_raises_clear_error_on_empty_time_series():
    with pytest.raises(EmptyVisualizationInputError):
        annual_distribution_by_country(_empty_eda_result())


def test_surveillance_measure_distribution_raises_clear_error_on_zero_count():
    with pytest.raises(EmptyVisualizationInputError):
        surveillance_measure_distribution(_empty_eda_result())


def test_surveillance_resolution_profile_returns_none_not_error_on_empty_result():
    # Both resolution and case_definition are None on the empty fixture —
    # this is the *optional* graceful-omission path, not an error.
    assert surveillance_resolution_profile(_empty_eda_result()) is None


def test_population_normalized_distribution_returns_none_not_error_on_empty_result():
    assert population_normalized_distribution(_empty_eda_result()) is None
