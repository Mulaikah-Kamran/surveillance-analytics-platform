"""Milestone 7 tests: SARIMA primary model and seasonal-naive baseline (ADR-009).

Uses small synthetic seasonal series -- real SARIMA fits, not mocks,
kept short enough to run quickly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from surveillance_platform.forecasting.model import (
    SEASONAL_PERIOD,
    SarimaOrder,
    fit_and_forecast_sarima,
    seasonal_naive_forecast,
    select_sarima_order,
)


def _synthetic_seasonal_series(n_months: int = 60, seed: int = 0) -> pd.Series:
    """A deterministic seasonal-plus-noise series, always non-negative."""
    rng = np.random.default_rng(seed)
    t = np.arange(n_months)
    seasonal = 5 + 4 * np.sin(2 * np.pi * t / SEASONAL_PERIOD)
    trend = 0.02 * t
    noise = rng.normal(0, 0.5, n_months)
    values = np.clip(seasonal + trend + noise, 0, None)
    index = pd.period_range("2010-01", periods=n_months, freq="M")
    return pd.Series(values, index=index)


def test_select_sarima_order_returns_valid_order():
    series = _synthetic_seasonal_series()
    result = select_sarima_order(series)
    assert isinstance(result, SarimaOrder)
    assert len(result.order) == 3
    assert len(result.seasonal_order) == 4
    assert result.seasonal_order[3] == SEASONAL_PERIOD
    assert np.isfinite(result.aic)


def test_fit_and_forecast_sarima_returns_correct_length_and_nonnegative():
    series = _synthetic_seasonal_series()
    order = select_sarima_order(series)
    mean, lower, upper = fit_and_forecast_sarima(series, order, horizon=3)
    assert len(mean) == len(lower) == len(upper) == 3
    assert (mean >= 0).all()
    assert (lower >= 0).all()
    assert (upper >= 0).all()
    assert (upper >= lower).all()


def test_fit_and_forecast_sarima_intervals_are_floored_not_fabricated():
    """Reproduces the real negative-interval problem found on Bangladesh
    data and confirms the floor is applied, per ADR-009.
    """
    # A near-constant-zero series with a single spike produces a wide,
    # log-space interval whose lower bound would go negative before
    # flooring on the original scale.
    values = np.zeros(60)
    values[::12] = 50  # one seasonal spike per year
    index = pd.period_range("2010-01", periods=60, freq="M")
    series = pd.Series(values, index=index)
    order = select_sarima_order(series)
    _, lower, _ = fit_and_forecast_sarima(series, order, horizon=3)
    assert (lower >= 0).all()


def test_seasonal_naive_forecast_uses_lag_12_lookup():
    index = pd.period_range("2010-01", periods=24, freq="M")
    values = np.arange(24, dtype=float)
    series = pd.Series(values, index=index)
    forecast = seasonal_naive_forecast(series, horizon=3)
    # Forecasting months 25, 26, 27 (indices 24,25,26) as months 13,14,15
    # (indices 12,13,14) one year prior.
    np.testing.assert_array_equal(forecast, [12.0, 13.0, 14.0])


def test_seasonal_naive_forecast_returns_nan_when_no_lag_12_value():
    """A track shorter than SEASONAL_PERIOD has no lag-12 value to use."""
    index = pd.period_range("2010-01", periods=6, freq="M")
    series = pd.Series(np.arange(6, dtype=float), index=index)
    forecast = seasonal_naive_forecast(series, horizon=3)
    assert np.isnan(forecast).all()
