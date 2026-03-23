# the access to operational data needs a setup (based on relevant combinations)
#
# this file defines the setup for the edge cases related to access to operational data
# Access to the cases and case cols depend on the access policies
# they do not depend on the share policies
#
# a case can only be accesssed if
#   there is an organization access policy that grants access to the organization of the user
# AND a user access policy that grants access to the user, both for the case in question
# a case has a case type and a is in a data collection
# it can be in another data collection
# (sidenote how you would retrieve this:
# For each case retrieve which data collection it belongs to through the created_in_data_collection_id field and the
# case data collection links table (link table)
#  -> Data collections)


# For the edge cases related to access to operational data, we need to set up specific combinations of:
# - organization access policies (org_access)
#    case type (ct) of case is in the case type set of the org access policy yes/no
#    data collection (dc) of case is in the data collection set of the org access policy yes/no
#    column (col) of case is in the column set of the org access policy yes/no
#         for this we will create 2 column sets, one with all columns and one with partial columns
#    so this gives us 8 combinations for org access policies
#    but they can be simplified to 4 combinations by only including the org access policies with the following combinations of case type set, data collection set and column set:
#    dc in set:
#      ct in set:
#        1. col in set (partial colset with col1 and col2)
#        2. col in another set (partial colset with col2 and col3)
#      3. ct not in set (rest irrelant, because no access to case if ct not in set)
#    4. dc not in set: (rest irrelant, because no access to case if dc not in set)
# - user access policies (user_access)
#    comparable combinations as org access policies
#    dc in set:
#      ct in set:
# .       For the columns access
#        1. col in set (partial colset with col1 and col2)
#        2. col in another set (partial colset woth col2 and col3)
#      3. ct not in set (rest irrelant, because no access to case if ct not in set)
#    4. dc not in set: (rest irrelant, because no access to case if dc not in set)
# we need to combine the 4 org access policy combinations with the 4 user access policy combinations,
# which gives us 16 combinations
# For each of the 16 combinations, we would use the same single case when we
# assume a case belonging to a single data collection
# BUT we want to test a case being in 2 data collections
# and each data collection should have the above 16 combinations of org access and user access policies represented
#
# and we need 3 data collections and 4 cases for 4 different situations:
# Each case[ct_n]_n has case type ct[ct_n] where ct_n is the caste type number
# case1 is in dc1 (dc1 configured with colset1)
# case2 is in dc2 (dc2 configured with colset2)
# case3 is in dc1 and dc2 (dc1 and dc2 are configured with partially overlapping colsers colset and colset2)
# case4 is in dc3

# to test the negative case of not having access to a case, we can use a case that is in a data collection that is not in any of the org access policies or user access policies
# case 5 is in dc4, and dc4 is not in any of the org access policies or user access policies
# we also need a case that has a case type that is not in any of the org access policies or user access policies
# case 6 has a case type that is not in any of the org access policies or user access policies

# Asssumptions:
# 1) If a case is in 2 data collections and through dc1 it has access to the partial colset
# and through dc2 it has access to the whole colset,
# then the user should have access to the whole colset of the case.
# 2) The user only has access to the cases and cols that are in the intersection of the org access policies and user access policies,
# so if either the org access policy or the user access policy does not include the case type, data collection or column,
# then the user should not have access to the case or column.


# We need the following capabilities in the casedb test client:
#
# - Create cases with specific columns
# - Create cases in specific data collections
# - Read cols from the json in the content field of a case

# For testing:
# For each edge case, we need to make assertions for both the cases and the columns in a case

