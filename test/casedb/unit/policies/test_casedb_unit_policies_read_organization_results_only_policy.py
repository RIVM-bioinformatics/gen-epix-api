"""Test casedb organization-scoped read policy registration."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.casedb.domain import command
from gen_epix.casedb.policies import read_organization_results_only_policy as module
from gen_epix.casedb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)
from gen_epix.commondb.policies import (
    ReadOrganizationResultsOnlyPolicy as CommonReadOrganizationResultsOnlyPolicy,
)

ORGANIZATION_COMMAND_CLASSES = {
    command.OrganizationAccessCasePolicyCrudCommand,
    command.OrganizationShareCasePolicyCrudCommand,
}
USER_COMMAND_CLASSES = {
    command.UserAccessCasePolicyCrudCommand,
    command.UserShareCasePolicyCrudCommand,
}


@pytest.fixture
def abac_service() -> Mock:
    """Provide an ABAC service mock whose mapped classes are identity."""
    service = Mock()
    service.app.impl.get_mapped_class.side_effect = lambda cls: cls
    return service


@pytest.fixture
def policy(abac_service: Mock) -> ReadOrganizationResultsOnlyPolicy:
    """Provide the casedb policy under test."""
    return ReadOrganizationResultsOnlyPolicy(abac_service)


@pytest.fixture
def common_policy(abac_service: Mock) -> CommonReadOrganizationResultsOnlyPolicy:
    """Provide the unextended commondb policy as a baseline."""
    return CommonReadOrganizationResultsOnlyPolicy(abac_service)


class TestInit:
    """Test constructor behavior."""

    def test_extends_common_policy(self, policy: ReadOrganizationResultsOnlyPolicy):
        """Verify inheritance from the commondb policy."""
        assert isinstance(policy, CommonReadOrganizationResultsOnlyPolicy)
        assert module.CommonReadOrganizationResultsOnlyPolicy is (
            CommonReadOrganizationResultsOnlyPolicy
        )

    def test_stores_abac_service_and_kwargs(self, abac_service: Mock):
        """Verify the service and extra kwargs reach the base policy."""
        policy = ReadOrganizationResultsOnlyPolicy(abac_service, foo="bar")

        assert policy.abac_service is abac_service
        assert policy.props == {"foo": "bar"}

    def test_registers_case_policy_organization_commands(
        self,
        policy: ReadOrganizationResultsOnlyPolicy,
        common_policy: CommonReadOrganizationResultsOnlyPolicy,
    ):
        """Verify case-policy organization commands extend the common set."""
        assert (
            policy.has_organization_id_attr_command_classes
            == common_policy.has_organization_id_attr_command_classes
            | ORGANIZATION_COMMAND_CLASSES
        )

    def test_registers_case_policy_user_commands(
        self,
        policy: ReadOrganizationResultsOnlyPolicy,
        common_policy: CommonReadOrganizationResultsOnlyPolicy,
    ):
        """Verify case-policy user commands are added to an empty common set."""
        assert common_policy.has_user_id_attr_command_classes == set()
        assert policy.has_user_id_attr_command_classes == USER_COMMAND_CLASSES

    def test_instances_do_not_share_command_sets(self, abac_service: Mock):
        """Verify mutating one instance's sets does not affect another."""
        first = ReadOrganizationResultsOnlyPolicy(abac_service)
        second = ReadOrganizationResultsOnlyPolicy(abac_service)

        first.has_user_id_attr_command_classes.clear()

        assert second.has_user_id_attr_command_classes == USER_COMMAND_CLASSES
