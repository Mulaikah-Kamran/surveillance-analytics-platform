"""Acquire the second validation dataset (ADR-011) into data/raw/.

Source: CDC NNDSS weekly data, a live government API. Unlike
OpenDengue's fixed release, this keeps growing over time, so
reproducing this download later will pick up a few more recent weeks,
not fewer or different historical rows.

This script only reshapes the data enough to load it (CDC splits time
into separate year/week columns, so those get combined into one date
column). Actual cleaning still happens in the normal pipeline step,
not here.

Two choices made here, worth knowing about: locations are filtered
down to the 50 states plus DC (dropping territories, regions, and
national totals, which would otherwise look like extra "locations" and
throw off any aggregate statistic), and state names are normalized to
one consistent capitalization. See docs/m9-validation-results.md for
what happened when this data ran through the full pipeline.

Usage:
    python data/download_nndss_validation_dataset.py [CONDITION]

    CONDITION defaults to "Chlamydia trachomatis infection". Any other single,
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
