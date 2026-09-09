"""Forecasting module.

Implements Milestone 7 per ADR-009: monthly, population-normalized
forecasting per (country, case-definition track), using SARIMA as the
primary workflow evaluated against a seasonal-naive baseline.

Builds on Milestone 4's ``prepared_data`` directly (not Milestone 5's
``EDAResult``, which only stores boolean homogeneity flags -- see
ADR-009) and the same ``RoleConfiguration``.

Public API:

* :func:`forecast` -- run the full M7 pipeline: detect every
  candidate track and forecast each one.
* :func:`forecast_track` -- run the pipeline for a single, already-
  detected track.
* :class:`ForecastResult` -- the pipeline's per-track output.
* :class:`Track` -- a candidate forecasting track (see
  :func:`detect_tracks`).

Each stage is also independently importable for testing, e.g.
``surveillance_platform.forecasting.eligibility.detect_tracks``.

See ``docs/adr/ADR-009-forecasting-strategy.md`` for the full design.
"""

from surveillance_platform.forecasting.aggregation import (
    monthly_series,
    population_rate,
)
from surveillance_platform.forecasting.backtest import (
    BacktestRecord,
    Metrics,
    compute_baseline_metrics,
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
from surveillance_platform.forecasting.pipeline import forecast, forecast_track
from surveillance_platform.forecasting.report import (
    ForecastResult,
    ResidualDiagnostics,
    Track,
)

__all__ = [
    "BacktestRecord",
    "ForecastResult",
    "Metrics",
    "ResidualDiagnostics",
    "SarimaOrder",
    "Track",
    "compute_baseline_metrics",
    "compute_metrics",
    "detect_tracks",
    "fit_and_forecast_sarima",
    "forecast",
    "forecast_track",
    "monthly_series",
    "population_rate",
    "rolling_origin_backtest",
    "seasonal_naive_forecast",
    "select_sarima_order",
]
