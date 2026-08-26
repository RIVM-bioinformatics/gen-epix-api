# Own Cases Policy Tests

> 41 nodes · cohesion 0.10

## Key Concepts

- **BaseIsOwnCasesTestCase** (16 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.attach_abac_policy()** (15 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.create_command()** (13 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.set_retrieve_cases_result()** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **TestRetrieveIsOwnCasesOwnership** (10 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.create_case()** (9 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.create_case_type_access_abac()** (9 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_case_not_owned_when_no_private_data_collection_matches()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_case_owned_via_created_in_data_collection_id()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_case_owned_via_data_collection_link()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_mixed_ownership_returns_correct_mapping()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_no_private_data_collections_makes_all_cases_not_own()** (7 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **_FakeCaseAbacPolicy** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **TestRetrieveIsOwnCasesEdgeCases** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **TestRetrieveIsOwnCasesUnauthorized** (6 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_empty_case_ids_returns_empty_mapping()** (5 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_no_cases_returned_yields_empty_mapping()** (5 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **TestRetrieveIsOwnCasesFullAccess** (5 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **scenario_ids** (4 connections)
- **UUID** (4 connections)
- **.test_full_access_bypasses_permission_check()** (4 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.test_unauthorized_case_type_raises()** (4 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **Any** (3 connections)
- **.test_case_type_not_in_partial_permissions_raises()** (3 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **.get_content()** (2 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- *... and 16 more nodes in this community*

## Relationships

- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (18 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (3 shared connections)
- [Read User Policy Tests](Read_User_Policy_Tests.md) (1 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`

## Audit Trail

- EXTRACTED: 104 (96%)
- INFERRED: 4 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*