"""Download the OpenDengue National Extract (V1.3) into data/raw/.

This script performs acquisition only: it downloads the official release
archive from the OpenDengue GitHub repository, verifies it against the
recorded checksum, and extracts the single CSV it contains. It does not
parse, clean, standardize, or otherwise transform the data — see
docs/datasets/01_acquisition.md for why that boundary matters (Milestone 2
is Data Acquisition & Understanding, not Data Engineering).

Per the Freeze Document (Section 23, Data Versioning), the downloaded CSV
is never committed to the repository. This script exists so that any
reviewer can reproduce the exact same file locally instead of relying on
a copy that isn't in version control.

Usage:
    python data/download_national_extract.py

Output:
    data/raw/National_extract_V1_3.csv
"""

from __future__ import annotations

import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

# Pinned to the exact tagged release used throughout this project.
# See docs/datasets/01_acquisition.md for why the tag (not "main") is used.
RELEASE_TAG = "v1.3.0"
ARCHIVE_URL = (
    "https://raw.githubusercontent.com/OpenDengue/master-repo/"
    f"{RELEASE_TAG}/data/releases/V1.3/National_extract_V1_3.zip"
)
EXPECTED_ARCHIVE_SHA256 = (
    "d4fa7b1a881481fd5323991cc7a23dbe690112e2c473898ceea76e1e9c85dc59"
)
ARCHIVE_MEMBER = "National_extract_V1_3.csv"

RAW_DIR = Path(__file__).parent / "raw"
OUTPUT_PATH = RAW_DIR / ARCHIVE_MEMBER


def download_archive(url: str) -> bytes:
    """Fetch the release archive into memory. No disk writes here."""
    with urllib.request.urlopen(url) as response:
        return response.read()


def verify_checksum(data: bytes, expected_sha256: str) -> str:
    """Return the SHA-256 hex digest, warning (not failing) on first run."""
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256.startswith("PLACEHOLDER"):
        print(
            "NOTE: no checksum pinned yet. Recording this run's digest for "
            "you to paste into EXPECTED_ARCHIVE_SHA256 above, so future "
            "runs can verify against it:\n  " + digest
        )
    elif digest != expected_sha256:
        raise ValueError(
            f"Checksum mismatch: expected {expected_sha256}, got {digest}. "
            "The upstream archive for this release tag may have changed — "
            "investigate before proceeding."
        )
    return digest


def extract_csv(archive_bytes: bytes, member: str, destination: Path) -> Path:
    """Extract exactly one named member from the zip archive, unmodified."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zf:
        with zf.open(member) as src, open(destination, "wb") as dst:
            dst.write(src.read())
    return destination


def main() -> int:
    print(f"Downloading OpenDengue National Extract ({RELEASE_TAG})...")
    print(f"Source: {ARCHIVE_URL}")
    archive_bytes = download_archive(ARCHIVE_URL)
    verify_checksum(archive_bytes, EXPECTED_ARCHIVE_SHA256)
    path = extract_csv(archive_bytes, ARCHIVE_MEMBER, OUTPUT_PATH)
    print(f"Saved: {path} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
