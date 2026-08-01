# ADR-007 — Temporal Standardization Strategy

**Status:** Locked

## Decision

Version 1 standardizes temporal information to a single analytical
Time variable. When datasets provide reporting intervals, the start
date is used as the representative analytical time value. Original
temporal columns are retained for transparency.

## Full Time Role Definition

The platform operates on a single standardized Time role. If a dataset
represents time as a reporting interval (e.g. `calendar_start_date` /
`calendar_end_date`, as OpenDengue does), the preprocessing /
standardization stage derives one representative analytical time
variable before downstream analysis. Version 1 uses the start date of
the reporting period as the representative time value, because it is
deterministic, reproducible, easy to explain, and avoids introducing
extra calculations. The original temporal columns are preserved in the
cleaned dataset for transparency and traceability.
