"""Annual time-series summary — country + calendar year.

Uses the standardized ``time`` column Milestone 4's Temporal
Standardization stage already derived (never ``role_config.time``
directly, since ``time`` is the frozen analytical column M4
guarantees is present and typed ``datetime64[ns]``).

Methodological rule (frozen): before an annual reported-case aggregate
is interpreted, this module checks whether ``T_res`` and
``case_definition_standardised`` are each homogeneous within the
country-year. If either is heterogeneous, the aggregate is still
produced and the relevant flag is set to ``False`` — never silently
corrected, reconciled, or discarded. This is a generic rule evaluated
against whatever data is passed in; no specific country or year is
ever hard-coded. Both checks degrade gracefully (the corresponding
flag is ``None``, not ``False``) when the underlying column is absent,
so a dataset without ``T_res`` or ``case_definition_standardised``
still produces a full time-series summary.

Reporting gaps use the same "max year gap" definition already
established in Milestone 2's data quality profile: the largest
difference between two consecutive reported calendar years for a
country.
"""

from __future__ import annotations

from itertools import pairwise

import pandas as pd

from surveillance_platform.eda.report import (
    CountryGapSummary,
    CountryYearSummary,
    TimeSeriesSummary,
)
from surveillance_platform.role_configuration import RoleConfiguration

_TIME_COLUMN = "time"
_RESOLUTION_COLUMN = "T_res"
_CASE_DEFINITION_COLUMN = "case_definition_standardised"


def _max_year_gap(years: list[int]) -> int:
    """Largest gap between consecutive reported years (0 if <2 years)."""
    if len(years) < 2:
        return 0
    ordered = sorted(years)
    return max(b - a for a, b in pairwise(ordered))


def time_series_summary(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> TimeSeriesSummary:
    """Build the annual (country, year) time-series summary.

    Does not mutate ``data``. Rows with a null ``time`` value are
    excluded from grouping (there is no calendar year to group them
    by); Milestone 4's Cleaning stage already removes rows with an
    unparseable Time value, so this should rarely, if ever, exclude
    anything additional here.
    """
    working = data.copy()
    working["_eda_year"] = working[_TIME_COLUMN].dt.year
    working = working[working["_eda_year"].notna()]

    has_resolution = _RESOLUTION_COLUMN in data.columns
    has_case_definition = _CASE_DEFINITION_COLUMN in data.columns

    country_years: list[CountryYearSummary] = []
    grouped = working.groupby([role_config.location, "_eda_year"], sort=True)
    for (country, year), group in grouped:
        measure = pd.to_numeric(
            group[role_config.surveillance_measure], errors="coerce"
        )

        resolution_homogeneous = (
            bool(group[_RESOLUTION_COLUMN].nunique(dropna=True) <= 1)
            if has_resolution
            else None
        )
        case_definition_homogeneous = (
            bool(group[_CASE_DEFINITION_COLUMN].nunique(dropna=True) <= 1)
            if has_case_definition
            else None
        )

        country_years.append(
            CountryYearSummary(
                country=country,
                year=int(year),
                first_date=group[_TIME_COLUMN].min(),
                last_date=group[_TIME_COLUMN].max(),
                observation_count=len(group),
                reported_case_total=float(measure.sum()),
                resolution_homogeneous=resolution_homogeneous,
                case_definition_homogeneous=case_definition_homogeneous,
            )
        )

    gaps: list[CountryGapSummary] = []
    for country, group in working.groupby(role_config.location, sort=True):
        years = sorted({int(y) for y in group["_eda_year"].dropna().unique()})
        gaps.append(
            CountryGapSummary(
                country=country,
                years_covered=years,
                max_year_gap=_max_year_gap(years),
            )
        )

    return TimeSeriesSummary(country_years=country_years, gaps=gaps)
