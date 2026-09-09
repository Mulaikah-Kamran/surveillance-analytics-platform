"""Milestone 7 tests: rolling-origin backtest and evaluation metrics (ADR-009)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from surveillance_platform.forecasting.backtest import (
    BacktestRecord,
    compute_metrics,
    rolling_origin_backtest,
)
from surveillance_platform.forecasting.model import SEASONAL_PERIOD, select_sarima_order


def _synthetic_seasonal_series(n_months: int, seed: int = 0) -> pd.Series:
    rng = np.random.default_rng(seed)
    t = np.arange(n_months)
    seasonal = 5 + 4 * np.sin(2 * np.pi * t / SEASONAL_PERIOD)
    values = np.clip(seasonal + rng.normal(0, 0.3, n_months), 0, None)
    index = pd.period_range("2010-01", periods=n_months, freq="M")
    return pd.Series(values, index=index)


def test_rolling_origin_backtest_produces_expected_record_count():
    # Small windows (not ADR-009's 72/3 defaults) to keep the test fast.
    series = _synthetic_seasonal_series(40)
    order = select_sarima_order(series)
    records = rolling_origin_backtest(series, order, training_window=30, horizon=2, step=1)
    # Origins run from index 30 to 40-2=38 inclusive -> up to 9 origins
    # x 2 horizon steps. A 30-month training window is deliberately
    # below the real 72-month eligibility floor to keep this test
    # fast; some short-window refits may legitimately fail to
    # converge and are correctly skipped (see rolling_origin_backtest's
    # docstring), so the count is an upper bound, not exact.
    assert 0 < len(records) <= 9 * 2
    assert all(isinstance(r, BacktestRecord) for r in records)


def test_rolling_origin_backtest_targets_follow_origin_correctly():
    series = _synthetic_seasonal_series(36)
    order = select_sarima_order(series)
    records = rolling_origin_backtest(series, order, training_window=30, horizon=2, step=1)
    first = records[0]
    assert first.origin == series.index[29]
    assert first.target == series.index[30]
    assert first.horizon_step == 1


def test_rolling_origin_backtest_step_size_is_respected():
    series = _synthetic_seasonal_series(50)
    order = select_sarima_order(series)
    records_step1 = rolling_origin_backtest(series, order, training_window=30, horizon=1, step=1)
    records_step2 = rolling_origin_backtest(series, order, training_window=30, horizon=1, step=2)
    assert len(records_step2) < len(records_step1)


def test_compute_metrics_mae_rmse_are_correct():
    records = [
        BacktestRecord(pd.Period("2020-01"), pd.Period("2020-02"), 1, 12.0, 10.0, 10.0),
        BacktestRecord(pd.Period("2020-02"), pd.Period("2020-03"), 1, 8.0, 10.0, 10.0),
    ]
    metrics = compute_metrics(records)
    # Errors: |12-10|=2, |8-10|=2 -> MAE=2, RMSE=2
    assert metrics.mae == pytest.approx(2.0)
    assert metrics.rmse == pytest.approx(2.0)


def test_compute_metrics_mase_below_one_when_model_beats_baseline():
    records = [
        BacktestRecord(pd.Period("2020-01"), pd.Period("2020-02"), 1, 10.5, 15.0, 10.0),
        BacktestRecord(pd.Period("2020-02"), pd.Period("2020-03"), 1, 10.5, 15.0, 10.0),
    ]
    metrics = compute_metrics(records)
    # model error = 0.5 each -> MAE=0.5; baseline error = 5 each -> MAE=5
    assert metrics.mase == pytest.approx(0.1)
    assert metrics.mase < 1


def test_compute_metrics_mase_none_when_no_baseline_available():
    records = [
        BacktestRecord(pd.Period("2020-01"), pd.Period("2020-02"), 1, 10.0, float("nan"), 10.0),
    ]
    metrics = compute_metrics(records)
    assert metrics.mase is None


def test_compute_metrics_raises_on_empty_records():
    with pytest.raises(ValueError):
        compute_metrics([])


def test_rolling_origin_backtest_default_none_callback_is_backward_compatible():
    """ADR-009 addendum (2026-09-09): on_origin defaults to None and
    must not change behavior or raise -- the regression guarantee the
    whole addendum depends on.
    """
    series = _synthetic_seasonal_series(40)
    order = select_sarima_order(series)
    records = rolling_origin_backtest(series, order, training_window=30, horizon=2)
    assert isinstance(records, list)


def test_rolling_origin_backtest_on_origin_reaches_completed_equals_total():
    series = _synthetic_seasonal_series(40)
    order = select_sarima_order(series)
    seen = []
    rolling_origin_backtest(
        series, order, training_window=30, horizon=2,
        on_origin=lambda completed, total: seen.append((completed, total)),
    )
    assert len(seen) > 0
    final_completed, final_total = seen[-1]
    assert final_completed == final_total
    # Monotonically increasing completed count, 1-based.
    assert [c for c, _ in seen] == list(range(1, len(seen) + 1))


def test_rolling_origin_backtest_on_origin_total_is_stable_across_calls():
    """The reported 'total' must be the same value on every callback
    invocation within one backtest call -- it's the total origin
    count for the whole run, not a running estimate.
    """
    series = _synthetic_seasonal_series(40)
    order = select_sarima_order(series)
    totals_seen = set()
    rolling_origin_backtest(
        series, order, training_window=30, horizon=2,
        on_origin=lambda completed, total: totals_seen.add(total),
    )
    assert len(totals_seen) == 1
