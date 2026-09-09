"""Milestone 7 integration tests: the full forecast() pipeline (ADR-009).

Uses a synthetic series just long enough to be eligible (78 months,
above the 72-month floor) to keep the test fast while still
exercising every stage: track detection, aggregation, population
normalization, SARIMA + baseline, backtest, and residual diagnostics.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from surveillance_platform.forecasting import ForecastResult, forecast, forecast_track
from surveillance_platform.forecasting.eligibility import detect_tracks
from surveillance_platform.forecasting.model import SEASONAL_PERIOD
from surveillance_platform.role_configuration import RoleConfiguration

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _seasonal_country_data(country: str, n_months: int, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n_months)
    seasonal = 50 + 40 * np.sin(2 * np.pi * t / SEASONAL_PERIOD)
    values = np.clip(seasonal + rng.normal(0, 5, n_months), 0, None).round()
    periods = pd.period_range("2010-01", periods=n_months, freq="M")
    return pd.DataFrame(
        {
            "adm_0_name": country,
            "time": periods.to_timestamp(),
            "dengue_total": values,
            "T_res": "Month",
            "case_definition_standardised": "Confirmed",
        }
    )


def _population(start_year: int = 2010, n_years: int = 12) -> pd.Series:
    years = range(start_year, start_year + n_years)
    return pd.Series({y: 10_000_000 for y in years})


def test_forecast_returns_one_result_per_detected_track():
    eligible = _seasonal_country_data("Eligiland", 78)
    ineligible = _seasonal_country_data("Ineligiland", 20)
    data = pd.concat([eligible, ineligible], ignore_index=True)
    population = {"Eligiland": _population(), "Ineligiland": _population()}

    results = forecast(data, ROLE_CONFIG, population)
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(results) == len(tracks)
    assert all(isinstance(r, ForecastResult) for r in results)


def test_eligible_track_produces_full_result():
    data = _seasonal_country_data("Eligiland", 78)
    population = {"Eligiland": _population()}
    [result] = forecast(data, ROLE_CONFIG, population)

    assert result.track.eligible is True
    assert result.model_order is not None
    assert len(result.forecast_mean) == 3
    assert all(v >= 0 for v in result.forecast_mean)
    assert all(v >= 0 for v in result.forecast_lower)
    assert result.model_metrics is not None
    assert result.baseline_metrics is not None
    assert result.residual_diagnostics is not None
    assert result.limitations == []


def test_ineligible_track_is_illustrative_only_no_backtest():
    data = _seasonal_country_data("Shortland", 20)
    population = {"Shortland": _population()}
    [result] = forecast(data, ROLE_CONFIG, population)

    assert result.track.eligible is False
    assert result.backtest_records == []
    assert result.model_metrics is None
    assert result.baseline_metrics is None
    assert any("eligibility floor" in msg for msg in result.limitations)
    assert any("no backtest is possible" in msg for msg in result.limitations)
    # An illustrative forecast should still be produced, not withheld.
    assert len(result.forecast_mean) == 3


def test_missing_population_data_produces_documented_empty_result():
    data = _seasonal_country_data("Nopopland", 78)
    [result] = forecast(data, ROLE_CONFIG, population_by_country={})

    assert result.forecast_mean == []
    assert result.model_order is None
    assert any("No population data available" in msg for msg in result.limitations)


def test_forecast_track_matches_forecast_for_a_single_track():
    """forecast_track() on one detected track should match the
    corresponding entry from the full forecast() orchestration.
    """
    data = _seasonal_country_data("Eligiland", 78)
    population = {"Eligiland": _population()}
    [track] = detect_tracks(data, ROLE_CONFIG)
    direct_result = forecast_track(data, ROLE_CONFIG, track, population["Eligiland"])
    [orchestrated_result] = forecast(data, ROLE_CONFIG, population)

    assert direct_result.track == orchestrated_result.track
    assert direct_result.model_order == orchestrated_result.model_order


def test_forecast_does_not_mutate_input():
    data = _seasonal_country_data("Eligiland", 78)
    original = data.copy(deep=True)
    forecast(data, ROLE_CONFIG, {"Eligiland": _population()})
    pd.testing.assert_frame_equal(data, original)


def test_forecast_with_no_tracks_returns_empty_list():
    data = _seasonal_country_data("Eligiland", 78).iloc[0:0]
    results = forecast(data, ROLE_CONFIG, {})
    assert results == []


def test_forecast_track_default_none_callbacks_are_backward_compatible():
    """ADR-009 addendum (2026-09-09): on_candidate/on_origin default to
    None and must not change forecast_track()'s behavior -- the
    regression guarantee this addendum depends on.
    """
    data = _seasonal_country_data("Eligiland", 78)
    [track] = detect_tracks(data, ROLE_CONFIG)
    result = forecast_track(data, ROLE_CONFIG, track, _population())
    assert result.model_order is not None


def test_forecast_track_passes_through_on_candidate_and_on_origin():
    data = _seasonal_country_data("Eligiland", 78)
    [track] = detect_tracks(data, ROLE_CONFIG)
    candidates_seen, origins_seen = [], []
    result = forecast_track(
        data,
        ROLE_CONFIG,
        track,
        _population(),
        on_candidate=lambda *a: candidates_seen.append(a),
        on_origin=lambda *a: origins_seen.append(a),
    )
    assert len(candidates_seen) == 36  # 3x3x2x2 grid, per ADR-009
    assert len(origins_seen) > 0
    assert origins_seen[-1][0] == origins_seen[-1][1]  # completed == total
    assert result.model_order is not None


def test_forecast_track_with_and_without_callbacks_produce_identical_results():
    data = _seasonal_country_data("Eligiland", 78)
    [track] = detect_tracks(data, ROLE_CONFIG)
    with_cb = forecast_track(
        data,
        ROLE_CONFIG,
        track,
        _population(),
        on_candidate=lambda *a: None,
        on_origin=lambda *a: None,
    )
    without_cb = forecast_track(data, ROLE_CONFIG, track, _population())
    assert with_cb == without_cb
