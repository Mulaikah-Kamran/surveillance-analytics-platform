"""Country-comparison summary.

For each country present in the data (the study scope remains the
four ADR-008 countries; this module does not itself enforce or expand
that scope — it simply summarizes whatever countries are present):
observation count, temporal coverage, Surveillance Measure descriptive
statistics, post-cleaning missingness, and the ``case_definition_standardised``
/ ``T_res`` distributions (present only if those columns exist).

The descriptive statistics here characterize *reported case counts*
for that country — never incidence, disease burden, or true case
counts (PFD Section 30). No cross-country statistical significance
testing is performed; that is explicitly out of scope for M5.
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.eda.descriptive import (
    case_definition_summary,
    descriptive_statistics,
    resolution_summary,
)
from surveillance_platform.eda.missingness import missingness_summary
from surveillance_platform.eda.report import CountryComparison, CountryComparisonEntry
from surveillance_platform.role_configuration import RoleConfiguration

_TIME_COLUMN = "time"


def country_comparison(
    data: pd.DataFrame, role_config: RoleConfiguration
) -> CountryComparison:
    """Build the per-country comparison summary. Does not mutate ``data``."""
    entries: list[CountryComparisonEntry] = []
    for country, group in data.groupby(role_config.location, sort=True):
        entries.append(
            CountryComparisonEntry(
                country=country,
                observation_count=len(group),
                first_date=group[_TIME_COLUMN].min(),
                last_date=group[_TIME_COLUMN].max(),
                descriptive=descriptive_statistics(group, role_config),
                missingness=missingness_summary(group),
                case_definition_distribution=case_definition_summary(group),
                resolution_distribution=resolution_summary(group),
            )
        )
    return CountryComparison(countries=entries)
