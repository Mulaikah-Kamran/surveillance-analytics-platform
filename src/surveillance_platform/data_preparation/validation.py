"""Validation stage — dataset-level structural prerequisites.

This is deliberately distinct from Milestone 3's ``validate()``: M3
validates whether a :class:`RoleConfiguration` is itself valid
(required roles present, columns exist). This module assumes that has
already happened and instead checks whether the *dataset*, once
role-mapped, satisfies the minimal structural preconditions needed
before the rest of the pipeline can run.

Detection only — no mutation. A failure here is a hard, pipeline-
halting failure (raises :class:`DataPreparationError`), because these
are preconditions for the pipeline to run meaningfully at all, not
row-level data-quality issues.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.data_preparation.exceptions import DataPreparationError
from surveillance_platform.role_configuration import RoleConfiguration

_REQUIRED_ROLE_FIELDS = ("time", "location", "surveillance_measure")


def validate_dataset(data: pd.DataFrame, role_config: RoleConfiguration) -> None:
    """Check dataset-level structural prerequisites.

    Assumes ``role_config`` has already been validated by Milestone
    3's ``validate()`` — this function does not re-check whether the
    configured columns exist. It checks:

    - the dataset is non-empty
    - the configured Time-role column is not entirely null
    - the configured Location-role column is not entirely null
    - the configured Surveillance Measure-role column is not entirely
      null

    Raises :class:`DataPreparationError` listing every violation found
    if any check fails. Returns ``None`` if the dataset passes.
    """
    violations: list[str] = []

    if data.empty:
        violations.append("Dataset is empty.")

    if not violations:
        for field_name in _REQUIRED_ROLE_FIELDS:
            column = getattr(role_config, field_name)
            if data[column].isna().all():
                violations.append(
                    f"Required role '{field_name}' is assigned to column "
                    f"'{column}', which is entirely null."
                )

    if violations:
        raise DataPreparationError(violations)
