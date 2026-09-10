"""Quality Assessment stage — structured, evidence-based findings.

These checks are grounded in the current OpenDengue study dataset and
Milestone 2's data quality profile (see
``docs/about-the-data.md``); they are not universal
assumptions about all surveillance datasets. Milestone 9 will
determine what, if anything, needs adaptation for a second dataset.

This stage only reports findings — it never mutates data and never
dictates that a finding must be corrected. Whether (and how) a finding
is acted on is decided entirely by the Cleaning stage's explicitly
defined policies; some findings (e.g. interval inversions) currently
have no defined correction and are reported only.

One column referenced here — ``calendar_end_date`` — has no
corresponding role in :class:`RoleConfiguration` and is inherently
specific to OpenDengue's interval-based time representation (see
ADR-007). This is the known, localized point of dataset-specific
coupling anticipated by the M4 design; checks involving it are skipped
gracefully if the column is absent, rather than raising, so this stage
never halts the pipeline.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.data_preparation.report import QualityFinding
from surveillance_platform.role_configuration import RoleConfiguration

_REQUIRED_ROLE_FIELDS = ("time", "location", "surveillance_measure")

# Inherent to OpenDengue's interval-based time representation
# (ADR-007); not part of the general role model.
_INTERVAL_END_COLUMN = "calendar_end_date"


def _check_duplicate_key(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> list[QualityFinding]:
    """Flag rows sharing (location, time, interval end) — evidence: M2's
    confirmed duplicate-key check on
    (adm_0_name, calendar_start_date, calendar_end_date)."""
    if _INTERVAL_END_COLUMN not in data.columns:
        return []

    key_columns = [role_config.location, role_config.time, _INTERVAL_END_COLUMN]
    duplicated_mask = data.duplicated(subset=key_columns, keep=False)
    if not duplicated_mask.any():
        return []

    row_indices = data.index[duplicated_mask].tolist()
    return [
        QualityFinding(
            check="duplicate_key",
            severity="warning",
            message=(
                f"{len(row_indices)} row(s) share the same "
                f"({role_config.location}, {role_config.time}, "
                f"{_INTERVAL_END_COLUMN}) key."
            ),
            row_indices=row_indices,
        )
    ]


def _check_negative_surveillance_measure(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> list[QualityFinding]:
    """Flag negative values in the configured Surveillance Measure
    column — evidence: M2 confirmed 0 negative values are expected."""
    column = data[role_config.surveillance_measure]
    numeric = pd.to_numeric(column, errors="coerce")
    negative_mask = numeric < 0
    if not negative_mask.any():
        return []

    row_indices = data.index[negative_mask].tolist()
    return [
        QualityFinding(
            check="negative_surveillance_measure",
            severity="warning",
            message=(
                f"{len(row_indices)} row(s) have a negative value in "
                f"'{role_config.surveillance_measure}'."
            ),
            row_indices=row_indices,
        )
    ]


def _check_interval_inversion(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> list[QualityFinding]:
    """Flag rows where the interval end precedes the interval start —
    evidence: M2 confirmed 0 such rows are expected. Reported only;
    Cleaning has no defined correction for this finding."""
    if _INTERVAL_END_COLUMN not in data.columns:
        return []

    start = pd.to_datetime(data[role_config.time], errors="coerce")
    end = pd.to_datetime(data[_INTERVAL_END_COLUMN], errors="coerce")
    inverted_mask = end < start
    if not inverted_mask.any():
        return []

    row_indices = data.index[inverted_mask].tolist()
    return [
        QualityFinding(
            check="interval_inversion",
            severity="warning",
            message=(
                f"{len(row_indices)} row(s) have {_INTERVAL_END_COLUMN} "
                f"earlier than {role_config.time}."
            ),
            row_indices=row_indices,
        )
    ]


def _check_non_numeric_surveillance_measure(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> list[QualityFinding]:
    """Flag rows where the surveillance measure isn't null, but also
    isn't a usable number (e.g. placeholder text like 'unknown' or
    'not available', sometimes used in real surveillance exports in
    place of a true missing value).

    Caught via a real crash, not assumed: a column with a genuine mix
    of numbers and non-numeric text passed the existing missing-value
    check (since the text values aren't null), then reached
    forecasting's population-rate calculation and raised a raw
    TypeError there, with a full stack trace shown to the user
    instead of a clear message at the right stage.
    """
    column = data[role_config.surveillance_measure]
    non_null_mask = column.notna()
    numeric = pd.to_numeric(column, errors="coerce")
    non_numeric_mask = non_null_mask & numeric.isna()
    if not non_numeric_mask.any():
        return []

    row_indices = data.index[non_numeric_mask].tolist()
    return [
        QualityFinding(
            check="non_numeric_surveillance_measure",
            severity="warning",
            message=(
                f"{len(row_indices)} row(s) have a non-numeric value for "
                f"required role 'surveillance_measure' "
                f"(column '{role_config.surveillance_measure}')."
            ),
            row_indices=row_indices,
        )
    ]


def _check_missing_required_values(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> list[QualityFinding]:
    """Flag rows missing a value in a required role column."""
    findings: list[QualityFinding] = []
    for field_name in _REQUIRED_ROLE_FIELDS:
        column = getattr(role_config, field_name)
        missing_mask = data[column].isna()
        if not missing_mask.any():
            continue

        row_indices = data.index[missing_mask].tolist()
        findings.append(
            QualityFinding(
                check="missing_required_value",
                severity="warning",
                message=(
                    f"{len(row_indices)} row(s) missing a value for "
                    f"required role '{field_name}' (column '{column}')."
                ),
                row_indices=row_indices,
            )
        )
    return findings


def assess_quality(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> list[QualityFinding]:
    """Run all Quality Assessment checks and return the findings.

    Never mutates ``data`` and never halts the pipeline — findings are
    purely informational at this stage. What happens next (if
    anything) is entirely Cleaning's decision, per its explicitly
    defined policies.
    """
    findings: list[QualityFinding] = []
    findings.extend(_check_duplicate_key(data, role_config))
    findings.extend(_check_negative_surveillance_measure(data, role_config))
    findings.extend(_check_non_numeric_surveillance_measure(data, role_config))
    findings.extend(_check_interval_inversion(data, role_config))
    findings.extend(_check_missing_required_values(data, role_config))
    return findings
