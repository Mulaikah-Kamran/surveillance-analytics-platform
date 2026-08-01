# Time Representation — OpenDengue National Extract

**Milestone:** 2 — Data Acquisition & Understanding
**Status:** Documentation only. This describes how the raw data
represents time and restates the already-locked design decision for
handling it. No standardization code is implemented in this milestone —
that belongs to the Data Preparation Pipeline (Milestone 4).

## How OpenDengue Represents Time

Every row's time reference is a **reporting interval**, not a single
date: `calendar_start_date` and `calendar_end_date` (format `YYYY-mm-dd`),
alongside a `T_res` column stating the nominal resolution of that
interval (`Week`, `Month`, or `Year`). Verified directly against the
National Extract:

| `T_res` | Row count | Interval length (days) |
|---|---|---|
| Week | 23,248 | always 6 days (7-day inclusive interval) |
| Month | 3,130 | 27–30 days |
| Year | 3,495 | 364–365 days |

There is no single-date column anywhere in the schema — `Year` is a
derived integer summary, not a substitute for a date. This means the
platform cannot simply "pick a date column"; a representative analytical
date has to be derived from the interval.

## The Locked Design Decision (ADR-007)

This exact situation — reporting intervals rather than single dates — was
anticipated during planning and is already locked as **ADR-007 (Temporal
Standardization Strategy)**:

> "The platform operates on a single standardized Time role. If a dataset
> represents time as a reporting interval (e.g. `calendar_start_date` /
> `calendar_end_date`, as OpenDengue does), the preprocessing/
> standardization stage derives one representative analytical time
> variable before downstream analysis. Version 1 uses the start date of
> the reporting period as the representative time value, because it is
> deterministic, reproducible, easy to explain, and avoids introducing
> extra calculations. The original temporal columns are preserved in the
> cleaned dataset for transparency and traceability."
> — `docs/adr/ADR-007-temporal-standardization-strategy.md`

Concretely, once the standardization module exists (Milestone 4), the
representative analytical `Time` value for every row will be
`calendar_start_date`, with `calendar_start_date` and `calendar_end_date`
both retained unchanged alongside it — not replaced.

## Why This Milestone Doesn't Implement It

The workflow ordering locked in the Freeze Document (Section 14) places
Temporal Standardization after Validation, Profiling, and Quality
Assessment — all of which happen in later milestones, on top of role
configuration (Milestone 3) that doesn't exist yet. Milestone 2's job is
narrower: confirm the interval-based representation actually matches
what ADR-007 assumed (it does — see the table above), so Milestone 4 can
implement standardization against a verified, not assumed, schema.

## One Observation for Milestone 4

The three `T_res` categories correspond to visibly different, fixed
interval lengths (6 / 27–30 / 364–365 days) rather than a continuum. This
is useful context for the eventual standardization module: `T_res` itself
is a reliable, already-present signal of reporting granularity, and could
reasonably be surfaced alongside the derived Time value rather than
discarded, so that downstream forecasting/EDA modules can account for
countries whose historical record mixes weekly, monthly, and yearly
reporting periods (see `05_data_quality_profile.md` for how common this
mixing is across the candidate South Asian countries).
