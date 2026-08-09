"""Download the World Bank WDI population reference table into data/raw/.

This script performs acquisition only: it queries the World Bank
Indicators API (V2) for the ``SP.POP.TOTL`` ("Population, total")
indicator, for exactly the four ADR-008 study countries, and writes a
small CSV with the minimal schema Milestone 5's population
normalization actually needs — nothing else. It does not compute
rates, join against surveillance data, or transform values in any way;
see ``docs/eda.md`` for why population normalization is scoped this
way, and ``docs/adr/ADR-008-study-country-selection.md`` for the
locked study country list.

Follows the same acquisition/reproducibility pattern established by
``data/download_national_extract.py``: the output is git-ignored (per
Freeze Document Section 23) and never committed, and the response is
verified against a pinned checksum so any reviewer can reproduce the
exact same file. Unlike the OpenDengue archive, the WDI API has no
tagged, immutable release — a query today and the same query next year
should return identical historical values, but this is an external
API, not a version-pinned file, so the checksum protects against the
unexpected case where a historical figure is revised upstream, exactly
as it does for the OpenDengue script.

Usage:
    python data/download_population_reference.py

Output:
    data/raw/population_reference.csv

Output schema (see surveillance_platform.eda.population for how this
is consumed): columns ``country`` (matching the surveillance dataset's
Location-role values *exactly as OpenDengue represents them* — e.g.
``"SRI LANKA"``, uppercase, not an ISO3 code and not title-cased),
``year``, ``population``.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

# WDI indicator for total population, per-country, per-year.
INDICATOR = "SP.POP.TOTL"

# ISO3 codes -> the country-name spelling used by adm_0_name in the
# OpenDengue National Extract (i.e. the values that will actually
# appear in the surveillance dataset's configured Location-role
# column). OpenDengue represents adm_0_name in uppercase (confirmed by
# direct inspection of the real National Extract, e.g. "SRI LANKA",
# not "Sri Lanka") — this mapping is written to match that exact
# representation, deliberately and explicitly, rather than introducing
# case-insensitive or otherwise general-purpose normalization into the
# join logic in surveillance_platform.eda.population. This is the one,
# deliberately localized, place where a WDI-specific detail (ISO3
# codes) is translated into the platform's role-model-facing
# vocabulary — surveillance_platform.eda itself never needs to know
# about ISO3 codes, or about OpenDengue's casing convention.
STUDY_COUNTRIES = {
    "LKA": "SRI LANKA",
    "BGD": "BANGLADESH",
    "MDV": "MALDIVES",
    "NPL": "NEPAL",
}

ARCHIVE_URL = (
    "https://api.worldbank.org/v2/country/"
    f"{';'.join(STUDY_COUNTRIES)}/indicator/{INDICATOR}"
    "?format=json&per_page=20000"
)

# Pinned SHA-256 digest, provided by the Antigravity review's own
# verified download of this exact query — NOT independently
# re-downloaded or re-verified by Claude, because api.worldbank.org is
# outside this sandbox's network allowlist (confirmed: HTTP 403 from
# the egress proxy on every attempt). If a future run reports a
# checksum mismatch, that could mean either (a) the upstream WDI
# response has genuinely changed since this was pinned, or (b) this
# pinned value was never independently verified against a live
# download in this environment — investigate before replacing it,
# do not silently substitute a newly generated digest.
EXPECTED_RESPONSE_SHA256 = (
    "7681e342a74f5b1fd05980c26ae612ca0899247a7285d79d2edb9e8a060c473d"
)

RAW_DIR = Path(__file__).parent / "raw"
OUTPUT_PATH = RAW_DIR / "population_reference.csv"


def download_response(url: str) -> bytes:
    """Fetch the API response into memory. No disk writes here."""
    with urllib.request.urlopen(url) as response:
        return response.read()


def verify_checksum(data: bytes, expected_sha256: str) -> str:
    """Return the SHA-256 hex digest, warning (not failing) on first run."""
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256.startswith("PLACEHOLDER"):
        print(
            "NOTE: no checksum pinned yet. Recording this run's digest for "
            "you to paste into EXPECTED_RESPONSE_SHA256 above, so future "
            "runs can verify against it:\n  " + digest
        )
    elif digest != expected_sha256:
        raise ValueError(
            f"Checksum mismatch: expected {expected_sha256}, got {digest}. "
            "A historical population figure may have been revised upstream "
            "since this was pinned — investigate before proceeding."
        )
    return digest


def parse_and_write_csv(response_bytes: bytes, destination: Path) -> Path:
    """Extract exactly (country, year, population) from the API response."""
    payload = json.loads(response_bytes)
    # payload[0] is pagination metadata; payload[1] is the data records.
    records = payload[1] if len(payload) > 1 and payload[1] else []

    rows = []
    for record in records:
        value = record.get("value")
        if value is None:
            continue
        iso3 = record["countryiso3code"]
        if iso3 not in STUDY_COUNTRIES:
            continue
        rows.append(
            {
                "country": STUDY_COUNTRIES[iso3],
                "year": int(record["date"]),
                "population": int(value),
            }
        )
    rows.sort(key=lambda r: (r["country"], r["year"]))

    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["country", "year", "population"])
        writer.writeheader()
        writer.writerows(rows)
    return destination


def main() -> int:
    print("Downloading World Bank WDI population reference (SP.POP.TOTL)...")
    print(f"Source: {ARCHIVE_URL}")
    response_bytes = download_response(ARCHIVE_URL)
    verify_checksum(response_bytes, EXPECTED_RESPONSE_SHA256)
    path = parse_and_write_csv(response_bytes, OUTPUT_PATH)
    with open(path) as f:
        row_count = sum(1 for _ in f) - 1  # exclude header
    print(f"Saved: {path} ({row_count} country-year rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
