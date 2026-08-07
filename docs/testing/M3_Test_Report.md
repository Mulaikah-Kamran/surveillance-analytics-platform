# Milestone 3 Test Report

**Milestone:** 3 — Role Configuration
**Scope:** Unit tests for the `role_configuration` subsystem —
`RoleConfiguration`, structural validation, and dataset-compatibility
validation against a synthetic column list. No real dataset is
required for these tests.

## Environment

- OS: Linux (Ubuntu)
- Python: 3.12.3

## Commands Executed and Expected Outputs

### 1. Tests

```bash
pytest -v
```

**Expected:** all Milestone 1, 2, and 3 tests pass or skip as
designed; no regressions in existing M1/M2 tests.

**Result:** ✅ Passed — 17 passed, 4 skipped (the 4 skips are the
existing Milestone 2 checks that require the git-ignored raw dataset,
unaffected by this milestone):

- `test_valid_configuration_passes`
- `test_missing_required_role_fails` (parametrized: `time`,
  `location`, `surveillance_measure`)
- `test_unknown_column_fails`
- `test_duplicate_column_mapping_fails`
- `test_optional_identifier_absent_is_valid`
- `test_optional_identifier_supplied_is_valid`
- `test_invalid_identifier_unknown_column_fails`
- `test_identifier_duplicating_another_role_fails`
- `test_malformed_role_value_fails`
- `test_multiple_violations_are_all_reported`

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

## Milestone 3 Exit Criterion (Freeze Document, Section 29)

> "Platform recognizes Time, Location, Surveillance Measure, and
> optional Identifier."

| Requirement | Status |
|---|---|
| Explicit `RoleConfiguration` model (no inference) | ✅ `src/surveillance_platform/role_configuration/config.py` |
| Required roles enforced | ✅ tested |
| Optional Identifier supported | ✅ tested |
| Duplicate column assignment rejected | ✅ tested |
| Unknown column assignment rejected | ✅ tested |
| Informative, non-generic validation errors | ✅ `RoleConfigurationError`, tested |
| No dataset/pandas dependency introduced | ✅ `available_columns: Iterable[str]` |
| No new runtime dependency | ✅ stdlib only |
| Unit tests | ✅ this report |
