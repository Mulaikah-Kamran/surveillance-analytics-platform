"""Cleaning stage — the only stage allowed to modify or remove data.

Applies only two explicitly defined policies (see the frozen M4
design and Milestone 2's data quality profile):

A. Casing correction: normalizes the confirmed M2 anomaly in
   ``case_definition_standardised`` (lowercase ``confirmed`` -> the
   dominant ``Confirmed``). This column is inherent to the OpenDengue
   study dataset and unrelated to the role model; the check is skipped
   gracefully if the column is absent.
B. Required-role exclusions: removes rows flagged by Quality
   Assessment as missing a required role value, or flagged by
   Temporal Standardization as having an unparseable Time value.

No other correction is applied. In particular, findings such as
interval inversions are reported by Quality Assessment but have no
defined cleaning policy here, and are therefore left unmodified and
unexcluded — this is intentional, not an oversight. Cleaning never
imputes and never invents a missing value.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.data_preparation.report import QualityFinding

_CASE_DEFINITION_COLUMN = "case_definition_standardised"
_CASING_ANOMALY_VALUE = "confirmed"
_CASING_CANONICAL_VALUE = "Confirmed"

_EXCLUSION_FINDING_CHECKS = ("missing_required_value", "unparseable_time")


def apply_casing_correction(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Normalize the confirmed case-definition casing anomaly.

    Returns a copy of ``data`` with the correction applied (if the
    column is present and the anomaly occurs) and a list of
    human-readable action descriptions. Does not mutate the input.
    """
    cleaned = data.copy()
    actions: list[str] = []

    if _CASE_DEFINITION_COLUMN not in cleaned.columns:
        return cleaned, actions

    anomaly_mask = cleaned[_CASE_DEFINITION_COLUMN] == _CASING_ANOMALY_VALUE
    count = int(anomaly_mask.sum())
    if count > 0:
        cleaned.loc[anomaly_mask, _CASE_DEFINITION_COLUMN] = _CASING_CANONICAL_VALUE
        actions.append(
            f"Normalized {count} row(s) in '{_CASE_DEFINITION_COLUMN}' from "
            f"'{_CASING_ANOMALY_VALUE}' to '{_CASING_CANONICAL_VALUE}'."
        )

    return cleaned, actions


def exclude_unusable_required_rows(
    data: pd.DataFrame, findings: list[QualityFinding]
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Remove rows flagged as having an unusable required-role value.

    Only findings with a check name in ``_EXCLUSION_FINDING_CHECKS``
    (missing required value, unparseable time) are acted on; other
    findings — such as interval inversions — have no defined
    correction and are left alone. Returns the filtered dataframe (a
    new object; the input is not mutated) and a mapping of exclusion
    reason -> row count.
    """
    exclusion_reasons: dict[str, int] = {}
    row_indices_to_exclude: set = set()

    for finding in findings:
        if finding.check not in _EXCLUSION_FINDING_CHECKS:
            continue
        new_indices = [
            index
            for index in finding.row_indices
            if index not in row_indices_to_exclude
        ]
        if new_indices:
            exclusion_reasons[finding.check] = exclusion_reasons.get(
                finding.check, 0
            ) + len(new_indices)
        row_indices_to_exclude.update(finding.row_indices)

    if not row_indices_to_exclude:
        return data.copy(), exclusion_reasons

    cleaned = data.drop(index=list(row_indices_to_exclude))
    return cleaned, exclusion_reasons


def clean(
    data: pd.DataFrame, findings: list[QualityFinding]
) -> tuple[pd.DataFrame, dict[str, int], list[str]]:
    """Apply the Cleaning stage's explicitly defined policies.

    Returns the cleaned dataframe, a mapping of exclusion reason -> row
    count, and a list of human-readable cleaning-action descriptions.
    Never mutates the input ``data``.
    """
    cleaned, casing_actions = apply_casing_correction(data)
    cleaned, exclusion_reasons = exclude_unusable_required_rows(cleaned, findings)

    actions = list(casing_actions)
    for reason, count in exclusion_reasons.items():
        actions.append(f"Excluded {count} row(s) due to '{reason}'.")

    return cleaned, exclusion_reasons, actions
