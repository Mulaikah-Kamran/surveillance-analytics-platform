"""Report structures for the forecasting module.

Kept minimal, matching the M4/M5 convention: plain typed dataclasses,
no formal enum hierarchy, no logging framework.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class Track:
    """A candidate monthly forecasting track for one country.

    Produced by :func:`surveillance_platform.forecasting.eligibility.detect_tracks`.
    Represents one contiguous run of sub-annual reporting under one
    consistent case definition (ADR-009). Ineligible tracks are still
    returned, not discarded -- ADR-009 Point 7 requires below-threshold
    tracks to be shown with a reliability warning, not hidden.

    ``case_definition`` is ``None`` when the ``case_definition_standardised``
    column was absent from the input (see ADR-009's 2026-09-08 addendum)
    or did not vary within the dataset.
    """

    country: str
    case_definition: str | None
    start: pd.Period
    end: pd.Period
    n_months: int
    gap_months: int
    eligible: bool
