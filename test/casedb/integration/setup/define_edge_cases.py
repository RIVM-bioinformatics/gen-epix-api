"""
This module defines the EDGE_CASES data structure, both used
1) to generate test data in setup_case_type_data and
2) to drive the test scenarios in test_casedb_edge_cases_refdata_access.

EDGE_CASES is a comprehensive set of edge cases for testing ABAC access control on CaseDB reference data (case types, case type sets,
and case type column sets). Each edge case represents a unique combination of organizational membership and policies at both the org and user level,
along with the expected access results for that scenario.

The expectations are defined based on the principle that for reference data access,
only org-level policies (both access and share) should determine access,
while user-level policies should not grant any additional access beyond what the org-level policies provide.
(implementation: expectations are not derived from querying the created policies (set up in setup_case_type_data) directly,
but from this principle and the org-level policies in each case).


TODO
- case types can also be accessed by being referred to by a case type col
    - so we have to configure what case types are referred to by case type cols in case type col sets
    - this is by naming convention (code: case_type_col{ct}_{dim}_{occ}_{col_rank}) where ct is the case type number (e.g. 1, 2, 3, 4)


- define case type col sets
    - with sets of case type cols that are partly overlapping
    between col sets to test that access is correctly determined at the col set level, not just the case type level
- define case type cols, cols, and dims for each case type col set
- add tests that user-level policies do not grant access to additional case type col sets, case type cols, cols, or dims beyond what org-level policies grant access to
    - this is currently only tested at the case type and case type set level, but should be tested at the col set, col, and dim level as well



"""

import re
from dataclasses import dataclass
from itertools import product


