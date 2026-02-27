from dataclasses import dataclass
from test.casedb.casedb_test_client import CasedbTestClient as Env

import pytest

from gen_epix.casedb.domain import enum as casedb_enum


VERBOSE = True  # Set to True to enable detailed print statements during setup for debugging purposes;


# Test data setup for case type column access edge cases:
# user 1
# org_user1_1 -> org1 -> oscp1 (from dc1, to dc2) -> oacp1 (to dc1) -> ctcs1 -> {ctc1, ctc2}
# org1 -> oacp2 (to dc3) -> ctcs2 -> {ctc2, ctc3}
# user 2
# org_user_1_2 -> org1 # has the same org-level policies as org_user1_1 plus user-level policies
# so should have the same access to case type col sets and cols as org_user1_1
# additionally:
# org_user1_2 -> uscp1 (from dc1, to dc2) -> oacp1 (to dc1) -> ctcs1 -> {ctc1, ctc2}
# org_user1_2 -> uacp2 (to dc3) -> ctcs2 -> {ctc2, ctc3}
# ctc1 -> col1 -> dim1, ctc2 -> col2 -> dim2, ctc3 -> col3 -> dim3, etc
#
# additional negative controls (not linked):
# ctc4, col4, dim4, ctcs3 (ctc4 only) — not linked to any policies, so should be inaccessible to all users
#
# Abbreviations:
#   oacp  = OrgAccessCasePolicy   (name format: {prefix}{org_num}_{dc_num})
#   oscp  = OrgShareCasePolicy    (name format: {prefix}{org_num}_{to_dc_num}_{from_dc_num})
#   uacp  = UserAccessCasePolicy
#   uscp  = UserShareCasePolicy
#   ctcs  = CaseTypeColSet
#   cts   = CaseTypeSet
#   ctc   = CaseTypeCol           (code: case_type_col{ct}_{dim}_{occ}_{col_rank})
#   ctd   = CaseTypeDim           (code: case_type_dim{ct}_{dim}_{occ})
#   col   = Col                   (code: col{dim}_{rank})
#   dim   = Dim
#   dc    = DataCollection


@dataclass
class CaseColSpec:
    user_name: str
    description: str
    expected_case_type_col_sets: list[str]
    expected_case_type_cols: list[str]
    expected_cols: list[str]
    expected_dims: list[str]


CASE_COL_SPECS = [
    CaseColSpec(
        user_name="org_user1_1",
        description="User with org-level policies granting access to ctcs1 and ctcs2, but no user-level policies",
        expected_case_type_col_sets=["ctcs1", "ctcs2"],
        expected_case_type_cols=[
            "case_type_col1_1_1_1",
            "case_type_col2_2_1_1",
            "case_type_col3_3_1_1",
        ],
        expected_cols=["col1_1", "col2_1", "col3_1"],
        expected_dims=["dim1", "dim2", "dim3"],
    ),
    CaseColSpec(
        user_name="org_user1_2",
        description="User with the same org-level policies as org_user1_1 plus user-level policies that mirror the org-level policies",
        expected_case_type_col_sets=["ctcs1", "ctcs2"],
        expected_case_type_cols=[
            "case_type_col1_1_1_1",
            "case_type_col2_2_1_1",
            "case_type_col3_3_1_1",
        ],
        expected_cols=["col1_1", "col2_1", "col3_1"],
        expected_dims=["dim1", "dim2", "dim3"],
    ),
]


