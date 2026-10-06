"""Tests for sequence representation helpers."""

import pytest

from gen_epix.seqdb.domain.model.seq.base import (
    decode_ascii_from_gzip_base64,
    encode_ascii_as_gzip_base64,
)


@pytest.mark.parametrize("value", ["", "ACGTN", "line one\nline two"])
def test_gzip_base64_round_trip_is_deterministic(value: str) -> None:
    """Encode ASCII content reproducibly and recover the exact input."""
    encoded = encode_ascii_as_gzip_base64(value)

    assert encode_ascii_as_gzip_base64(value) == encoded
    assert decode_ascii_from_gzip_base64(encoded) == value


@pytest.mark.parametrize("value", ["not base64!", "", "YWJj"])
def test_decode_rejects_invalid_or_non_gzip_payloads(value: str) -> None:
    """Normalize malformed base64 and gzip data to a consistent ValueError."""
    with pytest.raises(ValueError, match="not a valid base64-encoded gzip archive"):
        decode_ascii_from_gzip_base64(value)
