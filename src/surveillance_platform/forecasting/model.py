"""SARIMA primary model and seasonal-naive baseline (ADR-009).

Order selection runs once per track via a small AIC grid search
*within* the SARIMA family (ADR-009: this is standard Box-Jenkins
model identification, not the "Automated model selection (AutoML)"
the Freeze Document excludes, which targets selecting between
different model families). The chosen order is then reused across
every rolling-origin backtest refit -- re-running the grid search at
every origin would be both computationally wasteful and inconsistent
with ADR-009's "per eligible track" wording.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

#: ADR-009: p, q in {0,1,2}; P, Q in {0,1}; d = D = 1 fixed per
#: standard seasonal-differencing practice. Every published SARIMA
#: dengue study surveyed during M7 design independently fits its own
#: order this way (Yangon, Rajasthan, Bangladesh).
_P_RANGE = (0, 1, 2)
_Q_RANGE = (0, 1, 2)
_SEASONAL_P_RANGE = (0, 1)
_SEASONAL_Q_RANGE = (0, 1)
_D, _SEASONAL_D = 1, 1
SEASONAL_PERIOD = 12


@dataclass
class SarimaOrder:
    """The order chosen for one track, and the AIC that selected it."""

    order: tuple[int, int, int]
    seasonal_order: tuple[int, int, int, int]
    aic: float


def select_sarima_order(
    rate_series: pd.Series,
    on_candidate: Callable[[tuple[int, int, int], tuple[int, int, int, int], float | None, bool], None]
    | None = None,
) -> SarimaOrder:
    """AIC grid search within the SARIMA family, on ``log1p(rate_series)``.

    Fit on the log-transform, not the raw rate: real project data is
    heavily zero-inflated and right-skewed (18% of Bangladesh's
    Confirmed-era months are exactly zero), and an untransformed
    SARIMA fit on this project's own data produced a nonsensical
    negative case-rate interval (ADR-009). Candidate orders that fail
    to converge are skipped, not treated as an error.

    ``on_candidate``, if given, is called after every candidate fit
    attempt (whether it converged, failed to converge, or raised) as
    ``on_candidate(order, seasonal_order, aic, converged)`` --
    ``aic`` is ``None`` if fitting raised an exception. Purely
    additive: default ``None`` means zero behavior change from before
    this parameter existed (ADR-009 addendum, 2026-09-09). Intended
    for a caller to observe real progress through the grid, not to
    influence the selection itself.
    """
    log_rate = np.log1p(rate_series.to_numpy(dtype=float))
    best: SarimaOrder | None = None
    for p in _P_RANGE:
        for q in _Q_RANGE:
            for seasonal_p in _SEASONAL_P_RANGE:
                for seasonal_q in _SEASONAL_Q_RANGE:
                    order = (p, _D, q)
                    seasonal_order = (seasonal_p, _SEASONAL_D, seasonal_q, SEASONAL_PERIOD)
                    try:
                        fitted = SARIMAX(
                            log_rate,
                            order=order,
                            seasonal_order=seasonal_order,
                            enforce_stationarity=False,
                            enforce_invertibility=False,
                        ).fit(disp=False)
                    except Exception:
                        if on_candidate is not None:
                            on_candidate(order, seasonal_order, None, False)
                        continue
                    # A fit that raises no exception can still have
                    # failed to converge (statsmodels only warns, it
                    # does not raise) -- such a fit's AIC is
                    # unreliable and must not win the comparison.
                    converged = fitted.mle_retvals.get("converged", True)
                    if on_candidate is not None:
                        on_candidate(order, seasonal_order, float(fitted.aic), converged)
                    if not converged:
                        continue
                    if best is None or fitted.aic < best.aic:
                        best = SarimaOrder(order, seasonal_order, float(fitted.aic))
    if best is None:
        raise ValueError("No SARIMA order in the grid converged for this series.")
    return best


def fit_and_forecast_sarima(
    rate_series: pd.Series, chosen_order: SarimaOrder, horizon: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit SARIMA with a pre-chosen order and forecast ``horizon`` steps ahead.

    Returns ``(point_forecast, lower_ci, upper_ci)``, all back-transformed
    to the original rate scale via ``expm1`` and floored at 0 -- a
    stated reporting convention (ADR-009), not a silent patch, since a
    disease rate cannot be negative and the log transform alone does
    not fully guarantee non-negative interval bounds at every horizon.
    Missing months (``NaN``, from tolerated gaps) are handled natively
    by SARIMAX's Kalman filter -- never imputed.
    """
    log_rate = np.log1p(rate_series.to_numpy(dtype=float))
    fitted = SARIMAX(
        log_rate,
        order=chosen_order.order,
        seasonal_order=chosen_order.seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)
    if not fitted.mle_retvals.get("converged", True):
        raise ValueError(
            "SARIMA fit did not converge for this window; caller should "
            "treat this origin/track as unreliable rather than use the result."
        )
    forecast = fitted.get_forecast(steps=horizon)
    mean = np.expm1(forecast.predicted_mean)
    ci = np.expm1(forecast.conf_int())
    lower, upper = np.maximum(ci[:, 0], 0.0), np.maximum(ci[:, 1], 0.0)
    return np.maximum(mean, 0.0), lower, upper


def seasonal_naive_forecast(rate_series: pd.Series, horizon: int) -> np.ndarray:
    """Seasonal-naive (lag-12) baseline: forecast month *t* as month *t-12*.

    No fitted parameters -- purely a transparent evaluation reference
    per ADR-005, not a competing model. Assumes ``rate_series`` has at
    least ``SEASONAL_PERIOD`` observations, which the 72-month
    eligibility floor guarantees for any track this is called on.
    """
    target_periods = pd.period_range(
        rate_series.index[-1] + 1, periods=horizon, freq="M"
    )
    lookup = rate_series.reindex(target_periods - SEASONAL_PERIOD)
    return lookup.to_numpy()
