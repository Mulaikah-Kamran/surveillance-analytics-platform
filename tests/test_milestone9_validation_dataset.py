"""Milestone 9 regression tests -- CDC NNDSS validation dataset (ADR-011).

Two kinds of test here, mirroring Milestone 2's own established pattern
(tests/test_milestone2_dataset_acquisition.py):

1. Unit tests for the acquisition script's transformation logic
   (MMWR week math, location filtering/normalization) -- fast,
   deterministic, no network or file dependency, always run.
2. A full-pipeline regression test against the actual acquired file --
   skips gracefully (not fails) when that file isn't present locally,
   e.g. in CI, since per data/README.md the raw file is never
   committed. Run `python data/download_nndss_validation_dataset.py`
   first to exercise it.

This is the M9 roadmap's "regression test" deliverable (PFD Section 29,
Milestone 9): confirms the architecture continues to accept this
second dataset with zero pipeline code changes, the way it did when
first verified during M9 implementation.
"""

from __future__ import annotations

import datetime
import sys
from pathlib import Path

import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "data"))

from download_nndss_validation_dataset import (
    _mmwr_week_start,
    to_pipeline_shape,
)

VALIDATION_CSV = REPO_ROOT / "data" / "raw" / "nndss_validation_dataset.csv"


# --- MMWR week math -- verified against a real, independently-sourced ---
# --- reference before being trusted (see the function's own docstring) --


def test_mmwr_week_start_matches_known_reference_date():
    # CDC's own published "week ending August 14, 2021 (Week 32)".
    start = _mmwr_week_start(2021, 32)
    end = start + datetime.timedelta(days=6)
    assert end == datetime.date(2021, 8, 14)


def test_mmwr_week_53_does_not_raise():
    """2025 has an MMWR week 53, which does not exist under strict ISO
    8601 week numbering -- this is exactly the real bug caught during
    implementation (pandas' ISO-week parser raised on this).
    """
    result = _mmwr_week_start(2025, 53)
    assert isinstance(result, datetime.date)
    assert result.year in (2025, 2026)  # week 53 spans the year boundary


def test_mmwr_week_1_start_is_a_sunday():
    for year in (2022, 2023, 2024, 2025, 2026):
        assert _mmwr_week_start(year, 1).weekday() == 6  # Sunday


# --- to_pipeline_shape() -- location filtering and normalization -------


def _raw_sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "states": ["ALABAMA", "Alabama", "TOTAL", "East North Central", "Guam"],
            "year": ["2022", "2022", "2022", "2022", "2022"],
            "week": ["1", "2", "1", "1", "1"],
            "label": ["X"] * 5,
            "m1": ["10", "20", "999", "50", "5"],
        }
    )


def test_to_pipeline_shape_normalizes_casing_to_one_canonical_form():
    shaped = to_pipeline_shape(_raw_sample())
    # "ALABAMA" and "Alabama" must collapse to the same normalized value.
    assert set(shaped["state"].unique()) == {"Alabama"}


def test_to_pipeline_shape_excludes_non_state_locations():
    """TOTAL (national aggregate), East North Central (regional
    aggregate), and Guam (territory, not one of the 50 states + DC)
    must all be excluded -- otherwise they'd be treated as Location
    values equally distinct from real states, corrupting any aggregate
    statistic (M9 Dataset Compatibility Report, Section 4).
    """
    shaped = to_pipeline_shape(_raw_sample())
    assert "TOTAL" not in shaped["state"].values
    assert "East North Central" not in shaped["state"].values
    assert "Guam" not in shaped["state"].values
    assert len(shaped) == 2  # only the two Alabama rows survive


def test_to_pipeline_shape_produces_the_three_required_columns():
    shaped = to_pipeline_shape(_raw_sample())
    assert {"report_date", "state", "weekly_case_count"}.issubset(shaped.columns)


# --- Full pipeline regression -- skips gracefully if file is absent ----


@pytest.mark.skipif(
    not VALIDATION_CSV.exists(),
    reason=(
        "M9 validation dataset not present locally -- run "
        "'python data/download_nndss_validation_dataset.py' first."
    ),
)
class TestFullPipelineAgainstRealValidationDataset:
    """Confirms M3-M7's existing, unmodified pipeline accepts this
    second real dataset -- the actual Milestone 9 finding.
    """

    @pytest.fixture(scope="class")
    @classmethod
    def role_config(cls):
        from surveillance_platform.role_configuration import RoleConfiguration

        return RoleConfiguration(
            time="report_date",
            location="state",
            surveillance_measure="weekly_case_count",
            identifier=None,
        )

    @pytest.fixture(scope="class")
    @classmethod
    def prepared(cls, role_config):
        from surveillance_platform.data_preparation import prepare

        raw = pd.read_csv(VALIDATION_CSV)
        return prepare(raw, role_config)

    def test_role_configuration_validates(self, role_config):
        from surveillance_platform.role_configuration import validate

        raw = pd.read_csv(VALIDATION_CSV)
        validate(role_config, raw.columns)  # raises on failure

    def test_preparation_excludes_missing_measure_rows_not_crash(self, prepared):
        assert prepared.report.rows_out > 0
        assert prepared.report.rows_excluded > 0
        assert any(
            f.check == "missing_required_value"
            for f in prepared.report.quality_findings
        )

    def test_eda_produces_real_nondegenerate_statistics(self, prepared, role_config):
        from surveillance_platform.eda import analyze

        result = analyze(prepared.data, role_config)
        # Unlike HDX's rejected candidate, this must NOT be degenerate
        # (e.g. constant 1s) -- confirms a genuine numeric measure.
        assert result.descriptive.std > 0
        assert result.descriptive.mean > 0

    def test_forecasting_correctly_finds_zero_eligible_tracks(
        self, prepared, role_config
    ):
        """The exact, anticipated (ADR-011) and now-confirmed finding:
        2022-2026 is shorter than ADR-009's 72-month eligibility floor.
        This must be a graceful, documented limitation, not a crash or
        a silently-wrong forecast.
        """
        from surveillance_platform.forecasting import detect_tracks

        tracks = detect_tracks(prepared.data, role_config)
        assert len(tracks) > 0  # tracks ARE detected
        assert all(not t.eligible for t in tracks)  # none pass the floor
        assert all(t.n_months < 72 for t in tracks)
