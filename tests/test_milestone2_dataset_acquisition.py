"""Milestone 2 verification tests — Data Acquisition & Understanding.

These are milestone-verification checks, not preprocessing tests: they
confirm the dataset was successfully acquired, the expected file exists
with the documented shape, the schema documentation matches the
downloaded data, and the selected study countries are actually present.
No cleaning, validation, or role-assignment logic is exercised here —
those don't exist yet (Milestone 3+).

Per the Freeze Document's dependency principle ("start minimal, grow
with justification"), pandas is not yet a project dependency — it is
introduced in the milestone that first needs it for real analytical
work. These tests therefore use only the standard library `csv` module.

The raw dataset itself is never committed (see data/README.md and
docs/about-the-data.md), so tests that need the actual file
skip gracefully — rather than fail — when it isn't present locally,
e.g. in CI. Run `python data/download_national_extract.py` first to
exercise the skipped checks.
"""

import csv
import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOWNLOAD_SCRIPT = REPO_ROOT / "data" / "download_national_extract.py"
RAW_CSV = REPO_ROOT / "data" / "raw" / "National_extract_V1_3.csv"

# Schema documented in docs/about-the-data.md — kept in sync manually,
# since this is a documentation-verification test, not a schema-inference
# tool.
EXPECTED_COLUMNS = [
    "adm_0_name",
    "adm_1_name",
    "adm_2_name",
    "full_name",
    "ISO_A0",
    "FAO_GAUL_code",
    "RNE_iso_code",
    "IBGE_code",
    "calendar_start_date",
    "calendar_end_date",
    "Year",
    "dengue_total",
    "case_definition_standardised",
    "S_res",
    "T_res",
    "UUID",
]

# Selected in docs/adr/ADR-008-study-country-selection.md.
SELECTED_COUNTRIES = ["SRI LANKA", "BANGLADESH", "MALDIVES", "NEPAL"]

skip_if_not_acquired = pytest.mark.skipif(
    not RAW_CSV.exists(),
    reason=(
        "Raw dataset not present locally (expected — it is git-ignored). "
        "Run `python data/download_national_extract.py` to acquire it "
        "and exercise this check."
    ),
)


def _load_download_script():
    """Import data/download_national_extract.py as a module.

    It lives outside the src/ package layout deliberately (see
    docs/about-the-data.md) — it's a one-off acquisition script,
    not part of the installed analytical package.
    """
    spec = importlib.util.spec_from_file_location(
        "download_national_extract", DOWNLOAD_SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_acquisition_script_exists():
    """The reproducible acquisition script documented in Milestone 2 exists."""
    assert DOWNLOAD_SCRIPT.exists()


def test_acquisition_script_pins_release_and_checksum():
    """The script pins an exact release tag and a non-placeholder checksum.

    This guards against the acquisition silently drifting to whatever
    OpenDengue's `main` branch happens to contain later.
    """
    module = _load_download_script()

    assert module.RELEASE_TAG == "v1.3.0"
    assert module.RELEASE_TAG in module.ARCHIVE_URL
    assert len(module.EXPECTED_ARCHIVE_SHA256) == 64
    assert not module.EXPECTED_ARCHIVE_SHA256.startswith("PLACEHOLDER")


@skip_if_not_acquired
def test_dataset_successfully_acquired():
    """The expected raw file exists and is non-trivially sized."""
    assert RAW_CSV.exists()
    # Sanity floor, not an exact byte match — just confirms this isn't an
    # empty file or an HTML error page saved by mistake.
    assert RAW_CSV.stat().st_size > 1_000_000


@skip_if_not_acquired
def test_schema_documentation_matches_downloaded_data():
    """The documented columns (03_schema.md) match the actual CSV header."""
    with open(RAW_CSV, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == EXPECTED_COLUMNS


@skip_if_not_acquired
def test_selected_countries_exist_in_dataset():
    """Every country selected in the Milestone 2 decision log is present."""
    with open(RAW_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        countries_present = {row["adm_0_name"] for row in reader}

    for country in SELECTED_COUNTRIES:
        assert country in countries_present, (
            f"{country} was selected in "
            "docs/adr/ADR-008-study-country-selection.md but does "
            "not appear in the downloaded National Extract"
        )


@skip_if_not_acquired
def test_no_duplicate_country_reporting_period_rows():
    """(country, start_date, end_date) has zero duplicates, as documented
    in docs/about-the-data.md — this is the dataset's true row key."""
    seen = set()
    with open(RAW_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (
                row["adm_0_name"],
                row["calendar_start_date"],
                row["calendar_end_date"],
            )
            assert key not in seen, f"Duplicate row key found: {key}"
            seen.add(key)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
