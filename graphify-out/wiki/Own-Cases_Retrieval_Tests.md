# Own-Cases Retrieval Tests

> 46 nodes · cohesion 0.10

## Key Concepts

- **test_casedb_retrieve_is_own_cases.py** (20 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`
- **case_service_retrieve_is_own_cases()** (18 connections) — `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
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
- *... and 21 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (10 shared connections)
- [Case Access Rights ABAC](Case_Access_Rights_ABAC.md) (4 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (3 shared connections)
- [Exists Filters](Exists_Filters.md) (3 shared connections)
- [Case Ownership & File Commands](Case_Ownership_&_File_Commands.md) (2 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (2 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (1 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/retrieve_is_own_cases.py`
- `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_is_own_cases.py`

## Audit Trail

- EXTRACTED: 126 (95%)
- INFERRED: 6 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*