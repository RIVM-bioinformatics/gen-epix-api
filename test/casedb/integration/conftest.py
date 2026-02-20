from dataclasses import dataclass
from itertools import product

import pytest

from test.casedb.casedb_test_client import CasedbTestClient as Env
from gen_epix.casedb.domain import model

# These fixtures are used across multiple test modules in the integration test suite, so they are defined in conftest.py
# to avoid duplication and ensure consistent setup of test users, organizations, and reference data for all tests.


@dataclass
class EdgeCaseSpec:
    """
    Declarative specification for a single ABAC edge case.

    Captures all relevant dimensions for a user-based access control test scenario:
    - user_name / org_name: identity and organizational membership
    - org_policy_sets: case type sets shared at org level with this user's org
    - user_policy_sets: case type sets granted directly to this user via user-level policies
    - expected_case_types: expected accessible case type names given the above combination

    Both setup fixtures iterate EDGE_CASES to drive user/org creation and policy setup.
    Adding a new edge case is a single entry in EDGE_CASES below.
    Tests can use EDGE_CASE_BY_USER[user_name].expected_case_types for assertions
    and .description for human-readable output.
    """

    user_name: str
    org_name: str
    label: str
    org_policy_sets: list[str]
    user_policy_sets: list[str]
    expected_case_types: list[str]

    @property
    def description(self) -> str:
        org_p = ", ".join(self.org_policy_sets) if self.org_policy_sets else "∅"
        usr_p = ", ".join(self.user_policy_sets) if self.user_policy_sets else "∅"
        exp = ", ".join(self.expected_case_types) if self.expected_case_types else "∅"
        return (
            f"[{self.user_name}@{self.org_name}] {self.label}\n"
            f"  org_policies=[{org_p}], user_policies=[{usr_p}] → expected=[{exp}]"
        )


# ---------------------------------------------------------------------------
# Edge case generation
# ---------------------------------------------------------------------------
# EDGE_CASES is generated as the Cartesian product of ORG_POLICY_COMBOS ×
# USER_POLICY_COMBOS. Each org-policy combination gets its own org (shared by
# all users with that org-level policy). Each user-policy combination produces
# one user within that org.
#
# To add a new dimension: extend one of the combo lists below. Both fixtures
# and the parametrized test will pick it up automatically.

# Each entry is the list of case type sets granted at org level for one org.
_ORG_POLICY_COMBOS: list[list[str]] = [
    ["case_type_set1"],  # org has access to case_type_set1
    [],  # org has no access
]

# Each entry is the list of case type sets granted directly to one user.
_USER_POLICY_COMBOS: list[list[str]] = [
    [],  # no user-level policy
    ["case_type_set1"],  # user policy on the same set as the org policy
    ["case_type_set2"],  # user policy on a different set
]


def _compute_expected_case_types(org_policy_sets: list[str]) -> list[str]:
    """For reference data access, only org-level policies determine access.
    User policies are intentionally ignored — tests verify this explicitly."""
    return [s.replace("_set", "_") for s in org_policy_sets]


def _generate_label(org_policy_sets: list[str], user_policy_sets: list[str]) -> str:
    has_org = bool(org_policy_sets)
    has_usr = bool(user_policy_sets)
    if not has_org and not has_usr:
        return "no policies at all — should have no access to any case types"
    if not has_org:
        return "user policy only, no org policy — case types are shared at org level so user policy must not grant access"
    if not has_usr:
        return "org policy only — should access org-shared case types, nothing more"
    if set(org_policy_sets) == set(user_policy_sets):
        return "org + user policy on the same set — overlap must not cause issues, org access preserved"
    return "org + user policy on different sets — user policy must not grant access beyond the org policy"


# The key semantic is: an org-level policy applies to every user in that org.
# Sharing an org between multiple users within the same _ORG_POLICY_COMBOS entry
# is what lets you test the cross-user dimension:
EDGE_CASES: list[EdgeCaseSpec] = [
    EdgeCaseSpec(
        user_name=f"org_user{org_idx + 1}_{usr_idx + 1}",
        org_name=f"org{org_idx + 1}",
        label=_generate_label(org_policies, user_policies),
        org_policy_sets=org_policies,
        user_policy_sets=user_policies,
        expected_case_types=_compute_expected_case_types(org_policies),
    )
    for (org_idx, org_policies), (usr_idx, user_policies) in product(
        enumerate(_ORG_POLICY_COMBOS), enumerate(_USER_POLICY_COMBOS)
    )
]


# Hardcoded edge cases — kept as the reference for the current test suite.
# Compare with EDGE_CASES above to verify the generation logic
# produces the same combinations before switching over.
# Also we keep these as exampels of manually specifying edge cases for clarity and ease of debugging, and to allow for custom labels and expected results if needed in the future.
# EDGE_CASES: list[EdgeCaseSpec] = [
#     EdgeCaseSpec(
#         user_name="org_user1_1",
#         org_name="org1",
#         label="org policy only — should access org-shared case types, nothing more",
#         org_policy_sets=["case_type_set1"],
#         user_policy_sets=[],
#         expected_case_types=["case_type_1"],
#     ),
#     EdgeCaseSpec(
#         user_name="org_user1_2",
#         org_name="org1",
#         label="org + user policy on different sets — user policy must not grant access beyond the org policy",
#         org_policy_sets=["case_type_set1"],
#         user_policy_sets=["case_type_set2"],
#         expected_case_types=["case_type_1"],
#     ),
#     EdgeCaseSpec(
#         user_name="org_user1_3",
#         org_name="org1",
#         label="org + user policy on the same set — overlap must not cause issues, org access preserved",
#         org_policy_sets=["case_type_set1"],
#         user_policy_sets=["case_type_set1"],
#         expected_case_types=["case_type_1"],
#     ),
#     EdgeCaseSpec(
#         user_name="org_user2_1",
#         org_name="org2",
#         label="no policies at all — should have no access to any case types",
#         org_policy_sets=[],
#         user_policy_sets=[],
#         expected_case_types=[],
#     ),
#     EdgeCaseSpec(
#         user_name="org_user2_2",
#         org_name="org2",
#         label="user policy only, no org policy — case types are shared at org level so user policy must not grant access",
#         org_policy_sets=[],
#         user_policy_sets=["case_type_set1"],
#         expected_case_types=[],
#     ),
# ]


