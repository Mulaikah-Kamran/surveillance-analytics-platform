"""Data Profiling stage — descriptive facts only.

Produces plain descriptive facts about the dataset. Does not clean,
filter, correct, or judge whether anything found is acceptable — that
distinction belongs to Quality Assessment. Profiling never raises a
quality failure and never mutates the input.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def profile(data: pd.DataFrame) -> dict[str, Any]:
    """Produce descriptive facts about ``data``.

    Returns a plain dictionary of facts (row count, column count,
    per-column dtypes, per-column missing-value counts). Performs no
    judgment and no mutation; feeds Quality Assessment and the
    eventual preparation report.
    """
    return {
        "row_count": len(data),
        "column_count": len(data.columns),
        "dtypes": {column: str(dtype) for column, dtype in data.dtypes.items()},
        "missing_counts": {
            column: int(data[column].isna().sum()) for column in data.columns
        },
    }
