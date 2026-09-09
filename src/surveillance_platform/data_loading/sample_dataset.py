"""Sample dataset download, for the "Download sample dataset" button (ADR-010).

Deliberately self-contained rather than importing from
``data/download_national_extract.py``: that script lives outside
``src/`` by design (Section 25's skeleton keeps acquisition scripts
and Source Modules in separate categories), and M2 is frozen. A few
lines of duplicated download/verify logic is a smaller risk than
crossing that boundary or reopening frozen work. The URL, checksum,
and output path below are identical to that script's, so both stay in
sync with the same pinned release.
"""

from __future__ import annotations

import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path

RELEASE_TAG = "v1.3.0"
ARCHIVE_URL = (
    "https://raw.githubusercontent.com/OpenDengue/master-repo/"
    f"{RELEASE_TAG}/data/releases/V1.3/National_extract_V1_3.zip"
)
EXPECTED_ARCHIVE_SHA256 = (
    "d4fa7b1a881481fd5323991cc7a23dbe690112e2c473898ceea76e1e9c85dc59"
)
ARCHIVE_MEMBER = "National_extract_V1_3.csv"

# Same path M2's script writes to -- whichever runs first, the other
# reuses the cached file rather than re-downloading (ADR-010's
# Security section: dedupe repeated "Download sample dataset" clicks).
OUTPUT_PATH = (
    Path(__file__).parent.parent.parent.parent / "data" / "raw" / ARCHIVE_MEMBER
)


class ChecksumMismatchError(ValueError):
    """Raised when the downloaded archive doesn't match the pinned checksum."""


def get_sample_dataset() -> bytes:
    """Return the real, checksum-verified National Extract CSV bytes.

    Reuses the local cached copy if already present (from a previous
    call, or from M2's own script having already been run) --
    verified deliberately by *existence*, not by re-hashing the
    archive, since re-verifying would require re-downloading it
    anyway, defeating the point of deduplication.
    """
    if OUTPUT_PATH.exists():
        return OUTPUT_PATH.read_bytes()

    with urllib.request.urlopen(ARCHIVE_URL) as response:
        archive_bytes = response.read()

    digest = hashlib.sha256(archive_bytes).hexdigest()
    if digest != EXPECTED_ARCHIVE_SHA256:
        raise ChecksumMismatchError(
            f"Checksum mismatch: expected {EXPECTED_ARCHIVE_SHA256}, got "
            f"{digest}. The upstream archive for {RELEASE_TAG} may have "
            "changed -- investigate before proceeding."
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with (
        zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf,
        zf.open(ARCHIVE_MEMBER) as src,
    ):
        csv_bytes = src.read()
    OUTPUT_PATH.write_bytes(csv_bytes)
    return csv_bytes
