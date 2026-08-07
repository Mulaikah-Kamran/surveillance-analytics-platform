"""Role configuration module.

Responsible for explicit, user-assigned analytical role mapping
(Time, Location, Surveillance Measure, optional Identifier) and role
validation, per ADR-004 (Minimal Analytical Role Model). The platform
never infers or suggests roles — the user assigns them, and this
module validates the assignment against structural rules and, when a
dataset's columns are provided, against that dataset.

Public API:

* :class:`RoleConfiguration` — the role-to-column mapping.
* :func:`validate` — validate a configuration structurally and
  against a dataset's available columns; raises
  :class:`RoleConfigurationError` if invalid.
* :func:`validate_structure` — structural validation only.
* :func:`validate_against_columns` — dataset-compatibility validation
  only.
* :class:`RoleConfigurationError` — raised on any validation failure.
"""

from surveillance_platform.role_configuration.config import (
    RoleConfiguration,
    validate,
    validate_against_columns,
    validate_structure,
)
from surveillance_platform.role_configuration.exceptions import (
    RoleConfigurationError,
)

__all__ = [
    "RoleConfiguration",
    "RoleConfigurationError",
    "validate",
    "validate_against_columns",
    "validate_structure",
]
