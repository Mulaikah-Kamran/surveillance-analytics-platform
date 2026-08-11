# Visualization

**Milestone:** 6 — Visualization
**Module:** `src/surveillance_platform/visualization/`

## Purpose

Represents Milestone 5's analytical output (`EDAResult`) visually,
using Plotly. M6 is a pure representation layer: it produces the five
finalized visualizations and performs no cleaning, imputation,
recomputation of M5 statistics, hypothesis testing, regression,
correlation, PCA, clustering, forecasting, or smoothing/interpolation
of its own.

## M5 / M6 boundary

M5 computes analytical results; M6 represents those results visually.
`visualize()` and every individual visualization function consume
only an `EDAResult` — never `prepared_data` — mirroring the same
input-narrowing discipline already established between M3/M4 and
M4/M5 (M5 consumes `PreparationResult.data`, never the whole
`PreparationResult`; M6 consumes `EDAResult`, never `prepared_data`).

## Output contract

```python
from surveillance_platform.visualization import visualize

result = visualize(eda_result)
```

Returns a `VisualizationResult` — see
`surveillance_platform.visualization.report` for the five fields.
Never mutates `eda_result`. Each visualization function is also
independently importable and testable, e.g.
`surveillance_platform.visualization.trend.annual_surveillance_trend`.

## The five visualizations

| Visualization | Function | `EDAResult` input |
| --- | --- | --- |
| Annual surveillance trend | `annual_surveillance_trend` | `time_series.country_years` |
| Annual distribution by country | `annual_distribution_by_country` | `time_series.country_years` |
| Population-normalized distribution | `population_normalized_distribution` | `population_normalized` (optional) |
| Surveillance resolution / case-definition profile | `surveillance_resolution_profile` | `resolution`, `case_definition` (each optional) |
| Surveillance measure distribution | `surveillance_measure_distribution` | `descriptive`, `distribution` |

### Annual surveillance trend

One subplot per country ("small multiples") rather than a single
chart sharing one y-axis, since study countries can differ by orders
of magnitude in reported-case volume. Plots the annual
`reported_case_total` M5 already aggregated per (country, year) — no
smoothing, interpolation, or forecasting, and the reported-case
terminology is preserved throughout (never "incidence").

**Heterogeneity flags.** M5's per-country-year
`resolution_homogeneous` / `case_definition_homogeneous` flags (never
hard-coded to a specific country or year) are read generically: any
country-year where either flag is `False` is rendered with a distinct
marker (diamond, larger, red-outlined) and a hover tooltip naming
which check failed. On the real OpenDengue National Extract this
currently flags exactly the one country-year `docs/eda.md` documents
(Bangladesh 2021, heterogeneous `case_definition_standardised`) — an
empirical fact surfaced by the generic check, not a hard-coded case.

### Annual distribution by country

A box-and-strip plot of the same per-(country, year)
`reported_case_total` values, one box per country. Labeled as reported
counts throughout — never incidence or population-adjusted burden.

### Population-normalized distribution

Optional, mirroring M5's own optionality. If
`EDAResult.population_normalized` is `None` (or has no rate entries),
this function returns `None` and `visualize()` simply omits it from
`VisualizationResult` — never an error, never a fabricated or
independently-acquired population figure. When present, a box plot of
`reported_cases_per_100000`, one box per country, always labeled
*reported cases per 100,000 population* — never "incidence" (PFD
Section 30, extended by `docs/eda.md` to the normalized figure).

### Surveillance resolution / case-definition profile

Two side-by-side bar charts — `T_res` and
`case_definition_standardised` value counts — visualizing surveillance
*reporting characteristics*, deliberately kept visually and
semantically separate from the reported-case-count visualizations
above so the distinction between reporting metadata and disease burden
is never blurred. `resolution` and `case_definition` are each
independently optional on `EDAResult` (absent when the corresponding
column doesn't exist in the analyzed dataset); this visualization
renders whichever is available and returns `None` only if neither is.

### Surveillance measure distribution

Built entirely from M5's already-computed `DescriptiveSummary` (count,
mean, min, max, std) and `DistributionSummary` (q25, q50, q75,
zero-value share) — a Plotly "pre-computed" box trace
(`q1`/`median`/`q3`/`lowerfence`/`upperfence`/`mean`/`sd`) is
constructed directly from these five-and-more numbers. No row-level
data is accessed and no statistic is recomputed; this is a direct
visual rendering of M5's own summary output, not a new analysis.

## Empty/partial input handling

* If a visualization's *required* input is genuinely empty (e.g. zero
  country-years, zero Surveillance Measure observations), the
  function raises `EmptyVisualizationInputError`
  (`surveillance_platform.visualization._theme`) rather than
  producing a misleading empty or fabricated chart.
* If a visualization's input is *optional* by M5's own contract
  (`population_normalized`, or both `resolution` and
  `case_definition` absent), the function returns `None` instead —
  this is the expected, non-error "absent, not an error" path M5
  already established, not a failure.

## What is deferred

Forecasting or any trend/seasonality modeling (Milestone 7),
Streamlit/UI or dashboard/application layout (Milestone 8), deployment
functionality, and cross-dataset (second-dataset) validation are all
explicitly out of scope here, per the frozen M6 contract. M6 also
performs no data cleaning or imputation, does not modify `EDAResult`,
and does not recompute M5's analytical statistics beyond what
rendering a chosen chart type inherently requires (e.g. Plotly's own
box-plot rendering math over M5's already-aggregated annual values).
