from dataclasses import dataclass
from itertools import product

import pytest

from gen_epix.casedb.domain.model.case.reference_data import CaseType
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
    - org_access_policy_sets: case type sets granted at org level via OrganizationAccessCasePolicy
    - org_share_policy_sets: case type sets granted at org level via OrganizationShareCasePolicy
    - user_access_policy_sets: case type sets granted directly to this user via UserAccessCasePolicy
    - user_share_policy_sets: case type sets granted directly to this user via UserShareCasePolicy
    - expected_case_types: expected accessible case type names (union of org access + org share)
    - expected_case_type_sets: expected accessible case type set names (union of org access + org share)

    For reference data (case types / case type sets), only org-level policies determine access.
    User-level policies (both access and share) are intentionally ignored — tests verify this.

    Both setup fixtures iterate EDGE_CASES to drive user/org creation and policy setup.
    Adding a new edge case is a single entry in EDGE_CASES below.
    Tests can use EDGE_CASE_BY_USER[user_name].expected_case_types for assertions
    and .description for human-readable output.
    """

    user_name: str
    org_name: str
    label: str
    org_access_policy_sets: list[str]
    org_share_policy_sets: list[str]
    user_access_policy_sets: list[str]
    user_share_policy_sets: list[str]
    expected_case_types: list[str]
    expected_case_type_sets: list[str]

    @property
    def description(self) -> str:
        def _fmt(items: list[str]) -> str:
            return ", ".join(items) if items else "∅"

        return (
            f"[{self.user_name}@{self.org_name}] {self.label}\n"
            f"  org_access=[{_fmt(self.org_access_policy_sets)}], "
            f"org_share=[{_fmt(self.org_share_policy_sets)}]\n"
            f"  user_access=[{_fmt(self.user_access_policy_sets)}], "
            f"user_share=[{_fmt(self.user_share_policy_sets)}]\n"
            f"  → expected_case_types=[{_fmt(self.expected_case_types)}], "
            f"expected_case_type_sets=[{_fmt(self.expected_case_type_sets)}]"
        )


# ---------------------------------------------------------------------------
# Edge case generation
# ---------------------------------------------------------------------------
# EDGE_CASES is generated as the Cartesian product of four policy dimensions:
#   _ORG_ACCESS_COMBOS × _ORG_SHARE_COMBOS × _USER_ACCESS_COMBOS × _USER_SHARE_COMBOS
#
# The org is determined by the combination of org-level policies (access + share).
# All users sharing the same org-level combo live in the same org — this is what
# lets you test the cross-user dimension within one org.
# The user within that org is determined by the user-level combo (access + share).
#
# For reference data (case types / case type sets), access = union of:
#   OrganizationAccessCasePolicy ∪ OrganizationShareCasePolicy
# User-level policies (both access and share) have NO influence.

# Each entry is the list of case type sets granted at org level via OrganizationAccessCasePolicy.
_ORG_ACCESS_COMBOS: list[list[str]] = [
    ["case_type_set1"],  # org has direct access to case_type_set1
    [],  # org has no direct access
]

# Each entry is the list of case type sets granted at org level via OrganizationShareCasePolicy.
_ORG_SHARE_COMBOS: list[list[str]] = [
    [],  # org has no shared access
    ["case_type_set2"],  # org has shared access to case_type_set2
]

# Each entry is the list of case type sets granted directly to one user via UserAccessCasePolicy.
_USER_ACCESS_COMBOS: list[list[str]] = [
    [],  # no user-level access policy
    ["case_type_set1"],  # user access policy on the same set as the org access policy
    ["case_type_set2"],  # user access policy on a different set
]

# Each entry is the list of case type sets granted directly to one user via UserShareCasePolicy.
_USER_SHARE_COMBOS: list[list[str]] = [
    [],  # no user-level share policy
    ["case_type_set1"],  # user share policy on case_type_set1
]


def _compute_expected_case_types(
    org_access_sets: list[str], org_share_sets: list[str]
) -> list[str]:
    """For reference data access, only org-level policies determine access (union of access + share).
    User policies are intentionally ignored — tests verify this explicitly."""
    combined = sorted(set(org_access_sets) | set(org_share_sets))
    return [s.replace("_set", "_") for s in combined]


def _compute_expected_case_type_sets(
    org_access_sets: list[str], org_share_sets: list[str]
) -> list[str]:
    """Only the case type sets referenced in org-level policies (access ∪ share) are accessible.
    User policies are intentionally ignored — tests verify this explicitly."""
    return sorted(set(org_access_sets) | set(org_share_sets))


def _generate_label(
    org_access: list[str],
    org_share: list[str],
    user_access: list[str],
    user_share: list[str],
) -> str:
    has_org_access = bool(org_access)
    has_org_share = bool(org_share)
    has_org = has_org_access or has_org_share
    has_user = bool(user_access) or bool(user_share)

    # Describe the org-level dimension
    if has_org_access and has_org_share:
        org_desc = "org access + org share"
    elif has_org_access:
        org_desc = "org access only"
    elif has_org_share:
        org_desc = "org share only"
    else:
        org_desc = "no org policies"

    # Describe the user-level dimension
    if bool(user_access) and bool(user_share):
        user_desc = "user access + user share"
    elif bool(user_access):
        user_desc = "user access only"
    elif bool(user_share):
        user_desc = "user share only"
    else:
        user_desc = "no user policies"

    if not has_org and not has_user:
        return "no policies at all — should have no access"
    if not has_org:
        return f"{user_desc}, {org_desc} — user policies must not grant ref data access"
    if not has_user:
        return f"{org_desc} — should access org-level case types/sets"
    return f"{org_desc} + {user_desc} — user policies must not extend ref data access beyond org"


# Org index = combination of org-level policies (access × share).
# User index within that org = combination of user-level policies (access × share).
_org_combos = list(
    enumerate(product(enumerate(_ORG_ACCESS_COMBOS), enumerate(_ORG_SHARE_COMBOS)))
)
_user_combos = list(
    enumerate(product(enumerate(_USER_ACCESS_COMBOS), enumerate(_USER_SHARE_COMBOS)))
)

EDGE_CASES: list[EdgeCaseSpec] = [
    EdgeCaseSpec(
        user_name=f"org_user{org_idx + 1}_{usr_idx + 1}",
        org_name=f"org{org_idx + 1}",
        label=_generate_label(org_access, org_share, user_access, user_share),
        org_access_policy_sets=org_access,
        org_share_policy_sets=org_share,
        user_access_policy_sets=user_access,
        user_share_policy_sets=user_share,
        expected_case_types=_compute_expected_case_types(org_access, org_share),
        expected_case_type_sets=_compute_expected_case_type_sets(org_access, org_share),
    )
    for org_idx, ((_, org_access), (_, org_share)) in _org_combos
    for usr_idx, ((_, user_access), (_, user_share)) in _user_combos
]


# Hardcoded edge cases — kept as the reference for the current test suite.
# Compare with EDGE_CASES above to verify the generation logic
# produces the same combinations before switching over.
# Also we keep these as examples of manually specifying edge cases for clarity
# and ease of debugging, and to allow for custom labels and expected results
# if needed in the future.
#
# EDGE_CASES: list[EdgeCaseSpec] = [
#     EdgeCaseSpec(
#         user_name='org_user1_1',
#         org_name='org1',
#         label='org access only — should access org-level case types/sets',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=[],
#         user_access_policy_sets=[],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_1'],
#         expected_case_type_sets=['case_type_set1'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user1_2',
#         org_name='org1',
#         label='org access only + user share only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=[],
#         user_access_policy_sets=[],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_1'],
#         expected_case_type_sets=['case_type_set1'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user1_3',
#         org_name='org1',
#         label='org access only + user access only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_1'],
#         expected_case_type_sets=['case_type_set1'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user1_4',
#         org_name='org1',
#         label='org access only + user access + user share — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_1'],
#         expected_case_type_sets=['case_type_set1'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user1_5',
#         org_name='org1',
#         label='org access only + user access only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_1'],
#         expected_case_type_sets=['case_type_set1'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user1_6',
#         org_name='org1',
#         label='org access only + user access + user share — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_1'],
#         expected_case_type_sets=['case_type_set1'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user2_1',
#         org_name='org2',
#         label='org access + org share — should access org-level case types/sets',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=[],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_1', 'case_type_2'],
#         expected_case_type_sets=['case_type_set1', 'case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user2_2',
#         org_name='org2',
#         label='org access + org share + user share only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=[],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_1', 'case_type_2'],
#         expected_case_type_sets=['case_type_set1', 'case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user2_3',
#         org_name='org2',
#         label='org access + org share + user access only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_1', 'case_type_2'],
#         expected_case_type_sets=['case_type_set1', 'case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user2_4',
#         org_name='org2',
#         label='org access + org share + user access + user share — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_1', 'case_type_2'],
#         expected_case_type_sets=['case_type_set1', 'case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user2_5',
#         org_name='org2',
#         label='org access + org share + user access only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_1', 'case_type_2'],
#         expected_case_type_sets=['case_type_set1', 'case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user2_6',
#         org_name='org2',
#         label='org access + org share + user access + user share — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=['case_type_set1'],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_1', 'case_type_2'],
#         expected_case_type_sets=['case_type_set1', 'case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user3_1',
#         org_name='org3',
#         label='no policies at all — should have no access',
#         org_access_policy_sets=[],
#         org_share_policy_sets=[],
#         user_access_policy_sets=[],
#         user_share_policy_sets=[],
#         expected_case_types=[],
#         expected_case_type_sets=[],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user3_2',
#         org_name='org3',
#         label='user share only, no org policies — user policies must not grant ref data access',
#         org_access_policy_sets=[],
#         org_share_policy_sets=[],
#         user_access_policy_sets=[],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=[],
#         expected_case_type_sets=[],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user3_3',
#         org_name='org3',
#         label='user access only, no org policies — user policies must not grant ref data access',
#         org_access_policy_sets=[],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=[],
#         expected_case_types=[],
#         expected_case_type_sets=[],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user3_4',
#         org_name='org3',
#         label='user access + user share, no org policies — user policies must not grant ref data access',
#         org_access_policy_sets=[],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=[],
#         expected_case_type_sets=[],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user3_5',
#         org_name='org3',
#         label='user access only, no org policies — user policies must not grant ref data access',
#         org_access_policy_sets=[],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=[],
#         expected_case_types=[],
#         expected_case_type_sets=[],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user3_6',
#         org_name='org3',
#         label='user access + user share, no org policies — user policies must not grant ref data access',
#         org_access_policy_sets=[],
#         org_share_policy_sets=[],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=[],
#         expected_case_type_sets=[],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user4_1',
#         org_name='org4',
#         label='org share only — should access org-level case types/sets',
#         org_access_policy_sets=[],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=[],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_2'],
#         expected_case_type_sets=['case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user4_2',
#         org_name='org4',
#         label='org share only + user share only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=[],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=[],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_2'],
#         expected_case_type_sets=['case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user4_3',
#         org_name='org4',
#         label='org share only + user access only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=[],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_2'],
#         expected_case_type_sets=['case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user4_4',
#         org_name='org4',
#         label='org share only + user access + user share — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=[],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set1'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_2'],
#         expected_case_type_sets=['case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user4_5',
#         org_name='org4',
#         label='org share only + user access only — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=[],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=[],
#         expected_case_types=['case_type_2'],
#         expected_case_type_sets=['case_type_set2'],
#     ),
#     EdgeCaseSpec(
#         user_name='org_user4_6',
#         org_name='org4',
#         label='org share only + user access + user share — user policies must not extend ref data access beyond org',
#         org_access_policy_sets=[],
#         org_share_policy_sets=['case_type_set2'],
#         user_access_policy_sets=['case_type_set2'],
#         user_share_policy_sets=['case_type_set1'],
#         expected_case_types=['case_type_2'],
#         expected_case_type_sets=['case_type_set2'],
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
    Create reference data (diseases, etiological agents, case types, and all four policy types) for tests.
    Objects are automatically stored in env.db by create methods.

    Policy creation is driven by EDGE_CASES:
    - Org access policies: one per unique (org, case_type_set) from org_access_policy_sets.
    - Org share policies: one per unique (org, case_type_set) from org_share_policy_sets.
      These require a from_data_collection (data_collection2) to represent the sharing source.
    - User access policies: one per (user, case_type_set) entry in user_access_policy_sets.
    - User share policies: one per (user, case_type_set) entry in user_share_policy_sets.
      These also require from_data_collection (data_collection2).

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
        ct_name = ct_set_name.replace("_set", "_")
        case_type: CaseType = env.create_case_type(
            root_user, ct_name, "disease_1", "etiological_agent_1"
        )
        assert case_type is not None, f"Failed to create case type '{ct_name}'"
        env.create_case_type_set(root_user, ct_set_name, [case_type], "category_1")

    # data_collection1: target collection referenced by all policies
    # data_collection2: source collection for share policies (from_data_collection)
    env.create_data_collection(root_user, "data_collection1")
    env.create_data_collection(root_user, "data_collection2")

    # --- Org access policies ---
    # One per unique (org, case_type_set) from org_access_policy_sets.
    # Naming: "org_access_policy{org_num}_{dc_num}" e.g. "org_access_policy1_1"
    created_org_access: set[tuple[str, str]] = set()
    for spec in EDGE_CASES:
        for ct_set in spec.org_access_policy_sets:
            key = (spec.org_name, ct_set)
            if key not in created_org_access:
                org_num = spec.org_name[len("org") :]
                policy_name = f"org_access_policy{org_num}_1"
                env.create_organization_access_case_policy(
                    root_user, policy_name, ct_set
                )
                created_org_access.add(key)

    # --- Org share policies ---
    # One per unique (org, case_type_set) from org_share_policy_sets.
    # Naming: "org_share_policy{org_num}_{dc_num}_{from_dc_num}" e.g. "org_share_policy1_1_2"
    # Shares from data_collection2 into data_collection1.
    created_org_share: set[tuple[str, str]] = set()

    for spec in EDGE_CASES:
        for ct_set in spec.org_share_policy_sets:
            key = (spec.org_name, ct_set)
            if key not in created_org_share:
                org_num = spec.org_name[len("org") :]
                policy_name = f"org_share_policy{org_num}_1_2"
                env.create_organization_share_case_policy(
                    root_user, policy_name, ct_set
                )
                created_org_share.add(key)

    # --- User access policies ---
    # One per (user, case_type_set) in user_access_policy_sets.
    # Note: user access policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.
    for spec in EDGE_CASES:
        for ct_set in spec.user_access_policy_sets:
            env.create_user_access_case_policy(
                root_user, spec.user_name, "data_collection1", ct_set
            )

    # --- User share policies ---
    # One per (user, case_type_set) in user_share_policy_sets.
    # Shares from data_collection2 into data_collection1.
    # Note: user share policies are intentionally ignored for reference data access —
    # the tests verify this behaviour explicitly.
    for spec in EDGE_CASES:
        for ct_set in spec.user_share_policy_sets:
            env.create_user_share_case_policy(
                root_user,
                spec.user_name,
                "data_collection1",
                "data_collection2",
                ct_set,
            )
