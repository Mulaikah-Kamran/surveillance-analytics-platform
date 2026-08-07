"""Exceptions raised by the data preparation pipeline.

A single exception type is used for hard, pipeline-halting failures —
currently only the Validation stage (dataset-level structural
prerequisites) can raise one. Quality Assessment findings, cleaning
exclusions, and other row-level or advisory issues are never raised as
exceptions; they are reported in ``PreparationResult.report`` instead.
See ``docs/data_preparation.md`` for the full failure model.
"""

from __future__ import annotations


class DataPreparationError(Exception):
    """Raised when the dataset fails a hard, pipeline-halting structural check.

    Reserved for Validation-stage failures only (PFD Section 14 /
    ADR-003): an empty dataset, or a required-role column that is
    entirely null. Row-level or advisory issues are never raised this
    way — they are recorded as findings in the preparation report.
    """

    def __init__(self, violations: list[str]) -> None:
        if not violations:
            raise ValueError(
                "DataPreparationError requires at least one violation message."
            )
        self.violations = list(violations)
        message = "Dataset failed structural validation:\n" + "\n".join(
            f"- {violation}" for violation in self.violations
        )
        super().__init__(message)
