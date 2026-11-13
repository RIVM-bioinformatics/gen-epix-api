"""Validate constructor contracts shared by commondb ABAC policy bases."""

from inspect import isabstract
from test.util.mock_compat import Mock

import pytest

from gen_epix.commondb.domain.policy.abac import (
    BaseAbacPolicy,
    BaseIsOrganizationAdminPolicy,
    BaseReadOrganizationResultsOnlyPolicy,
    BaseReadSelfResultsOnlyPolicy,
    BaseReadUserPolicy,
    BaseUpdateUserPolicy,
)

ABAC_POLICY_CLASSES = (
    BaseAbacPolicy,
    BaseReadOrganizationResultsOnlyPolicy,
    BaseReadSelfResultsOnlyPolicy,
    BaseReadUserPolicy,
    BaseUpdateUserPolicy,
)


@pytest.mark.parametrize(
    "policy_class",
    ABAC_POLICY_CLASSES,
    ids=lambda policy_class: policy_class.__name__,
)
@pytest.mark.parametrize(
    "kwargs, expected_props",
    [
        pytest.param({}, {}, id="no-properties"),
        pytest.param({"option": None}, {"option": None}, id="none-property"),
        pytest.param(
            {"enabled": True, "scopes": ("organization", "self")},
            {"enabled": True, "scopes": ("organization", "self")},
            id="multiple-properties",
        ),
    ],
)
def test_abac_policy_stores_service_and_properties(
    policy_class: type[BaseAbacPolicy],
    kwargs: dict[str, object],
    expected_props: dict[str, object],
) -> None:
    """Store the ABAC service and supplied properties on each policy."""
    abac_service = Mock()

    policy = policy_class(abac_service, **kwargs)

    assert policy.abac_service is abac_service
    assert policy.props == expected_props


def test_abac_policy_properties_are_instance_local() -> None:
    """Keep separately constructed policy properties independent."""
    abac_service = Mock()

    first_policy = BaseAbacPolicy(abac_service, enabled=True)
    second_policy = BaseAbacPolicy(abac_service, enabled=False)

    first_policy.props["local"] = True

    assert second_policy.props == {"enabled": False}


def test_organization_admin_policy_remains_abstract() -> None:
    """Require concrete policies to implement organization-scope resolution."""
    assert isabstract(BaseIsOrganizationAdminPolicy)
