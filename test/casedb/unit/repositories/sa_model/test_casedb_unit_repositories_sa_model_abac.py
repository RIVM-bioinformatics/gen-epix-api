import pytest

import gen_epix.casedb.repositories.sa_model.abac as abac


@pytest.mark.parametrize(
    (
        "mapped_model",
        "table_name",
        "column_names",
        "unique_key_names",
        "nullable_names",
    ),
    [
        (
            abac.OrganizationAccessCasePolicy,
            "organization_access_case_policy",
            {
                "id",
                "created_at",
                "modified_at",
                "modified_by",
                "organization_id",
                "data_collection_id",
                "case_type_set_id",
                "is_active",
                "is_private",
                "add_case",
                "remove_case",
                "add_case_set",
                "remove_case_set",
                "read_col_set_id",
                "write_col_set_id",
                "read_case_set",
                "write_case_set",
            },
            {"organization_id", "data_collection_id"},
            {"modified_by", "read_col_set_id", "write_col_set_id"},
        ),
        (
            abac.UserAccessCasePolicy,
            "user_access_case_policy",
            {
                "id",
                "created_at",
                "modified_at",
                "modified_by",
                "user_id",
                "data_collection_id",
                "case_type_set_id",
                "is_active",
                "add_case",
                "remove_case",
                "add_case_set",
                "remove_case_set",
                "read_col_set_id",
                "write_col_set_id",
                "read_case_set",
                "write_case_set",
            },
            {"user_id", "data_collection_id"},
            {"modified_by", "read_col_set_id", "write_col_set_id"},
        ),
        (
            abac.OrganizationShareCasePolicy,
            "organization_share_case_policy",
            {
                "id",
                "created_at",
                "modified_at",
                "modified_by",
                "organization_id",
                "data_collection_id",
                "case_type_set_id",
                "from_data_collection_id",
                "is_active",
                "add_case",
                "remove_case",
                "add_case_set",
                "remove_case_set",
            },
            {"organization_id", "data_collection_id", "from_data_collection_id"},
            {"modified_by"},
        ),
        (
            abac.UserShareCasePolicy,
            "user_share_case_policy",
            {
                "id",
                "created_at",
                "modified_at",
                "modified_by",
                "user_id",
                "data_collection_id",
                "case_type_set_id",
                "from_data_collection_id",
                "is_active",
                "add_case",
                "remove_case",
                "add_case_set",
                "remove_case_set",
            },
            {"user_id", "data_collection_id", "from_data_collection_id"},
            {"modified_by"},
        ),
    ],
    ids=["organization-access", "user-access", "organization-share", "user-share"],
)
def test_abac_policy_maps_expected_table_columns_and_keys(
    mapped_model, table_name, column_names, unique_key_names, nullable_names
):
    table = mapped_model.__table__

    assert table.name == table_name
    assert set(table.columns.keys()) == column_names
    assert set(table.primary_key.columns.keys()) == {"id"}
    assert any(
        set(constraint.columns.keys()) == unique_key_names
        for constraint in table.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    )
    assert {
        column.name for column in table.columns if column.nullable
    } == nullable_names
