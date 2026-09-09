"""Spatial-resolution sanity check (ADR-010).

Opportunistic, not a hard dependency: ``S_res`` is an OpenDengue-
specific column (the same pattern already established for ``T_res``/
``case_definition_standardised`` in ADR-009's addendum), not part of
ADR-004's frozen role model. Its absence is not an error.
"""

from __future__ import annotations

import pandas as pd

#: The only value the real National Extract contains (verified
#: directly against the acquired data during ADR-010 design: 29,873/
#: 29,873 rows are "Admin0"). ADR-002 documents the Temporal Extract
#: as ~93% Admin2-level -- untested against this pipeline.
EXPECTED_SPATIAL_RESOLUTION = "Admin0"


def check_spatial_resolution(data: pd.DataFrame) -> str | None:
    """Warn (never block) if uploaded data looks sub-national.

    Returns a human-readable warning message, or ``None`` if the
    ``S_res`` column is absent (nothing to check) or every value
    already matches :data:`EXPECTED_SPATIAL_RESOLUTION`.
    """
    if "S_res" not in data.columns:
        return None
    unexpected = data.loc[data["S_res"] != EXPECTED_SPATIAL_RESOLUTION, "S_res"]
    if unexpected.empty:
        return None
    distinct = sorted(unexpected.dropna().unique().tolist())
    return (
        "This file appears to contain sub-national records "
        f"(S_res values other than '{EXPECTED_SPATIAL_RESOLUTION}' found: "
        f"{', '.join(str(v) for v in distinct)}). This project is validated "
        "against national-level surveillance data -- results with "
        "sub-national data have not been tested."
    )
