# Read User Policy Filter

> 17 nodes · cohesion 0.25

## Key Concepts

- **ReadUserPolicy** (24 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **.filter()** (8 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **User** (7 connections)
- **.get_admin_user_ids_own_organization()** (7 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **UUID** (6 connections)
- **._get_org_and_user_ids()** (6 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **._get_admin_user_ids()** (5 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **._filter_read_one()** (4 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **._filter_read_some()** (4 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **.setup_method()** (4 connections) — `test/commondb/unit/policies/test_read_user_policy.py`
- **._check_invalid_filter_input()** (3 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **.__init__()** (3 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **._is_no_abac_user()** (3 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **Command** (2 connections)
- **Any** (1 connections)
- **BaseAbacService** (1 connections)
- **Set up test fixtures.** (1 connections) — `test/commondb/unit/policies/test_read_user_policy.py`

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (9 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (4 shared connections)
- [Read User Policy Tests](Read_User_Policy_Tests.md) (3 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (1 shared connections)
- [OMOP Read User Policy](OMOP_Read_User_Policy.md) (1 shared connections)
- [Seqdb Read User Policy](Seqdb_Read_User_Policy.md) (1 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (1 shared connections)
- [User Read Policy Tests](User_Read_Policy_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/policies/read_user_policy.py`
- `test/commondb/unit/policies/test_read_user_policy.py`

## Audit Trail

- EXTRACTED: 50 (91%)
- INFERRED: 5 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*