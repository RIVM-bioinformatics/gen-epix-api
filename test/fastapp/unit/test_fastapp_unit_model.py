"""Validate default FastApp model and policy contracts."""

from test.fastapp.model import Model1_1
from typing import Any, ClassVar
from uuid import uuid4

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import CrudOperation, PermissionType
from gen_epix.fastapp.model import (
    Command,
    CrudCommand,
    Model,
    ModelFieldProps,
    Permission,
    Policy,
    User,
)
from gen_epix.filter.base import Filter


class _AnyFilter(Filter):
    def _match(self, value: Any) -> bool:
        return True


@pytest.mark.parametrize(
    "method_name", ["is_allowed", "get_content", "get_content_return_type", "filter"]
)
def test_unimplemented_policy_methods_share_error_contract(method_name: str) -> None:
    """Require unimplemented policy hooks to raise the documented exception."""
    policy = Policy()
    command = Command()
    method = getattr(policy, method_name)
    args = (command, None) if method_name == "filter" else (command,)

    with pytest.raises(
        NotImplementedError, match="^Method is not implemented for this policy$"
    ):
        method(*args)


def test_model_metadata_and_id_contracts() -> None:
    class NamedModel(Model1_1):
        NAME: ClassVar[str | None] = "named_model"

    item_id = uuid4()
    item = Model1_1(id=item_id, var1=1, var2="value")
    item_without_id = Model1_1(id=None, var1=1, var2="value")

    assert Model1_1.model_entity() is Model1_1.ENTITY
    assert NamedModel.model_name() == "named_model"
    assert item.get_id() == item_id
    assert item_without_id.get_id() is None
    with pytest.raises(exc.InvalidIdsError):
        item_without_id.get_id(raise_on_missing=True)


def test_model_metadata_requires_entity_and_name() -> None:
    class UnnamedModel(Model):
        NAME: ClassVar[str | None] = None

    with pytest.raises(exc.InitializationServiceError, match="Entity not set"):
        Model.model_entity()
    with pytest.raises(exc.InitializationServiceError, match="Name not set"):
        UnnamedModel.model_name()


def test_user_and_command_identity_accessors() -> None:
    user_id = uuid4()
    user = User(id=user_id)
    command_with_user = Command(user=user)
    command_without_user = Command()

    assert user.get_key() == str(user_id)
    assert command_with_user.get_user_id() == user_id
    assert command_without_user.get_user_id() is None
    with pytest.raises(ValueError, match="User is missing"):
        command_without_user.get_user_id(raise_on_missing=True)
    assert command_with_user.get_permission_type() == PermissionType.EXECUTE


@pytest.mark.parametrize(
    ("permission_type", "sort_value"),
    [
        (PermissionType.EXECUTE, 0),
        (PermissionType.CREATE, 1),
        (PermissionType.READ, 2),
        (PermissionType.UPDATE, 3),
        (PermissionType.DELETE, 4),
    ],
)
def test_permission_name_sort_repr_equality_and_serialization(
    permission_type: PermissionType, sort_value: int
) -> None:
    permission = Permission(command_name="sample", permission_type=permission_type)
    same_permission = Permission(command_name="sample", permission_type=permission_type)

    assert permission.name == f"sample_{permission_type.value}"
    assert permission.sort_key == ("sample", sort_value)
    assert permission == same_permission
    assert permission != object()
    assert repr(permission) == f"(sample,{permission_type.value})"
    assert (
        permission._serialize_permission_type(permission_type) == permission_type.value
    )


def test_crud_command_validation_rejects_invalid_operation_state() -> None:
    item = Model1_1(id=uuid4(), var1=1, var2="value")
    item_id = uuid4()
    invalid_commands = [
        ({"operation": CrudOperation.READ_ONE}, "obj_ids=None"),
        (
            {"operation": CrudOperation.CREATE_ONE, "obj_ids": [item_id]},
            "obj_ids=list",
        ),
        ({"operation": CrudOperation.READ_ALL, "obj_ids": item_id}, "obj_ids=obj_id"),
        ({"operation": CrudOperation.CREATE_ONE}, "objects=None"),
        (
            {
                "operation": CrudOperation.READ_ONE,
                "obj_ids": item_id,
                "objs": [item],
            },
            "objs=list",
        ),
        (
            {"operation": CrudOperation.READ_ONE, "obj_ids": item_id, "objs": item},
            "objs=object",
        ),
        (
            {
                "operation": CrudOperation.CREATE_ONE,
                "objs": item,
                "query_filter": _AnyFilter(),
            },
            "query_filter not None",
        ),
        (
            {
                "operation": CrudOperation.READ_ONE,
                "obj_ids": item_id,
                "return_id": True,
            },
            "return_id=True",
        ),
        (
            {"operation": CrudOperation.READ_ONE, "obj_ids": item_id, "limit": 1},
            "Invalid operation for limit",
        ),
    ]

    for fields, message in invalid_commands:
        with pytest.raises(ValueError, match=message):
            CrudCommand(**fields)