@dataclass
class EdgeCaseSpec:
    """
    Declarative specification for a single ABAC edge case.

    Captures all relevant dimensions for a user-based access control test scenario:
    - user_name / org_name: identity and organizational membership
    - org_access_policies: (case_type_set, case_type_col_set) pairs granted at org level via OrganizationAccessCasePolicy
    - org_share_policy_sets: case type sets granted at org level via OrganizationShareCasePolicy
    - user_access_policies: (case_type_set, case_type_col_set) pairs granted directly to this user via UserAccessCasePolicy
    - user_share_policy_sets: case type sets granted directly to this user via UserShareCasePolicy
    - expected_case_types: expected accessible case type names (union of org access + org share)
    - expected_case_type_sets: expected accessible case type set names (union of org access + org share)
    - expected_case_type_col_sets: expected accessible col set names (from org access policies only — share policies do not grant col access)
    - expected_case_type_cols: expected accessible col codes — intersection of cols in accessible col sets
      with the accessible case types (cols reference a case type via naming convention case_type_col{ct}_...)

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
    org_access_policies: list[
        tuple[str, str]
    ]  # [(case_type_set, case_type_col_set), ...]
    org_share_policy_sets: list[str]
    user_access_policies: list[
        tuple[str, str]
    ]  # [(case_type_set, case_type_col_set), ...]
    user_share_policy_sets: list[str]
    expected_case_types: list[str]
    expected_case_type_sets: list[str]
    expected_case_type_col_sets: list[str]
    expected_case_type_cols: list[str]

    @property
    def description(self) -> str:
        def _fmt(items: list[str]) -> str:
            return ", ".join(items) if items else "∅"

        def _fmt_access(policies: list[tuple[str, str]]) -> str:
            return ", ".join(f"{ct}+{cs}" for ct, cs in policies) if policies else "∅"

        return (
            f"[{self.user_name}@{self.org_name}] {self.label}\n"
            f"  org_access=[{_fmt_access(self.org_access_policies)}], "
            f"org_share=[{_fmt(self.org_share_policy_sets)}]\n"
            f"  user_access=[{_fmt_access(self.user_access_policies)}], "
            f"user_share=[{_fmt(self.user_share_policy_sets)}]\n"
            f"  → expected_case_types=[{_fmt(self.expected_case_types)}], "
            f"expected_case_type_sets=[{_fmt(self.expected_case_type_sets)}], "
            f"expected_case_type_col_sets=[{_fmt(self.expected_case_type_col_sets)}], "
            f"expected_case_type_cols=[{_fmt(self.expected_case_type_cols)}]"
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

# Each entry is a list of (case_type_set, case_type_col_set) tuples granted at org level via
# OrganizationAccessCasePolicy. The col set is independent of the case type set, enabling tests
# of inconsistent pairings (e.g. set1 with colset2).
_ORG_ACCESS_COMBOS: list[list[tuple[str, str]]] = [
    [],  # no org access policy
    [("case_type_set1", "colset1")],  # set1 with matching colset1
    [("case_type_set1", "colset2")],  # set1 with inconsistent colset2
    [("case_type_set2", "colset1")],  # set2 with inconsistent colset1 (reversed)
    [("case_type_set2", "colset3")],  # set2 with overlapping colset3
]

# Each entry is the list of case type sets granted at org level via OrganizationShareCasePolicy.
# Share policies do NOT grant col set access — only access policies determine col set access.
_ORG_SHARE_COMBOS: list[list[str]] = [
    [],  # no org share policy
    ["case_type_set2"],  # org has shared access to case_type_set2
    ["case_type_set3"],  # org has shared access to case_type_set3
]

# Each entry is a list of (case_type_set, case_type_col_set) tuples granted directly to one user
# via UserAccessCasePolicy. User policies do NOT affect reference data access — tests verify this.
_USER_ACCESS_COMBOS: list[list[tuple[str, str]]] = [
    [],  # no user-level access policy
    [("case_type_set1", "colset1")],  # user access matching common org access
    [("case_type_set2", "colset2")],  # user access on a different set/colset
]

# Each entry is the list of case type sets granted directly to one user via UserShareCasePolicy.
_USER_SHARE_COMBOS: list[list[str]] = [
    [],  # no user-level share policy
    ["case_type_set1"],  # user share policy on case_type_set1
    ["case_type_set3"],  # user share policy on case_type_set3
]

# Define case type set
# should contain case types
CASE_TYPE_SETS = {
    "case_type_set1": ["case_type1", "case_type2"],
    "case_type_set2": ["case_type2", "case_type3"],
    "case_type_set3": ["case_type4"],
}


# col (code: col{dim}_{rank})

# (code: case_type_col{ct}_{dim}_{occ}_{col_rank})
CASE_TYPE_COL_SETS = {
    # colset1 contains cols for case_type_1, case_type_2, and case_type_3 (from ct sets 1 and 2)
    "colset1": ["case_type_col1_1_1_1", "case_type_col2_2_1_1", "case_type_col3_3_1_1"],
    # colset2 contains cols for case_type_4 (from ct set 3) — negative control
    "colset2": ["case_type_col4_4_1_1"],
    # colset3 partially overlaps: shares col2_2_1_1 with colset1, and col4_4_1_1 with colset2
    "colset3": ["case_type_col2_2_1_1", "case_type_col4_4_1_1"],
}


def _compute_expected_case_types(
    org_access_policies: list[tuple[str, str]], org_share_sets: list[str]
) -> list[str]:
    """For reference data access, only org-level policies determine access (union of access + share).
    Case types are looked up from CASE_TYPE_SETS. User policies are intentionally ignored.
    """
    ct_sets = {ct_set for ct_set, _ in org_access_policies} | set(org_share_sets)
    result: set[str] = set()
    for s in ct_sets:
        result.update(CASE_TYPE_SETS.get(s, []))
    return sorted(result)


def _compute_expected_case_type_sets(
    org_access_policies: list[tuple[str, str]], org_share_sets: list[str]
) -> list[str]:
    """Only the case type sets referenced in org-level policies (access ∪ share) are accessible.
    User policies are intentionally ignored — tests verify this explicitly."""
    ct_sets = {ct_set for ct_set, _ in org_access_policies} | set(org_share_sets)
    return sorted(ct_sets)


def _compute_expected_case_type_col_sets(
    org_access_policies: list[tuple[str, str]],
) -> list[str]:
    """Col set access comes exclusively from org access policies — not from share policies and not
    from user-level policies. The col set is taken directly from each access policy tuple and is
    independent of the case type set, supporting inconsistent pairings."""
    return sorted({col_set for _, col_set in org_access_policies})


def _generate_label(
    org_access: list[tuple[str, str]],
    org_share: list[str],
    user_access: list[tuple[str, str]],
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


def _get_case_type_from_col(col_code: str) -> str:
    """Extract the case type name from a case_type_col code by naming convention:
    case_type_col{ct}_{dim}_{occ}_{col_rank} → case_type{ct}"""
    m = re.match(r"^case_type_col(\d+)_", col_code)
    assert m, f"Cannot extract case type index from col code: '{col_code}'"
    return f"case_type{m.group(1)}"


def _compute_expected_case_type_cols(
    org_access_policies: list[tuple[str, str]],
    org_share_sets: list[str],
) -> list[str]:
    """Accessible cols = those in accessible col sets whose embedded case type is accessible.

    Col set access = org access policies only (not share).
    Accessible case types = org access policies + org share policies (union).
    The intersection is restrictive: a col is only included if its referenced case type
    (embedded in the col code as case_type_col{ct}_...) is in the accessible case types.
    """
    accessible_case_types = set(
        _compute_expected_case_types(org_access_policies, org_share_sets)
    )
    accessible_col_sets = _compute_expected_case_type_col_sets(org_access_policies)
    result: set[str] = set()
    for colset in accessible_col_sets:
        for col_code in CASE_TYPE_COL_SETS.get(colset, []):
            if _get_case_type_from_col(col_code) in accessible_case_types:
                result.add(col_code)
    return sorted(result)


EDGE_CASES: list[EdgeCaseSpec] = [
    EdgeCaseSpec(
        user_name=f"org_user{org_idx + 1}_{usr_idx + 1}",
        org_name=f"org{org_idx + 1}",
        label=_generate_label(org_access, org_share, user_access, user_share),
        org_access_policies=org_access,
        org_share_policy_sets=org_share,
        user_access_policies=user_access,
        user_share_policy_sets=user_share,
        expected_case_types=_compute_expected_case_types(org_access, org_share),
        expected_case_type_sets=_compute_expected_case_type_sets(org_access, org_share),
        expected_case_type_col_sets=_compute_expected_case_type_col_sets(org_access),
        expected_case_type_cols=_compute_expected_case_type_cols(org_access, org_share),
    )
    for org_idx, ((_, org_access), (_, org_share)) in _org_combos
    for usr_idx, ((_, user_access), (_, user_share)) in _user_combos
]


# Lookup by user_name for use in tests:
#   EDGE_CASE_BY_USER["org_user1_2"].expected_case_types
#   EDGE_CASE_BY_USER["org_user1_2"].description
EDGE_CASE_BY_USER: dict[str, EdgeCaseSpec] = {s.user_name: s for s in EDGE_CASES}
