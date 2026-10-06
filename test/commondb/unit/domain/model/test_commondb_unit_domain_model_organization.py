"""Validate organization foreign-key descriptions in CommonDB schemas."""

import pytest

from gen_epix.commondb.domain.model.organization import (
    OrganizationIdentifierIssuerLink,
    OrganizationSetMember,
    Site,
)

ORGANIZATION_ID_DESCRIPTION = "The ID of the organization. FOREIGN KEY"


@pytest.mark.parametrize(
    ("model_class", "field_name"),
    [
        (OrganizationIdentifierIssuerLink, "organization_id"),
        (OrganizationSetMember, "organization_id"),
        (Site, "organization_id"),
    ],
)
def test_organization_foreign_key_schema_description(
    model_class: type, field_name: str
) -> None:
    """Keep organization links described as foreign keys in the schema."""
    assert (
        model_class.model_fields[field_name].description == ORGANIZATION_ID_DESCRIPTION
    )
