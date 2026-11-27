"""Verify commondb SQL mapper update rules."""

from types import SimpleNamespace

from pydantic import BaseModel

from gen_epix.commondb.repositories.sa_mapper import CommondbSAMapper
from gen_epix.fastapp.enum import FieldTypeSet


class DomainModel(BaseModel):
    """Minimal model with one non-metadata value field."""

    value: str | None = None


def _create_mapper() -> SimpleNamespace:
    """Provide the field maps consumed by CommondbSAMapper.update."""
    field_set = FieldTypeSet.MODEL_DB_COMMON
    return SimpleNamespace(
        _field_names_by_set={field_set: ("value", "modified_by")},
        _row_field_names_by_set={field_set: ("value", "modified_by")},
    )


def test_none_input_preserves_existing_row_value() -> None:
    """Do not clear populated database values from None model fields."""
    row = SimpleNamespace(value="existing", modified_by="previous")

    updated = CommondbSAMapper.update(
        _create_mapper(), user_id="current", obj=DomainModel(), row=row
    )

    assert updated is False
    assert row.value == "existing"
    assert row.modified_by == "previous"


def test_explicit_none_clears_existing_row_value() -> None:
    """Clear a stored value when None was explicitly supplied by the caller."""
    row = SimpleNamespace(value="existing", modified_by="previous")

    updated = CommondbSAMapper.update(
        _create_mapper(), user_id="current", obj=DomainModel(value=None), row=row
    )

    assert updated is True
    assert row.value is None
    assert row.modified_by == "current"


def test_non_none_input_updates_value_and_audit_user() -> None:
    """Apply changed values and attribute the update to the current user."""
    row = SimpleNamespace(value="existing", modified_by="previous")

    updated = CommondbSAMapper.update(
        _create_mapper(),
        user_id="current",
        obj=DomainModel(value="updated"),
        row=row,
    )

    assert updated is True
    assert row.value == "updated"
    assert row.modified_by == "current"
