"""Role configuration model and validation.

Implements the explicit, user-assigned analytical role mapping
required by ADR-004 (Minimal Analytical Role Model): the platform
never infers, guesses, or suggests roles — the user assigns them, and
this module only validates the assignment.

Two independent kinds of validity are checked, matching the Milestone
3 design:

* **Structural validity** — is the ``RoleConfiguration`` itself
  well-formed (required roles present and non-empty, no duplicate
  column assignments across roles, correct field types)?
* **Dataset compatibility** — do the assigned columns actually exist
  in a given dataset's available columns?

Neither check inspects column *contents* (e.g. "does this column
actually look like a date?"). That is a data preparation concern for
a later milestone, not role configuration.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from surveillance_platform.role_configuration.exceptions import (
    RoleConfigurationError,
)

# The four roles fixed by ADR-004. Not a registry — the role model is
# frozen, not extensible.
_REQUIRED_ROLE_FIELDS = ("time", "location", "surveillance_measure")
_ALL_ROLE_FIELDS = (*_REQUIRED_ROLE_FIELDS, "identifier")


@dataclass
class RoleConfiguration:
    """An explicit, user-assigned mapping from analytical roles to columns.

    ``time``, ``location``, and ``surveillance_measure`` are required
    roles (ADR-004) and must be non-empty column-name strings.
    ``identifier`` is optional and defaults to ``None``.

    Constructing a ``RoleConfiguration`` does not validate it — call
    :func:`validate` (or :func:`validate_structure` /
    :func:`validate_against_columns`) explicitly. This keeps
    construction and validation separate, so a test (or caller) can
    build a deliberately invalid configuration and inspect exactly
    what is wrong with it.
    """

    time: str
    location: str
    surveillance_measure: str
    identifier: str | None = None


def validate_structure(config: RoleConfiguration) -> list[str]:
    """Check that ``config`` is internally well-formed.

    Returns a list of violation messages (empty if the configuration
    is structurally valid). Does not check the configuration against
    any dataset.
    """
    violations: list[str] = []

    for field_name in _REQUIRED_ROLE_FIELDS:
        value = getattr(config, field_name)
        if not isinstance(value, str) or not value.strip():
            violations.append(
                f"Required role '{field_name}' must be a non-empty string "
                f"(got {value!r})."
            )

    identifier = config.identifier
    if identifier is not None and (
        not isinstance(identifier, str) or not identifier.strip()
    ):
        violations.append(
            f"Optional role 'identifier' must be None or a non-empty string "
            f"(got {identifier!r})."
        )

    # Duplicate-column check only makes sense among assignments that are
    # themselves valid strings — an invalid field is already reported
    # above, so skip it here to avoid a redundant/misleading message.
    assigned: dict[str, list[str]] = {}
    for field_name in _ALL_ROLE_FIELDS:
        value = getattr(config, field_name)
        if isinstance(value, str) and value.strip():
            assigned.setdefault(value, []).append(field_name)

    for column, roles in assigned.items():
        if len(roles) > 1:
            role_list = ", ".join(roles)
            violations.append(
                f"Column '{column}' is assigned to more than one role: " f"{role_list}."
            )

    return violations


def validate_against_columns(
    config: RoleConfiguration, available_columns: Iterable[str]
) -> list[str]:
    """Check that every assigned column in ``config`` exists in the dataset.

    ``available_columns`` is a plain iterable of column-name strings —
    not a pandas DataFrame or a Dataset abstraction — so this module
    stays independent of however a dataset is actually loaded.

    Returns a list of violation messages (empty if every assigned
    column is present). Does not repeat structural checks; call
    :func:`validate_structure` for those.
    """
    columns = set(available_columns)
    violations: list[str] = []

    for field_name in _ALL_ROLE_FIELDS:
        value = getattr(config, field_name)
        if isinstance(value, str) and value.strip() and value not in columns:
            violations.append(
                f"Role '{field_name}' is assigned to column '{value}', which "
                f"is not present in the available columns."
            )

    return violations


def validate(config: RoleConfiguration, available_columns: Iterable[str]) -> None:
    """Validate ``config`` structurally and against ``available_columns``.

    Raises :class:`RoleConfigurationError` listing every violation
    found if the configuration is invalid — both structural problems
    and dataset-compatibility problems are collected together, so an
    otherwise-valid role pointing at a missing column is reported even
    if another role also has a structural problem. Returns ``None`` if
    the configuration is fully valid.
    """
    structural_violations = validate_structure(config)
    # validate_against_columns already skips fields with no valid
    # string value, so it is safe to run regardless of structural
    # violations elsewhere in the configuration.
    column_violations = validate_against_columns(config, available_columns)

    violations = structural_violations + column_violations
    if violations:
        raise RoleConfigurationError(violations)
