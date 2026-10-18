"""Verify optional UUID identifier behavior on the OmopDB base model."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from gen_epix.omopdb.domain.model.base import Model

MODEL_ID = UUID("00000000-0000-0000-0000-000000000001")


@pytest.mark.parametrize(
    "data",
    [{}, {"id": None}],
    ids=["omitted", "explicit-none"],
)
def test_id_defaults_to_none(data: dict[str, UUID | None]) -> None:
    """An omitted or null ID should remain unset."""
    assert Model(**data).id is None


def test_uuid_id_is_preserved() -> None:
    """A UUID ID should be retained by the model."""
    assert Model(id=MODEL_ID).id == MODEL_ID


def test_uuid_string_id_is_parsed() -> None:
    """A valid UUID string should be parsed as a UUID."""
    assert Model(id=str(MODEL_ID)).id == MODEL_ID


def test_malformed_uuid_string_is_rejected() -> None:
    """A malformed UUID string should fail model validation."""
    with pytest.raises(ValidationError):
        Model(id="not-a-uuid")
