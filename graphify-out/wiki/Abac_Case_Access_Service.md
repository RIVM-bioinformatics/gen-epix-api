# Abac Case Access Service

> 20 nodes · cohesion 0.17

## Key Concepts

- **AbacService** (18 connections) — `gen_epix/casedb/services/abac.py`
- **UUID** (7 connections)
- **._get_access_dict()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._get_access_intersect()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.get_case_type_share_abac_dict()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._get_share_dict()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._get_share_intersect()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.update_user_own_organization()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.get_case_abac()** (4 connections) — `gen_epix/casedb/services/abac.py`
- **.get_ref_data_access()** (4 connections) — `gen_epix/casedb/services/abac.py`
- **Command** (4 connections)
- **OrganizationShareCasePolicy** (3 connections)
- **UserShareCasePolicy** (3 connections)
- **._invalidate_cache()** (2 connections) — `gen_epix/casedb/services/abac.py`
- **.register_policies()** (2 connections) — `gen_epix/casedb/services/abac.py`
- **OrganizationAccessCasePolicy** (2 connections)
- **User** (2 connections)
- **UserAccessCasePolicy** (2 connections)
- **BaseAbacService** (1 connections)
- **Behaviour: - Update User.organization - Create UserAccessCasePolicies for the…** (1 connections) — `gen_epix/casedb/services/abac.py`

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (9 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (5 shared connections)
- [ABAC Test Base](ABAC_Test_Base.md) (1 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (1 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [Case ABAC Tests](Case_ABAC_Tests.md) (1 shared connections)
- [Case Query & Rights Retrieval](Case_Query_&_Rights_Retrieval.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/abac.py`

## Audit Trail

- EXTRACTED: 52 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*