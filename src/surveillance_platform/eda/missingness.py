"""Post-cleaning missingness summary.

Deliberately distinct from Milestone 4's Data Profiling stage: M4's
``profile()`` runs on the *raw* input to feed Quality Assessment. This
module runs on the *analysis-ready* (post-Cleaning) dataset, and
answers a different question — what does the dataset an analyst is
about to work with actually look like? Computing this independently is
not a duplication of M4's profiling; the two serve different consumers
at different pipeline stages.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.eda.report import MissingnessSummary


def missingness_summary(data: pd.DataFrame) -> MissingnessSummary:
    """Per-column missing counts and fractions for ``data``.

    Never mutates ``data``. Performs no imputation and no judgment —
    purely descriptive, matching M4 Data Profiling's own stance on its
    raw-data equivalent.
    """
    row_count = len(data)
    missing_counts = {column: int(data[column].isna().sum()) for column in data.columns}
    missing_fractions = {
        column: (count / row_count if row_count else 0.0)
        for column, count in missing_counts.items()
    }
    return MissingnessSummary(
        row_count=row_count,
        missing_counts=missing_counts,
        missing_fractions=missing_fractions,
    )
