"""CSV loading, with a defense-in-depth size guard.

The primary size constraint lives at the Streamlit widget level
(``st.file_uploader(type=["csv"])`` with a stated max size, per
ADR-010's Security section) -- this module's own check exists so
``load_csv`` is still safe if ever called from a context that isn't
gated by that widget.
"""

from __future__ import annotations

from typing import BinaryIO

import pandas as pd

#: ADR-010: generous relative to the real ~4.2MB National Extract,
#: small enough to bound memory use from a bad-faith upload.
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


class FileTooLargeError(ValueError):
    """Raised when an input file exceeds ``MAX_UPLOAD_BYTES``."""


def load_csv(file: BinaryIO) -> pd.DataFrame:
    """Load a CSV file-like object into a DataFrame.

    ``file`` must support ``.seek()`` and ``.read()`` (as both
    Streamlit's ``UploadedFile`` and a plain opened file do). Never
    writes anything to disk -- reads directly into memory, per
    ADR-010's Security section (uploaded files are processed
    in-memory only, avoiding path-traversal risk entirely rather than
    requiring filename sanitization).
    """
    file.seek(0, 2)  # seek to end
    size = file.tell()
    file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise FileTooLargeError(
            f"File is {size:,} bytes, exceeding the {MAX_UPLOAD_BYTES:,}-byte limit."
        )
    return pd.read_csv(file)
