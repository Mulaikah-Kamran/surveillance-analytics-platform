# Exploratory Data Analysis

**Milestone:** 5 — Exploratory Data Analysis
**Module:** `src/surveillance_platform/eda/`

## Purpose

Characterizes and interprets the analysis-ready dataset produced by
Milestone 4 (`PreparationResult.data`): descriptive statistics and
distribution summary for the configured Surveillance Measure,
post-cleaning missingness, `T_res` / `case_definition_standardised`
interpretation checks, annual time-series summaries, country
comparisons, and an optional annual population-normalized reported-case
rate.

M5 does not clean, correct, or otherwise modify data — that is
Milestone 4's responsibility. It also does not visualize (Milestone
6), forecast (Milestone 7), or expose any UI (Milestone 8).

## M4 / M5 boundary

M5 consumes the plain, cleaned DataFrame from
`PreparationResult.data` and the same `RoleConfiguration` — never the
whole `PreparationResult`, so M5 stays decoupled from M4's internal
report structure, mirroring the same boundary discipline already
established between M3 and M4.

M4's Data Profiling stage and M5's missingness summary look similar
but answer different questions for different audiences: M4 profiles
the *raw* input to feed Quality Assessment; M5 profiles the
*analysis-ready* dataset an analyst is actually about to work with.
Computing this independently in M5 is not a duplication of M4.

## Output contract

```python
from surveillance_platform.eda import analyze

result = analyze(prepared_data, role_config, population_data=None)
```

`prepared_data` is `PreparationResult.data`. `population_data` is
optional (see below). Returns an `EDAResult` — see
`surveillance_platform.eda.report` for every nested result dataclass.
Never mutates either input. Each analytical function (`descriptive_statistics`,
`distribution_summary`, `missingness_summary`, `resolution_summary`,
`case_definition_summary`, `time_series_summary`, `country_comparison`,
`population_normalized_summary`) is also independently importable and
testable.

## Variable scope

The configured Surveillance Measure column is the only column given
full quantitative treatment (descriptive statistics, distribution) —
M5 never scans or analyzes every numeric column in the dataset. Time
and Location are treated structurally, through the time-series and
country-comparison summaries, not as generic variables to describe.

`T_res` and `case_definition_standardised` are the two additional
OpenDengue columns explicitly analyzed, because Milestone 2 evidence
and direct data inspection (below) demonstrated they materially affect
interpretation. Every other additional column (`ISO_A0`,
`FAO_GAUL_code`, `RNE_iso_code`, `S_res`, `Year`, `adm_1_name`,
`adm_2_name`, `IBGE_code`) is redundant, constant, or derivable per
`docs/datasets/03_schema.md`, and is not analyzed. Both `T_res` and
`case_definition_standardised` checks degrade gracefully — the
corresponding `EDAResult` field is `None`, not an error — if the
column is absent, the same pattern M4 already established for
`calendar_end_date`.

## Annual aggregation and the homogeneity checks

M5 produces annual reported-case aggregates grouped by `(country,
calendar year)`, using the `time` column M4's Temporal Standardization
stage already derived (never `role_config.time` directly).

Before an annual aggregate is interpreted, two checks run per
country-year:

* Is `T_res` homogeneous within the country-year?
* Is `case_definition_standardised` homogeneous within the
  country-year?

If either is heterogeneous, the aggregate is **still produced** and
the relevant flag (`resolution_homogeneous` /
`case_definition_homogeneous` on `CountryYearSummary`) is set to
`False` — never silently corrected, reconciled, or discarded. This
extends the same "assess and report, don't silently correct"
philosophy M4 already applies to interval inversions.

This is a **generic rule**, evaluated fresh against whatever data is
passed in — no country or year is ever hard-coded. On the real
OpenDengue National Extract, restricted to the four ADR-008 study
countries, this rule currently finds:

* **0** country-years with heterogeneous `T_res` (confirmed by direct
  inspection: annual and sub-annual rows never overlap in time for any
  study country, and no country-year mixes resolutions).
