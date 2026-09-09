"""Acquire the Milestone 9 validation dataset (ADR-011) into data/raw/.

Source: CDC NNDSS weekly data, single-table resource
(data.cdc.gov/resource/x9gk-5huc), a live, currently-updating
government Socrata API -- not a versioned release archive like
OpenDengue's, so there is no fixed checksum to pin. Reproducibility
here means: the same query parameters (condition, date range) will
always return the same *historical* rows, though the live resource
continues to grow with new weeks after this script's documented
acquisition date.

This script performs acquisition and the *minimum* structural
transformation needed to produce a valid pipeline input -- not
cleaning. Per M2's own acquisition/cleaning boundary
(docs/datasets/01_acquisition.md), acquisition should not parse,
clean, standardize, or otherwise transform data beyond what's needed
to get it into a loadable shape; the pipeline's own Data Preparation
stage (M4) is where missingness and quality assessment belong.

The one unavoidable structural step: CDC represents time as two
separate columns (year, week), but our Role Configuration model
(ADR-004) requires a Time role to be a single column of date-parseable
values. Combining them here is the direct analogue of OpenDengue's own
already-ready calendar_start_date column -- not a cleaning decision.

Two decisions ARE made here, deliberately documented as acquisition
choices, not silent defaults (see the M9 Dataset Compatibility Report,
docs/m9-dataset-compatibility-report.md, Sections 4 and 9 for the full
evidence):

1. Location is filtered to the 50 states + DC only, excluding US
   territories, Census regional aggregates, and national totals
   (TOTAL/US RESIDENTS/Total) -- the direct analogue of OpenDengue's
   own S_res=Admin0 pre-filtering to one consistent granularity before
   the pipeline ever sees the data. Left unfiltered, "Alabama" and
   "TOTAL" would be treated as equally distinct, non-overlapping
   Location values by the pipeline, corrupting any aggregate statistic.
2. Case is normalized to title case (Alabama, not ALABAMA/alabama),
   resolving the casing inconsistency found directly in the raw data.

Usage:
    python data/download_nndss_validation_dataset.py [CONDITION]

    CONDITION defaults to "Chlamydia trachomatis infection" (the
    condition profiled in the Compatibility Report). Any other single,
    unstratified label works the same way.

Output:
    data/raw/nndss_validation_dataset.csv
"""

from __future__ import annotations

import datetime
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

DEFAULT_CONDITION = "Chlamydia trachomatis infection"
RESOURCE_ID = "x9gk-5huc"
BASE_URL = f"https://data.cdc.gov/resource/{RESOURCE_ID}.json"

RAW_DIR = Path(__file__).parent / "raw"
OUTPUT_PATH = RAW_DIR / "nndss_validation_dataset.csv"

# The 50 states + DC, canonical title case -- used both to filter out
# territories/regions/national aggregates and to normalize casing.
_US_STATES = [
    "Alabama",
    "Alaska",
    "Arizona",
    "Arkansas",
    "California",
    "Colorado",
    "Connecticut",
    "Delaware",
    "District of Columbia",
    "Florida",
    "Georgia",
    "Hawaii",
    "Idaho",
    "Illinois",
    "Indiana",
    "Iowa",
    "Kansas",
    "Kentucky",
    "Louisiana",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Michigan",
    "Minnesota",
    "Mississippi",
    "Missouri",
    "Montana",
    "Nebraska",
    "Nevada",
    "New Hampshire",
    "New Jersey",
    "New Mexico",
    "New York",
    "North Carolina",
    "North Dakota",
    "Ohio",
    "Oklahoma",
    "Oregon",
    "Pennsylvania",
    "Rhode Island",
    "South Carolina",
    "South Dakota",
    "Tennessee",
    "Texas",
    "Utah",
    "Vermont",
    "Virginia",
    "Washington",
    "West Virginia",
    "Wisconsin",
    "Wyoming",
]
_US_STATES_UPPER = {s.upper(): s for s in _US_STATES}


def fetch_condition(condition: str) -> pd.DataFrame:
    """Pull every row for one condition across all locations and weeks.

    A plain, unauthenticated request -- confirmed during M9 evaluation
    (ADR-011) that this endpoint requires no API key or login.
    """
    query = urllib.parse.urlencode({"$where": f"label='{condition}'", "$limit": 50000})
    url = f"{BASE_URL}?{query}"
    with urllib.request.urlopen(url) as response:
        return pd.read_json(response, dtype=str)


def _mmwr_week_start(year: int, week: int) -> datetime.date:
    """First day (Sunday) of a CDC MMWR epidemiological week.

    CDC's "week" column is an MMWR week, not a strict ISO 8601 week --
    confirmed the hard way: pandas' ISO-week parsing raises on 2025's
    week 53, which is valid under MMWR numbering but doesn't exist
    under ISO's (they use different rules for which years get a 53rd
    week). Verified against a real, independently-sourced reference
    before trusting this: CDC's own published "week ending August 14,
    2021 (Week 32)" matches mmwr_week_start(2021, 32) + 6 days exactly.
    """
    jan4 = datetime.date(year, 1, 4)
    week1_start = jan4 - datetime.timedelta(days=(jan4.weekday() + 1) % 7)
    return week1_start + datetime.timedelta(weeks=week - 1)


def to_pipeline_shape(raw: pd.DataFrame) -> pd.DataFrame:
    """The minimum structural transformation to produce a loadable file.

    Combines year+week into one date column (Role Configuration needs
    a single Time column) and filters+normalizes location to one
    consistent granularity (the 50 states + DC) -- both documented
    acquisition decisions above, not cleaning. Everything else
    (missingness, the null/dash-flag zero convention) is left for the
    pipeline's own Data Preparation stage to handle, per M2's
    acquisition/cleaning boundary.
    """
    df = raw.copy()
    df["state_normalized"] = df["states"].str.upper().map(_US_STATES_UPPER)
    df = df[df["state_normalized"].notna()].copy()

    # MMWR year/week -> the Sunday that begins that week, the same
    # "representative timestamp for a reporting interval" principle
    # ADR-007 already established for OpenDengue's own interval data.
    df["report_date"] = [
        _mmwr_week_start(int(y), int(w)) for y, w in zip(df["year"], df["week"])
    ]

    return pd.DataFrame(
        {
            "report_date": df["report_date"].astype(str),
            "state": df["state_normalized"],
            "condition": df["label"],
            "weekly_case_count": df["m1"],
        }
    ).sort_values(["state", "report_date"])


def main() -> int:
    condition = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONDITION
    print(f"Fetching CDC NNDSS data for: {condition}")
    print(f"Source: {BASE_URL}")
    raw = fetch_condition(condition)
    print(f"Fetched {len(raw):,} raw rows (all locations, all weeks)")

    shaped = to_pipeline_shape(raw)
    print(f"After filtering to 50 states + DC: {len(shaped):,} rows")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    shaped.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
