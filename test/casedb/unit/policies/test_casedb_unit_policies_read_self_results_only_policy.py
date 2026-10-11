from test.util.mock_compat import Mock

import pytest

from gen_epix.casedb.domain import command
from gen_epix.casedb.policies.read_self_results_only_policy import (
    ReadSelfResultsOnlyPolicy,
)
from gen_epix.commondb.domain import command as common_command
from gen_epix.commondb.policies import (
    ReadSelfResultsOnlyPolicy as CommonReadSelfResultsOnlyPolicy,
)


@pytest.fixture
def abac_service() -> Mock:
    return Mock()


def test_is_subclass_of_common_policy() -> None:
    assert issubclass(ReadSelfResultsOnlyPolicy, CommonReadSelfResultsOnlyPolicy)


def test_init_registers_casedb_and_common_id_attrs(abac_service: Mock) -> None:
    policy = ReadSelfResultsOnlyPolicy(abac_service)

    assert policy.id_attr_by_command_class == {
        common_command.UserCrudCommand: "id",
        common_command.UserInvitationCrudCommand: "invited_by_user_id",
        command.UserAccessCasePolicyCrudCommand: "user_id",
        command.UserShareCasePolicyCrudCommand: "user_id",
    }


def test_init_keeps_service_role_maps_and_props(abac_service: Mock) -> None:
    policy = ReadSelfResultsOnlyPolicy(abac_service, foo="bar")

    assert policy.abac_service is abac_service
    assert policy.role_map is abac_service.app.impl.role_map
    assert policy.role_set_map is abac_service.app.impl.role_set_map
    assert policy.props == {"foo": "bar"}


def test_init_does_not_share_id_attr_mapping_between_instances(
    abac_service: Mock,
) -> None:
    first = ReadSelfResultsOnlyPolicy(abac_service)
    second = ReadSelfResultsOnlyPolicy(abac_service)

    first.id_attr_by_command_class.clear()

    assert len(second.id_attr_by_command_class) == 4
