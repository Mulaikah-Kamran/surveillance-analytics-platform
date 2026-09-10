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

import csv
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


# The four countries this project was actually built and evaluated
# around (ADR-008). A first-time user downloading "the sample dataset"
# and landing on 129 countries they don't recognize is a worse first
# impression than a small, focused starter file -- so the download
# button offers this subset by default, with a separate link to
# OpenDengue's own site for anyone who wants a different country.
STARTER_COUNTRIES = ("SRI LANKA", "BANGLADESH", "MALDIVES", "NEPAL")


def get_starter_sample_dataset() -> bytes:
    """Return just the four ADR-008 study countries, as CSV bytes.

    Reuses get_sample_dataset()'s full download/cache/verify logic
    unchanged (other tooling, e.g. the M2 acquisition tests, expects
    the shared cache file at OUTPUT_PATH to stay the complete,
    unfiltered National Extract) -- this only filters the bytes
    returned here, in memory, never touching that cached file.
    """
    full_csv = get_sample_dataset()
    reader = csv.DictReader(io.StringIO(full_csv.decode("utf-8")))
    fieldnames = reader.fieldnames
    rows = [row for row in reader if row["adm_0_name"] in STARTER_COUNTRIES]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")
