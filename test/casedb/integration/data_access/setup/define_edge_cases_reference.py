"""
This module defines the EDGE_CASES data structure, both used to:
1) generate test data in setup_case_data_reference and
2) drive the test scenarios in test_casedb_edge_cases_refdata_access.

EDGE_CASES is a comprehensive set of edge cases for testing ABAC access control on CaseDB reference data (CaseTypes, CaseTypeSets,
and Col sets). Each edge case represents a unique combination of organizational membership and policies at both the org and user level,
along with the expected access results for that scenario.

The expectations are defined based on the principle that for reference data access,
only org-level policies (both access and share) should determine access,
while user-level policies should not grant any additional access beyond what the org-level policies provide.
(implementation: expectations are *NOT* derived from querying the created policies (set up in setup_case_data_reference) directly,
but from this principle and the org-level policies in each case).


- CaseTypes can also be accessed by being referred to by a Col
    - so we configure what CaseTypes are referred to by Cols in ColSets
    - this is by naming convention (code: col{ct}_{ref_dim}_{occ}_{col_rank}) where ct is the CaseType number (e.g. 1, 2, 3, 4)

Method:
- define ColSets
    - with sets of Cols that are partly overlapping
    between ColSets to test that access is correctly determined at the ColSet level, not just the CaseType level
- define Cols, and dims for each ColSet
- add tests that user-level policies do not grant access to additional ColSets, Cols, RefCols, or RefDims beyond what org-level policies grant access to


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
    - org_access_policies: (case_type_set, ColSet) pairs granted at org level via OrganizationAccessCasePolicy
    - org_share_policy_sets: CaseTypeSets granted at org level via OrganizationShareCasePolicy
    - user_access_policies: (case_type_set, ColSet) pairs granted directly to this user via UserAccessCasePolicy
    - user_share_policy_sets: CaseTypeSets granted directly to this user via UserShareCasePolicy
    - expected_case_types: expected accessible CaseType names (union of org access + org share)
    - expected_case_type_sets: expected accessible CaseTypeSet names (union of org access + org share)
    - expected_col_sets: expected accessible ColSet names (from org access policies only — share policies do not grant Col access)
    - expected_cols: expected accessible Col codes — intersection of Cols in accessible ColSets
      with the accessible CaseTypes (Cols reference a CaseType via naming convention col{ct}_...)

    For reference data (CaseTypes / CaseTypeSets / ColSets), only org-level policies determine access.
    User-level policies (both access and share) are intentionally ignored — tests verify this.

    Both setup fixtures iterate EDGE_CASES to drive user/org creation and policy setup.
    Adding a new edge case is a single entry in EDGE_CASES below.
    Tests can use EDGE_CASE_BY_USER[user_name].expected_case_types for assertions
    and .description for human-readable output.
    """

    user_name: str
    org_name: str
    label: str
    org_access_policies: list[tuple[str, str]]  # [(case_type_set, ColSet), ...]
    org_share_policy_sets: list[str]
    user_access_policies: list[tuple[str, str]]  # [(case_type_set, ColSet), ...]
    user_share_policy_sets: list[str]
    expected_case_types: list[str]
    expected_case_type_sets: list[str]
    expected_col_sets: list[str]
    expected_cols: list[str]
    expected_ref_cols: list[str]
    expected_ref_dims: list[str]
    expected_cases: list[str]

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
            f"expected_col_sets=[{_fmt(self.expected_col_sets)}], "
            f"expected_cols=[{_fmt(self.expected_cols)}], "
            f"expected_ref_cols=[{_fmt(self.expected_ref_cols)}], "
            f"expected_ref_dims=[{_fmt(self.expected_ref_dims)}], "
            f"expected_cases=[{_fmt(self.expected_cases)}]"
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
# For reference data (CaseTypes / CaseTypeSets), access = union of:
#   OrganizationAccessCasePolicy ∪ OrganizationShareCasePolicy
# User-level policies (both access and share) have NO influence.

# Each entry is a list of (case_type_set, ColSet) tuples granted at org level via
# OrganizationAccessCasePolicy. The ColSet is independent of the CaseTypeSet, enabling tests
# of inconsistent pairings (e.g. case_type_set1 with col_set2).
_ORG_ACCESS_COMBOS: list[list[tuple[str, str]]] = [
    [],  # no org access policy
    [("case_type_set1", "col_set1")],  # set1 with matching col_set1
    [("case_type_set1", "col_set2")],  # set1 with inconsistent col_set2
    [("case_type_set2", "col_set1")],  # set2 with inconsistent col_set1 (reversed)
    [("case_type_set2", "col_set3")],  # set2 with overlapping col_set3
]