# ---------------------------------------------------------------------------
# Design notes
# ---------------------------------------------------------------------------
# Policy structure: (case_type_set, data_collection, col_set)
# A policy grants access to cases whose case_type is in case_type_set AND that
# belong to data_collection, with cols restricted to col_set.
#
# OrganizationAccessCasePolicy and UserAccessCasePolicy are each unique per
# (org/user, data_collection) — so each combo may have AT MOST ONE triple per dc.
# Where a dc contains multiple case_types (dc1: ct1+ct3, dc2: ct2+ct3), the policy
# uses a multi-ct case_type_set (case_type_set_dc1, case_type_set_dc2).
#
# Case access requires BOTH org AND user to have a matching (ct_set, dc) triple.
# Accessible cols for a case = union over all accessible dcs of:
#   (org col_set for (ct, dc)) ∩ (user col_set for (ct, dc))
# filtered to cols whose embedded case_type matches the case.
#
# Share policies are NOT modelled — operational data access and col access are
# determined exclusively by access policies.
#
# Active cases and their data collections:
#   case1_1: case_type1, in dc1
#   case2_1: case_type2, in dc2
#   case3_1: case_type3, in dc1 AND dc2  (tests union of col access across dcs)
#   case4_1: case_type4, in dc3
#
# Negative controls (never accessible):
#   case5_1: case_type5, in dc4    (dc not covered by any policy)
#   case6_1: case_type6, in dc1    (case_type not in any case_type_set)
#
# Total combinations: 5 org_access × 5 user_access = 25

import re
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Case type sets — one case_type per set
# ---------------------------------------------------------------------------
CASE_TYPE_SETS_OP: dict[str, list[str]] = {
    # Single-ct sets — used when only one case_type is accessed via a dc
    "case_type_set1": ["case_type1"],   # ct1 only — dc1 single-ct access
    "case_type_set4": ["case_type4"],   # ct4 only — dc3 access
    # Multi-ct sets — required because (org/user, dc) policies are unique per dc;
    # dc1 contains ct1 and ct3, dc2 contains ct2 and ct3
    "case_type_set_dc1": ["case_type1", "case_type3"],  # ct1+ct3 — broad dc1 access
    "case_type_set_dc2": ["case_type2", "case_type3"],  # ct2+ct3 — broad dc2 access
    # case_type2, case_type3 do not have single-ct sets: they only appear in multi-ct dc sets
    # case_type5 and case_type6 are intentionally NOT in any set (negative controls)
}

# ---------------------------------------------------------------------------
# Data collections and the cases that live in each
# ---------------------------------------------------------------------------
# dc1, dc2, dc3 are covered by policy combos.
# dc4 is NOT covered by any policy (negative control for dc access).
DATA_COLLECTIONS_OP: dict[str, list[str]] = {
    "dc1": ["case1_1", "case3_1", "case6_1"],  # case3_1 spans dc1+dc2; case6_1: ct6 not in any set
    "dc2": ["case2_1", "case3_1"],
    "dc3": ["case4_1"],
    "dc4": ["case5_1"],  # negative control: dc not in any policy
}

