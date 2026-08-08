"""Optional annual population-normalized reported-case rate.

Population normalization is included because the study countries
(ADR-008) differ substantially in population size, making raw reported
counts alone inadequate for meaningful cross-country comparison — but
it is strictly optional: if ``population_data`` is not supplied,
:func:`population_normalized_summary` returns ``None`` and the rest of
``analyze()`` runs normally. This keeps population normalization from
ever becoming a required dependency (in particular, not a requirement
for Milestone 9's second-dataset work).

The rate is computed from the already homogeneity-checked *annual*
aggregate in :class:`TimeSeriesSummary` — never from raw or sub-annual
rows — which is exactly why this module depends on a
:class:`TimeSeriesSummary` rather than the raw prepared DataFrame. No
interpolation, no demographic projection, no sub-annual rate is
computed.

Expected ``population_data`` schema — a plain DataFrame with columns:

* ``country`` — country name, matching the values in the dataset's
  configured Location-role column (e.g. ``"Sri Lanka"``), *not* an
  ISO3 code. Any ISO3-to-name mapping needed for a given source is an
  acquisition-time concern (see ``docs/eda.md``), not this module's.
* ``year`` — calendar year (int).
* ``population`` — total population for that country-year (int).

A (country, year) present in the time-series summary but absent from
``population_data`` is skipped gracefully — not an error — since a
single missing population figure shouldn't prevent every other rate
from being reported.

The result is always labelled a *reported-case rate per 100,000
population*, never incidence or true disease burden (PFD Section 30).
"""

from __future__ import annotations

import pandas as pd

from surveillance_platform.eda.report import (
    PopulationNormalizedSummary,
    PopulationRateEntry,
    TimeSeriesSummary,
)

_RATE_BASIS = 100_000


def population_normalized_summary(
    time_series: TimeSeriesSummary, population_data: pd.DataFrame | None
) -> PopulationNormalizedSummary | None:
    """Compute annual reported-case rates from an annual time-series summary.

    Returns ``None`` if ``population_data`` is not supplied. Never
    mutates ``population_data``.
    """
    if population_data is None:
        return None

    lookup = {
        (str(row["country"]), int(row["year"])): row["population"]
        for _, row in population_data.iterrows()
    }

    rates: list[PopulationRateEntry] = []
    for country_year in time_series.country_years:
        key = (country_year.country, country_year.year)
        population = lookup.get(key)
        if population is None:
            continue

        rate = (country_year.reported_case_total / population) * _RATE_BASIS
        rates.append(
            PopulationRateEntry(
                country=country_year.country,
                year=country_year.year,
                population=int(population),
                reported_case_total=country_year.reported_case_total,
                reported_cases_per_100000=float(rate),
            )
        )

    return PopulationNormalizedSummary(rates=rates)
