"""
Setup fixtures for operational data edge case tests.

Creates users, organizations, case types, col infrastructure, data collections,
cases, and access policies — all driven by EDGE_CASES_OP from
define_edge_cases_operational.py.

Comparable to setup_case_type_data.py and setup_test_users_and_organizations.py
for the reference data tests, but for the operational data edge cases.

Used by test/casedb/integration/edge_cases_access/test_edge_cases_access.py.

Notes:
- Data collections dc1-dc4 are created as data_collection1-data_collection4 so that
  the naming convention expected by create_organization_access_case_policy is satisfied
  (it parses the policy name to look up org{n} and data_collection{n}).
- Be careful not to create duplicates: codes and names are keys in the test client
  shadow database.
"""

import re
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.casedb.integration.edge_cases_access.setup.define_edge_cases_operational import (
    CASE_TYPE_SETS_OP,
    COL_SETS_OP,
    DATA_COLLECTIONS_OP,
    EDGE_CASES_OP,
)

import pytest

from gen_epix.casedb.domain import enum as casedb_enum

VERBOSE = True

# Map dc identifiers used in define_edge_cases_operational.py to the actual
# data collection names used in the test environment.
# These names encode the dc index for create_organization_access_case_policy's
# naming convention (it looks up data_collection{n} from the policy name).
_DC_TO_DATA_COLLECTION: dict[str, str] = {
    "dc1": "data_collection1",
    "dc2": "data_collection2",
    "dc3": "data_collection3",
    "dc4": "data_collection4",
}


