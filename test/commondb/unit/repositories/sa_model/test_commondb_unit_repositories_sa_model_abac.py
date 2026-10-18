from sqlalchemy import UniqueConstraint

from gen_epix.commondb.domain import model as domain_model
from gen_epix.commondb.repositories.sa_model.abac import (
    OrganizationAdminPolicy,
)


def test_organization_admin_policy_table_matches_domain_model() -> None:
    policy_model = domain_model.OrganizationAdminPolicy
    columns = OrganizationAdminPolicy.__table__.columns
    relationship_field_names = set(policy_model.ENTITY.get_relationship_field_names())

    assert OrganizationAdminPolicy.__tablename__ == policy_model.ENTITY.table_name
    for field_name, field_info in policy_model.model_fields.items():
        if field_name in relationship_field_names:
            continue
        assert field_name in columns
        expected_nullable = not field_info.is_required()
        if field_name in {"id", "created_at", "modified_at"}:
            expected_nullable = False
        assert columns[field_name].nullable is expected_nullable

    actual_unique_keys = {
        tuple(column.name for column in constraint.columns)
        for constraint in OrganizationAdminPolicy.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    expected_unique_keys = {
        tuple(field_names) for field_names in policy_model.ENTITY.get_keys_field_names()
    }
    assert expected_unique_keys <= actual_unique_keys
