"""Unit tests for the SeqDB organization-results policy adapter."""

from test.util.mock_compat import Mock

from gen_epix.commondb.domain import command
from gen_epix.commondb.policies import (
    ReadOrganizationResultsOnlyPolicy as CommonReadOrganizationResultsOnlyPolicy,
)
from gen_epix.seqdb.policies.read_organization_results_only_policy import (
    ReadOrganizationResultsOnlyPolicy,
)


def test_is_subclass_of_common_policy() -> None:
    """Reuse the shared organization-results policy contract."""
    assert issubclass(
        ReadOrganizationResultsOnlyPolicy, CommonReadOrganizationResultsOnlyPolicy
    )


def test_init_preserves_common_mappings_and_configuration() -> None:
    """Retain shared command mappings and forward policy configuration."""
    abac_service = Mock()

    policy = ReadOrganizationResultsOnlyPolicy(abac_service, foo="bar")

    assert policy.abac_service is abac_service
    assert policy.props == {"foo": "bar"}
    assert policy.has_organization_id_attr_command_classes == {
        command.UserCrudCommand,
        command.OrganizationAdminPolicyCrudCommand,
        command.UserInvitationCrudCommand,
        command.OrganizationIdentifierIssuerLinkCrudCommand,
        command.OrganizationSetOrganizationUpdateAssociationCommand,
        command.OrganizationIdentifierIssuerUpdateAssociationCommand,
    }
    assert policy.has_user_id_attr_command_classes == set()
