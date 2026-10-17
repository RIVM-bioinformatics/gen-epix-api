"""Validate the organization-admin policy model contract."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from gen_epix.commondb.domain.model.abac import OrganizationAdminPolicy


@pytest.mark.parametrize("is_active", [True, False])
def test_organization_admin_policy_accepts_required_fields(is_active: bool) -> None:
    organization_id = uuid4()
    user_id = uuid4()

    policy = OrganizationAdminPolicy(
        organization_id=organization_id,
        user_id=user_id,
        is_active=is_active,
    )

    assert policy.organization_id == organization_id
    assert policy.user_id == user_id
    assert policy.is_active is is_active
    assert policy.organization is None
    assert policy.user is None


@pytest.mark.parametrize("missing_field", ["organization_id", "user_id", "is_active"])
def test_organization_admin_policy_requires_foreign_keys_and_active_state(
    missing_field: str,
) -> None:
    values = {
        "organization_id": uuid4(),
        "user_id": uuid4(),
        "is_active": True,
    }
    del values[missing_field]

    with pytest.raises(ValidationError):
        OrganizationAdminPolicy(**values)


def test_organization_admin_policy_field_descriptions() -> None:
    fields = OrganizationAdminPolicy.model_fields

    assert fields["organization_id"].description == (
        "The ID of the organization. FOREIGN KEY"
    )
    assert fields["user_id"].description == "The ID of the user. FOREIGN KEY"
    assert fields["is_active"].description == (
        "Whether the user is an admin for the organization"
    )