# Each entry is the list of CaseTypeSets granted at org level via OrganizationShareCasePolicy.
# Share policies do NOT grant ColSet access — only access policies determine ColSet access.
_ORG_SHARE_COMBOS: list[list[str]] = [
    [],  # no org share policy
    ["case_type_set2"],  # org has shared access to case_type_set2
    ["case_type_set3"],  # org has shared access to case_type_set3
]

# Each entry is a list of (case_type_set, ColSet) tuples granted directly to one user
# via UserAccessCasePolicy. User policies do NOT affect reference data access — tests verify this.
_USER_ACCESS_COMBOS: list[list[tuple[str, str]]] = [
    [],  # no user-level access policy
    [("case_type_set1", "col_set1")],  # user access matching common org access
    [("case_type_set2", "col_set2")],  # user access on a different set/col_set
]

# Each entry is the list of CaseTypeSets granted directly to one user via UserShareCasePolicy.
_USER_SHARE_COMBOS: list[list[str]] = [
    [],  # no user-level share policy
    ["case_type_set1"],  # user share policy on case_type_set1
    ["case_type_set3"],  # user share policy on case_type_set3
]

# Define CaseTypeSet
# should contain CaseTypes
CASE_TYPE_SETS = {
    "case_type_set1": ["case_type1", "case_type2"],
    "case_type_set2": ["case_type2", "case_type3"],
    "case_type_set3": ["case_type4"],
}


# RefCol (code: ref_col{ref_dim}_{rank})

# (code: col{ct}_{ref_dim}_{occ}_{col_rank})
COL_SETS = {
    # col_set1 contains cols for case_type_1, case_type_2, and case_type_3 (from ct sets 1 and 2)
    "col_set1": ["col1_1_1_1", "col2_2_1_1", "col3_3_1_1"],
    # col_set2 contains cols for case_type_4 (from ct set 3) — negative control
    "col_set2": ["col4_4_1_1"],
    # col_set3 partially overlaps: shares col2_2_1_1 with col_set1, and col4_4_1_1 with col_set2
    "col_set3": ["col2_2_1_1", "col4_4_1_1"],
}


def _compute_expected_case_types(
    org_access_policies: list[tuple[str, str]], org_share_sets: list[str]
) -> list[str]:
    """For reference data access, only org-level policies determine access (union of access + share).
    CaseTypes are looked up from CASE_TYPE_SETS. User policies are intentionally ignored.
    """
    case_type_sets = {x for x, _ in org_access_policies} | set(org_share_sets)
    result: set[str] = set()
    for s in case_type_sets:
        result.update(CASE_TYPE_SETS.get(s, []))
    return sorted(result)


def _compute_expected_case_type_sets(
    org_access_policies: list[tuple[str, str]], org_share_sets: list[str]
) -> list[str]:
    """Only the CaseTypeSets referenced in org-level policies (access ∪ share) are accessible.
    User policies are intentionally ignored — tests verify this explicitly."""
    case_type_sets = {x for x, _ in org_access_policies} | set(org_share_sets)
    return sorted(case_type_sets)


def _compute_expected_col_sets(
    org_access_policies: list[tuple[str, str]],
) -> list[str]:
    """ColSet access comes exclusively from org access policies — not from share policies and not
    from user-level policies. The ColSet is taken directly from each access policy tuple and is
    independent of the CaseTypeSet, supporting inconsistent pairings."""
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
        return f"{org_desc} — should access org-level CaseTypes/sets"
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
    """Extract the CaseType name from a Col code by naming convention:
    col{ct}_{ref_dim}_{occ}_{col_rank} → case_type{ct}"""
    m = re.match(r"^col(\d+)_", col_code)
    assert m, f"Cannot extract CaseType index from col code: '{col_code}'"
    return f"case_type{m.group(1)}"


