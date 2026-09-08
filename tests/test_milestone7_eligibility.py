"""Milestone 7 tests: window/track detection (ADR-009).

Uses small, deterministic synthetic dataframes shaped like M4's
prepared-data output -- no real OpenDengue data is required. Mirrors
the M4/M5 test style: handcrafted scenarios, no mocking.
"""

from __future__ import annotations

import pandas as pd
import pytest

from surveillance_platform.forecasting.eligibility import (
    ELIGIBILITY_FLOOR_MONTHS,
    MAX_TOLERATED_GAP_MONTHS,
    detect_tracks,
)
from surveillance_platform.role_configuration import RoleConfiguration

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _monthly_rows(
    country: str,
    start: str,
    n_months: int,
    resolution: str = "Month",
    case_definition: str = "Confirmed",
    skip_months: set[int] | None = None,
) -> pd.DataFrame:
    """Build ``n_months`` consecutive monthly rows for one country.

    ``skip_months`` is a set of 0-indexed offsets from ``start`` to
    omit entirely, simulating missing reporting months.
    """
    skip_months = skip_months or set()
    periods = pd.period_range(start, periods=n_months, freq="M")
    rows = []
    for i, period in enumerate(periods):
        if i in skip_months:
            continue
        rows.append(
            {
                "adm_0_name": country,
                "time": period.to_timestamp(),
                "dengue_total": 10,
                "T_res": resolution,
                "case_definition_standardised": case_definition,
            }
        )
    return pd.DataFrame(rows)


def test_single_continuous_run_is_eligible_when_long_enough():
    data = _monthly_rows("Testland", "2010-01", ELIGIBILITY_FLOOR_MONTHS)
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(tracks) == 1
    assert tracks[0].eligible is True
    assert tracks[0].n_months == ELIGIBILITY_FLOOR_MONTHS
    assert tracks[0].gap_months == 0


def test_run_shorter_than_floor_is_returned_but_ineligible():
    data = _monthly_rows("Testland", "2010-01", ELIGIBILITY_FLOOR_MONTHS - 1)
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(tracks) == 1
    assert tracks[0].eligible is False


def test_case_definition_change_splits_the_run():
    part_a = _monthly_rows("Testland", "2010-01", 80, case_definition="Confirmed")
    part_b = _monthly_rows("Testland", "2016-09", 40, case_definition="Total")
    data = pd.concat([part_a, part_b], ignore_index=True)
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(tracks) == 2
    by_case_def = {t.case_definition: t for t in tracks}
    assert by_case_def["Confirmed"].n_months == 80
    assert by_case_def["Total"].n_months == 40
    assert by_case_def["Confirmed"].eligible is True
    assert by_case_def["Total"].eligible is False


def test_small_gap_is_tolerated_within_one_run():
    """A gap at or under MAX_TOLERATED_GAP_MONTHS does not split the run."""
    data = _monthly_rows(
        "Testland",
        "2010-01",
        ELIGIBILITY_FLOOR_MONTHS,
        skip_months={40, 41},  # 2 consecutive missing months
    )
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(tracks) == 1
    assert tracks[0].eligible is True
    assert tracks[0].gap_months == MAX_TOLERATED_GAP_MONTHS


def test_large_gap_splits_into_two_tracks():
    """A gap exceeding MAX_TOLERATED_GAP_MONTHS breaks the run in two,
    reproducing the real Maldives 2021 case that motivated this rule.
    """
    data = _monthly_rows(
        "Testland",
        "2010-01",
        ELIGIBILITY_FLOOR_MONTHS + 20,
        skip_months=set(range(40, 40 + MAX_TOLERATED_GAP_MONTHS + 1)),
    )
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(tracks) == 2
    assert tracks[0].n_months == 40
    assert tracks[1].n_months == ELIGIBILITY_FLOOR_MONTHS + 20 - 40 - (
        MAX_TOLERATED_GAP_MONTHS + 1
    )


def test_annual_resolution_years_are_excluded_from_the_run():
    # 84 months = exactly 2010-2016 (7 whole years), so the single
    # annual-resolution row for 2017 falls in a clean, separate year
    # -- real OpenDengue annual-resolution years are exactly one row
    # spanning the whole year, never mixed with monthly rows within
    # the same year.
    sub_annual = _monthly_rows("Testland", "2010-01", 84, resolution="Month")
    annual_year = _monthly_rows("Testland", "2017-01", 1, resolution="Year")
    data = pd.concat([sub_annual, annual_year], ignore_index=True)
    tracks = detect_tracks(data, ROLE_CONFIG)
    # Only the sub-annual run should appear; the annual-resolution
    # year never qualifies to start or extend a run.
    assert len(tracks) == 1
    assert tracks[0].n_months == 84


def test_missing_resolution_and_case_definition_columns_fall_back_generic():
    """ADR-009's 2026-09-08 addendum: absent T_res/case_definition_standardised
    columns must not crash detection -- it should fall back to
    continuity of the role-contracted columns alone.
    """
    data = _monthly_rows("Testland", "2010-01", ELIGIBILITY_FLOOR_MONTHS)
    data = data.drop(columns=["T_res", "case_definition_standardised"])
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert len(tracks) == 1
    assert tracks[0].eligible is True
    assert tracks[0].case_definition is None


def test_multiple_countries_are_detected_independently():
    a = _monthly_rows("Alpha", "2010-01", ELIGIBILITY_FLOOR_MONTHS)
    b = _monthly_rows("Beta", "2010-01", ELIGIBILITY_FLOOR_MONTHS - 10)
    data = pd.concat([a, b], ignore_index=True)
    tracks = detect_tracks(data, ROLE_CONFIG)
    by_country = {t.country: t for t in tracks}
    assert by_country["Alpha"].eligible is True
    assert by_country["Beta"].eligible is False


def test_does_not_mutate_input():
    data = _monthly_rows("Testland", "2010-01", ELIGIBILITY_FLOOR_MONTHS)
    original = data.copy(deep=True)
    detect_tracks(data, ROLE_CONFIG)
    pd.testing.assert_frame_equal(data, original)


def test_empty_dataframe_returns_no_tracks():
    data = pd.DataFrame(
        {
            "adm_0_name": pd.Series(dtype="object"),
            "time": pd.Series(dtype="datetime64[ns]"),
            "dengue_total": pd.Series(dtype="int64"),
            "T_res": pd.Series(dtype="object"),
            "case_definition_standardised": pd.Series(dtype="object"),
        }
    )
    tracks = detect_tracks(data, ROLE_CONFIG)
    assert tracks == []
