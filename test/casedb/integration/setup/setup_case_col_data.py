from dataclasses import dataclass
from test.casedb.casedb_test_client import CasedbTestClient as Env

import pytest

from gen_epix.casedb.domain import enum as casedb_enum


VERBOSE = True  # Set to True to enable detailed print statements during setup for debugging purposes;


# org_user1_1 -> org1 -> oscp1 (from dc1, to dc2) -> oacp1 (to dc1) -> ctcs1 -> {ctc1, ctc2}
# ctc1 -> col1 -> dim1 (identical for all other ctc's)
# org1 -> oacp2 (to dc3) -> ctcs2 -> {ctc2, ctc3}
#
# Abbreviations:
#   oacp  = OrgAccessCasePolicy
#   oscp  = OrgShareCasePolicy
#   ctcs  = CaseTypeColSet
#   ctc   = CaseTypeCol  (code: case_type_col{ct}_{dim}_{occ}_{col_rank})
#   col   = Col          (code: col{dim}_{rank})
#   dim   = Dim
#   dc    = DataCollection


@dataclass
class CaseColSpec:
    user_name: str
    org_name: str
    expected_case_type_col_sets: list[str]
    expected_case_type_cols: list[str]


CASE_COL_SPECS = [
    CaseColSpec(
        user_name="org_user1_1",
        org_name="org1",
        expected_case_type_col_sets=["ctcs1", "ctcs2"],
        expected_case_type_cols=[
            "case_type_col1_1_1_1",
            "case_type_col2_1_1_2",
            "case_type_col3_1_1_3",
        ],
    ),
    # Additional specs can be added here for more users/orgs and their expected access to case type column sets.
]


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
    for i in range(1, 4):
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

    # --- DIM (shared by all ctcs) ---
    env.create_dim(root_user, "dim1", casedb_enum.DimType.TEXT)

    # --- COLS (one per ctc, all in dim1) ---
    # code: col{dim_idx}_{rank}
    env.create_col(root_user, "col1_1", casedb_enum.ColType.TEXT)
    env.create_col(root_user, "col1_2", casedb_enum.ColType.TEXT)
    env.create_col(root_user, "col1_3", casedb_enum.ColType.TEXT)

    # --- CASE TYPE DIMS (one per case type, all linked to dim1) ---
    # code: case_type_dim{ct_idx}_{dim_idx}_{occ_idx}
    env.create_case_type_dim(root_user, "case_type_dim1_1_1")
    env.create_case_type_dim(root_user, "case_type_dim2_1_1")
    env.create_case_type_dim(root_user, "case_type_dim3_1_1")

    # --- CASE TYPE COLS ---
    # code: case_type_col{ct_idx}_{dim_idx}_{occ_idx}_{col_rank}
    # ctc1: case_type1 + case_type_dim1_1_1 + col1_1
    # ctc2: case_type2 + case_type_dim2_1_1 + col1_2
    # ctc3: case_type3 + case_type_dim3_1_1 + col1_3
    env.create_case_type_col(root_user, "case_type_col1_1_1_1")
    env.create_case_type_col(root_user, "case_type_col2_1_1_2")
    env.create_case_type_col(root_user, "case_type_col3_1_1_3")

    if VERBOSE:
        print(
            "Created dim1, cols col1_1/col1_2/col1_3, case_type_dims, and case_type_cols ctc1/ctc2/ctc3"
        )

    # --- CASE TYPE COL SETS ---
    # ctcs1 = {ctc1, ctc2}, ctcs2 = {ctc2, ctc3}
    # Note: ctc2 intentionally appears in both sets to test multi-set col access.
    env.create_case_type_col_set(
        root_user, "ctcs1", {"case_type_col1_1_1_1", "case_type_col2_1_1_2"}
    )
    env.create_case_type_col_set(
        root_user, "ctcs2", {"case_type_col2_1_1_2", "case_type_col3_1_1_3"}
    )

    if VERBOSE:
        print("Created col sets ctcs1={ctc1,ctc2} and ctcs2={ctc2,ctc3}")

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
