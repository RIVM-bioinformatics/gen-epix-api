"""
This module defines the setup_case_type_data fixture, which creates reference data
(diseases, etiological agents, CaseTypes, CaseTypeSets, ColSets,
and all four policy types) for tests.
"""

import re
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.data_access.setup.define_edge_cases_reference import (
    CASE_TYPE_SETS,
    COL_SETS,
    EDGE_CASES,
)

import pytest

from gen_epix.casedb.domain import enum as casedb_enum
from gen_epix.casedb.domain import model

VERBOSE = False  # Set to True to enable detailed print statements during setup for debugging purposes;


# setup_case_type_data depends on setup_test_users_and_organizations to ensure that users and
# organizations are created before policies reference them.
# The parameter is intentionally unused in the body — its presence enforces fixture ordering.
@pytest.fixture(scope="module")
def setup_case_data_reference(
    env: Env, setup_test_users_and_organizations_reference: None  # noqa: ARG001
) -> None:  # noqa: ARG001
    """
    Create reference data (diseases, etiological agents, CaseTypes, CaseTypeSets, ColSets, and all four policy types) for tests.
    Objects are automatically stored in env.db by create methods.

    Policy creation is driven by EDGE_CASES:
    - Org access/share policies: one per unique (org, case_type_set) from org_access_policy_sets/org_share_policy_sets.
    - User access/share policies: one per (user, case_type_set) entry in user_access_policy_sets/user_share_policy_sets.
    - For ColSets: same logic, but with ColSet names (e.g. colset1) and ColSet objects.

    Data collections:
    - data_collection1: the target collection referenced by all policies.
    - data_collection2: the source collection for share policies (from_data_collection).

    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")

    # Create CaseTypes using pre-created reference data from env.db.
    env.create_case_type_set_category(root_user, "category_1", 0)

    # --- CaseTypes & CaseTypeSets ---
    # Use CASE_TYPE_SETS from define_edge_cases.py
    created_case_types = set()
    for case_type_set_name, case_type_names in CASE_TYPE_SETS.items():
        # Create all CaseTypes for this set (if not already created)
        for case_type_name in case_type_names:
            if case_type_name not in created_case_types:
                case_type = env.create_case_type(
                    root_user, case_type_name, "disease_1", "etiological_agent_1"
                )
                assert (
                    case_type is not None
                ), f"Failed to create CaseType '{case_type_name}'"
                created_case_types.add(case_type_name)
        # Create the CaseTypeSet with all its CaseTypes
        env.create_case_type_set(
            root_user, case_type_set_name, set(case_type_names), "category_1"
        )

    # --- Cols & ColSets ---
    # Use COL_SETS from define_edge_cases.py.
    # RefDims, RefCols, Dims, and Cols may be shared across ColSets
    # (e.g. colset3 reuses cols from colset1 and colset2) — create each only once.
    ref_col_ids_by_set: dict[str, list[str]] = {}
    created_ref_dims: set[str] = set()
    created_ref_cols: set[str] = set()
    created_dims: set[str] = set()
    created_cols: set[str] = set()
    for col_set_name, col_codes in sorted(COL_SETS.items()):
        col_objs: set[str] = set()
        ref_col_codes: list[str] = []
        for col_code in col_codes:
            if col_code not in created_cols:
                # Parse indices from naming convention: col{ct}_{ref_dim}_{occ}_{col_rank}
                m = re.match(
                    r"^(.*?)(?P<ct>\d+)_(?P<ref_dim>\d+)_(?P<occ>\d+)_(?P<rank>\d+)$",
                    col_code.lower(),
                )
                assert m, f"Invalid col_code format: '{col_code}'"
                case_type_idx, ref_dim_idx, occ_idx, col_rank = (
                    m.group("ct"),
                    m.group("ref_dim"),
                    m.group("occ"),
                    m.group("rank"),
                )
                ref_dim_code = f"ref_dim{ref_dim_idx}"
                ref_col_code = f"ref_col{ref_dim_idx}_{col_rank}"
                dim_code = f"dim{case_type_idx}_{ref_dim_idx}_{occ_idx}"
                if ref_dim_code not in created_ref_dims:
                    env.create_ref_dim(
                        root_user, ref_dim_code, casedb_enum.DimType.TEXT
                    )
                    created_ref_dims.add(ref_dim_code)
                if ref_col_code not in created_ref_cols:
                    ref_col: model.RefCol = env.create_ref_col(
                        root_user, ref_col_code, casedb_enum.ColType.TEXT
                    )
                    assert (
                        ref_col is not None
                    ), f"Failed to create ref col '{ref_col_code}'"
                    created_ref_cols.add(ref_col_code)
                    ref_col_codes.append(ref_col_code)
                if dim_code not in created_dims:
                    env.create_dim(root_user, dim_code)
                    created_dims.add(dim_code)
                env.create_col(root_user, col_code)
                created_cols.add(col_code)
            col_objs.add(col_code)
        col_set: model.ColSet = env.create_col_set(root_user, col_set_name, col_objs)
        if VERBOSE:
            print(f"Created col set '{col_set_name}' with cols {sorted(col_objs)}")
        ref_col_ids_by_set[col_set_name] = ref_col_codes

    # --- DataCollections ---
    # data_collection1: target collection referenced by all policies
    # data_collection2: source collection for share policies (from_data_collection)
    env.create_data_collection(root_user, "data_collection1")
    env.create_data_collection(root_user, "data_collection2")

    # --- Cases ---
    # One case per unique CaseType, in data_collection1.
    # Naming convention: case{case_type_index}_1 (e.g. case1_1 for case_type1).
    for case_type_name in sorted(created_case_types):
        m = re.match(r"^case_type(\d+)$", case_type_name)
        assert m, f"Unexpected CaseType name format: '{case_type_name}'"
        case_code = f"case{m.group(1)}_1"
        env.create_case(root_user, case_code, "data_collection1")
        if VERBOSE:
            print(f"Created case '{case_code}' for '{case_type_name}'")

    # --- OrganizationAccessCasePolicies (CaseTypeSets & ColSets) ---
    # One per unique (Organization, CaseTypeSet, ColSet) from org_access_policies.
    # Naming: "org_access_policy{org_num}_{dc_num}" e.g. "org_access_policy1_1"

    created_org_access: set[tuple[str, str, str]] = set()
    for spec in EDGE_CASES:
        for case_type_set, col_set in spec.org_access_policies:
            key = (spec.org_name, case_type_set, col_set)
            if key not in created_org_access:
                org_num = spec.org_name[len("org") :]

                dc_num = 1  # for demo, all policies reference data_collection1
                policy_name = f"org_access_policy{org_num}_{dc_num}"

                env.create_organization_access_case_policy(
                    root_user,
                    policy_name,
                    case_type_set,
                    read_col_set=col_set,
                )

                created_org_access.add(key)

    # --- OrganizationShareCasePolicies (CaseTypeSets & ColSets) ---
    # One per unique (org, case_type_set) from org_share_policy_sets.
    # Naming: "org_share_policy{org_num}_{dc_num}_{from_dc_num}" e.g. "org_share_policy1_1_2"
    # Shares from data_collection2 into data_collection1.

    created_org_share: set[tuple[str, str]] = set()
    for spec in EDGE_CASES:
        for case_type_set in spec.org_share_policy_sets:
            key = (spec.org_name, case_type_set)
            if key not in created_org_share:
                org_num = spec.org_name[len("org") :]
                # Naming: org_share_policy{org_num}_1_2 (should reference data collections)
                # Convention: org_share_policy{org_num}_{target_dc_num}_{source_dc_num}
                target_dc_num = 1
                source_dc_num = 2
                policy_name = (
                    f"org_share_policy{org_num}_{target_dc_num}_{source_dc_num}"
                )
                env.create_organization_share_case_policy(
                    root_user, policy_name, case_type_set
                )
                created_org_share.add(key)

    # --- UserAccessCasePolicies (CaseTypeSets & ColSets) ---
    # One per (User, CaseTypeSet, ColSet) in user_access_policies.
    # Note: user access policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.

    for spec in EDGE_CASES:
        for case_type_set, col_set in spec.user_access_policies:
            # Use variable for data collection name for clarity and consistency
            target_data_collection = "data_collection1"
            env.create_user_access_case_policy(
                root_user,
                spec.user_name,
                target_data_collection,
                case_type_set,
                read_col_set=col_set,
            )

    # --- UserShareCasePolicies (CaseTypeSets & ColSets) ---
    # One per (User, CaseTypeSet) in user_share_policy_sets.
    # Shares from data_collection2 into data_collection1.
    # Note: user share policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.

    for spec in EDGE_CASES:
        for case_type_set in spec.user_share_policy_sets:
            env.create_user_share_case_policy(
                root_user,
                spec.user_name,
                data_collection="data_collection1",
                from_data_collection="data_collection2",
                case_type_set=case_type_set,
            )
