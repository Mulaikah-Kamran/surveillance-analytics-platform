# Data Preparation Pipeline

**Milestone:** 4 — Data Preparation Pipeline
**Module:** `src/surveillance_platform/data_preparation/`

## Purpose

Transforms a raw, role-mapped surveillance dataset into an
analysis-ready dataset through five stages run in a frozen order
(PFD Section 14 / ADR-003):

```
Validation -> Data Profiling -> Quality Assessment
           -> Temporal Standardization -> Cleaning
```

## M3 / M4 boundary

Milestone 3's `role_configuration.validate()` owns **role
configuration validity**: is the `RoleConfiguration` itself
well-formed, and do the assigned columns exist in the dataset? Callers
must run that validation before calling `prepare()`.

Milestone 4's Validation stage owns **dataset-content prerequisites**:
given an already role-valid configuration, is the dataset itself
usable — non-empty, with the required-role columns not entirely null?
M4 never re-checks role-column existence.

## Stage responsibilities

| Stage | Purpose | May mutate data? | Failure behavior |
|---|---|---|---|
| Validation | Dataset-level structural prerequisites | No | Hard stop (`DataPreparationError`) |
| Data Profiling | Descriptive facts only (counts, dtypes, missingness) | No | Never fails |
| Quality Assessment | Evidence-based structured findings | No | Never fails; findings are informational |
| Temporal Standardization | Derive `time` (`datetime64[ns]`) from the configured Time role | Adds one column only | Unparseable values become a finding, not a hard stop |
| Cleaning | Apply only explicitly defined policies | Yes — the only stage that changes/removes data | Never fails |

Quality Assessment findings do not imply Cleaning will act on them. In
particular, **interval inversions are reported but never
automatically corrected** — there is no defined cleaning policy for
that finding, only for the two below.

## Evidence-based cleaning policy

Grounded entirely in Milestone 2's `05_data_quality_profile.md`
findings for the OpenDengue study dataset — nothing speculative:

1. **Casing correction**: `case_definition_standardised` values of
   `confirmed` are normalized to `Confirmed`.
2. **Required-role exclusions**: rows flagged as missing a required
   role value, or as having an unparseable Time value, are excluded
   and the exclusion is recorded. No value is ever imputed.

These checks and their OpenDengue-specific column references
(`calendar_end_date`, `case_definition_standardised`) are explicitly
dataset-specific, not universal assumptions — Milestone 9 will
determine what generalizes to a second surveillance dataset.

## Output contract

```python
from surveillance_platform.data_preparation import prepare

result = prepare(raw_data, role_config)
result.data     # prepared DataFrame; role columns + derived `time`
result.report   # PreparationReport: rows_in, rows_out, rows_excluded,
                 # exclusion_reasons, quality_findings, cleaning_actions,
                 # warnings, profile
```

`prepare()` never mutates its `raw_data` argument and is deterministic
— identical inputs always produce an identical `PreparationResult`.

## What is deferred

Imputation, missing-value-token normalization beyond pandas defaults,
automatic correction of findings without a defined cleaning policy,
`T_res`-aware processing, a generic/pluggable cleaning framework,
Workflow Controller integration, and any adaptation for a
non-interval-based dataset are all explicitly out of scope for this
milestone.
