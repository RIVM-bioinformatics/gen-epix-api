# TestCaseUpload

> 21 nodes

## Key Concepts

- **TestCaseUpload** (10 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **CaseUploadSetup** (6 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._create_case()** (6 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Env** (6 connections)
- **.setup()** (5 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._setup_casedb_app()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._setup_seqdb_app()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **get_test_client()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.test_case_upload()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **.test_case_validation()** (4 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._encode_pairing_function()** (2 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **fixture** (2 connections)
- **UUID** (2 connections)
- **Execute all case CRUD and similar commands in case_crud_commands** (2 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **._decode_pairing_function()** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Any** (1 connections)
- **Case** (1 connections)
- **scenario_ids** (1 connections)
- **skip** (1 connections)
- **Add sequencing and assembly protocols to seqdb, as well as identifier issuers.** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **Only for y values < 100, otherwise switch to Cantor's pairing function** (1 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`

## Relationships

- [CrudOperation](CrudOperation.md) (5 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (4 shared connections)
- [CaseForUpload](CaseForUpload.md) (1 shared connections)

## Source Files

- `test/casedb/integration/case_upload/test_casedb_case_upload.py`

## Audit Trail

- EXTRACTED: 36 (92%)
- INFERRED: 3 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*