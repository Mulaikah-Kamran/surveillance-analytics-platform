"""Descriptive statistics and distribution summary — the primary
quantitative variable only.

The configured Surveillance Measure column is the sole target of
quantitative descriptive analysis (frozen M5 variable scope): this
module never scans or analyzes every numeric column in the dataset,
only ``role_config.surveillance_measure``.

Also produces the overall (dataset-wide) categorical distribution for
``T_res`` and ``case_definition_standardised`` when present — these
two columns are used because Milestone 2 evidence and direct data
inspection demonstrated they materially affect interpretation, not
because every additional column is analyzed generically. Both checks
degrade gracefully (return ``None``) if the column is absent, the
same pattern M4 already established for ``calendar_end_date``.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.eda.report import (
    CategoricalDistribution,
    DescriptiveSummary,
    DistributionSummary,
)
from surveillance_platform.role_configuration import RoleConfiguration

_RESOLUTION_COLUMN = "T_res"
_CASE_DEFINITION_COLUMN = "case_definition_standardised"


def descriptive_statistics(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> DescriptiveSummary:
    """Count/mean/median/min/max/std for the configured Surveillance Measure."""
    measure = pd.to_numeric(data[role_config.surveillance_measure], errors="coerce")
    return DescriptiveSummary(
        count=int(measure.count()),
        mean=float(measure.mean()),
        median=float(measure.median()),
        minimum=float(measure.min()),
        maximum=float(measure.max()),
        std=float(measure.std()),
    )


def distribution_summary(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> DistributionSummary:
    """Quartiles and zero-value share for the configured Surveillance Measure.

    ``zero_value_share`` reuses the metric already computed manually in
    Milestone 2's data quality profile, rather than introducing a new one.
    """
    measure = pd.to_numeric(data[role_config.surveillance_measure], errors="coerce")
    non_null = measure.dropna()
    zero_share = float((non_null == 0).sum() / len(non_null)) if len(non_null) else 0.0
    return DistributionSummary(
        q25=float(measure.quantile(0.25)),
        q50=float(measure.quantile(0.50)),
        q75=float(measure.quantile(0.75)),
        zero_value_share=zero_share,
    )


def resolution_summary(data: pd.DataFrame) -> CategoricalDistribution | None:
    """Overall ``T_res`` value-count distribution, or ``None`` if absent."""
    if _RESOLUTION_COLUMN not in data.columns:
        return None
    counts = data[_RESOLUTION_COLUMN].value_counts(dropna=True)
    return CategoricalDistribution(counts={str(k): int(v) for k, v in counts.items()})


def case_definition_summary(data: pd.DataFrame) -> CategoricalDistribution | None:
    """Overall ``case_definition_standardised`` distribution, or ``None`` if absent."""
    if _CASE_DEFINITION_COLUMN not in data.columns:
        return None
    counts = data[_CASE_DEFINITION_COLUMN].value_counts(dropna=True)
    return CategoricalDistribution(counts={str(k): int(v) for k, v in counts.items()})