# setup_case_col_data depends on setup_test_users_and_organizations to ensure that users and
# organizations are created before policies reference them.
# The parameter is intentionally unused in the body — its presence enforces fixture ordering.
@pytest.fixture(scope="module")
def setup_case_col_data(
    env: Env, setup_test_users_and_organizations: None  # noqa: ARG001
) -> None:  # noqa: ARG001

    if VERBOSE:
        print("\n--- Setting up case type column set data for edge case tests ---")

    root_user = env.get_root_user()

    # --- PREREQUISITES ---
    env.create_disease(root_user, "disease_col_1")
    env.create_etiological_agent(root_user, "etiological_agent_col_1")
    env.create_case_type_set_category(root_user, "category_col_1", 0)

    # --- CASE TYPES ---
    # Names must match the lookup in create_case_type_dim: "case_type{ct_idx}"
    # case_type4 is created here for the negative control ctc4; it is not linked to any policy.
    for i in range(1, 5):
        env.create_case_type(
            root_user, f"case_type{i}", "disease_col_1", "etiological_agent_col_1"
        )

    # --- CASE TYPE SETS ---
    # col_case_type_set12: case_type1 + case_type2 — referenced by oacp1 and oscp1
    # col_case_type_set23: case_type2 + case_type3 — referenced by oacp2
    env.create_case_type_set(
        root_user, "col_case_type_set12", {"case_type1", "case_type2"}, "category_col_1"
    )
    env.create_case_type_set(
        root_user, "col_case_type_set23", {"case_type2", "case_type3"}, "category_col_1"
    )

    # --- DIMS (one per ctc) ---
    env.create_dim(root_user, "dim1", casedb_enum.DimType.TEXT)
    env.create_dim(root_user, "dim2", casedb_enum.DimType.TEXT)
    env.create_dim(root_user, "dim3", casedb_enum.DimType.TEXT)

    # --- COLS (one per ctc, each in its own dim) ---
    # code: col{dim_idx}_{rank}
    env.create_col(root_user, "col1_1", casedb_enum.ColType.TEXT)
    env.create_col(root_user, "col2_1", casedb_enum.ColType.TEXT)
    env.create_col(root_user, "col3_1", casedb_enum.ColType.TEXT)

    # --- CASE TYPE DIMS (one per case type, each linked to its own dim) ---
    # code: case_type_dim{ct_idx}_{dim_idx}_{occ_idx}
    env.create_case_type_dim(root_user, "case_type_dim1_1_1")
    env.create_case_type_dim(root_user, "case_type_dim2_2_1")
    env.create_case_type_dim(root_user, "case_type_dim3_3_1")

    # --- CASE TYPE COLS ---
    # code: case_type_col{ct_idx}_{dim_idx}_{occ_idx}_{col_rank}
    # ctc1: case_type1 + case_type_dim1_1_1 + col1_1
    # ctc2: case_type2 + case_type_dim2_2_1 + col2_1
    # ctc3: case_type3 + case_type_dim3_3_1 + col3_1
    env.create_case_type_col(root_user, "case_type_col1_1_1_1")
    env.create_case_type_col(root_user, "case_type_col2_2_1_1")
    env.create_case_type_col(root_user, "case_type_col3_3_1_1")

    if VERBOSE:
        print(
            "Created dim1/dim2/dim3, cols col1_1/col2_1/col3_1, case_type_dims, and case_type_cols ctc1/ctc2/ctc3"
        )

    # --- CASE TYPE COL SETS ---
    # ctcs1 = {ctc1, ctc2}, ctcs2 = {ctc2, ctc3}
    # Note: ctc2 intentionally appears in both sets to test multi-set col access.
    env.create_case_type_col_set(
        root_user, "ctcs1", {"case_type_col1_1_1_1", "case_type_col2_2_1_1"}
    )
    env.create_case_type_col_set(
        root_user, "ctcs2", {"case_type_col2_2_1_1", "case_type_col3_3_1_1"}
    )

    if VERBOSE:
        print("Created col sets ctcs1={ctc1,ctc2} and ctcs2={ctc2,ctc3}")

    # --- NEGATIVE CONTROLS (not linked to any policy) ---
    # ctc4 -> col4 -> dim4, grouped in ctcs3 — must be inaccessible to all org users.
    env.create_dim(root_user, "dim4", casedb_enum.DimType.TEXT)
    env.create_col(root_user, "col4_1", casedb_enum.ColType.TEXT)
    env.create_case_type_dim(root_user, "case_type_dim4_4_1")
    env.create_case_type_col(root_user, "case_type_col4_4_1_1")
    env.create_case_type_col_set(root_user, "ctcs3", {"case_type_col4_4_1_1"})

    if VERBOSE:
        print("Created negative controls: dim4, col4_1, ctc4, ctcs3 (unlinked)")

    # --- DATA COLLECTIONS ---
    # data_collection1: target for oacp1 and source for oscp1
    # data_collection2: share destination for oscp1
    # data_collection3: target for oacp2
    env.create_data_collection(root_user, "data_collection1")
    env.create_data_collection(root_user, "data_collection2")
    env.create_data_collection(root_user, "data_collection3")

    # --- ORG ACCESS POLICY 1 (oacp1): org1 → dc1, read ctcs1 ---
    # Name format: {prefix}{org_num}_{dc_num}
    env.create_organization_access_case_policy(
        root_user,
        "org_access_col_policy1_1",
        "col_case_type_set12",
        read_case_type_col_set="ctcs1",
    )

    # --- ORG SHARE POLICY (oscp1): org1 shares from dc1 to dc2 ---
    # Name format: {prefix}{org_num}_{to_dc_num}_{from_dc_num}
    env.create_organization_share_case_policy(
        root_user,
        "org_share_col_policy1_2_1",
        "col_case_type_set12",
    )

    # --- ORG ACCESS POLICY 2 (oacp2): org1 → dc3, read ctcs2 ---
    env.create_organization_access_case_policy(
        root_user,
        "org_access_col_policy1_3",
        "col_case_type_set23",
        read_case_type_col_set="ctcs2",
    )

    if VERBOSE:
        print(
            "Created policies: oacp1 (org1→dc1/ctcs1), oscp1 (org1: dc1→dc2), oacp2 (org1→dc3/ctcs2)"
        )

    # --- USER ACCESS POLICY 1 (uacp1): org_user1_2 → dc1, read ctcs1 — mirrors oacp1 ---
    env.create_user_access_case_policy(
        root_user,
        "org_user1_2",
        "data_collection1",
        "col_case_type_set12",
        read_case_type_col_set="ctcs1",
    )

    # --- USER SHARE POLICY (uscp1): org_user1_2 shares from dc1 to dc2 — mirrors oscp1 ---
    env.create_user_share_case_policy(
        root_user,
        "org_user1_2",
        data_collection="data_collection2",
        from_data_collection="data_collection1",
        case_type_set="col_case_type_set12",
    )

    # --- USER ACCESS POLICY 2 (uacp2): org_user1_2 → dc3, read ctcs2 — mirrors oacp2 ---
    env.create_user_access_case_policy(
        root_user,
        "org_user1_2",
        "data_collection3",
        "col_case_type_set23",
        read_case_type_col_set="ctcs2",
    )

    if VERBOSE:
        print(
            "Created user policies: uacp1 (org_user1_2→dc1/ctcs1), uscp1 (org_user1_2: dc1→dc2), uacp2 (org_user1_2→dc3/ctcs2)"
        )
