"""Test casedb geographic region command definitions."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

import gen_epix.casedb.domain.model.geo as model
from gen_epix.casedb.domain.command import geo
from gen_epix.fastapp.enum import CrudOperation, PermissionTypeSet

CRUD_COMMAND_MODELS = [
    pytest.param(geo.RegionSetCrudCommand, model.RegionSet, id="region-set"),
    pytest.param(geo.RegionCrudCommand, model.Region, id="region"),
    pytest.param(
        geo.RegionRelationCrudCommand, model.RegionRelation, id="region-relation"
    ),
    pytest.param(
        geo.RegionSetShapeCrudCommand, model.RegionSetShape, id="region-set-shape"
    ),
]


@pytest.mark.parametrize(("command_class", "model_class"), CRUD_COMMAND_MODELS)
def test_crud_command_binds_model_class(command_class, model_class) -> None:
    """Bind each CRUD command to its geographic model and CRUD permissions."""
    assert command_class.MODEL_CLASS is model_class
    assert command_class.PERMISSION_TYPE_SET == PermissionTypeSet.CRUD


@pytest.mark.parametrize(("command_class", "_model_class"), CRUD_COMMAND_MODELS)
def test_crud_command_accepts_read_all(command_class, _model_class) -> None:
    """Build a read-all command with default paging and no objects."""
    command = command_class(operation=CrudOperation.READ_ALL)

    assert command.operation == CrudOperation.READ_ALL
    assert command.obj_ids is None
    assert command.limit == 0


@pytest.mark.parametrize(("command_class", "_model_class"), CRUD_COMMAND_MODELS)
def test_crud_command_rejects_missing_operation(command_class, _model_class) -> None:
    """Require an explicit CRUD operation."""
    with pytest.raises(ValidationError):
        command_class()


def test_retrieve_containing_region_command_fields() -> None:
    """Keep the supplied IDs and level on a containing-region request."""
    region_ids = [uuid4(), uuid4()]
    region_set_id = uuid4()

    command = geo.RetrieveContainingRegionCommand(
        region_ids=region_ids, region_set_id=region_set_id, level=2
    )

    assert command.region_ids == region_ids
    assert command.region_set_id == region_set_id
    assert command.level == 2
    assert command.PERMISSION_TYPE_SET == PermissionTypeSet.E


def test_retrieve_containing_region_command_accepts_empty_region_ids() -> None:
    """Accept an empty region ID list; the command does not constrain its size."""
    command = geo.RetrieveContainingRegionCommand(
        region_ids=[], region_set_id=uuid4(), level=0
    )

    assert command.region_ids == []


@pytest.mark.parametrize(
    "missing_field", ["region_ids", "region_set_id", "level"], ids=str
)
def test_retrieve_containing_region_command_requires_fields(missing_field) -> None:
    """Reject a containing-region request that omits a required field."""
    kwargs = {"region_ids": [uuid4()], "region_set_id": uuid4(), "level": 1}
    del kwargs[missing_field]

    with pytest.raises(ValidationError):
        geo.RetrieveContainingRegionCommand(**kwargs)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("region_ids", ["not-a-uuid"], id="invalid-region-id"),
        pytest.param("region_set_id", "not-a-uuid", id="invalid-region-set-id"),
        pytest.param("level", "high", id="non-numeric-level"),
    ],
)
def test_retrieve_containing_region_command_rejects_invalid_types(field, value) -> None:
    """Reject values that cannot be coerced to the declared field types."""
    kwargs = {"region_ids": [uuid4()], "region_set_id": uuid4(), "level": 1}
    kwargs[field] = value

    with pytest.raises(ValidationError):
        geo.RetrieveContainingRegionCommand(**kwargs)