* **1** country-year with heterogeneous `case_definition_standardised`:
  Bangladesh 2021 (9 months reported as `Confirmed`, 3 months as
  `Total`) — discovered by the generic check above, not hard-coded.

These are empirical facts about the current dataset, not architectural
assumptions. A future or second dataset (Milestone 9) may behave
differently; the checks will surface whatever is actually true of
that dataset.

### Reporting gaps

`max_year_gap` (per country, in `CountryGapSummary`) is the largest
difference between two consecutive reported calendar years — the same
metric already used in Milestone 2's data quality profile
(`docs/datasets/05_data_quality_profile.md`), not a newly invented
statistic.

## Country comparison

For every country present in the data: observation count, temporal
coverage, Surveillance Measure descriptive statistics, post-cleaning
missingness, and the `case_definition_standardised` / `T_res`
distributions.

**Reported counts, not disease burden.** Every descriptive statistic
in the country-comparison output describes *reported case counts* for
that country — never incidence, disease burden, or true case counts,
per the Freeze Document's existing caution (PFD Section 30). No
cross-country statistical significance testing is performed.

## Population normalization

**Optional.** If `population_data` is not supplied to `analyze()`,
`EDAResult.population_normalized` is `None` and every other analytical
output is produced normally — this is never an error, and population
normalization is never a required input to Milestone 9's second
dataset.

**Source:** World Bank World Development Indicators, indicator
`SP.POP.TOTL` ("Population, total"), for the four ADR-008 study
countries (Sri Lanka `LKA`, Bangladesh `BGD`, Maldives `MDV`, Nepal
`NPL`). Selected over UN World Population Prospects specifically
because WDI's single-indicator query returns exactly the
`(country, year, population)` figure this project needs, without
filtering a larger multi-variant demographic release down to one
slice — consistent with this project's existing preference for the
smaller, more directly reproducible data artifact (e.g. the National
Extract over the Temporal Extract, ADR-002). Data: CC BY-4.0, no
authentication required, national-level annual estimates from 1960
onward — covering the full study period for all four countries.

**Acquisition:** `python data/download_population_reference.py`
follows the same acquisition/reproducibility pattern as
`data/download_national_extract.py` — queries the WDI API, verifies
the response against a pinned SHA-256 checksum, and writes a minimal
`country, year, population` CSV to `data/raw/population_reference.csv`
(git-ignored, never committed, reproducible by any reviewer). `country`
values match the OpenDengue National Extract's `adm_0_name`
representation exactly — uppercase (e.g. `"SRI LANKA"`, not
`"Sri Lanka"`), confirmed by direct inspection of the real dataset —
not an ADR-008-style title-cased name and not an ISO3 code. The
ISO3-to-name (and casing) mapping is handled once, inside the
acquisition script, so `surveillance_platform.eda.population` itself
never needs to know about ISO3 codes or OpenDengue's casing
convention.

**Methodology:** the rate is computed from the already
homogeneity-checked *annual* aggregate (`TimeSeriesSummary.country_years`),
never from raw or sub-annual rows — this sidesteps any question of how
to apply an annual population denominator to a weekly or monthly
count. No interpolation, no demographic projection, no sub-annual
rate. A `(country, year)` present in the time series but absent from
the population reference is skipped, not an error.

**Labeling.** The result is always a *reported-case rate per 100,000
population* — never incidence, incidence rate, disease burden, or true
disease rate. This extends the same reported-vs-true-burden caution
already established for raw counts (PFD Section 30) to the normalized
figure as well.

## What is deferred

Visualization (Milestone 6), forecasting or any trend/seasonality
modeling (Milestone 7), Streamlit/UI (Milestone 8), cross-dataset
adaptation (Milestone 9), and portfolio documentation (Milestone 10)
are all explicitly out of scope here. `T_res`-aware resolution
reconciliation (as opposed to flagging), sub-annual population rates,
hypothesis testing, regression, correlation analysis, PCA, clustering,
generic anomaly detection, feature engineering, dimensionality
reduction, and imputation are also explicitly out of scope for this
milestone.