def _compute_expected_cols(
    org_access_policies: list[tuple[str, str]],
    org_share_sets: list[str],
) -> list[str]:
    """Accessible Cols = those in accessible ColSets whose embedded CaseType is accessible.

    ColSet access = org access policies only (not share).
    Accessible CaseTypes = org access policies + org share policies (union).
    The intersection is restrictive: a Col is only included if its referenced CaseType
    (embedded in the Col code as col{ct}_...) is in the accessible CaseTypes.
    """
    accessible_case_type_codes = set(
        _compute_expected_case_types(org_access_policies, org_share_sets)
    )
    accessible_col_set_codes = _compute_expected_col_sets(org_access_policies)
    result: set[str] = set()
    for col_set_code in accessible_col_set_codes:
        for col_code in COL_SETS.get(col_set_code, []):
            if _get_case_type_from_col(col_code) in accessible_case_type_codes:
                result.add(col_code)
    return sorted(result)


def _parse_col(col_code: str) -> tuple[str, str, str, str]:
    """Parse col{ct}_{ref_dim}_{occ}_{rank} → (ct, ref_dim, occ, rank)."""
    m = re.match(r"^col(\d+)_(\d+)_(\d+)_(\d+)$", col_code)
    assert m, f"Cannot parse col code: '{col_code}'"
    return m.group(1), m.group(2), m.group(3), m.group(4)


def _compute_expected_ref_cols(col_codes: list[str]) -> list[str]:
    """RefCols referenced by the accessible Cols: ref_col{ref_dim}_{rank}."""
    result: set[str] = set()
    for col_code in col_codes:
        _, ref_dim, _, rank = _parse_col(col_code)
        result.add(f"ref_col{ref_dim}_{rank}")
    return sorted(result)


def _compute_expected_ref_dims(col_codes: list[str]) -> list[str]:
    """RefDims referenced by the accessible Cols: ref_dim{ref_dim}."""
    result: set[str] = set()
    for code in col_codes:
        _, ref_dim, _, _ = _parse_col(code)
        result.add(f"ref_dim{ref_dim}")
    return sorted(result)


def _compute_expected_cases(
    org_access_policies: list[tuple[str, str]],
    org_share_sets: list[str],
    user_access_policies: list[tuple[str, str]],
    user_share_sets: list[str],
) -> list[str]:
    """Determine the expected cases accessible for operational data.

    For operational data, a user must satisfy BOTH org-level AND user-level policies
    to gain access to CaseTypes (unlike reference data where only org-level matters):
    - access CaseTypes = CaseTypes in (org_access CaseTypeSets ∩ user_access CaseTypeSets)
    - share CaseTypes  = CaseTypes in (org_share CaseTypeSets ∩ user_share CaseTypeSets)
    - result           = union of access CaseTypes ∪ share CaseTypes

    For each accessible CaseType, exactly one case exists (naming: case{n}_1 for case_type{n}).
    """
    org_access_sets = {x for x, _ in org_access_policies}
    user_access_sets = {x for x, _ in user_access_policies}
    org_share_sets_set = set(org_share_sets)
    user_share_sets_set = set(user_share_sets)

    accessible_case_types: set[str] = set()
    for case_type_set in org_access_sets & user_access_sets:
        accessible_case_types.update(CASE_TYPE_SETS.get(case_type_set, []))
    for case_type_set in org_share_sets_set & user_share_sets_set:
        accessible_case_types.update(CASE_TYPE_SETS.get(case_type_set, []))

    result: list[str] = []
    for ct in accessible_case_types:
        m = re.match(r"^case_type(\d+)$", ct)
        assert m, f"Cannot extract CaseType index from: '{ct}'"
        result.append(f"case{m.group(1)}_1")
    return sorted(result)


# 135 combinations — 5 org_access x
#                 3 org_share x 3 user_access x 3 user_share (15 orgs x 9 users)
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
        expected_col_sets=_compute_expected_col_sets(org_access),
        expected_cols=_compute_expected_cols(org_access, org_share),
        expected_ref_cols=_compute_expected_ref_cols(
            _compute_expected_cols(org_access, org_share)
        ),
        expected_ref_dims=_compute_expected_ref_dims(
            _compute_expected_cols(org_access, org_share)
        ),
        expected_cases=_compute_expected_cases(
            org_access, org_share, user_access, user_share
        ),
    )
    for org_idx, ((_, org_access), (_, org_share)) in _org_combos
    for usr_idx, ((_, user_access), (_, user_share)) in _user_combos
]


# Lookup by user_name for use in tests:
#   EDGE_CASE_BY_USER["org_user1_2"].expected_case_types
#   EDGE_CASE_BY_USER["org_user1_2"].description
EDGE_CASE_BY_USER: dict[str, EdgeCaseSpec] = {s.user_name: s for s in EDGE_CASES}
