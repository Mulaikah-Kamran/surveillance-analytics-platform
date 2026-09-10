"""Milestone 4 tests: Data Preparation Pipeline.

Exercises the frozen M4 contract: the five-stage pipeline (Validation
-> Data Profiling -> Quality Assessment -> Temporal Standardization ->
Cleaning), the M3/M4 validation boundary, the evidence-based cleaning
policy, and the PreparationResult/report contract. Uses a small,
deterministic synthetic dataframe — no real OpenDengue data is
required.
"""

import pandas as pd
import pytest

from surveillance_platform.data_preparation import (
    DataPreparationError,
    prepare,
)
from surveillance_platform.data_preparation.cleaning import clean
from surveillance_platform.data_preparation.profiling import profile
from surveillance_platform.data_preparation.quality_assessment import assess_quality
from surveillance_platform.data_preparation.report import QualityFinding
from surveillance_platform.data_preparation.temporal_standardization import (
    standardize_time,
)
from surveillance_platform.data_preparation.validation import validate_dataset
from surveillance_platform.role_configuration import RoleConfiguration

ROLE_CONFIG = RoleConfiguration(
    time="calendar_start_date",
    location="adm_0_name",
    surveillance_measure="dengue_total",
    identifier=None,
)


def _synthetic_dataset() -> pd.DataFrame:
    """~10 handcrafted rows covering the documented M4 test scenarios."""
    return pd.DataFrame(
        {
            "adm_0_name": [
                "Sri Lanka",
                "Sri Lanka",
                "Sri Lanka",
                "Bangladesh",
                "Bangladesh",
                "Bangladesh",
                "Nepal",
                "Nepal",
                "Maldives",
                "Maldives",
            ],
            "calendar_start_date": [
                "2024-01-01",
                "2024-01-08",
                "2024-01-15",
                "2024-01-01",
                "2024-01-08",
                None,  # missing required-role value
                "2024-01-01",
                "not-a-date",  # unparseable time
                "2024-01-01",
                "2024-01-08",
            ],
            "calendar_end_date": [
                "2024-01-07",
                "2024-01-14",
                "2024-01-21",
                "2024-01-07",
                "2024-01-14",
                "2024-01-21",
                "2023-12-25",  # interval inversion: end before start
                "2024-01-14",
                "2024-01-07",
                "2024-01-14",
            ],
            "dengue_total": [10, 0, 5, 3, -2, 7, 4, 6, 0, 8],
            "case_definition_standardised": [
                "Confirmed",
                "confirmed",  # casing anomaly
                "Suspected",
                "Confirmed",
                "Confirmed",
                "Suspected",
                "Confirmed",
                "Confirmed",
                "Suspected",
                "Confirmed",
            ],
        }
    )


# ---------------------------------------------------------------------
# Validation stage
# ---------------------------------------------------------------------


def test_validate_dataset_passes_for_valid_data():
    data = _synthetic_dataset()
    assert validate_dataset(data, ROLE_CONFIG) is None


def test_validate_dataset_fails_for_empty_dataset():
    data = _synthetic_dataset().iloc[0:0]
    with pytest.raises(DataPreparationError):
        validate_dataset(data, ROLE_CONFIG)


def test_validate_dataset_fails_when_required_role_entirely_null():
    data = _synthetic_dataset().copy()
    data["dengue_total"] = None
    with pytest.raises(DataPreparationError) as excinfo:
        validate_dataset(data, ROLE_CONFIG)
    assert "surveillance_measure" in str(excinfo.value)


def test_validate_dataset_does_not_reject_partial_missingness():
    """A required-role column that is only partly null is a row-level
    Quality Assessment concern, not a Validation hard-stop."""
    data = _synthetic_dataset()
    # calendar_start_date has one missing value (row 5), not entirely null.
    assert validate_dataset(data, ROLE_CONFIG) is None


# ---------------------------------------------------------------------
# Data Profiling stage
# ---------------------------------------------------------------------


def test_profile_reports_descriptive_facts_only():
    data = _synthetic_dataset()
    facts = profile(data)
    assert facts["row_count"] == len(data)
    assert facts["column_count"] == len(data.columns)
    assert "calendar_start_date" in facts["dtypes"]
    assert facts["missing_counts"]["calendar_start_date"] == 1


def test_profile_does_not_mutate_input():
    data = _synthetic_dataset()
    original = data.copy()
    profile(data)
    pd.testing.assert_frame_equal(data, original)


# ---------------------------------------------------------------------
# Quality Assessment stage
# ---------------------------------------------------------------------


