"""Monthly aggregation and population-rate normalization (ADR-009).

Builds the actual monthly series a :class:`~surveillance_platform.forecasting.report.Track`
describes, from ``prepared_data`` directly. Both sub-annual source
resolutions (weekly or monthly OpenDengue rows) roll up to the same
kind of monthly total; no per-row flag distinguishes them (ADR-009
Point 4 -- resolution shifts within a track are aggregated silently).
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.forecasting.report import Track
from surveillance_platform.role_configuration import RoleConfiguration


def monthly_series(
    data: pd.DataFrame, role_config: RoleConfiguration, track: Track
) -> pd.Series:
    """Monthly-summed surveillance measure for one track.

    Filters ``data`` to ``track.country`` (and ``track.case_definition``,
    when not ``None``) and the track's date range, sums the
    surveillance measure per calendar month, and reindexes to the
    track's full month span -- months absent from the source data
    (tolerated gaps, per ADR-009) are left as ``NaN``, never imputed,
    for SARIMAX's native missing-observation handling. Never mutates
    ``data``.
    """
    working = data.copy()
    working["_ym"] = working["time"].dt.to_period("M")

    mask = (
        (working[role_config.location] == track.country)
        & (working["_ym"] >= track.start)
        & (working["_ym"] <= track.end)
    )
    if track.case_definition is not None:
        mask &= working["case_definition_standardised"] == track.case_definition

    filtered = working.loc[mask]
    monthly = filtered.groupby("_ym")[role_config.surveillance_measure].sum()

    full_span = pd.period_range(track.start, track.end, freq="M")
    return monthly.reindex(full_span)


def population_rate(
    monthly_counts: pd.Series, population_by_year: pd.Series
) -> pd.Series:
    """Convert monthly counts to a rate per 100,000 population.

    ``population_by_year`` is indexed by calendar year (e.g. the WDI
    ``SP.POP.TOTL`` series). The same annual population value is
    applied to every month within that year -- never interpolated
    between years (ADR-009: measured population growth in the actual
    eligible windows, up to ~32% over 8 years for Maldives, is large
    enough to bias a raw-count model's trend term with pure
    demographic growth). A month whose year has no population figure
    yields ``NaN``, consistent with never fabricating a value.
    """
    years = monthly_counts.index.year
    population = years.map(population_by_year)
    return monthly_counts / population.to_numpy() * 100_000
