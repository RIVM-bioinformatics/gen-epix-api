"""Tests for read-set validation and availability."""

from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.reads import ReadSet

_DUPLICATE_HASH = UUID("00000000-0000-0000-0000-000000000001")


def _read_set(**values: object) -> ReadSet:
    return ReadSet(sample_id=uuid4(), protocol_id=uuid4(), **values)


def test_read_set_availability_tracks_uri_and_file_links() -> None:
    """Report unavailable without links and available for either link kind."""
    assert not _read_set().is_available
    assert _read_set(fwd_uri="s3://reads/sample.fastq").is_available
    assert _read_set(
        rev_file_id=uuid4(), file_format=enum.ReadsFileFormat.FASTQ
    ).is_available


def test_file_links_require_format_and_default_compression() -> None:
    """Require a file format and default omitted compression to NONE."""
    with pytest.raises(ValidationError, match="file_format must be provided"):
        _read_set(fwd_file_id=uuid4())

    read_set = _read_set(
        fwd_file_id=uuid4(),
        file_format=enum.ReadsFileFormat.FASTQ,
    )

    assert read_set.file_compression == enum.FileCompression.NONE
    assert (
        read_set.model_dump(mode="json")["file_format"]
        == enum.ReadsFileFormat.FASTQ.value
    )


@pytest.mark.parametrize(
    "values",
    [
        {"fwd_uri": "same", "rev_uri": "same"},
        {"fwd_reads_hash": _DUPLICATE_HASH, "rev_reads_hash": _DUPLICATE_HASH},
    ],
)
def test_read_set_rejects_duplicate_forward_and_reverse_values(
    values: dict[str, object],
) -> None:
    """Reject duplicated forward/reverse URI and hash values."""
    with pytest.raises(ValidationError):
        _read_set(**values)


def test_read_set_rejects_mixed_uri_and_file_links() -> None:
    """Keep URI-backed and file-backed read references mutually exclusive."""
    with pytest.raises(ValidationError, match="Cannot have both uri and file_id"):
        _read_set(
            fwd_uri="s3://reads/sample.fastq",
            rev_file_id=uuid4(),
            file_format=enum.ReadsFileFormat.FASTQ,
        )