def test_assess_quality_flags_negative_surveillance_measure():
    data = _synthetic_dataset()
    findings = assess_quality(data, ROLE_CONFIG)
    checks = {f.check for f in findings}
    assert "negative_surveillance_measure" in checks


def test_assess_quality_flags_interval_inversion_without_correcting():
    """Interval inversions are reported but have no defined cleaning
    policy — Quality Assessment must never dictate a correction."""
    data = _synthetic_dataset()
    findings = assess_quality(data, ROLE_CONFIG)
    checks = {f.check for f in findings}
    assert "interval_inversion" in checks


def test_assess_quality_flags_missing_required_value():
    data = _synthetic_dataset()
    findings = assess_quality(data, ROLE_CONFIG)
    missing_findings = [f for f in findings if f.check == "missing_required_value"]
    assert len(missing_findings) == 1
    assert 5 in missing_findings[0].row_indices


def test_assess_quality_does_not_mutate_input():
    data = _synthetic_dataset()
    original = data.copy()
    assess_quality(data, ROLE_CONFIG)
    pd.testing.assert_frame_equal(data, original)


def test_assess_quality_uses_plain_severity_field_not_enum():
    """Frozen decision: QualityFinding.severity is a plain string field,
    no formal severity enum/hierarchy."""
    finding = QualityFinding(
        check="example", severity="warning", message="example finding"
    )
    assert isinstance(finding.severity, str)


# ---------------------------------------------------------------------
# Temporal Standardization stage
# ---------------------------------------------------------------------


def test_standardize_time_creates_datetime64_ns_column():
    data = _synthetic_dataset()
    standardized, _ = standardize_time(data, ROLE_CONFIG)
    assert standardized["time"].dtype == "datetime64[ns]"


def test_standardize_time_preserves_original_temporal_columns():
    data = _synthetic_dataset()
    standardized, _ = standardize_time(data, ROLE_CONFIG)
    pd.testing.assert_series_equal(
        standardized["calendar_start_date"], data["calendar_start_date"]
    )
    pd.testing.assert_series_equal(
        standardized["calendar_end_date"], data["calendar_end_date"]
    )


def test_standardize_time_flags_unparseable_time_without_hard_stop():
    data = _synthetic_dataset()
    standardized, findings = standardize_time(data, ROLE_CONFIG)
    checks = {f.check for f in findings}
    assert "unparseable_time" in checks
    # Row 7 has "not-a-date" -> time left null, not raised as an error.
    assert pd.isna(standardized.loc[7, "time"])


def test_standardize_time_does_not_mutate_input():
    data = _synthetic_dataset()
    original = data.copy()
    standardize_time(data, ROLE_CONFIG)
    pd.testing.assert_frame_equal(data, original)


# ---------------------------------------------------------------------
# Cleaning stage
# ---------------------------------------------------------------------


def test_clean_applies_casing_correction():
    data = _synthetic_dataset()
    cleaned, _, actions = clean(data, findings=[], role_config=ROLE_CONFIG)
    assert (cleaned["case_definition_standardised"] == "confirmed").sum() == 0
    assert any("case_definition_standardised" in action for action in actions)


def test_clean_excludes_rows_missing_required_value():
    data = _synthetic_dataset()
    finding = QualityFinding(
        check="missing_required_value",
        severity="warning",
        message="missing",
        row_indices=[5],
    )
    cleaned, exclusion_reasons, _ = clean(
        data, findings=[finding], role_config=ROLE_CONFIG
    )
    assert 5 not in cleaned.index
    assert exclusion_reasons["missing_required_value"] == 1


def test_clean_excludes_rows_with_unparseable_time():
    data = _synthetic_dataset()
    finding = QualityFinding(
        check="unparseable_time",
        severity="warning",
        message="unparseable",
        row_indices=[7],
    )
    cleaned, exclusion_reasons, _ = clean(
        data, findings=[finding], role_config=ROLE_CONFIG
    )
    assert 7 not in cleaned.index
    assert exclusion_reasons["unparseable_time"] == 1


def test_clean_does_not_correct_interval_inversion():
    """No cleaning policy exists for interval inversions — Cleaning
    must leave those rows and values unmodified."""
    data = _synthetic_dataset()
    finding = QualityFinding(
        check="interval_inversion",
        severity="warning",
        message="inverted",
        row_indices=[6],
    )
    cleaned, exclusion_reasons, _ = clean(
        data, findings=[finding], role_config=ROLE_CONFIG
    )
    assert 6 in cleaned.index
    assert "interval_inversion" not in exclusion_reasons


