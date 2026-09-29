# Integration Test Client

> 62 nodes · cohesion 0.06

## Key Concepts

- **TestClient** (205 connections) — `gen_epix/commondb/test/test_client.py`
- **TestCreate** (25 connections) — `test/commondb/integration/build_db/create.py`
- **TestCreate** (21 connections) — `test/omopdb/integration/build_db/create.py`
- **TestUpdate** (11 connections) — `test/seqdb/integration/build_db/update.py`
- **skipif** (6 connections)
- **skipif** (5 connections)
- **._get_dummy_link_defaults()** (3 connections) — `gen_epix/commondb/test/test_client.py`
- **.print_identifier_issuers()** (3 connections) — `gen_epix/commondb/test/test_client.py`
- **.print_org_admin_policies()** (3 connections) — `gen_epix/commondb/test/test_client.py`
- **.test_create_object_already_exists()** (3 connections) — `test/commondb/integration/build_db/create.py`
- **.test_create_object_invalid_reference()** (3 connections) — `test/commondb/integration/build_db/create.py`
- **.test_create_org_admin_policy_raise()** (3 connections) — `test/commondb/integration/build_db/create.py`
- **.test_create_organization_raise()** (3 connections) — `test/commondb/integration/build_db/create.py`
- **.test_create_user_raise()** (3 connections) — `test/commondb/integration/build_db/create.py`
- **.test_create_data_collection_raise()** (3 connections) — `test/omopdb/integration/build_db/create.py`
- **.test_create_object_already_exists()** (3 connections) — `test/omopdb/integration/build_db/create.py`
- **.test_create_object_invalid_reference()** (3 connections) — `test/omopdb/integration/build_db/create.py`
- **.test_create_org_admin_policy_raise()** (3 connections) — `test/omopdb/integration/build_db/create.py`
- **.test_create_organization_raise()** (3 connections) — `test/omopdb/integration/build_db/create.py`
- **.test_create_user_raise()** (3 connections) — `test/omopdb/integration/build_db/create.py`
- **.test_read_organization_admin_emails_raise()** (3 connections) — `test/seqdb/integration/build_db/read.py`
- **.test_read_user_raise()** (3 connections) — `test/seqdb/integration/build_db/read.py`
- **.test_update_data_collection_raise()** (3 connections) — `test/seqdb/integration/build_db/update.py`
- **.is_sub_role()** (2 connections) — `gen_epix/commondb/test/test_client.py`
- **.test_create_data_collection_with_override_of_metadat()** (2 connections) — `test/commondb/integration/build_db/create.py`
- *... and 37 more nodes in this community*

## Relationships

- [Organization Test Helpers](Organization_Test_Helpers.md) (39 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (26 shared connections)
- [Organization Delete Tests](Organization_Delete_Tests.md) (15 shared connections)
- [User Anonymization Tests](User_Anonymization_Tests.md) (12 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (11 shared connections)
- [Data Collection CRUD Tests](Data_Collection_CRUD_Tests.md) (11 shared connections)
- [Manual Read Policy Tests](Manual_Read_Policy_Tests.md) (7 shared connections)
- [User & Organization Printing](User_&_Organization_Printing.md) (6 shared connections)
- [SQL Injection Tests](SQL_Injection_Tests.md) (4 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (3 shared connections)
- [Commondb Metadata Masking Tests](Commondb_Metadata_Masking_Tests.md) (3 shared connections)
- [Record Metadata Stamping Tests](Record_Metadata_Stamping_Tests.md) (3 shared connections)

## Source Files

- `gen_epix/commondb/test/test_client.py`
- `test/commondb/integration/build_db/create.py`
- `test/omopdb/integration/build_db/create.py`
- `test/seqdb/integration/build_db/read.py`
- `test/seqdb/integration/build_db/update.py`

## Audit Trail

- EXTRACTED: 252 (89%)
- INFERRED: 30 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*