# Milestone 9 — Validation Workflow Report & Architecture Validation Summary

**Dataset:** CDC NNDSS weekly data, 2022–2026 ([ADR-011](adr/ADR-011-m9-validation-dataset-selection.md))
**Target condition:** Chlamydia trachomatis infection, 50 states + DC
**Preceding document:** [M9 Dataset Compatibility Report](m9-dataset-compatibility-report.md)
(pre-implementation analysis; this document records what actually
happened when that analysis was acted on)

## Evaluation Question, restated

PFD Section 7: *"To what extent can the proposed workflow and
architecture, designed primarily for the OpenDengue National Extract,
be validated using one additional surveillance dataset with minimal
adaptation while maintaining analytical reproducibility?"*

## What was built

Exactly one new artifact: `data/download_nndss_validation_dataset.py`,
an acquisition script mirroring `download_national_extract.py`'s own
boundary (acquire and do the minimum structural transformation needed
to produce a loadable file; leave cleaning decisions to the pipeline).
**Zero changes to `src/surveillance_platform/`** — the entire M3–M7
analytical pipeline (role configuration, data preparation, EDA,
visualization, forecasting) ran against this real, independently
sourced dataset completely unmodified.

## Workflow trace (each stage, against real data)

1. **Acquisition**: pulled 17,080 real rows via CDC's public Socrata
   API (no key, no login — confirmed during ADR-011's evaluation).
   Filtered to the 50 states + DC (12,444 rows), normalized casing,
   and combined `year`+`week` into one date column. One real
   implementation bug was caught and fixed here: CDC's "week" column
   is MMWR epidemiological week numbering, not strict ISO 8601 —
   `pandas.to_datetime`'s ISO-week parser raised on 2025's week 53,
   which is valid under MMWR rules but doesn't exist under ISO's. Fixed
   by implementing the MMWR week-start calculation directly (no new
   dependency — a well-defined, small algorithm, consistent with the
   project's "does the standard library already solve this?"
   principle), verified against a real, independently-sourced
   reference date (CDC's own published "week ending August 14, 2021
   (Week 32)") before being trusted.
2. **Role Configuration**: `RoleConfiguration(time="report_date",
   location="state", surveillance_measure="weekly_case_count")`
   validated successfully on the first attempt, no code changes.
3. **Data Preparation**: `prepare()` — completely unmodified —
   correctly identified and excluded 3,037 rows missing the
   Surveillance Measure value via its existing generic
   `missing_required_value` quality check (the same check OpenDengue's
   own data exercises), rather than crashing or requiring
   dataset-specific handling. 9,407 rows survived. This is the clearest
   single piece of evidence that the architecture generalizes: the
   same missingness-detection logic, built years earlier for a
   completely different dataset, correctly handled this source's own
   distinct missingness convention (null value + a documented "true
   zero" flag) with the same conservative default (exclude, don't
   guess) it would apply to any dataset.
4. **Exploratory Analysis**: `analyze()` — unmodified — produced
   genuine, non-degenerate descriptive statistics (mean 323.15, median
   178.0, std 409.24, real per-state variation from Alaska's mean of
   49.7 to Alabama's 557.9). Optional fields (`resolution`,
   `case_definition`) correctly returned `None`, exercising the
   "absent, not an error" contract this dataset has no columns for.
5. **Visualization**: `visualize()` — unmodified — produced a real
   Plotly figure for the annual trend; the two population/T_res-
   dependent optional figures correctly returned `None`, since this
   dataset supplies neither.
6. **Forecasting**: `detect_tracks()` — unmodified — detected 63
   tracks (one per state, some split by gaps) and correctly marked
   **all 63 as ineligible**, each reporting `n_months` in the mid-50s
   (Alabama: 56) — independently confirming, via the automated
   pipeline rather than manual arithmetic, the same ~56.4-month figure
   calculated by hand during the Compatibility Report. This is the
   anticipated, accepted consequence from ADR-011, now empirically
   verified rather than merely predicted.

## Adaptation log (final, matching the Compatibility Report's classification)

| Adaptation | Classification | Where it lives |
|---|---|---|
| Combine `year`+`week` into one Time column | Dataset-specific | Acquisition script only |
| MMWR (not ISO) week-to-date conversion | Dataset-specific | Acquisition script only |
| Filter to 50 states + DC, normalize casing | Small, generic (reusable pattern) | Acquisition script only |
| Missing-measure row exclusion | **None needed** — already generic | Existing M4 `prepare()`, untouched |
| Optional-field graceful absence | **None needed** — already generic | Existing M5/M6, untouched |
| Forecasting eligibility check | **None needed** — already generic | Existing M7 `detect_tracks()`, untouched |

Every adaptation needed lives entirely in one new acquisition script.
**No code inside `src/surveillance_platform/` was written, modified, or
special-cased for this dataset.**

## Architecture Validation Summary

**The architecture validated successfully, with minimal adaptation, on
a second, structurally different, independently sourced surveillance
dataset.**

What "minimal" means concretely here: one ~150-line acquisition
script, versus zero changes to five milestones' worth of analytical
pipeline code (M3 role configuration, M4 data preparation, M5 EDA, M6
visualization, M7 forecasting). The dataset differs from OpenDengue on
every axis the selection criteria asked for — different disease
(chlamydia, not dengue), different country (US, not South Asia),
different geographic granularity (states, not countries), different
missingness convention (null+flag, not OpenDengue's own pattern),
different temporal numbering (MMWR weeks, not calendar-date intervals)
— and the pipeline accepted all of it without modification.

The one genuine limitation (forecasting eligibility) is not a
weakness discovered by surprise — it was anticipated in ADR-011 before
implementation began, based on the dataset's known 2022–2026 span, and
this workflow trace confirms that anticipation was correct: the
architecture didn't fail or produce a wrong answer, it correctly
recognized a real constraint (insufficient historical span for this
specific validation dataset) and reported it as a documented,
graceful limitation via the exact same mechanism that already handles
this for OpenDengue's own Nepal.

This directly answers the Evaluation Question: the architecture
transfers with minimal (acquisition-only) adaptation while maintaining
full analytical reproducibility — every number in this report traces
to a real, independently verifiable CDC data pull, the same standard
applied to OpenDengue itself throughout this project.