def test_clean_does_not_remove_legitimate_zero_values():
    data = _synthetic_dataset()
    cleaned, _, _ = clean(data, findings=[], role_config=ROLE_CONFIG)
    assert (cleaned["dengue_total"] == 0).sum() == 2


def test_assess_quality_flags_non_numeric_surveillance_measure():
    data = _synthetic_dataset()
    data["dengue_total"] = data["dengue_total"].astype(object)
    data.loc[0, "dengue_total"] = "unknown"
    findings = assess_quality(data, ROLE_CONFIG)
    matching = [f for f in findings if f.check == "non_numeric_surveillance_measure"]
    assert len(matching) == 1
    assert matching[0].row_indices == [0]


def test_prepare_excludes_non_numeric_measure_and_fixes_the_column_dtype():
    """Real bug, caught via a real browser reproduction: a surveillance
    measure column with a genuine mix of numbers and non-numeric
    placeholder text (e.g. 'unknown') passed the existing missing-
    value check (the text isn't null), then crashed forecasting's
    rate calculation downstream with a raw TypeError, because pandas
    keeps a column at dtype 'object' once it has seen any non-numeric
    value, even after the offending rows are excluded.

    This is an end-to-end test through the real prepare() pipeline,
    not just the unit-level exclusion check, specifically to verify
    the dtype itself is fixed, not just the row count -- that's the
    part a narrower test could miss and still let the real crash
    through.
    """
    data = _synthetic_dataset()
    data["dengue_total"] = data["dengue_total"].astype(object)
    data.loc[0, "dengue_total"] = "unknown"
    data.loc[1, "dengue_total"] = "not available"

    result = prepare(data, ROLE_CONFIG)

    assert 0 not in result.data.index
    assert 1 not in result.data.index
    assert result.report.exclusion_reasons["non_numeric_surveillance_measure"] == 2
    assert pd.api.types.is_numeric_dtype(result.data["dengue_total"])


def test_clean_does_not_mutate_input():
    data = _synthetic_dataset()
    original = data.copy()
    clean(data, findings=[], role_config=ROLE_CONFIG)
    pd.testing.assert_frame_equal(data, original)


# ---------------------------------------------------------------------
# Pipeline orchestration / end-to-end
# ---------------------------------------------------------------------


def test_prepare_end_to_end_valid_dataset():
    data = _synthetic_dataset()
    result = prepare(data, ROLE_CONFIG)

    assert result.report.rows_in == 10
    # Row 5 (missing calendar_start_date) and row 7 (unparseable time)
    # are excluded; all other rows are retained.
    assert result.report.rows_out == 8
    assert result.report.rows_excluded == 2
    assert "time" in result.data.columns
    assert result.data["time"].dtype == "datetime64[ns]"


def test_prepare_reports_quality_findings_and_cleaning_actions():
    data = _synthetic_dataset()
    result = prepare(data, ROLE_CONFIG)

    checks = {f.check for f in result.report.quality_findings}
    assert "negative_surveillance_measure" in checks
    assert "interval_inversion" in checks
    assert "missing_required_value" in checks
    assert "unparseable_time" in checks
    assert any(
        "case_definition_standardised" in action
        for action in result.report.cleaning_actions
    )


def test_prepare_raises_data_preparation_error_on_hard_stop():
    data = _synthetic_dataset()
    data["dengue_total"] = None
    with pytest.raises(DataPreparationError):
        prepare(data, ROLE_CONFIG)


def test_prepare_does_not_mutate_raw_input():
    data = _synthetic_dataset()
    original = data.copy()
    prepare(data, ROLE_CONFIG)
    pd.testing.assert_frame_equal(data, original)


def test_prepare_is_deterministic():
    data = _synthetic_dataset()
    result_a = prepare(data, ROLE_CONFIG)
    result_b = prepare(data, ROLE_CONFIG)
    pd.testing.assert_frame_equal(
        result_a.data.reset_index(drop=True), result_b.data.reset_index(drop=True)
    )
    assert result_a.report.rows_in == result_b.report.rows_in
    assert result_a.report.rows_out == result_b.report.rows_out


def test_prepare_uses_role_configuration_columns_not_hardcoded_names():
    """The pipeline must access columns via role_config, not hardcoded
    OpenDengue-specific names, for the general role-mapped columns."""
    data = _synthetic_dataset().rename(
        columns={
            "adm_0_name": "country_name",
            "dengue_total": "case_count",
        }
    )
    renamed_config = RoleConfiguration(
        time="calendar_start_date",
        location="country_name",
        surveillance_measure="case_count",
        identifier=None,
    )
    result = prepare(data, renamed_config)
    assert result.report.rows_out == 8
