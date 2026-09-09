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


def test_select_sarima_order_rejects_non_converged_fits():
    """statsmodels only warns on non-convergence, it does not raise --
    select_sarima_order must explicitly check mle_retvals['converged']
    and exclude such a fit, even if its AIC looks attractive.
    """
    from unittest.mock import MagicMock, patch

    series = _synthetic_seasonal_series()
    mock_fitted = MagicMock()
    mock_fitted.aic = -9999.0  # would win on AIC alone if not rejected
    mock_fitted.mle_retvals = {"converged": False}
    mock_model = MagicMock()
    mock_model.fit.return_value = mock_fitted

    with (
        patch(
            "surveillance_platform.forecasting.model.SARIMAX", return_value=mock_model
        ),
        pytest.raises(ValueError, match="No SARIMA order"),
    ):
        select_sarima_order(series)


def test_fit_and_forecast_sarima_raises_on_non_converged_final_fit():
    """The final production fit (not just the grid search) must also
    reject a non-converged result rather than return an unreliable
    forecast.
    """
    from unittest.mock import MagicMock, patch

    series = _synthetic_seasonal_series()
    order = SarimaOrder(order=(1, 1, 1), seasonal_order=(1, 1, 1, 12), aic=0.0)
    mock_fitted = MagicMock()
    mock_fitted.mle_retvals = {"converged": False}
    mock_model = MagicMock()
    mock_model.fit.return_value = mock_fitted

    with (
        patch(
            "surveillance_platform.forecasting.model.SARIMAX", return_value=mock_model
        ),
        pytest.raises(ValueError, match="did not converge"),
    ):
        fit_and_forecast_sarima(series, order, horizon=3)


def test_select_sarima_order_default_none_callback_is_backward_compatible():
    """ADR-009 addendum (2026-09-09): on_candidate defaults to None and
    must not change behavior or raise -- this is the regression
    guarantee the whole addendum depends on.
    """
    series = _synthetic_seasonal_series()
    result = select_sarima_order(series)  # no on_candidate passed at all
    assert isinstance(result, SarimaOrder)


def test_select_sarima_order_on_candidate_reports_every_grid_point():
    series = _synthetic_seasonal_series()
    seen = []
    select_sarima_order(series, on_candidate=lambda *args: seen.append(args))
    # 3 (p) x 3 (q) x 2 (seasonal_p) x 2 (seasonal_q) = 36, per ADR-009.
    assert len(seen) == 36


def test_select_sarima_order_on_candidate_reports_converged_and_aic_together():
    series = _synthetic_seasonal_series()
    seen = []
    order = select_sarima_order(series, on_candidate=lambda *args: seen.append(args))
    matching = [
        c for c in seen if c[0] == order.order and c[1] == order.seasonal_order and c[3]
    ]
    assert len(matching) == 1
    assert matching[0][2] == pytest.approx(order.aic)


def test_select_sarima_order_on_candidate_reports_none_aic_on_exception():
    """A candidate that raises (not just fails to converge) must report
    aic=None, converged=False -- never a fabricated AIC value.
    """
    from unittest.mock import patch

    series = _synthetic_seasonal_series()
    seen = []
    with (
        patch(
            "surveillance_platform.forecasting.model.SARIMAX",
            side_effect=ValueError("boom"),
        ),
        pytest.raises(ValueError, match="No SARIMA order"),
    ):
        select_sarima_order(series, on_candidate=lambda *args: seen.append(args))
    assert len(seen) == 36
    assert all(c[2] is None and c[3] is False for c in seen)
