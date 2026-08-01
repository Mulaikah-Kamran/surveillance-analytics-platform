# Data Quality Profile — OpenDengue National Extract (v1.3)

**Milestone:** 2 — Data Acquisition & Understanding
**Status:** Observations only. Nothing in this document is cleaned,
imputed, or filtered — that is Milestone 4's job. This is the evidence
base the Milestone 4 quality-assessment module will later formalize into
reusable code; here it is exploratory analysis, not production logic
(consistent with the "No profiling code" boundary for this milestone).

## Global Profile (all 129 countries, 29,873 rows)

- **Date coverage:** 1924-01-20 to 2025-04-30 (~101 years, though see
  "Coverage is highly uneven" below — this is the extreme range, not the
  typical one).
- **Missing values:** `adm_1_name`, `adm_2_name`, and `IBGE_code` are
  100% missing, as expected — the National Extract is country-level only,
  and `IBGE_code` is Brazil-specific. All other columns are 0% missing.
- **Full duplicate rows:** 0.
- **Row-level key integrity:** 0 duplicate (`adm_0_name`,
  `calendar_start_date`, `calendar_end_date`) combinations across all
  29,873 rows.
- **Negative values:** `dengue_total` is never negative (0 rows).
- **Zero values:** 32.6% of rows report `dengue_total == 0`. This is not
  itself an anomaly — genuine zero-case reporting periods are expected —
  but it means naive log-transforms in later forecasting work will need
  to account for zeros.
- **Interval consistency:** 0 rows where `calendar_end_date` <
  `calendar_start_date`.
- **`case_definition_standardised` casing anomaly:** the category
  `Confirmed` (1,307 rows) and a separately-counted, lowercase
  `confirmed` (103 rows) both exist. This looks like an upstream
  normalization inconsistency rather than a substantive distinction, but
  it is recorded as an observation, not corrected, per this milestone's
  scope.

## Global Temporal Resolution and Case Definition Mix

| `T_res` | Rows | Share |
|---|---|---|
| Week | 23,248 | 77.8% |
| Year | 3,495 | 11.7% |
| Month | 3,130 | 10.5% |

| `case_definition_standardised` | Rows |
|---|---|
| Total | 23,592 |
| Suspected | 3,295 |
| Confirmed | 1,307 |
| Probable and confirmed | 1,074 |
| Suspected and confirmed | 399 |
| Probable | 103 |
| confirmed (lowercase) | 103 |

This directly confirms a caveat already anticipated in the Freeze
Document (Section 30, Dataset Limitations & Risks): case definitions vary
across the dataset (1997 vs. 2009 WHO standards, and across source
categories), so cross-country and even within-country-over-time
comparisons need to account for which case definition applied.

## South Asian Countries — Reporting Consistency and Completeness

All 8 SAARC countries are present in the National Extract. Profiled
directly for the country-selection decision (`../decision_logs/`):

| Country | Rows | Year range | Years reported / span | Max year gap | `T_res` mix | Case definitions used | Zero-value share | Source categories |
|---|---|---|---|---|---|---|---|---|
| Afghanistan | 94 | 2021–2025 | 5 / 5 | 0 | Week 67, Month 27 | Total, Suspected | 4.3% | WHOEMRO, WHO |
| Bangladesh | 209 | 1980–2025 | 42 / 46 | 5 | Month 183, Year 26 | Confirmed, Total | 19.1% | MOH, WHO, WHOSEARO, LITERATURE, TYCHO |
| Bhutan | 49 | 1985–2024 | 40 / 40 | 0 | Year 39, Month 10 | Total, Confirmed | 44.9% | WHOSEARO, MOH |
| India | 35 | 1991–2025 | 35 / 35 | 0 | Year 34, Month 1 | Total, Confirmed | 0.0% | WHOSEARO, MOH, LITERATURE, WHO |
| Maldives | 196 | 1985–2025 | 40 / 41 | 2 | Month 171, Year 25 | Total (only) | 5.6% | MOH, WHO, WHOSEARO |
| Nepal | 76 | 1985–2025 | 41 / 41 | 0 | Month 39, Year 37 | Total, Confirmed | 27.6% | WHO, MOH, WHOSEARO, LITERATURE |
| Pakistan | 43 | 1994–2025 | 26 / 32 | 6 | Year 23, Month 20 | Total, Suspected and confirmed, Confirmed | 0.0% | LITERATURE, WHO **(no MOH)** |
| Sri Lanka | 579 | 1965–2024 | 49 / 60 | 8 | Week 455, Month 92, Year 32 | Total (only) | 0.5% | MOH, WHO, TYCHO, WHOSEARO |

Notable observations, kept factual rather than interpretive (interpretation
and the resulting selection is in the decision log):

- **Row volume varies by >16x** across the 8 countries (35 for India vs.
  579 for Sri Lanka) despite all being long-observed countries.
- **India and Pakistan are almost entirely annual-resolution**: India has
  34 of 35 rows at `Year` resolution (only 1 `Month` row); Pakistan has
  23 of 43 at `Year` resolution. Both have far fewer datapoints than
  their multi-decade span would suggest a weekly/monthly-reporting
  country should produce.
- **Pakistan is the only one of the 8 with zero `MOH`-sourced rows** —
  all 43 rows trace to `LITERATURE` or `WHO` secondary compilations,
  and it is also the only country whose case-definition history includes
  three genuinely different categories (`Total`, `Suspected and
  confirmed`, `Confirmed`) rather than two.
- **Afghanistan's entire record spans only 5 years** (2021–2025) —
  every other country has at least 32 years of span.
- **Bhutan and Nepal have the highest zero-value shares** (44.9% and
  27.6%), consistent with lower-incidence or less consistently-monitored
  reporting relative to Sri Lanka, Maldives, and India.
- **`TYCHO`-sourced rows appear inside OpenDengue itself** for both Sri
  Lanka (36 rows) and Bangladesh (1 row) — i.e., Project Tycho is already
  one of the source categories OpenDengue compiled from for these two
  countries. This is relevant to the validation-dataset investigation
  (`06_validation_dataset_investigation.md`): a "second" dataset that
  Project Tycho supplied to the first one is not fully independent for
  those countries/periods.

## Coverage Is Highly Uneven Across All 129 Countries (Context)

The oldest record in the whole National Extract (1924) and the ~101-year
range quoted above are global extremes, not representative of the South
Asian subset — the earliest South Asian record is Sri Lanka's 1965 data.
This is noted here only to avoid an inflated impression of typical
historical depth; the country-selection decision log uses the per-country
figures in the table above, not the global range.
