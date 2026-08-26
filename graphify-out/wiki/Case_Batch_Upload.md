# Case Batch Upload

> 35 nodes · cohesion 0.11

## Key Concepts

- **UploadCasesCommand** (25 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseBatchUploadResult** (23 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **CaseBatchUploader** (22 connections) — `gen_epix/casedb/services/case/upload.py`
- **case_service_upload_cases()** (11 connections) — `gen_epix/casedb/services/case/upload.py`
- **._validate_merged_content()** (9 connections) — `gen_epix/casedb/services/case/upload.py`
- **.verify_batch()** (9 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_case_data_collections()** (8 connections) — `gen_epix/casedb/services/case/upload.py`
- **.upsert_batch()** (8 connections) — `gen_epix/casedb/services/case/upload.py`
- **._verify_abac_rights()** (8 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_case_validator()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_complete_case_type()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **._verify_case_content()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **.upload_samples()** (6 connections) — `gen_epix/casedb/services/case/upload.py`
- **._set_default_created_in_data_collection_id()** (5 connections) — `gen_epix/casedb/services/case/upload.py`
- **.upload_cases()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.upload_cases()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (4 connections)
- **.upload_cases()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.verify_user_rights()** (3 connections) — `gen_epix/casedb/services/case/upload.py`
- **.__init__()** (2 connections) — `gen_epix/casedb/services/case/upload.py`
- **Upload a batch of cases along with their associated data and return an upload…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **The result of uploading a batch of cases.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Upload cases in batch.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **BaseCaseService** (1 connections)
- **Extends batch upload to uploading the cases with this service, and the read…** (1 connections) — `gen_epix/casedb/services/case/upload.py`
- *... and 10 more nodes in this community*

## Relationships

- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (11 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (10 shared connections)
- [Case Data Validator](Case_Data_Validator.md) (9 shared connections)
- [Case Upload Feature Tests](Case_Upload_Feature_Tests.md) (6 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (4 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (3 shared connections)
- [Case Upload Tests](Case_Upload_Tests.md) (3 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (3 shared connections)
- [Case Validator Tests](Case_Validator_Tests.md) (2 shared connections)
- [CaseBatchUploader RBAC Tests](CaseBatchUploader_RBAC_Tests.md) (2 shared connections)
- [Casedb Endpoint Test Client](Casedb_Endpoint_Test_Client.md) (1 shared connections)
- [Case State Validation](Case_State_Validation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/case/upload.py`
- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 121 (96%)
- INFERRED: 5 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*