"""Tests for Pydantic-to-SQLAlchemy type conversion."""

from enum import Enum

import pytest
import sqlalchemy as sa
from pydantic import BaseModel, Field, JsonValue

from gen_epix.fastapp.repositories.sa.util import create_sa_type_from_field_info


class Status(Enum):
    """Enum used to verify native SQLAlchemy enum conversion."""

    READY = "ready"


class Payload(BaseModel):
    """Nested model used to verify JSON column conversion."""

    value: str


class ColumnModel(BaseModel):
    """Fields used to verify SQLAlchemy column type conversion."""

    text: str
    bounded_text: str = Field(max_length=12)
    count: int
    status: Status
    payload: Payload
    report: JsonValue | None = None


def test_create_sa_type_maps_primitives_enums_and_models() -> None:
    """Map supported Python field types to their SQLAlchemy equivalents."""
    assert isinstance(
        create_sa_type_from_field_info(ColumnModel.model_fields["count"], int),
        sa.Integer,
    )
    assert isinstance(
        create_sa_type_from_field_info(ColumnModel.model_fields["status"], Status),
        sa.Enum,
    )
    assert isinstance(
        create_sa_type_from_field_info(ColumnModel.model_fields["payload"], Payload),
        sa.JSON,
    )


def test_create_sa_type_maps_optional_json_value_to_json() -> None:
    """Map an optional JsonValue field, a type alias rather than a class, to JSON."""
    sa_type = create_sa_type_from_field_info(
        ColumnModel.model_fields["report"], JsonValue | None
    )

    assert isinstance(sa_type, sa.JSON)


def test_create_sa_type_uses_bounded_or_unbounded_text() -> None:
    """Preserve bounded string lengths and fall back above the configured limit."""
    bounded = create_sa_type_from_field_info(
        ColumnModel.model_fields["bounded_text"], str
    )
    unbounded = create_sa_type_from_field_info(ColumnModel.model_fields["text"], str)
    over_limit = create_sa_type_from_field_info(
        ColumnModel.model_fields["bounded_text"],
        str,
        max_unicode_column_length=8,
    )

    assert isinstance(bounded, sa.Unicode)
    assert bounded.length == 12
    assert isinstance(unbounded, sa.UnicodeText)
    assert isinstance(over_limit, sa.UnicodeText)


def test_create_sa_type_rejects_unsupported_annotations() -> None:
    """Report annotations without a registered SQLAlchemy type mapping."""
    with pytest.raises(NotImplementedError, match="Unsupported field type"):
        create_sa_type_from_field_info(ColumnModel.model_fields["count"], complex)
