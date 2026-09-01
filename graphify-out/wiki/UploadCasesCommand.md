# UploadCasesCommand

> 35 nodes

## Key Concepts

- **UploadCasesCommand** (25 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseBatchUploadResult** (23 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **CaseBatchUploader** (22 connections) — `gen_epix/casedb/services/case/upload.py`
- **case_service_upload_cases()** (11 connections) — `gen_epix/casedb/services/case/upload.py`
- **._validate_merged_content()** (9 connections) — `gen_epix/casedb/services/case/upload.py`
- **.verify_batch()** (9 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_case_data_collections()** (8 connections) — `gen_epix/casedb/services/case/upload.py`
- **._verify_abac_rights()** (8 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_case_validator()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_complete_case_type()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **._get_upload_samples_command()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **._verify_case_content()** (7 connections) — `gen_epix/casedb/services/case/upload.py`
- **.upload_samples()** (6 connections) — `gen_epix/casedb/services/case/upload.py`
- **._set_default_created_in_data_collection_id()** (5 connections) — `gen_epix/casedb/services/case/upload.py`
- **.upload_cases()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.upload_cases()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.upload_cases()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **UUID** (4 connections)
- **.verify_user_rights()** (3 connections) — `gen_epix/casedb/services/case/upload.py`
- **BaseCaseService** (1 connections)
- **Model** (1 connections)
- **Upload a batch of cases along with their associated data and return an upload…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **The result of uploading a batch of cases.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **Upload cases in batch.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Re-validate each case's content merged with what is already in the database, so…** (1 connections) — `gen_epix/casedb/services/case/upload.py`
- *... and 10 more nodes in this community*

## Relationships

- [BaseUnitOfWork](BaseUnitOfWork.md) (19 shared connections)
- [CaseValidator](CaseValidator.md) (9 shared connections)
- [.create_case_for_upload](create_case_for_upload.md) (6 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (5 shared connections)
- [test_casedb_upload.py](test_casedb_upload.py.md) (3 shared connections)
- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (3 shared connections)
- [test_casedb_case_validator.py](test_casedb_case_validator.py.md) (2 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (2 shared connections)
- [EndpointTestClient](EndpointTestClient.md) (1 shared connections)
- [TestVerifyUserRights](TestVerifyUserRights.md) (1 shared connections)
- [Command](Command.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/case/upload.py`
- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 120 (96%)
- INFERRED: 5 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*