def test_crud_command_object_accessors() -> None:
    item_id = uuid4()
    second_item_id = uuid4()
    first_item = Model1_1(id=item_id, var1=1, var2="first")
    second_item = Model1_1(id=second_item_id, var1=2, var2="second")
    item_without_id = Model1_1(id=None, var1=3, var2="third")

    no_objects = CrudCommand(operation=CrudOperation.READ_ALL)
    id_list_command = CrudCommand(
        operation=CrudOperation.READ_SOME,
        obj_ids=[item_id, second_item_id],
    )
    object_list_command = CrudCommand(
        operation=CrudOperation.CREATE_SOME,
        objs=[first_item, second_item, item_without_id],
    )
    single_object_command = CrudCommand(
        operation=CrudOperation.CREATE_ONE,
        objs=first_item,
    )
    single_id_command = CrudCommand(
        operation=CrudOperation.READ_ONE,
        obj_ids=item_id,
    )

    assert no_objects.get_obj_ids() is None
    assert no_objects.get_objs() is None
    assert id_list_command.get_obj_ids() == [item_id, second_item_id]
    assert id_list_command.get_obj_ids(as_set=True) == {item_id, second_item_id}
    assert object_list_command.get_obj_ids() == [item_id, second_item_id, None]
    assert object_list_command.get_obj_ids(as_set=True) == {item_id, second_item_id}
    assert object_list_command.get_objs() == [first_item, second_item, item_without_id]
    assert single_object_command.get_obj_ids() == [item_id]
    assert single_object_command.get_obj_ids(as_set=True) == {item_id}
    assert single_object_command.get_objs() == [first_item]
    assert single_id_command.get_obj_ids(as_set=True) == {item_id}


def test_crud_command_operation_helpers_and_permissions() -> None:
    permission_by_operation = {
        CrudOperation.CREATE_ONE: PermissionType.CREATE,
        CrudOperation.CREATE_SOME: PermissionType.CREATE,
        CrudOperation.READ_ALL: PermissionType.READ,
        CrudOperation.READ_SOME: PermissionType.READ,
        CrudOperation.READ_ONE: PermissionType.READ,
        CrudOperation.EXISTS_ONE: PermissionType.READ,
        CrudOperation.EXISTS_SOME: PermissionType.READ,
        CrudOperation.UPDATE_ONE: PermissionType.UPDATE,
        CrudOperation.UPDATE_SOME: PermissionType.UPDATE,
        CrudOperation.DELETE_ONE: PermissionType.DELETE,
        CrudOperation.DELETE_SOME: PermissionType.DELETE,
        CrudOperation.DELETE_ALL: PermissionType.DELETE,
    }

    for operation in CrudOperation:
        command = CrudCommand.model_construct(operation=operation)
        if operation in permission_by_operation:
            assert command.get_permission_type() == permission_by_operation[operation]
        else:
            with pytest.raises(NotImplementedError, match="Unsupported operation"):
                command.get_permission_type()

        assert command.is_create() == (
            operation in {CrudOperation.CREATE_ONE, CrudOperation.CREATE_SOME}
        )
        assert command.is_read() == (
            operation
            in {
                CrudOperation.READ_ALL,
                CrudOperation.READ_SOME,
                CrudOperation.READ_ONE,
                CrudOperation.EXISTS_ONE,
                CrudOperation.EXISTS_SOME,
            }
        )
        assert command.is_read(exclude_exists=True) == (
            operation
            in {
                CrudOperation.READ_ALL,
                CrudOperation.READ_SOME,
                CrudOperation.READ_ONE,
            }
        )
        assert command.is_read_all() == (operation == CrudOperation.READ_ALL)
        assert command.is_read_one() == (operation == CrudOperation.READ_ONE)
        assert command.is_update() == (
            operation in {CrudOperation.UPDATE_ONE, CrudOperation.UPDATE_SOME}
        )
        assert command.is_delete() == (
            operation
            in {
                CrudOperation.DELETE_ONE,
                CrudOperation.DELETE_SOME,
                CrudOperation.DELETE_ALL,
            }
        )
        assert command.is_delete_all() == (operation == CrudOperation.DELETE_ALL)
        assert command.is_exists() == (
            operation in {CrudOperation.EXISTS_ONE, CrudOperation.EXISTS_SOME}
        )
        assert command.is_write() == (
            operation
            in {
                CrudOperation.CREATE_ONE,
                CrudOperation.CREATE_SOME,
                CrudOperation.UPDATE_ONE,
                CrudOperation.UPDATE_SOME,
                CrudOperation.UPSERT_ONE,
                CrudOperation.UPSERT_SOME,
            }
        )
        assert command.is_crud_one() == (
            operation
            in {
                CrudOperation.CREATE_ONE,
                CrudOperation.READ_ONE,
                CrudOperation.UPDATE_ONE,
                CrudOperation.DELETE_ONE,
                CrudOperation.EXISTS_ONE,
            }
        )
        assert command.is_crud_all() == (
            operation in {CrudOperation.READ_ALL, CrudOperation.DELETE_ALL}
        )


@pytest.mark.parametrize(
    ("props", "stored_value", "expected"),
    [
        ({"is_mutable_always": True}, "value", True),
        ({}, None, True),
        ({"is_sub_field_dict": True}, None, True),
        ({"is_sub_field_dict": True}, {}, True),
        ({"is_sub_field_dict": True}, {"key": "value"}, False),
        ({}, "value", False),
    ],
)
def test_model_field_props_mutability(
    props: dict[str, bool], stored_value: object, expected: bool
) -> None:
    assert ModelFieldProps(**props).is_mutable_value(stored_value) is expected


def test_model_field_props_rejects_conflicting_mutability_flags() -> None:
    with pytest.raises(ValueError, match="is_mutable_always cannot be True"):
        ModelFieldProps(is_mutable_if_empty=False, is_mutable_always=True)
