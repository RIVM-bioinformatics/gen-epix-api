"""Validate the seqdb file model's content and persistence metadata."""

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain.model.file import File


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        pytest.param(b"", b"", id="empty"),
        pytest.param(b"\x00\xffsequence", b"\x00\xffsequence", id="binary"),
    ],
)
def test_file_preserves_binary_content(content: bytes, expected: bytes) -> None:
    """Preserve empty and arbitrary binary content."""
    file = File(content=content)

    assert file.content == expected


@pytest.mark.parametrize(
    "values",
    [
        pytest.param({}, id="missing"),
        pytest.param({"content": None}, id="none"),
    ],
)
def test_file_requires_content(values: dict[str, object]) -> None:
    """Reject missing and null content values."""
    with pytest.raises(ValidationError):
        File(**values)


def test_file_entity_describes_persisted_file_table() -> None:
    """Expose the file table's persistence metadata."""
    assert File.ENTITY.snake_case_plural_name == "files"
    assert File.ENTITY.table_name == "file"
    assert File.ENTITY.persistable is True
