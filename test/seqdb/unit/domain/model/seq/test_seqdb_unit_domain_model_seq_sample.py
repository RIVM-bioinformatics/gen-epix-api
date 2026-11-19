"""Verify sample model code normalization and validation."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.seqdb.domain.model.seq.sample import Sample


def test_sample_strips_string_code() -> None:
    """Normalize surrounding whitespace in string codes."""
    sample = Sample(created_in_data_collection_id=uuid4(), code="  sample-1  ")

    assert sample.code == "sample-1"


@pytest.mark.parametrize("code", [123, True, []], ids=["integer", "boolean", "list"])
def test_sample_rejects_non_string_code_with_validation_error(code: object) -> None:
    """Report invalid code types through Pydantic field validation."""
    with pytest.raises(ValidationError):
        Sample(created_in_data_collection_id=uuid4(), code=code)
