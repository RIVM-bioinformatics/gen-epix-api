# Case Upload Batch Models

> 107 nodes · cohesion 0.03

## Key Concepts

- **model/upload.py** (42 connections) — `gen_epix/commondb/domain/model/upload.py`
- **model/seq/upload.py** (41 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **commondb/domain/literal.py** (38 connections) — `gen_epix/commondb/domain/literal.py`
- **model/case/upload.py** (33 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **services/upload.py** (33 connections) — `gen_epix/commondb/services/upload.py`
- **BaseBatchForUpload** (26 connections) — `gen_epix/commondb/domain/model/upload.py`
- **etl/enum.py** (25 connections) — `gen_epix/etl/enum.py`
- **model/omop/upload.py** (25 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **services/omop/upload.py** (24 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **UploadPersonsCommand** (18 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **EtlStatusSet** (17 connections) — `gen_epix/etl/enum.py`
- **BaseOmopService** (14 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **PersonBatchUploadResult** (13 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **DataIssue** (11 connections) — `gen_epix/commondb/domain/model/upload.py`
- **PersonValidator** (11 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **services/omop/base.py** (10 connections) — `gen_epix/omopdb/services/omop/base.py`
- **person_validator.py** (9 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **omop/service.py** (9 connections) — `gen_epix/omopdb/services/omop/service.py`
- **BaseOmopService** (8 connections) — `gen_epix/omopdb/services/omop/base.py`
- **OmopService** (8 connections) — `gen_epix/omopdb/services/omop/service.py`
- **omop_service_upload_persons()** (8 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **CaseBatchForUpload** (7 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **PersonDataIssue** (7 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.validate_and_transform()** (7 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **._get_data_issues()** (6 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- *... and 82 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (34 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (24 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (24 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (22 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (19 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (16 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (15 shared connections)
- [Batch Upload Validation](Batch_Upload_Validation.md) (14 shared connections)
- [Case Upload Results](Case_Upload_Results.md) (14 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (9 shared connections)
- [User & Person Commands](User_&_Person_Commands.md) (8 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (7 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/commondb/domain/literal.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/commondb/services/upload.py`
- `gen_epix/etl/enum.py`
- `gen_epix/fastapp/enum.py`
- `gen_epix/omopdb/domain/command/omop.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `gen_epix/omopdb/services/client.py`
- `gen_epix/omopdb/services/omop/__init__.py`
- `gen_epix/omopdb/services/omop/base.py`
- `gen_epix/omopdb/services/omop/person_validator.py`
- `gen_epix/omopdb/services/omop/retrieve_person.py`
- `gen_epix/omopdb/services/omop/service.py`
- `gen_epix/omopdb/services/omop/upload.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`

## Audit Trail

- EXTRACTED: 417 (96%)
- INFERRED: 19 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*