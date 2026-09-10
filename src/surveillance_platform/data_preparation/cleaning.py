"""Cleaning stage — the only stage allowed to modify or remove data.

Applies only two explicitly defined policies (see the frozen M4
design and Milestone 2's data quality profile):

A. Casing correction: normalizes the confirmed M2 anomaly in
   ``case_definition_standardised`` (lowercase ``confirmed`` -> the
   dominant ``Confirmed``). This column is inherent to the OpenDengue
   study dataset and unrelated to the role model; the check is skipped
   gracefully if the column is absent.
B. Required-role exclusions: removes rows flagged by Quality
   Assessment as missing a required role value, having a non-numeric
   surveillance measure (e.g. placeholder text like "unknown" in
   place of a true missing value), or flagged by Temporal
   Standardization as having an unparseable Time value.

No other correction is applied. In particular, findings such as
interval inversions are reported by Quality Assessment but have no
defined cleaning policy here, and are therefore left unmodified and
unexcluded — this is intentional, not an oversight. Cleaning never
imputes and never invents a missing value.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.data_preparation.report import QualityFinding
from surveillance_platform.role_configuration import RoleConfiguration

_CASE_DEFINITION_COLUMN = "case_definition_standardised"
_CASING_ANOMALY_VALUE = "confirmed"
_CASING_CANONICAL_VALUE = "Confirmed"

_EXCLUSION_FINDING_CHECKS = (
    "missing_required_value",
    "unparseable_time",
    "non_numeric_surveillance_measure",
)


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
    data: pd.DataFrame, findings: list[QualityFinding], role_config: RoleConfiguration
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Remove rows flagged as having an unusable required-role value.

    Only findings with a check name in ``_EXCLUSION_FINDING_CHECKS``
    (missing required value, unparseable time, non-numeric
    surveillance measure) are acted on; other findings — such as
    interval inversions — have no defined correction and are left
    alone. Returns the filtered dataframe (a new object; the input is
    not mutated) and a mapping of exclusion reason -> row count.
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

    cleaned = (
        data.copy()
        if not row_indices_to_exclude
        else data.drop(index=list(row_indices_to_exclude))
    )

    # Real bug, caught via a real crash: excluding non-numeric rows
    # (e.g. placeholder text like "unknown" mixed in with real
    # numbers) isn't enough on its own -- pandas keeps the whole
    # column at dtype "object" once it has seen any non-numeric value
    # in it, even after those specific rows are gone. Forecasting's
    # own rate calculation (a plain division) then failed with a raw
    # TypeError on the remaining, perfectly valid numbers, because
    # they were still stored as an object-dtype column, not true
    # numbers. Converting explicitly here, once, after exclusion,
    # fixes this for every downstream stage rather than requiring
    # each one to defensively re-coerce the column itself.
    measure_column = role_config.surveillance_measure
    if measure_column in cleaned.columns:
        cleaned[measure_column] = pd.to_numeric(cleaned[measure_column])

    return cleaned, exclusion_reasons


def clean(
    data: pd.DataFrame, findings: list[QualityFinding], role_config: RoleConfiguration
) -> tuple[pd.DataFrame, dict[str, int], list[str]]:
    """Apply the Cleaning stage's explicitly defined policies.

    Returns the cleaned dataframe, a mapping of exclusion reason -> row
    count, and a list of human-readable cleaning-action descriptions.
    Never mutates the input ``data``.
    """
    cleaned, casing_actions = apply_casing_correction(data)
    cleaned, exclusion_reasons = exclude_unusable_required_rows(
        cleaned, findings, role_config
    )

    actions = list(casing_actions)
    for reason, count in exclusion_reasons.items():
        actions.append(f"Excluded {count} row(s) due to '{reason}'.")

    return cleaned, exclusion_reasons, actions
