# Case Upload Test Setup

> 21 nodes · cohesion 0.11

## Key Concepts

- **TestCaseUpload** (12 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **CaseUploadSetup** (10 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._create_case()** (6 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.setup()** (5 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._setup_casedb_app()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._setup_seqdb_app()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.test_case_upload()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.test_case_validation()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **get_test_client()** (3 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **fixture** (2 connections)
- **UUID** (2 connections)
- **._encode_pairing_function()** (2 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Any** (1 connections)
- **Case** (1 connections)
- **scenario_ids** (1 connections)
- **skip** (1 connections)
- **Add sequencing and assembly protocols to seqdb, as well as identifier issuers.** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Only for y values < 100, otherwise switch to Cantor's pairing function** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Execute all case CRUD and similar commands in case_crud_commands** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Execute all case CRUD and similar commands in case_crud_commands** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._decode_pairing_function()** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`

## Relationships

- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (8 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (1 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (1 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (1 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (1 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (1 shared connections)

## Source Files

- `test/casedb/integration/case_upload/test_casedb_case_upload.py`

## Audit Trail

- EXTRACTED: 35 (80%)
- INFERRED: 9 (20%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*