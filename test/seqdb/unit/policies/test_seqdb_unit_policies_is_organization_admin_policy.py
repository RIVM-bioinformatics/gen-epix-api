"""Validate seqdb organization-admin policy construction."""

from test.util.mock_compat import Mock

from gen_epix.commondb.domain import model as common_model
from gen_epix.commondb.domain.policy import BaseIsOrganizationAdminPolicy
from gen_epix.seqdb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy,
)


def test_policy_forwards_abac_service_and_configuration() -> None:
    """Initialize shared role mappings and resolvers from the seqdb app."""
    role_map = {"role": "seqdb-role"}
    role_set_map = {"role-set": frozenset({"seqdb-role"})}
    app_impl = Mock(
        get_mapped_class=Mock(return_value=common_model.User),
        role_map=role_map,
        role_set_map=role_set_map,
    )
    abac_service = Mock(app=Mock(impl=app_impl))

    policy = IsOrganizationAdminPolicy(abac_service, feature="seqdb")

    assert policy.abac_service is abac_service
    assert policy.props == {"feature": "seqdb"}
    assert policy.user_class is common_model.User
    assert policy.role_map is role_map
    assert policy.role_set_map is role_set_map
    assert isinstance(policy, BaseIsOrganizationAdminPolicy)
