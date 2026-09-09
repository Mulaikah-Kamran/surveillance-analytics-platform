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
  Extract CSV bytes, for the "Download sample dataset" button.

See ``docs/adr/ADR-010-ui-integration-strategy.md`` for the full design.
"""

from surveillance_platform.data_loading.loading import FileTooLargeError, load_csv
from surveillance_platform.data_loading.sample_dataset import (
    ChecksumMismatchError,
    get_sample_dataset,
)
from surveillance_platform.data_loading.sanity_check import check_spatial_resolution

__all__ = [
    "ChecksumMismatchError",
    "FileTooLargeError",
    "check_spatial_resolution",
    "get_sample_dataset",
    "load_csv",
]
