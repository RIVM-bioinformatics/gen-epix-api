from test.util.mock_compat import Mock
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy,
)
from gen_epix.commondb.domain import command as common_command
from gen_epix.fastapp import CrudOperation

ORGANIZATION_CASE_POLICY_COMMANDS = [
    command.OrganizationAccessCasePolicyCrudCommand,
    command.OrganizationShareCasePolicyCrudCommand,
]
USER_CASE_POLICY_COMMANDS = [
    command.UserAccessCasePolicyCrudCommand,
    command.UserShareCasePolicyCrudCommand,
]


@pytest.fixture
def abac_service() -> Mock:
    return Mock()


@pytest.fixture
def policy(abac_service: Mock) -> IsOrganizationAdminPolicy:
    return IsOrganizationAdminPolicy(abac_service)


def _make_command(command_class: type, objs: list[Mock]) -> Any:
    # Skip validation so lightweight stand-ins can be used as case policies
    return command_class.model_construct(
        user=model.User(roles={"role"}, organization_id=uuid4()),
        objs=objs,
        operation=CrudOperation.CREATE_SOME,
    )


@pytest.mark.parametrize(
    "command_class",
    ORGANIZATION_CASE_POLICY_COMMANDS + USER_CASE_POLICY_COMMANDS,
)
def test_init_registers_case_policy_handlers(
    policy: IsOrganizationAdminPolicy, command_class: type
) -> None:
    assert command_class in policy._get_organization_ids_handler_map


def test_init_keeps_common_handlers(policy: IsOrganizationAdminPolicy) -> None:
    assert common_command.SiteCrudCommand in policy._get_organization_ids_handler_map
    assert common_command.ContactCrudCommand in policy._get_organization_ids_handler_map


@pytest.mark.parametrize("command_class", ORGANIZATION_CASE_POLICY_COMMANDS)
def test_organization_case_policy_returns_policy_organization_ids(
    policy: IsOrganizationAdminPolicy, command_class: type
) -> None:
    org_1, org_2 = uuid4(), uuid4()
    objs = [
        Mock(organization_id=org_1),
        Mock(organization_id=org_2),
        Mock(organization_id=org_1),
    ]
    cmd = _make_command(command_class, objs)

    assert policy.retrieve_organization_ids(cmd) == {org_1, org_2}


@pytest.mark.parametrize("command_class", ORGANIZATION_CASE_POLICY_COMMANDS)
def test_organization_case_policy_empty_returns_empty_set(
    policy: IsOrganizationAdminPolicy, command_class: type
) -> None:
    cmd = _make_command(command_class, [])

    assert policy.retrieve_organization_ids(cmd) == set()


@pytest.mark.parametrize("command_class", USER_CASE_POLICY_COMMANDS)
def test_user_case_policy_resolves_organizations_through_users(
    policy: IsOrganizationAdminPolicy, abac_service: Mock, command_class: type
) -> None:
    user_1, user_2 = uuid4(), uuid4()
    org_1, org_2 = uuid4(), uuid4()
    objs = [Mock(user_id=user_1), Mock(user_id=user_2), Mock(user_id=user_1)]
    cmd = _make_command(command_class, objs)
    abac_service.app.handle.return_value = [
        Mock(organization_id=org_1),
        Mock(organization_id=org_2),
        Mock(organization_id=org_1),
    ]

    assert policy.retrieve_organization_ids(cmd) == {org_1, org_2}

    abac_service.app.handle.assert_called_once()
    user_cmd = abac_service.app.handle.call_args.args[0]
    assert isinstance(user_cmd, command.UserCrudCommand)
    assert user_cmd.user is cmd.user
    assert user_cmd.operation == CrudOperation.READ_SOME
    assert user_cmd.objs is None
    assert sorted(user_cmd.obj_ids) == sorted([user_1, user_2])


@pytest.mark.parametrize("command_class", USER_CASE_POLICY_COMMANDS)
def test_user_case_policy_without_policies_returns_empty_set(
    policy: IsOrganizationAdminPolicy, abac_service: Mock, command_class: type
) -> None:
    cmd = _make_command(command_class, [])
    abac_service.app.handle.return_value = []

    result: set[UUID] = policy.retrieve_organization_ids(cmd)

    assert result == set()
    assert abac_service.app.handle.call_args.args[0].obj_ids == []
