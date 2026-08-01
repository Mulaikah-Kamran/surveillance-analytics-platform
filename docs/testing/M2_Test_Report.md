# Milestone 2 Test Report

**Milestone:** 2 — Data Acquisition & Understanding
**Date:** 2026-08-01
**Scope:** Milestone-verification checks confirming the dataset was
successfully acquired, the expected file exists, the schema
documentation matches the downloaded data, and the selected study
countries are present. These are not preprocessing or analytical tests
— Milestone 2 introduces no preprocessing, cleaning, or role-assignment
logic, so there is nothing of that kind to test yet (that begins in
Milestone 3/4).

This report documents the commands executed and confirms their outcome.
It is a documentation record, not a raw console log.

## Environment

- OS: Linux (Ubuntu)
- Python: 3.12.3
- Additionally verified via GitHub Actions CI (`ubuntu-latest`, Python
  3.12) — see [CI Verification](#ci-verification) below.

## Commands Executed and Expected Outputs

### 1. Acquire the dataset

```bash
python data/download_national_extract.py
```

**Expected:** the OpenDengue National Extract v1.3 archive is
downloaded, its SHA-256 checksum verified against the pinned value, and
`data/raw/National_extract_V1_3.csv` is written.

**Result:** ✅ Passed. Output:

```
Downloading OpenDengue National Extract (v1.3.0)...
Source: https://raw.githubusercontent.com/OpenDengue/master-repo/v1.3.0/data/releases/V1.3/National_extract_V1_3.zip
Saved: data/raw/National_extract_V1_3.csv (4,235,643 bytes)
```

### 2. Linting

```bash
ruff check .
```

**Expected output:** `All checks passed!`

**Result:** ✅ Passed.

### 3. Formatting check

```bash
black --check .
```

**Expected output:** confirmation that all files are already formatted.

**Result:** ✅ Passed.

### 4. Tests — with the raw dataset present locally

```bash
python data/download_national_extract.py   # acquire first
pytest -v
```

**Expected output:** all collected tests pass, including the six new
Milestone 2 checks and the three pre-existing Milestone 1 smoke tests.

**Result:** ✅ Passed — 9 passed, 0 failed:

- `test_package_is_importable`
- `test_package_has_version`
- `test_submodules_are_importable`
- `test_acquisition_script_exists`
- `test_acquisition_script_pins_release_and_checksum`
- `test_dataset_successfully_acquired`
- `test_schema_documentation_matches_downloaded_data`
- `test_selected_countries_exist_in_dataset`
- `test_no_duplicate_country_reporting_period_rows`

### 5. Tests — without the raw dataset present (CI condition)

```bash
pytest -v
```

The raw CSV is git-ignored by design (Freeze Document Section 23, Data
Versioning) and is never present in a fresh checkout or in CI. This is
expected, not an error — the milestone-2 tests are written to confirm
that:

**Expected output:** the two acquisition-script structural checks still
run and pass (they don't need the actual data file); the four checks
that need the real CSV skip cleanly with a clear reason, rather than
failing or erroring.

**Result:** ✅ Passed as expected — 5 passed, 4 skipped:

- `test_package_is_importable` — passed
- `test_package_has_version` — passed
- `test_submodules_are_importable` — passed
- `test_acquisition_script_exists` — passed
- `test_acquisition_script_pins_release_and_checksum` — passed
- `test_dataset_successfully_acquired` — **skipped**
- `test_schema_documentation_matches_downloaded_data` — **skipped**
- `test_selected_countries_exist_in_dataset` — **skipped**
- `test_no_duplicate_country_reporting_period_rows` — **skipped**

This confirms CI will run green on every push without needing network
access to re-download a 4 MB file on every run, while still giving any
contributor an easy, documented way (`python
data/download_national_extract.py`) to exercise the full check locally.

## Documentation-Accuracy Checks

Two of the milestone-2 tests exist specifically to keep documentation
and data in sync, rather than to test code:

- `test_schema_documentation_matches_downloaded_data` fails loudly if
  `docs/datasets/03_schema.md`'s documented column list ever drifts from
  the actual file (e.g. if a future OpenDengue release adds/renames a
  column).
- `test_selected_countries_exist_in_dataset` fails loudly if a future
  OpenDengue release ever drops one of the four countries locked in
  ADR-008.

## CI Verification

The same sequence (`ruff check .` → `black --check .` → `pytest`) runs
automatically on every push and pull request. As designed, `pytest`
passes in CI with the four data-dependent Milestone 2 checks skipped
(no raw dataset present), consistent with the "Tests — without the raw
dataset present" result above.

## Milestone 2 Exit Criterion (Freeze Document, Section 29)

> "Study dataset and validation dataset both justified and documented."

| Requirement | Status |
|---|---|
| Study dataset acquired, sourced, cited, licensed | ✅ `docs/datasets/01_acquisition.md` |
| Dataset landscape (National vs. Temporal) confirmed against ADR-002 | ✅ `docs/datasets/02_dataset_landscape.md` |
| Schema documented and role-model mapping confirmed | ✅ `docs/datasets/03_schema.md` |
| Time representation documented against ADR-007 | ✅ `docs/datasets/04_time_representation.md` |
| Data quality profiled (observation only, no cleaning) | ✅ `docs/datasets/05_data_quality_profile.md` |
| Study countries selected and justified | ✅ `docs/adr/ADR-008-study-country-selection.md` |
| Validation dataset candidates investigated (R-001) | ✅ `docs/datasets/06_validation_dataset_investigation.md` — **not yet locked**, as instructed |
| Milestone-verification tests exist and pass | ✅ this report |

The validation dataset itself is intentionally **not** finalized at this
milestone — the evidence gathered (PLISA inaccessible; Project Tycho
accessible but with a coverage-recency and partial-independence caveat;
HDX promising in principle but no confirmed South Asian dengue dataset
found) does not clearly support locking one yet, and the milestone
instructions are explicit that it shouldn't be forced. This is carried
forward as an open item to Milestone 9 (Architecture Validation), not a
gap in this milestone's exit criteria.
