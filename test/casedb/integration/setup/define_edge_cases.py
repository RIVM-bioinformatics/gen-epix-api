from dataclasses import dataclass
from itertools import product


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
    - expected_case_type_col_sets: expected accessible case type column set names (union of org access + org share)

    For reference data (case types / case type sets / case type col sets), only org-level policies determine access.
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
    expected_case_type_col_sets: list[str]

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
            f"expected_case_type_sets=[{_fmt(self.expected_case_type_sets)}], "
            f"expected_case_type_col_sets=[{_fmt(self.expected_case_type_col_sets)}]"
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


def _compute_expected_case_type_col_sets(
    org_access_sets: list[str], org_share_sets: list[str]
) -> list[str]:
    # For demo: col set names are derived from set names (e.g. "case_type_set1" -> "colset1")
    combined = sorted(set(org_access_sets) | set(org_share_sets))
    return [s.replace("case_type_set", "colset") for s in combined]


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
        expected_case_type_col_sets=_compute_expected_case_type_col_sets(
            org_access,
            [],  # In this test setup, we only include case type col sets for org access policies, not org share policies, to demonstrate that user policies do not grant access to additional col sets. This also keeps the setup simpler by having a 1:1 mapping between case type sets and col sets.
        ),
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
#         expected_case_type_col_sets=['colset1'],
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
#         expected_case_type_col_sets=['colset1'],
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
#         expected_case_type_col_sets=['colset1'],
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
#         expected_case_type_col_sets=['colset1'],
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
#         expected_case_type_col_sets=['colset1'],
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
#         expected_case_type_col_sets=['colset1'],
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
#         expected_case_type_col_sets=['colset1', 'colset2'],
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
#         expected_case_type_col_sets=['colset1', 'colset2'],
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
#         expected_case_type_col_sets=['colset1', 'colset2'],
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
#         expected_case_type_col_sets=['colset1', 'colset2'],
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
#         expected_case_type_col_sets=['colset1', 'colset2'],
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
#         expected_case_type_col_sets=['colset1', 'colset2'],
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
#         expected_case_type_col_sets=[],
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
#         expected_case_type_col_sets=[],
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
#         expected_case_type_col_sets=[],
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
#         expected_case_type_col_sets=[],
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
#         expected_case_type_col_sets=[],
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
#         expected_case_type_col_sets=[],
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
#         expected_case_type_col_sets=['colset2'],
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
#         expected_case_type_col_sets=['colset2'],
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
#         expected_case_type_col_sets=['colset2'],
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
#         expected_case_type_col_sets=['colset2'],
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
#         expected_case_type_col_sets=['colset2'],
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
#         expected_case_type_col_sets=['colset2'],
#     ),
# ]


# Lookup by user_name for use in tests:
#   EDGE_CASE_BY_USER["org_user1_2"].expected_case_types
#   EDGE_CASE_BY_USER["org_user1_2"].description
EDGE_CASE_BY_USER: dict[str, EdgeCaseSpec] = {s.user_name: s for s in EDGE_CASES}
