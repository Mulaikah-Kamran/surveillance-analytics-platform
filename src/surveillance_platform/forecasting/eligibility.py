"""Window/track detection -- implements ADR-009's eligibility rule.

Groups each country's monthly history into contiguous candidate
forecasting tracks, each checked against the 72-month eligibility
floor. Reads ``prepared_data`` (Milestone 4's output) directly, since
Milestone 5's ``EDAResult`` only stores boolean homogeneity flags, not
the actual per-year dominant values this module needs to compare
across years (ADR-009).

Resolution- and case-definition-aware splitting (via the
OpenDengue-specific ``T_res`` / ``case_definition_standardised``
columns) is an opportunistic enhancement, not a hard dependency -- see
ADR-009's 2026-09-08 addendum. When those columns are absent, track
detection falls back to continuity of the role-contracted columns
alone (every period is treated as resolution-eligible and as one
constant case-definition).
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.forecasting.report import Track
from surveillance_platform.role_configuration import RoleConfiguration

#: ADR-009: ~6 years, grounded in the Box-Jenkins rule of thumb
#: (sample size >= 6x the seasonal lag) and published dengue SARIMA
#: practice (8-20 years in every study surveyed during M7 design).
ELIGIBILITY_FLOOR_MONTHS = 72

#: ADR-009: an isolated gap of up to this many consecutive months is
#: tolerated within a run (left as missing for SARIMAX's native
#: handling, never imputed); a larger gap splits the run.
MAX_TOLERATED_GAP_MONTHS = 2

#: Resolution values (from OpenDengue's ``T_res`` column) considered
#: fine enough to support monthly aggregation.
SUB_ANNUAL_RESOLUTIONS = {"Week", "Month"}


def _dominant(series: pd.Series) -> object:
    """Mode of a categorical series; ties broken by first-seen value."""
    return series.value_counts().index[0]


def _year_resolution_signals(
    country_data: pd.DataFrame, has_res: bool
) -> dict[int, object]:
    """Per-year dominant ``T_res`` for one country (``None`` if absent).

    Year-level granularity is appropriate here: an annual-resolution
    year contributes only one row per year (its ``calendar_start_date``
    spans the full year), so per-year dominance is exact for it, and
    a genuinely sub-annual year's weekly/monthly rows are overwhelmingly
    one resolution in practice.
    """
    if not has_res:
        return {}
    return {
        year: _dominant(group["T_res"])
        for year, group in country_data.groupby(country_data["time"].dt.year)
    }


def _month_case_definition_signals(
    country_data: pd.DataFrame, has_casedef: bool
) -> dict[pd.Period, object]:
    """Per-month dominant ``case_definition_standardised`` for one country.

    Month-level granularity is required here, not year-level: a
    case-definition change can happen mid-year (as Bangladesh's did,
    in October 2021 -- see ADR-009). Using a per-year dominant value
    would smear a few transition months into whichever definition had
    the yearly majority, misplacing the actual boundary.
    """
    if not has_casedef:
        return {}
    return {
        ym: _dominant(group["case_definition_standardised"])
        for ym, group in country_data.groupby(country_data["_ym"])
    }


def detect_tracks(data: pd.DataFrame, role_config: RoleConfiguration) -> list[Track]:
    """Detect candidate monthly forecasting tracks, per ADR-009.

    For each country, walks its full calendar-month span and starts a
    new run whenever: the dominant per-year resolution (if ``T_res``
    is present) is not sub-annual; the dominant per-year case
    definition (if present) changes; or a gap in reported months
    exceeds :data:`MAX_TOLERATED_GAP_MONTHS`. Ineligible runs are
    still returned (ADR-009 Point 7). Never mutates ``data``.
    """
    working = data.copy()
    working["_ym"] = working["time"].dt.to_period("M")
    has_res = "T_res" in working.columns
    has_casedef = "case_definition_standardised" in working.columns

    tracks: list[Track] = []

    for country, country_data in working.groupby(role_config.location):
        months_present = sorted(country_data["_ym"].unique())
        if not months_present:
            continue
        present_set = set(months_present)
        full_span = pd.period_range(months_present[0], months_present[-1], freq="M")
        year_resolution = _year_resolution_signals(country_data, has_res)
        month_case_def = _month_case_definition_signals(country_data, has_casedef)

        def resolution_ok(period: pd.Period) -> bool:
            if not has_res:
                return True
            return year_resolution.get(period.year) in SUB_ANNUAL_RESOLUTIONS

        def case_def_at(period: pd.Period) -> object:
            if not has_casedef:
                return None
            # A month absent from the data (within a tolerated gap)
            # has no case-definition signal of its own; treat it as a
            # continuation of the current run rather than forcing a
            # split on a month with no data to disagree with.
            return month_case_def.get(period, run_case_def)

        def close_run(run_start: pd.Period, case_def: object, last_seen: pd.Period) -> None:
            span = pd.period_range(run_start, last_seen, freq="M")
            gap_count = sum(1 for p in span if p not in present_set)
            n_months = len(span)
            tracks.append(
                Track(
                    country=country,
                    case_definition=case_def,
                    start=run_start,
                    end=last_seen,
                    n_months=n_months,
                    gap_months=gap_count,
                    eligible=n_months >= ELIGIBILITY_FLOOR_MONTHS,
                )
            )

        run_start: pd.Period | None = None
        run_case_def: object = None
        last_seen: pd.Period | None = None  # last period actually present in the run
        gap_streak = 0

        for period in full_span:
            if not resolution_ok(period):
                if run_start is not None:
                    close_run(run_start, run_case_def, last_seen)
                run_start, gap_streak = None, 0
                continue

            cd = case_def_at(period)
            if run_start is None:
                run_start, run_case_def = period, cd
                last_seen = period
                gap_streak = 0 if period in present_set else 1
                continue
            if cd != run_case_def:
                close_run(run_start, run_case_def, last_seen)
                run_start, run_case_def = period, cd
                last_seen = period
                gap_streak = 0 if period in present_set else 1
                continue

            if period in present_set:
                last_seen = period
                gap_streak = 0
            else:
                gap_streak += 1
                if gap_streak > MAX_TOLERATED_GAP_MONTHS:
                    close_run(run_start, run_case_def, last_seen)
                    run_start, gap_streak = None, 0

        if run_start is not None:
            close_run(run_start, run_case_def, last_seen)

    return tracks
