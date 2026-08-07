"""Pipeline orchestrator — runs the five frozen M4 stages in order.

Validation -> Data Profiling -> Quality Assessment ->
Temporal Standardization -> Cleaning (PFD Section 14 / ADR-003).

This module only coordinates the stages; each stage's actual logic
lives in its own module and is independently importable/testable. The
caller is responsible for constructing and validating a
:class:`RoleConfiguration` via Milestone 3's ``validate()`` before
calling :func:`prepare` — this pipeline does not re-check role
configuration validity.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.data_preparation import cleaning, quality_assessment
from surveillance_platform.data_preparation.profiling import profile
from surveillance_platform.data_preparation.report import (
    PreparationReport,
    PreparationResult,
)
from surveillance_platform.data_preparation.temporal_standardization import (
    standardize_time,
)
from surveillance_platform.data_preparation.validation import validate_dataset
from surveillance_platform.role_configuration import RoleConfiguration


def prepare(
    raw_data: pd.DataFrame, role_config: RoleConfiguration
) -> PreparationResult:
    """Run the Data Preparation Pipeline.

    ``role_config`` must already be valid (checked via Milestone 3's
    ``validate()``) — this function assumes that precondition and does
    not re-validate role configuration itself.

    Runs, in order: Validation (hard-stop on structural failure), Data
    Profiling, Quality Assessment, Temporal Standardization, and
    Cleaning. Never mutates ``raw_data``. Deterministic: identical
    inputs always produce an identical :class:`PreparationResult`.
    """
    validate_dataset(raw_data, role_config)

    profile_facts = profile(raw_data)

    quality_findings = quality_assessment.assess_quality(raw_data, role_config)

    standardized_data, temporal_findings = standardize_time(raw_data, role_config)

    all_findings = quality_findings + temporal_findings

    cleaned_data, exclusion_reasons, cleaning_actions = cleaning.clean(
        standardized_data, all_findings
    )

    rows_in = len(raw_data)
    rows_out = len(cleaned_data)

    report = PreparationReport(
        rows_in=rows_in,
        rows_out=rows_out,
        rows_excluded=rows_in - rows_out,
        exclusion_reasons=exclusion_reasons,
        quality_findings=all_findings,
        cleaning_actions=cleaning_actions,
        warnings=[],
        profile=profile_facts,
    )

    return PreparationResult(data=cleaned_data, report=report)
