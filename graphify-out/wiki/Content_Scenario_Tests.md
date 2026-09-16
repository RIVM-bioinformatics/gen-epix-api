# Content Scenario Tests

> 7 nodes · cohesion 0.29

## Key Concepts

- **TestContent** (9 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **.test_delete_all_operational_data()** (3 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **.test_retrieve_is_own_cases()** (3 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **.test_update_case_created_in_data_collection_endpoint()** (2 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **scenario_ids** (1 connections)
- **Happy-path test for RetrieveIsOwnCasesCommand. Finds an org user whose…** (1 connections) — `test/casedb/integration/content/test_casedb_content.py`
- **Delete operational content after all content scenarios have completed.** (1 connections) — `test/casedb/integration/content/test_casedb_content.py`

## Relationships

- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Range Filters](Range_Filters.md) (1 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (1 shared connections)

## Source Files

- `test/casedb/integration/content/test_casedb_content.py`

## Audit Trail

- EXTRACTED: 11 (79%)
- INFERRED: 3 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*