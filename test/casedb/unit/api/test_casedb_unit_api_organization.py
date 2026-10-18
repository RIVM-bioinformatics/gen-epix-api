import pytest
from pydantic import ValidationError

from gen_epix.casedb.api import organization
from gen_epix.casedb.domain import DOMAIN
from gen_epix.fastapp.enum import PermissionType


def test_command_name_enum_matches_domain_commands() -> None:
    """Expose exactly the domain's command names as same-valued members."""
    members = {member.name: member.value for member in organization.CommandName}

    assert members == {name: name for name in DOMAIN.command_names}


@pytest.fixture
def command_name() -> str:
    """Return a command name registered in the casedb domain."""
    return sorted(DOMAIN.command_names)[0]


@pytest.mark.parametrize("permission_type", list(PermissionType), ids=lambda x: x.name)
def test_api_permission_accepts_valid_values(
    command_name: str, permission_type: PermissionType
) -> None:
    """Build a permission from a valid command name and permission type."""
    permission = organization.ApiPermission(
        command_name=command_name, permission_type=permission_type
    )

    assert permission.command_name.value == command_name
    assert permission.permission_type is permission_type


def test_api_permission_accepts_enum_values_from_json(command_name: str) -> None:
    """Parse string values to enum members when validating from JSON."""
    permission = organization.ApiPermission.model_validate_json(
        f'{{"command_name": "{command_name}", "permission_type": "READ"}}'
    )

    assert permission.command_name is organization.CommandName(command_name)
    assert permission.permission_type is PermissionType.READ


@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({"command_name": "NotACommand"}, id="unknown_command"),
        pytest.param({"command_name": None}, id="none_command"),
        pytest.param({"command_name": ""}, id="empty_command"),
        pytest.param({"permission_type": "NOT_A_TYPE"}, id="unknown_type"),
        pytest.param({"permission_type": None}, id="none_type"),
    ],
)
def test_api_permission_rejects_invalid_values(
    command_name: str, overrides: dict
) -> None:
    """Reject unknown, empty, and null field values."""
    data = {"command_name": command_name, "permission_type": PermissionType.READ}
    data.update(overrides)

    with pytest.raises(ValidationError):
        organization.ApiPermission(**data)


@pytest.mark.parametrize("missing", ["command_name", "permission_type"])
def test_api_permission_requires_fields(command_name: str, missing: str) -> None:
    """Reject construction when a required field is omitted."""
    data = {"command_name": command_name, "permission_type": PermissionType.READ}
    del data[missing]

    with pytest.raises(ValidationError):
        organization.ApiPermission(**data)


def test_api_permission_is_frozen(command_name: str) -> None:
    """Disallow mutation of a constructed permission."""
    permission = organization.ApiPermission(
        command_name=command_name, permission_type=PermissionType.READ
    )

    with pytest.raises(ValidationError):
        permission.permission_type = PermissionType.DELETE  # type: ignore[misc]
