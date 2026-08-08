"""Result structures produced by the Exploratory Data Analysis module.

Kept deliberately flat and minimal, in the style of
``data_preparation.report``: a handful of small, plain dataclasses
bundled into one top-level :class:`EDAResult` returned by
:func:`surveillance_platform.eda.analyze`. No nested framework, no
serialization, no formal severity/enum machinery.

Several fields are ``None`` rather than an empty structure when the
underlying input genuinely isn't available (e.g. ``resolution`` when
``T_res`` is absent from the dataset, or ``population_normalized``
when no population reference data is supplied) — this is a deliberate
"absent, not an error" contract, matching the graceful-degradation
pattern M4 already established for ``calendar_end_date``.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DescriptiveSummary:
    """Descriptive statistics for the configured Surveillance Measure column."""

    count: int
    mean: float
    median: float
    minimum: float
    maximum: float
    std: float


@dataclass
class DistributionSummary:
    """A minimal distribution summary for the Surveillance Measure column.

    ``zero_value_share`` mirrors the metric already used in Milestone
    2's data quality profile (``docs/datasets/05_data_quality_profile.md``),
    not a newly invented statistic.
    """

    q25: float
    q50: float
    q75: float
    zero_value_share: float


@dataclass
class MissingnessSummary:
    """Post-cleaning missingness facts.

    Distinct from Milestone 4's raw-data profiling: this describes the
    analysis-ready dataset actually consumed by M5, not the original
    raw input.
    """

    row_count: int
    missing_counts: dict[str, int] = field(default_factory=dict)
    missing_fractions: dict[str, float] = field(default_factory=dict)


@dataclass
class CategoricalDistribution:
    """A simple value-count distribution for one categorical column."""

    counts: dict[str, int] = field(default_factory=dict)


@dataclass
class CountryYearSummary:
    """One (country, calendar year) annual summary row.

    ``resolution_homogeneous`` and ``case_definition_homogeneous`` are
    ``None`` when the corresponding column (``T_res`` /
    ``case_definition_standardised``) is absent from the dataset —
    not ``True`` or ``False`` — so an absent column is never silently
    read as "homogeneous".
    """

    country: str
    year: int
    first_date: object
    last_date: object
    observation_count: int
    reported_case_total: float
    resolution_homogeneous: bool | None
    case_definition_homogeneous: bool | None


@dataclass
class CountryGapSummary:
    """Reporting-gap facts for one country.

    ``max_year_gap`` uses the same definition already established in
    Milestone 2's data quality profile: the largest difference between
    two consecutive reported calendar years (0 if every year in the
    country's span was reported, or if fewer than two years exist).
    """

    country: str
    years_covered: list[int] = field(default_factory=list)
    max_year_gap: int = 0


@dataclass
class TimeSeriesSummary:
    """Annual time-series summaries, per (country, year), plus reporting gaps."""

    country_years: list[CountryYearSummary] = field(default_factory=list)
    gaps: list[CountryGapSummary] = field(default_factory=list)


@dataclass
class CountryComparisonEntry:
    """One country's row in the country-comparison summary.

    ``descriptive`` statistics describe *reported case counts* for
    this country, not disease burden or incidence (PFD Section 30).
    """

    country: str
    observation_count: int
    first_date: object
    last_date: object
    descriptive: DescriptiveSummary
    missingness: MissingnessSummary
    case_definition_distribution: CategoricalDistribution | None
    resolution_distribution: CategoricalDistribution | None


@dataclass
class CountryComparison:
    """Country-comparison summary across the study countries present in the data."""

    countries: list[CountryComparisonEntry] = field(default_factory=list)


@dataclass
class PopulationRateEntry:
    """One (country, year) reported-case rate.

    Explicitly a *reported-case rate per 100,000 population* — never
    incidence or true disease burden (PFD Section 30). Computed from
    the already homogeneity-checked annual aggregate in
    :class:`TimeSeriesSummary`, not from raw or sub-annual rows.
    """

    country: str
    year: int
    population: int
    reported_case_total: float
    reported_cases_per_100000: float


@dataclass
class PopulationNormalizedSummary:
    """Optional annual reported-case-rate summary.

    Only produced when ``population_data`` is supplied to
    :func:`surveillance_platform.eda.analyze`; absent (``None`` on
    :class:`EDAResult`) otherwise, never an error.
    """

    rates: list[PopulationRateEntry] = field(default_factory=list)


@dataclass
class EDAResult:
    """The output of :func:`surveillance_platform.eda.analyze`."""

    descriptive: DescriptiveSummary
    distribution: DistributionSummary
    missingness: MissingnessSummary
    resolution: CategoricalDistribution | None
    case_definition: CategoricalDistribution | None
    time_series: TimeSeriesSummary
    country_comparison: CountryComparison
    population_normalized: PopulationNormalizedSummary | None = None