# ---------------------------------------------------------------------------
# Col sets
# ---------------------------------------------------------------------------
# Naming convention for cols: col{ct}_{ref_dim}_{occ}_{col_rank}
#
# dc1 contains case_type1 (ref_dim 1, 3 cols) and case_type3 (ref_dim 2, 2 cols):
#   col_set_dc1    : full   — all cols for ct1 and ct3 in dc1
#   col_set_dc1_12 : partial — cols 1+2 per ct (shared by _12 and _23: col*_*_1_2)
#   col_set_dc1_23 : partial — cols 2+3 per ct
#
# dc2 contains case_type2 (ref_dim 3, 3 cols) and case_type3 (ref_dim 4, 2 cols):
#   col_set_dc2    : full
#   col_set_dc2_12 : partial — cols 1+2 per ct
#   col_set_dc2_23 : partial — cols 2+3 per ct
#
# dc3 contains case_type4 (ref_dim 5, 2 cols):
#   col_set_dc3    : full
#   col_set_dc3_1  : partial — col 1 only
COL_SETS_OP: dict[str, list[str]] = {
    "col_set_dc1": [
        "col1_1_1_1",
        "col1_1_1_2",
        "col1_1_1_3",
        "col3_2_1_1",
        "col3_2_1_2",
    ],
    "col_set_dc1_12": ["col1_1_1_1", "col1_1_1_2", "col3_2_1_1"],
    "col_set_dc1_23": ["col1_1_1_2", "col1_1_1_3", "col3_2_1_2"],
    "col_set_dc2": [
        "col2_3_1_1",
        "col2_3_1_2",
        "col2_3_1_3",
        "col3_4_1_1",
        "col3_4_1_2",
    ],
    "col_set_dc2_12": ["col2_3_1_1", "col2_3_1_2", "col3_4_1_1"],
    "col_set_dc2_23": ["col2_3_1_2", "col2_3_1_3", "col3_4_1_2"],
    "col_set_dc3": ["col4_5_1_1", "col4_5_1_2"],
    "col_set_dc3_1": ["col4_5_1_1"],
    # Negative-control case types: one col each so the setup user can create them.
    # These are NOT referenced in any access policy combo — they are only used so that
    # cases of these case types can be written in the setup fixture (write_col_ids must
    # be non-empty even for cases that should never be readable by test edge case users).
    "col_set_ct5": ["col5_6_1_1"],  # col for case_type5 (dc4, no policy covers dc4)
    "col_set_ct6": ["col6_7_1_1"],  # col for case_type6 (in dc1, ct not in any set)
}

# ---------------------------------------------------------------------------
# Policy combos
# ---------------------------------------------------------------------------
# Each entry is a list of (case_type_set, data_collection, col_set) triples.
# Case access requires BOTH org AND user to include a matching (ct_set, dc) triple.

# 5 org-level access combos — at most ONE triple per dc (one policy per (org, dc))
_ORG_ACCESS_COMBOS_OP: list[list[tuple[str, str, str]]] = [
    # 0: no access
    [],
    # 1: case1_1 via dc1, full cols (ct1 only)
    [("case_type_set1", "dc1", "col_set_dc1")],
    # 2: case1_1 via dc1, partial cols (12) (ct1 only) — tests org restricting to a subset
    [("case_type_set1", "dc1", "col_set_dc1_12")],
    # 3: broad multi-dc — ct1+ct3 via dc1 (one policy), ct2+ct3 via dc2 (one policy), full cols
    [
        ("case_type_set_dc1", "dc1", "col_set_dc1"),
        ("case_type_set_dc2", "dc2", "col_set_dc2"),
    ],
    # 4: case4_1 via dc3, full cols
    [("case_type_set4", "dc3", "col_set_dc3")],
]

# 5 user-level access combos — at most ONE triple per dc
_USER_ACCESS_COMBOS_OP: list[list[tuple[str, str, str]]] = [
    # 0: no access → no cases accessible
    [],
    # 1: case1_1 via dc1, partial cols (12) — org(1)∩user(1): full∩12=12; org(2)∩user(1): 12∩12=12
    [("case_type_set1", "dc1", "col_set_dc1_12")],
    # 2: case1_1 via dc1, partial cols (23) — org(1)∩user(2): full∩23=23; org(2)∩user(2): 12∩23={col2}
    [("case_type_set1", "dc1", "col_set_dc1_23")],
    # 3: multi-dc, mixed partial — tests case3_1 getting union of dc1 and dc2 cols
    [
        ("case_type_set_dc1", "dc1", "col_set_dc1_12"),
        ("case_type_set_dc2", "dc2", "col_set_dc2_23"),
    ],
    # 4: case4_1 via dc3, partial cols (col 1 only)
    [("case_type_set4", "dc3", "col_set_dc3_1")],
]


# ---------------------------------------------------------------------------
# Expected cases and cols computation
# ---------------------------------------------------------------------------
def _build_col_lookup(
    policies: list[tuple[str, str, str]],
) -> dict[tuple[str, str], set[str]]:
    """Build (case_type, dc) → union of col codes from all matching policies."""
    lookup: dict[tuple[str, str], set[str]] = {}
    for ct_set, dc, col_set_name in policies:
        for ct in CASE_TYPE_SETS_OP.get(ct_set, []):
            lookup.setdefault((ct, dc), set()).update(COL_SETS_OP.get(col_set_name, []))
    return lookup