# Lookup by user_name for use in tests:
#   EDGE_CASE_BY_USER["org_user1_2"].expected_case_types
#   EDGE_CASE_BY_USER["org_user1_2"].description
EDGE_CASE_BY_USER: dict[str, EdgeCaseSpec] = {s.user_name: s for s in EDGE_CASES}


@pytest.fixture(scope="module")
def setup_test_users_and_organizations(env: Env) -> None:
    """
    Set up common test users and organizations driven by EDGE_CASES.

    Creates:
    - root user (bootstrapped into env.db)
    - org1 (bootstrapped into env.db, pre-configured as the root organization)
    - any additional orgs referenced in EDGE_CASES (e.g. org2), in order of first appearance
    - one user per EdgeCaseSpec; role and org membership are derived from
      the user_name naming convention by invite_and_register_user
    """
    root_user = env.get_root_user()
    env._set_obj(root_user)

    org1 = env.read_one_by_property(root_user, model.Organization, "name", "org1")
    env._set_obj(org1)

    # Create orgs not already bootstrapped (org1 is pre-configured as the root org)
    created_orgs: set[str] = {"org1"}
    for spec in EDGE_CASES:
        if spec.org_name not in created_orgs:
            env.create_organization(root_user, spec.org_name)
            created_orgs.add(spec.org_name)

    # Create users; role and org membership are derived from user_name by invite_and_register_user
    for spec in EDGE_CASES:
        env.invite_and_register_user(root_user, spec.user_name)


# setup_case_type_data depends on setup_test_users_and_organizations to ensure that users and
# organizations are created before policies reference them. The parameter is intentionally
# unused in the body — its presence enforces fixture ordering.
@pytest.fixture(scope="module")
def setup_case_type_data(
    env: Env, setup_test_users_and_organizations: None
) -> None:  # noqa: ARG001
    """
    Create reference data (diseases, etiological agents, case types, and access policies) for tests.
    Objects are automatically stored in env.db by create methods.

    Policy creation is driven by EDGE_CASES:
    - Org-level access policies: one per unique (org, case_type_set) pair across all specs.
      Policy name convention: "org_case_policy{org_num}_1" (data_collection1 implied).
    - User-level access policies: one per (user, case_type_set) entry in user_policy_sets.
    """
    root_user = env.get_root_user()

    env.create_disease(root_user, "disease_1")
    env.create_disease(root_user, "disease_2")

    env.create_etiological_agent(root_user, "etiological_agent_1")
    env.create_etiological_agent(root_user, "etiological_agent_2")

    # Create case types using pre-created reference data from env.db.
    # case_type_1 is the primary case type shared via org policies.
    # case_type_2 tests that access to case_type_1 does not imply access to case_type_2
    # (no over-permissioning) and is used for user policy access tests.
    env.create_case_type_set_category(root_user, "category_1", 0)

    # Derive case types and case type sets from EDGE_CASES rather than hardcoding them.
    # Assumption: each case type set contains exactly one case type.
    # Naming convention: case_type_set{N} → case_type_{N} (replace "_set" with "_").
    # All case types share the same disease and etiological agent for now.
    all_ct_set_names = {
        ct_set_name
        for spec in EDGE_CASES
        for ct_set_name in spec.org_policy_sets + spec.user_policy_sets
    }
    for ct_set_name in all_ct_set_names:
        ct_name = ct_set_name.replace("_set", "_")
        case_type = env.create_case_type(
            root_user, ct_name, "disease_1", "etiological_agent_1"
        )
        assert case_type is not None, f"Failed to create case type '{ct_name}'"
        env.create_case_type_set(root_user, ct_set_name, [case_type.id], "category_1")

    env.create_data_collection(root_user, "data_collection1")

    # Create one org-level access policy per unique (org, case_type_set) combination.
    # Orgs with an empty org_policy_sets (e.g. org2) intentionally receive no org policy.
    created_org_policies: set[tuple[str, str]] = set()
    for spec in EDGE_CASES:
        for ct_set in spec.org_policy_sets:
            key = (spec.org_name, ct_set)
            if key not in created_org_policies:
                org_num = spec.org_name[len("org") :]
                policy_name = f"org_case_policy{org_num}_1"
                env.create_organization_access_case_policy(
                    root_user, policy_name, ct_set
                )
                created_org_policies.add(key)

    # Create user-level access policies for each user's declared user_policy_sets.
    # Note: user policies are intentionally ignored for reference data (case type) access —
    # the tests verify this behaviour explicitly.
    for spec in EDGE_CASES:
        for ct_set in spec.user_policy_sets:
            env.create_user_access_case_policy(
                root_user, spec.user_name, "data_collection1", ct_set
            )
