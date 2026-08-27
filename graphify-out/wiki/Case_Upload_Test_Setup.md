# Case Upload Test Setup

> 29 nodes · cohesion 0.09

## Key Concepts

- **TestCaseUpload** (10 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **commondb/util.py** (9 connections) — `test/commondb/util.py`
- **retrieve_db_data_from_file()** (9 connections) — `test/commondb/util.py`
- **CaseUploadSetup** (6 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Env** (6 connections)
- **._create_case()** (6 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.setup()** (5 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._setup_casedb_app()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._setup_seqdb_app()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **get_test_client()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.test_case_upload()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.test_case_validation()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **fixture** (2 connections)
- **UUID** (2 connections)
- **._encode_pairing_function()** (2 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **UUID** (2 connections)
- **Any** (1 connections)
- **Case** (1 connections)
- **scenario_ids** (1 connections)
- **skip** (1 connections)
- **Add sequencing and assembly protocols to seqdb, as well as identifier issuers.** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Only for y values < 100, otherwise switch to Cantor's pairing function** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Execute all case CRUD and similar commands in case_crud_commands** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Execute all case CRUD and similar commands in case_crud_commands** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._decode_pairing_function()** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- *... and 4 more nodes in this community*

## Relationships

- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (7 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (4 shared connections)
- [Integration Test Client Helpers](Integration_Test_Client_Helpers.md) (2 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (2 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (1 shared connections)

## Source Files

- `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- `test/commondb/util.py`

## Audit Trail

- EXTRACTED: 51 (93%)
- INFERRED: 4 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*