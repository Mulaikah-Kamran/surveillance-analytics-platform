"""Report structures for the forecasting module.

Kept minimal, matching the M4/M5 convention: plain typed dataclasses,
no formal enum hierarchy, no logging framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from surveillance_platform.forecasting.backtest import BacktestRecord, Metrics
from surveillance_platform.forecasting.model import SarimaOrder


@dataclass
class Track:
    """A candidate monthly forecasting track for one country.

    Produced by :func:`surveillance_platform.forecasting.eligibility.detect_tracks`.
    Represents one contiguous run of sub-annual reporting under one
    consistent case definition (ADR-009). Ineligible tracks are still
    returned, not discarded -- ADR-009 Point 7 requires below-threshold
    tracks to be shown with a reliability warning, not hidden.

    ``case_definition`` is ``None`` when the ``case_definition_standardised``
    column was absent from the input (see ADR-009's 2026-09-08 addendum)
    or did not vary within the dataset.
    """

    country: str
    case_definition: str | None
    start: pd.Period
    end: pd.Period
    n_months: int
    gap_months: int
    eligible: bool


@dataclass
class ResidualDiagnostics:
    """Ljung-Box test on the final model's residuals (PFD Section 16:
    forecasting must include residual analysis)."""

    ljung_box_stat: float
    ljung_box_pvalue: float
    lag: int


@dataclass
class ForecastResult:
    """The full ADR-009 output for one track.

    Produced by :func:`surveillance_platform.forecasting.pipeline.forecast_track`.
    A below-threshold or otherwise unusable track (SARIMA order
    selection or the final fit failing to converge, or no population
    data available for the country) still returns a ``ForecastResult``
    -- never raises -- with the relevant fields empty/``None`` and the
    reason recorded in ``limitations``, consistent with ADR-009 Point 7
    and the Freeze Document's "document, don't hide" testing philosophy.
    """

    track: Track
    forecast_periods: list[pd.Period]
    forecast_mean: list[float]
    forecast_lower: list[float]
    forecast_upper: list[float]
    model_order: SarimaOrder | None
    residual_diagnostics: ResidualDiagnostics | None
    backtest_records: list[BacktestRecord]
    model_metrics: Metrics | None
    baseline_metrics: Metrics | None
    limitations: list[str] = field(default_factory=list)
