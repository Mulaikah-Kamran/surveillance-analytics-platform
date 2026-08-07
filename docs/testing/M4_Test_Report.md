# Milestone 4 Test Report

**Milestone:** 4 — Data Preparation Pipeline
**Scope:** Unit and integration tests for the `data_preparation`
subsystem — each of the five pipeline stages independently, and the
`prepare()` orchestrator end-to-end. Uses a single ~10-row synthetic
dataframe; no real OpenDengue data is required.

## Environment

- OS: Linux (Ubuntu)
- Python: 3.12.3
- pandas: 3.0.5 (new dependency this milestone)

## Commands Executed and Expected Outputs

### 1. Tests

```bash
pytest -v
```

**Expected:** all Milestone 1–4 tests pass or skip as designed; no
regressions in existing M1/M2/M3 tests.

**Result:** ✅ Passed — 44 passed, 4 skipped (the 4 skips are the
existing Milestone 2 checks that require the git-ignored raw dataset,
unaffected by this milestone). 27 of the 44 passing tests are new for
Milestone 4, covering:

- Validation: valid dataset, empty dataset, entirely-null required
  role, partial missingness not rejected.
- Data Profiling: descriptive facts correctness, no mutation.
- Quality Assessment: negative surveillance-measure detection, interval
  inversion detection (without correction), missing-required-value
  detection, no mutation, plain-string severity field.
- Temporal Standardization: `datetime64[ns]` dtype, original temporal
  columns preserved, unparseable values flagged without a hard stop,
  no mutation.
- Cleaning: casing correction, exclusion of missing-required-value and
  unparseable-time rows, no automatic correction of interval
  inversions, legitimate zero values preserved, no mutation.
- Pipeline: end-to-end preparation, findings/actions reported, hard
  failure raised correctly, raw input untouched, deterministic
  repeated execution, role-configuration columns used rather than
  hardcoded names.

### 2. Linting

```bash
ruff check .
```

**Result:** ✅ Passed — `All checks passed!`

### 3. Formatting check

```bash
black --check .
```

**Result:** ✅ Passed — all files formatted.

## Milestone 4 Exit Criterion (Freeze Document, Section 29)

> "Pipeline produces reproducible outputs."

| Requirement | Status |
|---|---|
| Frozen stage order (Validation -> Profiling -> Quality Assessment -> Temporal Standardization -> Cleaning) | ✅ `pipeline.py` |
| M3 role-configuration validation not duplicated | ✅ `validation.py` docstring + tests |
| `time` column, dtype `datetime64[ns]`, derived via `role_config.time` | ✅ tested |
| `calendar_start_date`, `calendar_end_date`, `T_res` unchanged | ✅ tested |
| Quality findings use plain-string severity, no formal enum | ✅ tested |
| Interval inversions reported but not auto-corrected | ✅ tested |
| Only defined cleaning policies applied (casing, required-role exclusions) | ✅ tested |
| No imputation | ✅ by construction |
| Raw input never mutated | ✅ tested |
| Deterministic output | ✅ tested |
| `pandas` is the only new dependency | ✅ `requirements.txt` |
| Unit tests per module + integration test | ✅ this report |