def _compute_expected_cases_op(
    org_access: list[tuple[str, str, str]],
    user_access: list[tuple[str, str, str]],
) -> dict[str, list[str]]:
    """Return {case_code: sorted accessible col_codes} for this policy combination.

    For each (case_type, dc) pair covered by BOTH org and user:
      accessible_cols_via_dc = (org col_set ∩ user col_set), filtered to the case's ct.
    Total cols for a case = union across all accessible dcs.
    Cases with no accessible cols (no matching policy pair) are omitted.
    """
    org_lookup = _build_col_lookup(org_access)
    user_lookup = _build_col_lookup(user_access)

    result: dict[str, set[str]] = {}
    for dc, case_codes in DATA_COLLECTIONS_OP.items():
        for case_code in case_codes:
            m = re.match(r"^case(\d+)_\d+$", case_code)
            if not m:
                continue
            ct = f"case_type{m.group(1)}"
            key = (ct, dc)
            if key not in org_lookup or key not in user_lookup:
                continue  # no policy pair for this (ct, dc)

            ct_idx = m.group(1)
            accessible = {
                col
                for col in (org_lookup[key] & user_lookup[key])
                if col.startswith(f"col{ct_idx}_")
            }
            if accessible:
                result.setdefault(case_code, set()).update(accessible)

    return {case: sorted(cols) for case, cols in result.items()}


# ---------------------------------------------------------------------------
# Edge case spec
# ---------------------------------------------------------------------------
@dataclass
class EdgeCaseSpecOp:
    """
    Declarative specification for a single operational data access edge case.

    org_access_policies / user_access_policies: list of (case_type_set, dc, col_set) triples.
    expected_cases: {case_code: sorted list of accessible col codes}.
    A case appears only if at least one (ct, dc) pair is covered by both sides.
    """

    user_name: str
    org_name: str
    label: str
    org_access_policies: list[tuple[str, str, str]]
    user_access_policies: list[tuple[str, str, str]]
    expected_cases: dict[str, list[str]]

    @property
    def description(self) -> str:
        def _fmt(policies: list[tuple[str, str, str]]) -> str:
            if not policies:
                return "∅"
            return ", ".join(f"{ct}@{dc}[{cs}]" for ct, dc, cs in policies)

        lines = [
            f"[{self.user_name}@{self.org_name}] {self.label}",
            f"  org_access=[{_fmt(self.org_access_policies)}]",
            f"  user_access=[{_fmt(self.user_access_policies)}]",
            f"  → expected_cases={{"
            + ", ".join(f"{c}: {cols}" for c, cols in self.expected_cases.items())
            + "}",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Edge case list — 5 org_access × 5 user_access = 25 combinations
# ---------------------------------------------------------------------------
_org_combos_op = list(enumerate(_ORG_ACCESS_COMBOS_OP))
_user_combos_op = list(enumerate(_USER_ACCESS_COMBOS_OP))

EDGE_CASES_OP: list[EdgeCaseSpecOp] = [
    EdgeCaseSpecOp(
        user_name=f"org_user{org_idx + 1}_{usr_idx + 1}",
        org_name=f"org{org_idx + 1}",
        label=f"org_access=combo{org_idx}, user_access=combo{usr_idx}",
        org_access_policies=org_access,
        user_access_policies=user_access,
        expected_cases=_compute_expected_cases_op(org_access, user_access),
    )
    for org_idx, org_access in _org_combos_op
    for usr_idx, user_access in _user_combos_op
]

EDGE_CASES_OP_BY_USER: dict[str, EdgeCaseSpecOp] = {
    s.user_name: s for s in EDGE_CASES_OP
}
