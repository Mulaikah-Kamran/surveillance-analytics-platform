"""Exceptions raised by the role configuration subsystem.

A single, focused exception type is used for every role configuration
failure — both structural problems with a :class:`RoleConfiguration`
itself and dataset-compatibility problems detected when a
configuration is checked against a dataset's available columns. This
keeps the error model proportional to the small scope of Milestone 3
(see ADR-004 and the Milestone 3 decision audit): callers do not need
to distinguish exception subclasses, only read the reported
violations.
"""

from __future__ import annotations


class RoleConfigurationError(Exception):
    """Raised when a role configuration is invalid.

    Carries every violation found during validation (rather than
    stopping at the first one), so a caller — or a test — can see the
    complete set of problems with a configuration in a single
    exception instead of fixing and re-running one issue at a time.
    """

    def __init__(self, violations: list[str]) -> None:
        if not violations:
            raise ValueError(
                "RoleConfigurationError requires at least one violation message."
            )
        self.violations = list(violations)
        message = "Invalid role configuration:\n" + "\n".join(
            f"- {violation}" for violation in self.violations
        )
        super().__init__(message)
