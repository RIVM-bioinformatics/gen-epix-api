"""Verify the organization scope configured by the OmopDB read policy."""

from test.util.mock_compat import MagicMock

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.omopdb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)


def test_policy_retains_organization_scoped_command_configuration():
    """Keep command scope configuration intact and isolated per instance."""
    policy = ReadOrganizationResultsOnlyPolicy(MagicMock(spec=BaseAbacService))
    other_policy = ReadOrganizationResultsOnlyPolicy(MagicMock(spec=BaseAbacService))

    assert policy.has_organization_id_attr_command_classes == {
        command.UserCrudCommand,
        command.OrganizationAdminPolicyCrudCommand,
        command.UserInvitationCrudCommand,
        command.OrganizationIdentifierIssuerLinkCrudCommand,
        command.OrganizationSetOrganizationUpdateAssociationCommand,
        command.OrganizationIdentifierIssuerUpdateAssociationCommand,
    }
    assert policy.has_user_id_attr_command_classes == set()
    assert (
        policy.has_organization_id_attr_command_classes
        is not other_policy.has_organization_id_attr_command_classes
    )
