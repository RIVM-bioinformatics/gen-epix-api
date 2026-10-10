"""Check seqdb command permission payload validation and serialization."""

import pytest
from pydantic import ValidationError

from gen_epix.fastapp.enum import PermissionType
from gen_epix.seqdb.api.organization import ApiPermission, CommandName
from gen_epix.seqdb.domain import DOMAIN


def test_command_name_mirrors_registered_seqdb_commands() -> None:
    """Expose every registered seqdb command as an API enum member."""
    assert {name: member.value for name, member in CommandName.__members__.items()} == {
        name: name for name in DOMAIN.command_names
    }


@pytest.mark.parametrize(
    "permission_type",
    list(PermissionType),
    ids=lambda permission_type: permission_type.value,
)
def test_api_permission_coerces_and_serializes_values(
    permission_type: PermissionType,
) -> None:
    """Validate registered command names and serialize permission values."""
    command_name = min(DOMAIN.command_names)

    permission = ApiPermission(
        command_name=command_name,
        permission_type=permission_type.value,
    )

    assert permission.command_name is CommandName[command_name]
    assert permission.permission_type is permission_type
    assert permission.model_dump(mode="json") == {
        "command_name": command_name,
        "permission_type": permission_type.value,
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"command_name": "not-a-seqdb-command", "permission_type": "READ"},
        {"command_name": min(DOMAIN.command_names), "permission_type": "INVALID"},
        {"permission_type": "READ"},
        {"command_name": min(DOMAIN.command_names)},
    ],
    ids=[
        "unknown-command",
        "unknown-permission-type",
        "missing-command-name",
        "missing-permission-type",
    ],
)
def test_api_permission_rejects_invalid_or_missing_fields(
    payload: dict[str, str],
) -> None:
    """Reject unknown enum values and omitted required permission fields."""
    with pytest.raises(ValidationError):
        ApiPermission(**payload)


def test_api_permission_is_immutable() -> None:
    """Prevent changes to a validated permission instance."""
    command_name = min(DOMAIN.command_names)
    permission = ApiPermission(
        command_name=command_name,
        permission_type=PermissionType.READ,
    )

    with pytest.raises(ValidationError):
        permission.command_name = CommandName[command_name]
