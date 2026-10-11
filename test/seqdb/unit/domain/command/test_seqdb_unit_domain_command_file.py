"""Validate seqdb file-command fields and model association."""

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain import enum, model
from gen_epix.seqdb.domain.command.file import CreateFileCommand, FileCrudCommand


@pytest.mark.parametrize(
    "file_format",
    [enum.FileFormat.FASTA, enum.FileFormat.FASTQ],
    ids=lambda file_format: file_format.name,
)
def test_create_file_command_defaults_compression_to_none(
    file_format: enum.FileFormat,
) -> None:
    """Default omitted compression while preserving required file format."""
    file = model.File(content=b"payload")

    command = CreateFileCommand(file=file, format=file_format)

    assert command.file is file
    assert command.format is file_format
    assert command.compression is enum.FileCompression.NONE


@pytest.mark.parametrize(
    "compression",
    [enum.FileCompression.NONE, enum.FileCompression.GZIP],
    ids=lambda compression: compression.name,
)
def test_create_file_command_accepts_explicit_compression(
    compression: enum.FileCompression,
) -> None:
    """Preserve either supported compression when supplied explicitly."""
    command = CreateFileCommand(
        file=model.File(content=b"payload"),
        format=enum.FileFormat.FASTA,
        compression=compression,
    )

    assert command.compression is compression


@pytest.mark.parametrize(
    "missing_field",
    ["file", "format"],
    ids=lambda missing_field: f"missing-{missing_field}",
)
def test_create_file_command_requires_file_and_format(missing_field: str) -> None:
    """Reject construction when either required file input is omitted."""
    values: dict[str, object] = {
        "file": model.File(content=b"payload"),
        "format": enum.FileFormat.FASTA,
    }
    values.pop(missing_field)

    with pytest.raises(ValidationError):
        CreateFileCommand(**values)


@pytest.mark.parametrize(
    "field, value",
    [
        pytest.param("format", 99, id="invalid-format"),
        pytest.param("compression", 99, id="invalid-compression"),
    ],
)
def test_create_file_command_rejects_unsupported_enum_values(
    field: str, value: int
) -> None:
    """Reject file-format and compression values outside their enums."""
    values: dict[str, object] = {
        "file": model.File(content=b"payload"),
        "format": enum.FileFormat.FASTA,
    }
    values[field] = value

    with pytest.raises(ValidationError):
        CreateFileCommand(**values)


def test_file_crud_command_targets_file_model() -> None:
    """Associate CRUD file commands with the persisted file model."""
    assert FileCrudCommand.MODEL_CLASS is model.File
