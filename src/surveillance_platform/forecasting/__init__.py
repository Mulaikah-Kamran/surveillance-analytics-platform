"""Forecasting module.

Implements Milestone 7 per ADR-009: monthly, population-normalized
forecasting per (country, case-definition track), using SARIMA as the
primary workflow evaluated against a seasonal-naive baseline.

Builds on Milestone 4's ``prepared_data`` directly (not Milestone 5's
``EDAResult``, which only stores boolean homogeneity flags -- see
ADR-009) and the same ``RoleConfiguration``.

Public API is added incrementally as each part of ADR-009 is
implemented. Currently available:

* :func:`detect_tracks` -- window/track detection.
* :func:`monthly_series` -- monthly aggregation from prepared data.
* :func:`population_rate` -- population-normalized rate per 100,000.
* :class:`Track` -- a candidate forecasting track.
* :func:`select_sarima_order`, :func:`fit_and_forecast_sarima` --
  SARIMA primary model (order chosen once per track).
* :func:`seasonal_naive_forecast` -- the transparent baseline.
* :func:`rolling_origin_backtest`, :func:`compute_metrics` --
  expanding-window backtest and MAE/RMSE/MASE evaluation.

The full ``ForecastResult`` orchestration tying these together is not
yet implemented.

See ``docs/adr/ADR-009-forecasting-strategy.md`` for the full design.
"""

from surveillance_platform.forecasting.aggregation import monthly_series, population_rate
from surveillance_platform.forecasting.backtest import (
    BacktestRecord,
    Metrics,
    compute_metrics,
    rolling_origin_backtest,
)
from surveillance_platform.forecasting.eligibility import detect_tracks
from surveillance_platform.forecasting.model import (
    SarimaOrder,
    fit_and_forecast_sarima,
    seasonal_naive_forecast,
    select_sarima_order,
)
from surveillance_platform.forecasting.report import Track

__all__ = [
    "BacktestRecord",
    "Metrics",
    "SarimaOrder",
    "Track",
    "compute_metrics",
    "detect_tracks",
    "fit_and_forecast_sarima",
    "monthly_series",
    "population_rate",
    "rolling_origin_backtest",
    "seasonal_naive_forecast",
    "select_sarima_order",
]
