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

The SARIMA model, seasonal-naive baseline, rolling-origin backtest,
and the full ``ForecastResult`` orchestration are not yet implemented.

See ``docs/adr/ADR-009-forecasting-strategy.md`` for the full design.
"""

from surveillance_platform.forecasting.aggregation import monthly_series, population_rate
from surveillance_platform.forecasting.eligibility import detect_tracks
from surveillance_platform.forecasting.report import Track

__all__ = [
    "Track",
    "detect_tracks",
    "monthly_series",
    "population_rate",
]
