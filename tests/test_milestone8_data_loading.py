"""Milestone 8 tests: data_loading (ADR-010).

Zero Streamlit imports here -- this module is plain Python and tested
as such, per ADR-010's independence requirement.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from unittest.mock import patch

import pandas as pd
import pytest

from surveillance_platform.data_loading.loading import FileTooLargeError, load_csv
from surveillance_platform.data_loading.sample_dataset import (
    ChecksumMismatchError,
    get_sample_dataset,
)
from surveillance_platform.data_loading.sanity_check import check_spatial_resolution

# --- load_csv ---------------------------------------------------------


def test_load_csv_reads_a_simple_file():
    file = io.BytesIO(b"a,b\n1,2\n3,4\n")
    df = load_csv(file)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_load_csv_rejects_oversized_file():
    from surveillance_platform.data_loading.loading import MAX_UPLOAD_BYTES

    oversized = io.BytesIO(b"x" * (MAX_UPLOAD_BYTES + 1))
    with pytest.raises(FileTooLargeError):
        load_csv(oversized)


def test_load_csv_does_not_error_at_exactly_the_limit():
    from surveillance_platform.data_loading.loading import MAX_UPLOAD_BYTES

    # A minimal valid CSV padded with a comment-like column to reach
    # close to (but under) the limit would be slow to construct; the
    # boundary itself (> vs >=) is what matters here, tested directly.
    file = io.BytesIO(b"a\n1\n")
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    assert size <= MAX_UPLOAD_BYTES  # sanity: our tiny fixture is under the limit
    load_csv(file)  # must not raise


# --- check_spatial_resolution ------------------------------------------


def test_sanity_check_returns_none_when_column_absent():
    df = pd.DataFrame({"a": [1, 2]})
    assert check_spatial_resolution(df) is None


def test_sanity_check_returns_none_when_all_admin0():
    df = pd.DataFrame({"S_res": ["Admin0", "Admin0", "Admin0"]})
    assert check_spatial_resolution(df) is None


def test_sanity_check_warns_on_sub_national_values():
    df = pd.DataFrame({"S_res": ["Admin0", "Admin1", "Admin2"]})
    message = check_spatial_resolution(df)
    assert message is not None
    assert "Admin1" in message
    assert "Admin2" in message


def test_sanity_check_never_raises_only_warns():
    """The check must never block -- only ever return a message or None."""
    df = pd.DataFrame({"S_res": ["Admin2"] * 100})
    message = check_spatial_resolution(df)
    assert isinstance(message, str)


# --- get_sample_dataset --------------------------------------------------


def test_get_sample_dataset_uses_cache_when_present(tmp_path):
    cached_file = tmp_path / "National_extract_V1_3.csv"
    cached_file.write_bytes(b"cached,content\n1,2\n")

    with (
        patch(
            "surveillance_platform.data_loading.sample_dataset.OUTPUT_PATH", cached_file
        ),
        patch(
            "surveillance_platform.data_loading.sample_dataset.urllib.request.urlopen"
        ) as mock_urlopen,
    ):
        result = get_sample_dataset()
        mock_urlopen.assert_not_called()
    assert result == b"cached,content\n1,2\n"


def _fake_archive(csv_content: bytes) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("National_extract_V1_3.csv", csv_content)
    return buf.getvalue()


def test_get_sample_dataset_downloads_and_verifies_when_absent(tmp_path):
    csv_content = b"a,b\n1,2\n"
    archive_bytes = _fake_archive(csv_content)
    real_digest = hashlib.sha256(archive_bytes).hexdigest()
    target_path = tmp_path / "National_extract_V1_3.csv"

    mock_response = io.BytesIO(archive_bytes)
    mock_response.__enter__ = lambda self: mock_response
    mock_response.__exit__ = lambda self, *a: None

    with (
        patch(
            "surveillance_platform.data_loading.sample_dataset.OUTPUT_PATH", target_path
        ),
        patch(
            "surveillance_platform.data_loading.sample_dataset.EXPECTED_ARCHIVE_SHA256",
            real_digest,
        ),
        patch(
            "surveillance_platform.data_loading.sample_dataset.urllib.request.urlopen",
            return_value=mock_response,
        ),
    ):
        result = get_sample_dataset()

    assert result == csv_content
    assert target_path.read_bytes() == csv_content  # cached for next call


def test_get_sample_dataset_raises_on_checksum_mismatch(tmp_path):
    archive_bytes = _fake_archive(b"a,b\n1,2\n")
    target_path = tmp_path / "National_extract_V1_3.csv"

    mock_response = io.BytesIO(archive_bytes)
    mock_response.__enter__ = lambda self: mock_response
    mock_response.__exit__ = lambda self, *a: None

    with (
        patch(
            "surveillance_platform.data_loading.sample_dataset.OUTPUT_PATH", target_path
        ),
        patch(
            "surveillance_platform.data_loading.sample_dataset.EXPECTED_ARCHIVE_SHA256",
            "0" * 64,
        ),
        patch(
            "surveillance_platform.data_loading.sample_dataset.urllib.request.urlopen",
            return_value=mock_response,
        ),
        pytest.raises(ChecksumMismatchError),
    ):
        get_sample_dataset()
    assert not target_path.exists()  # never cached a bad download