@pytest.fixture(scope="module")
def setup_case_data(
    env: Env, setup_test_users_and_organizations_op: None  # noqa: ARG001
) -> None:
    """
    Create case types, col infrastructure, data collections, cases, and access
    policies for operational data edge case tests.
    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_case_type_set_category(root_user, "category_1", 0)

    # --- CaseTypes ---
    # Collect all case types from CASE_TYPE_SETS_OP plus negative controls
    # (case_type5 and case_type6 are not in any set but needed for case5_1 and case6_1).
    all_case_types: set[str] = set()
    for ct_list in CASE_TYPE_SETS_OP.values():
        all_case_types.update(ct_list)
    for case_codes in DATA_COLLECTIONS_OP.values():
        for case_code in case_codes:
            m = re.match(r"^case(\d+)_\d+$", case_code)
            if m:
                all_case_types.add(f"case_type{m.group(1)}")
    for ct_name in sorted(all_case_types):
        env.create_case_type(root_user, ct_name, "disease_1", "etiological_agent_1")
        if VERBOSE:
            print(f"Created case type '{ct_name}'")

    # --- CaseTypeSets ---
    for ct_set_name, ct_names in CASE_TYPE_SETS_OP.items():
        env.create_case_type_set(root_user, ct_set_name, set(ct_names), "category_1")
        if VERBOSE:
            print(f"Created case type set '{ct_set_name}' with {sorted(ct_names)}")

    # --- Col infrastructure (RefDims, RefCols, Dims, Cols, ColSets) ---
    # Parse col codes using convention col{ct}_{ref_dim}_{occ}_{rank}.
    # Create each RefDim, RefCol, Dim, and Col exactly once (they may be shared
    # across multiple ColSets — e.g. col3_2_1_1 appears in col_set_dc1 and col_set_dc1_12).
    created_ref_dims: set[str] = set()
    created_ref_cols: set[str] = set()
    created_dims: set[str] = set()
    created_cols: set[str] = set()
    for col_set_name, col_codes in sorted(COL_SETS_OP.items()):
        col_objs: set[str] = set()
        for col_code in col_codes:
            if col_code not in created_cols:
                m = re.match(r"^col(\d+)_(\d+)_(\d+)_(\d+)$", col_code.lower())
                assert m, f"Invalid col_code format: '{col_code}'"
                ct_idx, ref_dim_idx, occ_idx, rank = (
                    m.group(1),
                    m.group(2),
                    m.group(3),
                    m.group(4),
                )
                ref_dim_code = f"ref_dim{ref_dim_idx}"
                ref_col_code = f"ref_col{ref_dim_idx}_{rank}"
                dim_code = f"dim{ct_idx}_{ref_dim_idx}_{occ_idx}"
                if ref_dim_code not in created_ref_dims:
                    env.create_ref_dim(
                        root_user, ref_dim_code, casedb_enum.DimType.TEXT
                    )
                    created_ref_dims.add(ref_dim_code)
                if ref_col_code not in created_ref_cols:
                    env.create_ref_col(
                        root_user, ref_col_code, casedb_enum.ColType.TEXT
                    )
                    created_ref_cols.add(ref_col_code)
                if dim_code not in created_dims:
                    env.create_dim(root_user, dim_code)
                    created_dims.add(dim_code)
                env.create_col(root_user, col_code)
                created_cols.add(col_code)
            col_objs.add(col_code)
        env.create_col_set(root_user, col_set_name, col_objs)
        if VERBOSE:
            print(f"Created col set '{col_set_name}' with cols {sorted(col_objs)}")

    # --- DataCollections ---
    for dc, dc_name in _DC_TO_DATA_COLLECTION.items():
        env.create_data_collection(root_user, dc_name)
        if VERBOSE:
            print(f"Created data collection '{dc_name}' (for {dc})")

    # --- OrganizationAccessCasePolicies ---
    # One policy per unique (org, dc). Policy name encodes org_num and dc_num so that
    # create_organization_access_case_policy can look up org{org_num} and
    # data_collection{dc_num}.
    created_org_access: set[tuple[str, str]] = set()
    for spec in EDGE_CASES_OP:
        org_num = spec.org_name[len("org") :]
        for ct_set, dc, col_set in spec.org_access_policies:
            key = (spec.org_name, dc)
            if key not in created_org_access:
                dc_num = dc[len("dc") :]  # "dc1" → "1", "dc2" → "2", ...
                policy_name = f"op_policy{org_num}_{dc_num}"
                env.create_organization_access_case_policy(
                    root_user,
                    policy_name,
                    ct_set,
                    read_col_set=col_set,
                    # RG Manually added
                    write_col_set=col_set,
                )
                created_org_access.add(key)
                if VERBOSE:
                    print(
                        f"Created org access policy '{policy_name}': "
                        f"{spec.org_name}, {dc}, {ct_set}, {col_set}"
                    )

    # --- UserAccessCasePolicies ---
    # One policy per unique (user, dc).
    created_user_access: set[tuple[str, str]] = set()
    for spec in EDGE_CASES_OP:
        for ct_set, dc, col_set in spec.user_access_policies:
            key = (spec.user_name, dc)
            if key not in created_user_access:
                dc_name = _DC_TO_DATA_COLLECTION[dc]
                env.create_user_access_case_policy(
                    root_user,
                    spec.user_name,
                    dc_name,
                    ct_set,
                    read_col_set=col_set,
                    # RG manually added
                    write_col_set=col_set,
                )
                created_user_access.add(key)
                if VERBOSE:
                    print(
                        f"Created user access policy: "
                        f"{spec.user_name}, {dc}, {ct_set}, {col_set}"
                    )

    # RG: manually moved adding cases after the write rights on col sets were added to the policies,
    # --- Cases ---
    # Build case_code → [dc_names] from DATA_COLLECTIONS_OP.
    # Dict iteration order is insertion order, so dc1 is first for case3_1 —
    # its created_in_data_collection_id will be data_collection1; dc2 goes in the link table.
    # The user confirmed both have equal ABAC role in production code.
    case_to_dcs: dict[str, list[str]] = {}
    for dc, case_codes in DATA_COLLECTIONS_OP.items():
        dc_name = _DC_TO_DATA_COLLECTION[dc]
        for case_code in case_codes:
            case_to_dcs.setdefault(case_code, []).append(dc_name)

    for case_code, dc_names in sorted(case_to_dcs.items()):
        env.create_case(root_user, case_code, dc_names)
        if VERBOSE:
            print(f"Created case '{case_code}' in {dc_names}")
