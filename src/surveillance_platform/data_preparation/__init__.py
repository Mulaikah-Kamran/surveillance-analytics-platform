"""Data preparation module.

Implements the Milestone 4 Data Preparation Pipeline: Validation,
Data Profiling, Quality Assessment, Temporal Standardization, and
Cleaning, run in that frozen order (PFD Section 14 / ADR-003). Builds
on Milestone 3's Role Configuration contract rather than duplicating
it — callers must validate their ``RoleConfiguration`` via Milestone
3's ``validate()`` before calling :func:`prepare`.

Public API:

* :func:`prepare` — run the full pipeline.
* :class:`PreparationResult` — the pipeline's output (prepared data +
  report).
* :class:`PreparationReport` — the report bundled in a
  ``PreparationResult``.
* :class:`QualityFinding` — a single Quality Assessment finding.
* :class:`DataPreparationError` — raised on a hard, structural
  Validation failure.

Each stage is also independently importable for testing, e.g.
``surveillance_platform.data_preparation.validation.validate_dataset``.
"""

from surveillance_platform.data_preparation.exceptions import DataPreparationError
from surveillance_platform.data_preparation.pipeline import prepare
from surveillance_platform.data_preparation.report import (
    PreparationReport,
    PreparationResult,
    QualityFinding,
)

__all__ = [
    "DataPreparationError",
    "PreparationReport",
    "PreparationResult",
    "QualityFinding",
    "prepare",
]
