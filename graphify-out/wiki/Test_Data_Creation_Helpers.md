# Test Data Creation Helpers

> 62 nodes · cohesion 0.07

## Key Concepts

- **.get_obj()** (46 connections) — `test/casedb/casedb_test_client.py`
- **User** (39 connections)
- **Disease** (9 connections) — `gen_epix/casedb/domain/model/ontology.py`
- **.create_case_set()** (9 connections) — `test/casedb/casedb_test_client.py`
- **.create_ref_col()** (9 connections) — `test/casedb/casedb_test_client.py`
- **.create_concept_set()** (8 connections) — `test/casedb/casedb_test_client.py`
- **.update_association_case_data_collection()** (8 connections) — `test/casedb/casedb_test_client.py`
- **.create_case()** (7 connections) — `test/casedb/casedb_test_client.py`
- **.create_case_data_collection_link()** (7 connections) — `test/casedb/casedb_test_client.py`
- **.create_organization_access_case_policy()** (7 connections) — `test/casedb/casedb_test_client.py`
- **.create_user_access_case_policy()** (7 connections) — `test/casedb/casedb_test_client.py`
- **.read_case_types_with_any_right()** (7 connections) — `test/casedb/casedb_test_client.py`
- **.create_case_type()** (6 connections) — `test/casedb/casedb_test_client.py`
- **.create_col()** (6 connections) — `test/casedb/casedb_test_client.py`
- **.create_concept()** (6 connections) — `test/casedb/casedb_test_client.py`
- **.create_etiology()** (6 connections) — `test/casedb/casedb_test_client.py`
- **.create_genetic_distance_protocol()** (6 connections) — `test/casedb/casedb_test_client.py`
- **.create_user_share_case_policy()** (6 connections) — `test/casedb/casedb_test_client.py`
- **.read_user_access_case_policies_with_any_right()** (6 connections) — `test/casedb/casedb_test_client.py`
- **DataCollection** (6 connections)
- **UUID** (6 connections)
- **._convert_case_code_to_date()** (5 connections) — `test/casedb/casedb_test_client.py`
- **.create_col_set()** (5 connections) — `test/casedb/casedb_test_client.py`
- **.create_organization_share_case_policy()** (5 connections) — `test/casedb/casedb_test_client.py`
- **.create_ref_dim()** (5 connections) — `test/casedb/casedb_test_client.py`
- *... and 37 more nodes in this community*

## Relationships

- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (42 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (27 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (10 shared connections)
- [Case ABAC Policies](Case_ABAC_Policies.md) (8 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (2 shared connections)
- [Case Operational Data Models](Case_Operational_Data_Models.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)
- [Case Data Printing Helpers](Case_Data_Printing_Helpers.md) (1 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (1 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/ontology.py`
- `test/casedb/casedb_test_client.py`

## Audit Trail

- EXTRACTED: 218 (100%)
- INFERRED: 1 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*