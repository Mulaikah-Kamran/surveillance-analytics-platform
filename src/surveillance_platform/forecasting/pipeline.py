"""Top-level Milestone 7 orchestration (ADR-009).

Ties together window/track detection, monthly aggregation, the
SARIMA/baseline models, and the rolling-origin backtest into one
:class:`~surveillance_platform.forecasting.report.ForecastResult` per
track -- mirroring Milestone 4's ``prepare()`` pattern (one function,
one result object, never raises on an ordinary data limitation).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox

from surveillance_platform.forecasting.aggregation import monthly_series, population_rate
from surveillance_platform.forecasting.backtest import (
    HORIZON_MONTHS,
    TRAINING_WINDOW_MONTHS,
    compute_baseline_metrics,
    compute_metrics,
    rolling_origin_backtest,
)
from surveillance_platform.forecasting.eligibility import (
    ELIGIBILITY_FLOOR_MONTHS,
    detect_tracks,
)
from surveillance_platform.forecasting.model import (
    SEASONAL_PERIOD,
    SarimaOrder,
    fit_and_forecast_sarima,
    select_sarima_order,
)
from surveillance_platform.forecasting.report import ForecastResult, ResidualDiagnostics, Track
from surveillance_platform.role_configuration import RoleConfiguration


def _empty_result(track: Track, limitations: list[str]) -> ForecastResult:
    """A ForecastResult for a track that could not be forecast at all."""
    return ForecastResult(
        track=track,
        forecast_periods=[],
        forecast_mean=[],
        forecast_lower=[],
        forecast_upper=[],
        model_order=None,
        residual_diagnostics=None,
        backtest_records=[],
        model_metrics=None,
        baseline_metrics=None,
        limitations=limitations,
    )


def _residual_diagnostics(
    rate_series: pd.Series, order: SarimaOrder
) -> ResidualDiagnostics | None:
    """Ljung-Box test on the final full-track fit's residuals (PFD Section 16).

    Returns ``None`` (never a fabricated value) if the final fit
    itself does not converge.
    """
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    log_rate = np.log1p(rate_series.to_numpy(dtype=float))
    fitted = SARIMAX(
        log_rate,
        order=order.order,
        seasonal_order=order.seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False)
    if not fitted.mle_retvals.get("converged", True):
        return None
    residuals = fitted.resid[~np.isnan(fitted.resid)]
    if len(residuals) <= SEASONAL_PERIOD:
        # Too few residuals (short/ineligible track) for a lag-12
        # Ljung-Box test to be meaningful at all -- not fabricated.
        return None
    lb = acorr_ljungbox(residuals, lags=[SEASONAL_PERIOD], return_df=True)
    return ResidualDiagnostics(
        ljung_box_stat=float(lb["lb_stat"].iloc[0]),
        ljung_box_pvalue=float(lb["lb_pvalue"].iloc[0]),
        lag=SEASONAL_PERIOD,
    )


def forecast_track(
    data: pd.DataFrame,
    role_config: RoleConfiguration,
    track: Track,
    population_by_year: pd.Series | None,
    horizon: int = HORIZON_MONTHS,
) -> ForecastResult:
    """Run the full ADR-009 pipeline for one track.

    A below-threshold track (``track.eligible is False``) still
    produces a forward forecast for illustrative purposes, but never
    runs the rolling-origin backtest if it is shorter than the
    protocol's own training window -- that limitation is stated, not
    silently worked around with a smaller window (ADR-009 Point 7).
    Never raises on an ordinary data limitation; failures are recorded
    in ``limitations`` and the corresponding fields left empty/``None``.
    """
    limitations: list[str] = []
    if not track.eligible:
        limitations.append(
            f"Track has {track.n_months} months, below the "
            f"{ELIGIBILITY_FLOOR_MONTHS}-month eligibility floor "
            "(ADR-009). Forecast is illustrative only."
        )
    if track.gap_months > 0:
        limitations.append(
            f"Track contains {track.gap_months} tolerated missing month(s), "
            "handled natively by SARIMAX's Kalman filter, never imputed."
        )

    if population_by_year is None:
        limitations.append(
            f"No population data available for {track.country}; ADR-009's "
            "target (rate per 100,000) cannot be computed for this track."
        )
        return _empty_result(track, limitations)

    counts = monthly_series(data, role_config, track)
    rate = population_rate(counts, population_by_year)

    try:
        order = select_sarima_order(rate)
    except ValueError as exc:
        limitations.append(f"SARIMA order selection failed: {exc}")
        return _empty_result(track, limitations)

    forecast_periods = list(pd.period_range(track.end + 1, periods=horizon, freq="M"))
    try:
        mean, lower, upper = fit_and_forecast_sarima(rate, order, horizon)
        forecast_mean, forecast_lower, forecast_upper = list(mean), list(lower), list(upper)
    except ValueError as exc:
        limitations.append(f"Final forecast fit did not converge: {exc}")
        forecast_mean = forecast_lower = forecast_upper = [float("nan")] * horizon

    diagnostics = _residual_diagnostics(rate, order)
    if diagnostics is None:
        limitations.append(
            "Residual diagnostics unavailable (final fit did not converge, "
            "or too few residuals for a lag-12 Ljung-Box test)."
        )

    if len(rate) >= TRAINING_WINDOW_MONTHS + horizon:
        records = rolling_origin_backtest(
            rate, order, training_window=TRAINING_WINDOW_MONTHS, horizon=horizon
        )
        model_metrics = compute_metrics(records) if records else None
        baseline_metrics = compute_baseline_metrics(records) if records else None
        if not records:
            limitations.append("Backtest window fit but produced no usable origins.")
    else:
        records = []
        model_metrics = None
        baseline_metrics = None
        limitations.append(
            f"Track ({len(rate)} months) is shorter than the backtest "
            f"protocol's own training window ({TRAINING_WINDOW_MONTHS} months) "
            f"plus horizon ({horizon} months); no backtest is possible."
        )

    return ForecastResult(
        track=track,
        forecast_periods=forecast_periods,
        forecast_mean=forecast_mean,
        forecast_lower=forecast_lower,
        forecast_upper=forecast_upper,
        model_order=order,
        residual_diagnostics=diagnostics,
        backtest_records=records,
        model_metrics=model_metrics,
        baseline_metrics=baseline_metrics,
        limitations=limitations,
    )


def forecast(
    data: pd.DataFrame,
    role_config: RoleConfiguration,
    population_by_country: dict[str, pd.Series],
    horizon: int = HORIZON_MONTHS,
) -> list[ForecastResult]:
    """Detect every candidate track and forecast each one (ADR-009's full M7 pipeline).

    ``population_by_country`` maps each country name, as it appears in
    the location-role column, to its own annual population series
    (year -> population, e.g. the WDI ``SP.POP.TOTL`` series). Never
    mutates ``data``.
    """
    tracks = detect_tracks(data, role_config)
    return [
        forecast_track(data, role_config, track, population_by_country.get(track.country), horizon)
        for track in tracks
    ]
