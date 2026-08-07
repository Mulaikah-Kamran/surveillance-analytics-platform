"""Report structures shared across the data preparation pipeline stages.

Kept deliberately minimal per the frozen M4 design: a plain typed
``QualityFinding`` (no formal severity enum/hierarchy) and a small
``PreparationResult`` bundling prepared data with a report. No logging
framework, no database, no serialization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class QualityFinding:
    """A single structured finding produced by Quality Assessment.

    ``severity`` is a plain string field (e.g. ``"warning"``,
    ``"info"``) rather than a formal enum — the M4 design explicitly
    keeps this simple. A finding only reports a condition; it does not
    imply that Cleaning will act on it (see ``docs/data_preparation.md``
    for which findings have a defined cleaning policy and which do
    not, e.g. interval inversions are reported but never corrected).
    """

    check: str
    severity: str
    message: str
    row_indices: list[int] = field(default_factory=list)


@dataclass
class PreparationReport:
    """Metadata produced alongside the prepared dataset.

    Provides enough information for a downstream module or reviewer
    to understand what happened during preparation without needing a
    per-row audit log or logging framework.
    """

    rows_in: int
    rows_out: int
    rows_excluded: int
    exclusion_reasons: dict[str, int] = field(default_factory=dict)
    quality_findings: list[QualityFinding] = field(default_factory=list)
    cleaning_actions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    profile: dict[str, Any] = field(default_factory=dict)


@dataclass
class PreparationResult:
    """The output of :func:`surveillance_platform.data_preparation.prepare`.

    ``data`` is the prepared dataset (role columns preserved, plus the
    derived ``time`` column from Temporal Standardization).
    ``report`` carries the :class:`PreparationReport` describing what
    happened.
    """

    data: pd.DataFrame
    report: PreparationReport
