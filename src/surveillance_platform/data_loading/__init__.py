"""Dataset loading module (Milestone 8, ADR-010).

Formalizes CSV ingestion as a real, tested module -- replacing the
M1-era placeholder. Zero Streamlit imports: this module is fully
runnable and testable as plain Python (ADR-010's independence
requirement).

Public API:

* :func:`load_csv` -- load an uploaded/opened CSV file-like object
  into a DataFrame, with a defense-in-depth size guard.
* :func:`check_spatial_resolution` -- the opportunistic ``S_res``
  sanity check (warns, never blocks).
* :func:`get_sample_dataset` -- the real, checksum-verified National
  Extract CSV bytes, for anyone who wants the complete dataset.
* :func:`get_starter_sample_dataset` -- the same data, filtered to
  just the four countries this project was built around (ADR-008),
  for the "Download sample dataset" button's default, first-time-
  user-friendly option.
* :func:`get_country_iso3_lookup`, :func:`fetch_population_data`,
  :func:`population_by_country_series` -- population data acquisition
  (ADR-010 addendum), matched deterministically against the World
  Bank's own country registry -- never fuzzy, never hardcoded to any
  specific set of countries.

See ``docs/adr/ADR-010-ui-integration-strategy.md`` for the full design.
"""

from surveillance_platform.data_loading.loading import FileTooLargeError, load_csv
from surveillance_platform.data_loading.population_lookup import (
    fetch_population_data,
    get_country_iso3_lookup,
    population_by_country_series,
)
from surveillance_platform.data_loading.sample_dataset import (
    ChecksumMismatchError,
    get_sample_dataset,
    get_starter_sample_dataset,
)
from surveillance_platform.data_loading.sanity_check import check_spatial_resolution

__all__ = [
    "ChecksumMismatchError",
    "FileTooLargeError",
    "check_spatial_resolution",
    "fetch_population_data",
    "get_country_iso3_lookup",
    "get_sample_dataset",
    "get_starter_sample_dataset",
    "load_csv",
    "population_by_country_series",
]
