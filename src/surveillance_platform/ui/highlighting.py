"""Optional role-column highlighting heuristic (ADR-004, ADR-010).

ADR-004 permits the interface to "visually highlight columns whose
names or data types are commonly associated with a required role, as
a convenience" -- explicitly never to pre-select or auto-assign.
This module returns *suggestions* only; the page code that uses it
must never set a suggested column as a dropdown's default value,
only display it as a hint alongside the (always-blank-by-default)
dropdown.

Deliberately Streamlit-free: this is pure pattern-matching logic,
testable without a UI, even though its only consumer is the UI layer.
"""

from __future__ import annotations

import pandas as pd

_TIME_NAME_HINTS = ("date", "time", "period", "month", "year")
_LOCATION_NAME_HINTS = ("country", "location", "region", "adm", "place", "area", "nation")
_MEASURE_NAME_HINTS = ("case", "count", "total", "incidence", "cases", "measure")
_IDENTIFIER_NAME_HINTS = ("id", "uuid", "identifier", "code")


def _name_matches(column: str, hints: tuple[str, ...]) -> bool:
    lowered = column.lower()
    return any(hint in lowered for hint in hints)


def suggest_roles(data: pd.DataFrame) -> dict[str, str | None]:
    """Suggest one column per role, or ``None`` if nothing looks like a fit.

    Returns ``{"time": ..., "location": ..., "surveillance_measure":
    ..., "identifier": ...}``. A suggestion is never a certainty --
    it's a starting point for the user to confirm or override.
    """
    suggestions: dict[str, str | None] = {
        "time": None,
        "location": None,
        "surveillance_measure": None,
        "identifier": None,
    }

    for column in data.columns:
        is_datetime = pd.api.types.is_datetime64_any_dtype(data[column])
        is_numeric = pd.api.types.is_numeric_dtype(data[column])

        if suggestions["time"] is None and (
            is_datetime or _name_matches(column, _TIME_NAME_HINTS)
        ):
            suggestions["time"] = column
            continue
        if suggestions["location"] is None and _name_matches(column, _LOCATION_NAME_HINTS):
            suggestions["location"] = column
            continue
        if suggestions["identifier"] is None and _name_matches(
            column, _IDENTIFIER_NAME_HINTS
        ):
            suggestions["identifier"] = column
            continue
        if (
            suggestions["surveillance_measure"] is None
            and is_numeric
            and _name_matches(column, _MEASURE_NAME_HINTS)
        ):
            suggestions["surveillance_measure"] = column
            continue

    return suggestions
