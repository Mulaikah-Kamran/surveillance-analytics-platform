"""Temporal Standardization stage — implements ADR-007.

Derives a single analytical ``time`` column (dtype ``datetime64[ns]``)
from the column assigned to the Time role in
:class:`RoleConfiguration`. The source column is always obtained via
``role_config.time`` — never a hardcoded column name — even though it
currently resolves to ``calendar_start_date`` for the OpenDengue study
configuration.

``calendar_start_date``, ``calendar_end_date``, and ``T_res`` are
never modified, renamed, or removed; ``time`` is added alongside them.
``T_res`` is passthrough only and never influences this stage's
behavior.

A Time-role value that cannot be parsed as a date is left null in
``time`` and reported as a finding — it is never a hard pipeline
failure here. Cleaning decides whether to exclude the affected row.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.data_preparation.report import QualityFinding
from surveillance_platform.role_configuration import RoleConfiguration


def standardize_time(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> tuple[pd.DataFrame, list[QualityFinding]]:
    """Add a derived ``time`` column (datetime64[ns]) to a copy of ``data``.

    Returns the new dataframe and a list of findings for any rows
    whose Time-role value could not be parsed as a date. Does not
    mutate the input ``data``.
    """
    prepared = data.copy()
    # pandas 3.x's to_datetime no longer defaults to nanosecond
    # resolution; the frozen design locks `time` to datetime64[ns]
    # specifically, so the resolution is made explicit here.
    parsed = pd.to_datetime(prepared[role_config.time], errors="coerce").astype(
        "datetime64[ns]"
    )
    prepared["time"] = parsed

    unparseable_mask = parsed.isna() & prepared[role_config.time].notna()
    findings: list[QualityFinding] = []
    if unparseable_mask.any():
        row_indices = prepared.index[unparseable_mask].tolist()
        findings.append(
            QualityFinding(
                check="unparseable_time",
                severity="warning",
                message=(
                    f"{len(row_indices)} row(s) have a value in "
                    f"'{role_config.time}' that could not be parsed as a date."
                ),
                row_indices=row_indices,
            )
        )

    return prepared, findings
