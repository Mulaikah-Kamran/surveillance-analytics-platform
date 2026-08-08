"""Exploratory Data Analysis module.

Implements Milestone 5: descriptive statistics, distribution summary,
post-cleaning missingness, ``T_res`` / ``case_definition_standardised``
interpretation checks, annual time-series summaries, country
comparisons, and an optional annual population-normalized reported-case
rate. Builds directly on Milestone 4's output
(``PreparationResult.data``) and the same ``RoleConfiguration`` —
never on M4's internal report structure.

Public API:

* :func:`analyze` — run the full M5 analysis.
* :class:`EDAResult` — the analysis output (see ``surveillance_platform.eda.report``
  for every nested result dataclass).

Each analytical function is also independently importable for testing,
e.g. ``surveillance_platform.eda.time_series.time_series_summary``.

See ``docs/eda.md`` for the full M5 design and interpretation caveats.
"""

from surveillance_platform.eda.pipeline import analyze
from surveillance_platform.eda.report import EDAResult

__all__ = [
    "EDAResult",
    "analyze",
]
