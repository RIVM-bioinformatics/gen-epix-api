"""
This module defines the setup_case_type_data fixture, which creates reference data
(diseases, etiological agents, case types, case type sets, case type col sets,
and all four policy types) for tests.
"""

import re
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.setup.define_edge_cases import (
    CASE_TYPE_COL_SETS,
    CASE_TYPE_SETS,
    EDGE_CASES,
)

import pytest

from gen_epix.casedb.domain import enum as casedb_enum
from gen_epix.casedb.domain import model

VERBOSE = True  # Set to True to enable detailed print statements during setup for debugging purposes;


# setup_case_type_data depends on setup_test_users_and_organizations to ensure that users and
# organizations are created before policies reference them.
# The parameter is intentionally unused in the body — its presence enforces fixture ordering.
@pytest.fixture(scope="module")
def setup_case_type_data(
    env: Env, setup_test_users_and_organizations: None  # noqa: ARG001
) -> None:  # noqa: ARG001
    """
    Create reference data (diseases, etiological agents, case types, case type sets, case type col sets, and all four policy types) for tests.
    Objects are automatically stored in env.db by create methods.

    Policy creation is driven by EDGE_CASES:
    - Org access/share policies: one per unique (org, case_type_set) from org_access_policy_sets/org_share_policy_sets.
    - User access/share policies: one per (user, case_type_set) entry in user_access_policy_sets/user_share_policy_sets.
    - For col sets: same logic, but with col set names (e.g. colset1) and col set objects.

    Data collections:
    - data_collection1: the target collection referenced by all policies.
    - data_collection2: the source collection for share policies (from_data_collection).

    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")

    # Create case types using pre-created reference data from env.db.
    env.create_case_type_set_category(root_user, "category_1", 0)

    # --- CASE TYPES & SETS ---
    # Use CASE_TYPE_SETS from define_edge_cases.py
    created_case_types = set()
    for ct_set_name, ct_names in CASE_TYPE_SETS.items():
        # Create all case types for this set (if not already created)
        for ct_name in ct_names:
            if ct_name not in created_case_types:
                case_type = env.create_case_type(
                    root_user, ct_name, "disease_1", "etiological_agent_1"
                )
                assert case_type is not None, f"Failed to create case type '{ct_name}'"
                created_case_types.add(ct_name)
        # Create the case type set with all its case types
        env.create_case_type_set(root_user, ct_set_name, set(ct_names), "category_1")

    # --- CASE TYPE COLS & COL SETS ---
    # Use CASE_TYPE_COL_SETS from define_edge_cases.py.
    # Dims, cols, case_type_dims, and case_type_cols may be shared across col sets
    # (e.g. colset3 reuses cols from colset1 and colset2) — create each only once.
    col_ids_by_colset: dict[str, list[str]] = {}
    created_dims: set[str] = set()
    created_cols: set[str] = set()
    created_case_type_dims: set[str] = set()
    created_case_type_cols: set[str] = set()
    for colset_name, case_type_col_codes in sorted(CASE_TYPE_COL_SETS.items()):
        case_type_col_objs: set[str] = set()
        col_codes: list[str] = []
        for case_type_col_code in case_type_col_codes:
            if case_type_col_code not in created_case_type_cols:
                # Parse indices from naming convention: case_type_col{ct}_{dim}_{occ}_{col_rank}
                m = re.match(
                    r"^(.*?)(?P<ct>\d+)_(?P<dim>\d+)_(?P<occ>\d+)_(?P<rank>\d+)$",
                    case_type_col_code.lower(),
                )
                assert m, f"Invalid case_type_col_code format: '{case_type_col_code}'"
                ct_idx, dim_idx, occ_idx, col_rank = (
                    m.group("ct"),
                    m.group("dim"),
                    m.group("occ"),
                    m.group("rank"),
                )
                dim_code = f"dim{dim_idx}"
                col_code = f"col{dim_idx}_{col_rank}"
                case_type_dim_code = f"case_type_dim{ct_idx}_{dim_idx}_{occ_idx}"
                if dim_code not in created_dims:
                    env.create_dim(root_user, dim_code, casedb_enum.DimType.TEXT)
                    created_dims.add(dim_code)
                if col_code not in created_cols:
                    col: model.Col = env.create_col(
                        root_user, col_code, casedb_enum.ColType.TEXT
                    )
                    assert col is not None, f"Failed to create col '{col_code}'"
                    created_cols.add(col_code)
                    col_codes.append(col_code)
                if case_type_dim_code not in created_case_type_dims:
                    env.create_case_type_dim(root_user, case_type_dim_code)
                    created_case_type_dims.add(case_type_dim_code)
                env.create_case_type_col(root_user, case_type_col_code)
                created_case_type_cols.add(case_type_col_code)
            case_type_col_objs.add(case_type_col_code)
        ct_col_set: model.CaseTypeColSet = env.create_case_type_col_set(
            root_user, colset_name, case_type_col_objs
        )
        if VERBOSE:
            print(
                f"Created col set '{colset_name}' with case type cols {sorted(case_type_col_objs)}"
            )
        col_ids_by_colset[colset_name] = col_codes

    # --- DATA COLLECTIONS ---
    # data_collection1: target collection referenced by all policies
    # data_collection2: source collection for share policies (from_data_collection)
    env.create_data_collection(root_user, "data_collection1")
    env.create_data_collection(root_user, "data_collection2")

    # --- ORG ACCESS POLICIES (case type sets & col sets) ---
    # One per unique (org, case_type_set, case_type_col_set) from org_access_policies.
    # Naming: "org_access_policy{org_num}_{dc_num}" e.g. "org_access_policy1_1"

    created_org_access: set[tuple[str, str, str]] = set()
    for spec in EDGE_CASES:
        for ct_set, col_set in spec.org_access_policies:
            key = (spec.org_name, ct_set, col_set)
            if key not in created_org_access:
                org_num = spec.org_name[len("org") :]

                dc_num = 1  # for demo, all policies reference data_collection1
                policy_name = f"org_access_policy{org_num}_{dc_num}"

                env.create_organization_access_case_policy(
                    root_user,
                    policy_name,
                    ct_set,
                    read_case_type_col_set=col_set,
                )

                created_org_access.add(key)

    # --- ORG SHARE POLICIES (case type sets & col sets) ---
    # One per unique (org, case_type_set) from org_share_policy_sets.
    # Naming: "org_share_policy{org_num}_{dc_num}_{from_dc_num}" e.g. "org_share_policy1_1_2"
    # Shares from data_collection2 into data_collection1.

    created_org_share: set[tuple[str, str]] = set()
    for spec in EDGE_CASES:
        for ct_set in spec.org_share_policy_sets:
            key = (spec.org_name, ct_set)
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
                    root_user, policy_name, ct_set
                )
                created_org_share.add(key)

    # --- USER ACCESS POLICIES (case type sets & col sets) ---
    # One per (user, case_type_set, case_type_col_set) in user_access_policies.
    # Note: user access policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.

    for spec in EDGE_CASES:
        for ct_set, col_set in spec.user_access_policies:
            # Use variable for data collection name for clarity and consistency
            target_data_collection = "data_collection1"
            env.create_user_access_case_policy(
                root_user,
                spec.user_name,
                target_data_collection,
                ct_set,
                read_case_type_col_set=col_set,
            )

    # --- USER SHARE POLICIES (case type sets & col sets) ---
    # One per (user, case_type_set) in user_share_policy_sets.
    # Shares from data_collection2 into data_collection1.
    # Note: user share policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.

    for spec in EDGE_CASES:
        for ct_set in spec.user_share_policy_sets:
            env.create_user_share_case_policy(
                root_user,
                spec.user_name,
                data_collection="data_collection1",
                from_data_collection="data_collection2",
                case_type_set=ct_set,
            )
