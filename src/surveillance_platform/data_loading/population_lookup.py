"""World Bank population registry lookup and per-dataset population fetch.

Deterministic, exact (case-insensitive) matching against the World
Bank's own country registry -- never fuzzy, never hardcoded to any
specific set of countries. What generalizes is the *mechanism*, not a
guarantee of coverage: for any uploaded dataset whose Location values
can be deterministically matched to World Bank's registry, this
obtains the corresponding population data. A location that doesn't
match (e.g. a naming variant World Bank doesn't use) is simply
omitted -- not a new failure mode this module needs to solve, since
forecasting's existing per-country "population data unavailable"
limitation (already built and tested in M7) already handles it
gracefully.

Self-contained, mirroring sample_dataset.py's boundary reasoning: uses
only the stdlib (urllib), no new dependency.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import pandas as pd

COUNTRY_LIST_URL = "https://api.worldbank.org/v2/country?format=json&per_page=300"
POPULATION_INDICATOR_URL_TEMPLATE = (
    "https://api.worldbank.org/v2/country/{codes}/indicator/SP.POP.TOTL"
    "?format=json&per_page=20000"
)

# Same conventional "raw external data cache" directory as
# sample_dataset.py's OUTPUT_PATH -- a cache artifact, not code, so
# this does not touch M2's frozen acquisition scripts.
_CACHE_PATH = (
    Path(__file__).parent.parent.parent.parent / "data" / "raw" / "wb_country_registry.json"
)


def _fetch_country_registry() -> list[dict]:
    with urllib.request.urlopen(COUNTRY_LIST_URL) as response:
        payload = json.load(response)
    return payload[1]


def get_country_iso3_lookup() -> dict[str, str]:
    """``{COUNTRY NAME (uppercase) -> ISO3 code}``, real countries only.

    Excludes World Bank's ~78 "Aggregates" region/income-group entries
    (e.g. "World", "South Asia", "OECD members") -- these are not
    countries and would corrupt matching if included. Cached to disk:
    the registry changes extremely rarely, so this is fetched once per
    environment, mirroring ``sample_dataset.py``'s existence-check
    dedup pattern.
    """
    if _CACHE_PATH.exists():
        entries = json.loads(_CACHE_PATH.read_text())
    else:
        entries = _fetch_country_registry()
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(entries))

    return {
        entry["name"].upper(): entry["id"]
        for entry in entries
        if entry["region"]["value"] != "Aggregates"
    }


def fetch_population_data(location_values: list[str]) -> pd.DataFrame:
    """Population data for whichever ``location_values`` match the registry.

    Exact, case-insensitive matching only -- never fuzzy. Returns a
    DataFrame with columns ``(country, year, population)``, where
    ``country`` is the *original* string from ``location_values``
    with its exact casing preserved, never an ISO3 code -- per M5's
    ``eda/population.py`` contract, which requires population data to
    match the dataset's own Location values exactly. A location value
    with no registry match is simply omitted, not an error.
    """
    lookup = get_country_iso3_lookup()
    matched = {
        value: lookup[value.upper()] for value in location_values if value.upper() in lookup
    }
    if not matched:
        return pd.DataFrame(columns=["country", "year", "population"])

    codes = ";".join(sorted(set(matched.values())))
    url = POPULATION_INDICATOR_URL_TEMPLATE.format(codes=codes)
    with urllib.request.urlopen(url) as response:
        payload = json.load(response)

    # Multiple original location strings could map to the same ISO3
    # (e.g. two differently-cased duplicates); keep the first seen.
    iso3_to_original: dict[str, str] = {}
    for original, iso3 in matched.items():
        iso3_to_original.setdefault(iso3, original)

    records = []
    for entry in payload[1] or []:
        if entry["value"] is None:
            continue
        original = iso3_to_original.get(entry["countryiso3code"])
        if original is None:
            continue
        records.append(
            {"country": original, "year": int(entry["date"]), "population": int(entry["value"])}
        )
    return pd.DataFrame(records, columns=["country", "year", "population"])


def population_by_country_series(population_data: pd.DataFrame) -> dict[str, pd.Series]:
    """Reshape the ``(country, year, population)`` table for forecasting.

    Milestone 7's ``forecast()`` expects ``population_by_country:
    dict[str, pd.Series]`` (year -> population) -- a different shape
    from M5's flat DataFrame. One fetch serves both consumers via this
    reshape, rather than fetching twice.
    """
    return {
        country: group.set_index("year")["population"]
        for country, group in population_data.groupby("country")
    }
