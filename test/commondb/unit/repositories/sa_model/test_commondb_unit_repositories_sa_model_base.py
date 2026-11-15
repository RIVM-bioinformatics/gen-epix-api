"""Verify nullable SQLAlchemy audit metadata annotations."""

from typing import get_type_hints
from uuid import UUID

from sqlalchemy.orm import Mapped

from gen_epix.commondb.repositories.sa_model.base import (
    NoIdRowMetadataMixin,
    RowMetadataMixin,
)


def test_nullable_modified_by_columns_allow_none_in_type_hints() -> None:
    """Keep Python annotations consistent with nullable mapped columns."""
    expected_type = Mapped[UUID | None]

    assert get_type_hints(RowMetadataMixin)["modified_by"] == expected_type
    assert get_type_hints(NoIdRowMetadataMixin)["modified_by"] == expected_type
