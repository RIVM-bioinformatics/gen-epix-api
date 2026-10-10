"""Test the OmopDB organization-administrator policy wrapper."""

from types import SimpleNamespace

from gen_epix.commondb.policies import (
    IsOrganizationAdminPolicy as CommonIsOrganizationAdminPolicy,
)
from gen_epix.omopdb.policies.is_organization_admin_policy import (
    IsOrganizationAdminPolicy,
)


def test_is_subclass_of_common_policy() -> None:
    """Inherit the shared organization-administrator policy contract."""
    assert issubclass(IsOrganizationAdminPolicy, CommonIsOrganizationAdminPolicy)


def test_init_forwards_service_and_configuration() -> None:
    """Preserve the shared ABAC service and optional policy properties."""
    app_impl = SimpleNamespace(
        get_mapped_class=lambda model_class: model_class,
        role_map={},
        role_set_map={},
    )
    abac_service = SimpleNamespace(app=SimpleNamespace(impl=app_impl))

    policy = IsOrganizationAdminPolicy(abac_service, foo="bar")

    assert policy.abac_service is abac_service
    assert policy.props == {"foo": "bar"}
