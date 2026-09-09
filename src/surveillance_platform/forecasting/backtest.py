"""Rolling-origin backtest and evaluation metrics (ADR-009)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from surveillance_platform.forecasting.model import (
    SarimaOrder,
    fit_and_forecast_sarima,
    seasonal_naive_forecast,
)

#: ADR-009 deliberately reuses the eligibility floor as the initial
#: training window, for internal consistency rather than an
#: independent number.
TRAINING_WINDOW_MONTHS = 72
HORIZON_MONTHS = 3
STEP_MONTHS = 1


@dataclass
class BacktestRecord:
    """One rolling-origin forecast vs. its actual, for both model and baseline."""

    origin: pd.Period
    target: pd.Period
    horizon_step: int
    model_forecast: float
    baseline_forecast: float  # NaN if the baseline had no valid lag-12 value
    actual: float


def rolling_origin_backtest(
    rate_series: pd.Series,
    chosen_order: SarimaOrder,
    training_window: int = TRAINING_WINDOW_MONTHS,
    horizon: int = HORIZON_MONTHS,
    step: int = STEP_MONTHS,
    on_origin: Callable[[int, int], None] | None = None,
) -> list[BacktestRecord]:
    """Expanding-window backtest: refit at each origin, forecast ``horizon`` ahead.

    Reuses ``chosen_order`` (selected once per track, per ADR-009) at
    every origin, rather than re-running the AIC grid search each
    time -- that would be both computationally wasteful and
    inconsistent with ADR-009's "per eligible track" wording. A
    target month with a missing (``NaN``) actual is skipped, not
    treated as an error.

    ``on_origin``, if given, is called after every origin is processed
    (whether its fit succeeded or was skipped) as ``on_origin(index,
    total)``, both 1-based, so a caller can display real progress
    through the backtest. Purely additive: default ``None`` means
    zero behavior change from before this parameter existed (ADR-009
    addendum, 2026-09-09).
    """
    records: list[BacktestRecord] = []
    n = len(rate_series)
    total_origins = max(0, (n - horizon - training_window) // step + 1)
    origin_idx = training_window
    completed = 0
    while origin_idx + horizon <= n:
        train = rate_series.iloc[:origin_idx]
        actual_window = rate_series.iloc[origin_idx : origin_idx + horizon]
        try:
            model_mean, _, _ = fit_and_forecast_sarima(train, chosen_order, horizon)
        except Exception:  # noqa: BLE001 -- SARIMAX can raise many distinct
            # exception types for numerical/convergence issues; any of them
            # means this origin is skipped (ADR-009), not a bug to narrow.
            origin_idx += step
            completed += 1
            if on_origin is not None:
                on_origin(completed, total_origins)
            continue
        baseline_mean = seasonal_naive_forecast(train, horizon)
        for h in range(horizon):
            actual = actual_window.iloc[h]
            if pd.isna(actual):
                continue
            records.append(
                BacktestRecord(
                    origin=rate_series.index[origin_idx - 1],
                    target=actual_window.index[h],
                    horizon_step=h + 1,
                    model_forecast=float(model_mean[h]),
                    baseline_forecast=float(baseline_mean[h]),
                    actual=float(actual),
                )
            )
        origin_idx += step
        completed += 1
        if on_origin is not None:
            on_origin(completed, total_origins)
    return records


@dataclass
class Metrics:
    """MAE and RMSE (model, over all valid origins) plus MASE.

    ``mase`` is ``None`` when no origin has a valid baseline
    comparison (e.g. very early in a track); it is never fabricated.
    """

    mae: float
    rmse: float
    mase: float | None


def compute_metrics(records: list[BacktestRecord]) -> Metrics:
    """MAE, RMSE, and MASE (scaled against the seasonal-naive baseline).

    MAPE/sMAPE are deliberately excluded (ADR-009): 18% of
    Bangladesh's real Confirmed-era months are exactly zero, which
    breaks MAPE. MASE directly operationalizes ADR-005's stated
    purpose for the baseline: MASE < 1 means the primary model beats
    seasonal-naive. To keep the ratio a fair comparison, MASE's own
    numerator is computed over the same subset of origins as its
    denominator -- not over every origin used for the overall MAE/RMSE.
    """
    if not records:
        raise ValueError("Cannot compute metrics from an empty backtest.")

    model_errors = np.array([abs(r.model_forecast - r.actual) for r in records])
    mae = float(model_errors.mean())
    rmse = float(np.sqrt(np.mean(model_errors**2)))

    comparable = [r for r in records if not np.isnan(r.baseline_forecast)]
    if comparable:
        comparable_model_mae = float(
            np.mean([abs(r.model_forecast - r.actual) for r in comparable])
        )
        baseline_mae = float(
            np.mean([abs(r.baseline_forecast - r.actual) for r in comparable])
        )
        mase = comparable_model_mae / baseline_mae if baseline_mae > 0 else None
    else:
        mase = None

    return Metrics(mae=mae, rmse=rmse, mase=mase)


def compute_baseline_metrics(records: list[BacktestRecord]) -> Metrics | None:
    """MAE and RMSE for the seasonal-naive baseline itself.

    ADR-009 calls for reporting all three metrics "for each" (model
    and baseline) so a reviewer can compare them directly, not just
    via the MASE ratio. ``mase`` is always ``None`` here -- a
    baseline's error scaled against itself is trivially 1 and
    conveys nothing. Returns ``None`` (not a fabricated value) if no
    origin has a valid baseline comparison.
    """
    comparable = [r for r in records if not np.isnan(r.baseline_forecast)]
    if not comparable:
        return None
    errors = np.array([abs(r.baseline_forecast - r.actual) for r in comparable])
    return Metrics(
        mae=float(errors.mean()), rmse=float(np.sqrt(np.mean(errors**2))), mase=None
    )
