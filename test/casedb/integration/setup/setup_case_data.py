import pytest

from test.casedb.casedb_test_client import CasedbTestClient as Env
from gen_epix.casedb.domain import model
from gen_epix.casedb.domain import enum as casedb_enum

from test.casedb.integration.setup.define_edge_cases import EDGE_CASES

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
    # Derive case types and case type sets from all four policy dimensions in EDGE_CASES.
    # Assumption: each case type set contains exactly one case type.
    # Naming convention: case_type_set{N} → case_type_{N} (replace "_set" with "_").

    all_ct_set_names = {
        ct_set_name
        for spec in EDGE_CASES
        for ct_set_name in (
            spec.org_access_policy_sets
            + spec.org_share_policy_sets
            + spec.user_access_policy_sets
            + spec.user_share_policy_sets
        )
    }
    for ct_set_name in sorted(all_ct_set_names):
        ct_name = ct_set_name.replace("_set", "")
        case_type = env.create_case_type(
            root_user, ct_name, "disease_1", "etiological_agent_1"
        )
        assert case_type is not None, f"Failed to create case type '{ct_name}'"
        env.create_case_type_set(root_user, ct_set_name, {ct_name}, "category_1")

    # --- CASE TYPE COLS & COL SETS ---
    # For demo: create one col per set, and one col set per set (colset1, colset2, ...)
    all_col_set_names = {s.replace("case_type_set", "colset") for s in all_ct_set_names}

    col_ids_by_colset: dict[str, list] = {}

    # For this demo, we create one dimension and one col per set, using the correct model and naming conventions.
    # Naming: case_type_col_{ct_idx}_{dim_idx}_{occ_idx}_{col_idx}
    # We'll use ct_idx = set index, dim_idx = 1, occ_idx = 1, col_idx = 1
    # Note: we should also create a unique dim and col per set
    for i, colset_name in enumerate(sorted(all_col_set_names), 1):
        ct_idx = i
        dim_idx = i
        occ_idx = 1
        col_idx = 1
        col_code = f"col{dim_idx}_1"  # 1 is the ranking of the col within the dimension, for demo we have only one col per dim
        dim_code = f"dim{dim_idx}"

        # Ensure the dimension exists (TEXT type for demo)
        env.create_dim(root_user, dim_code, casedb_enum.DimType.TEXT)
        # Create the col (TEXT type for demo)
        col = env.create_col(root_user, col_code, casedb_enum.ColType.TEXT)
        assert col is not None, f"Failed to create col '{col_code}'"
        # Create the col set and add the col as its only member

        # Note: there is an error here, case_type_col_1_1_1_1 not found
        # Col is not part of a col set, case_type_col is part of a case_type_col_set

        # case_type_dim should be case_type_dim_1_2_3
        # where 1 = ct_idx, 2 = dim_idx, 3 = occ_idx
        case_type_dim_code = f"case_type_dim{ct_idx}_{dim_idx}_{occ_idx}"
        env.create_case_type_dim(root_user, case_type_dim_code)

        # case_type_dim1_1_1 not found error
        case_type_col_code = f"case_type_col{ct_idx}_{dim_idx}_{occ_idx}_{col_idx}"
        env.create_case_type_col(root_user, case_type_col_code, col.id)

        if VERBOSE:
            print(
                f"Created col '{col_code}' (id={col.id}), case type dim '{case_type_dim_code}', and case type col '{case_type_col_code}' for col set '{colset_name}'"
            )

        # Note: case type col set members are automatically created
        # when we create the case type col set with the col set name matching the case type set name
        # (e.g. "colset1" for "case_type_set1") and passing the case type col code as a member.
        ct_col_set: model.CaseTypeColSet = env.create_case_type_col_set(
            root_user, colset_name, {case_type_col_code}
        )
        if VERBOSE:
            print(
                f"Created col set '{colset_name}' with col '{col_code}' (id={col.id}) and case type col '{case_type_col_code}')"
            )

        col_ids_by_colset[colset_name] = [col.id]

    # --- DATA COLLECTIONS ---
    # data_collection1: target collection referenced by all policies
    # data_collection2: source collection for share policies (from_data_collection)
    env.create_data_collection(root_user, "data_collection1")
    env.create_data_collection(root_user, "data_collection2")

    # --- ORG ACCESS POLICIES (case type sets & col sets) ---
    # One per unique (org, case_type_set) from org_access_policy_sets.
    # Naming: "org_access_policy{org_num}_{dc_num}" e.g. "org_access_policy1_1"

    created_org_access: set[tuple[str, str]] = set()
    for spec in EDGE_CASES:
        for ct_set in spec.org_access_policy_sets:
            key = (spec.org_name, ct_set)
            if key not in created_org_access:
                org_num = spec.org_name[len("org") :]

                dc_num = 1  # for demo, all policies reference data_collection1
                policy_name = f"org_access_policy{org_num}_{dc_num}"

                # Note: we already created the col type sets and col sets with the same naming convention as the case type sets (e.g. "case_type_set1" → "colset1"),
                # so we can pass the col set
                # Also create col set access policy
                colset_name = ct_set.replace("case_type_set", "colset")

                env.create_organization_access_case_policy(
                    root_user,
                    policy_name,
                    ct_set,
                    read_case_type_col_set=colset_name,
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
    # One per (user, case_type_set) in user_access_policy_sets.
    # Note: user access policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.

    for spec in EDGE_CASES:
        for ct_set in spec.user_access_policy_sets:
            # Use variable for data collection name for clarity and consistency
            target_data_collection = "data_collection1"
            colset_name = ct_set.replace("case_type_set", "colset")
            env.create_user_access_case_policy(
                root_user,
                spec.user_name,
                target_data_collection,
                ct_set,
                read_case_type_col_set=colset_name,
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


# Is it possibel to include another fixture here
# that is defined in another file, e.g. setup_case_col_data.py
