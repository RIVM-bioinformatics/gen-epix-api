"""Verify FASTQ parser errors are normalized as invalid arguments."""

import pytest

from gen_epix.seqdb.domain import enum, exc
from gen_epix.seqdb.services.file import FileService


class FileServiceStub:
    """Expose file-content verification without application dependencies."""

    _get_file_text_stream = FileService._get_file_text_stream
    _verify_fastq_content = FileService._verify_fastq_content


def test_truncated_fastq_record_raises_invalid_arguments_error() -> None:
    """Normalize lazy parser errors for truncated FASTQ records."""
    content = b"@read1\nACGT\n+\n"

    with pytest.raises(exc.InvalidArgumentsError, match="Invalid FASTQ content"):
        FileServiceStub()._verify_fastq_content(content, enum.FileCompression.NONE)
