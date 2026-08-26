# Seqdb Upload Batch Processing

> 118 nodes · cohesion 0.04

## Key Concepts

- **BatchUploader** (59 connections) — `gen_epix/commondb/services/upload.py`
- **UploadBatchCommandMixin** (42 connections) — `gen_epix/commondb/domain/command/base.py`
- **BaseBatchUploadResult** (40 connections) — `gen_epix/commondb/domain/model/upload.py`
- **services/upload.py** (34 connections) — `gen_epix/commondb/services/upload.py`
- **services/omop/upload.py** (24 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **.is_null()** (14 connections) — `gen_epix/commondb/services/upload.py`
- **.upsert_batch()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_identifiers()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_link_id()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.create_identifiers()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.create_objects()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.get_parents_for_upload()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_children()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **PersonBatchUploader** (12 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **.create_child_identifiers()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.create_children()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.parent_result_items()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.update_children()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_batch()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **person_validator.py** (11 connections) — `gen_epix/omopdb/services/omop/person_validator.py`
- **omop/service.py** (11 connections) — `gen_epix/omopdb/services/omop/service.py`
- **UploadResultWithIdentifiers** (10 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._get_parents_and_children()** (10 connections) — `gen_epix/commondb/services/upload.py`
- **.update_objects()** (10 connections) — `gen_epix/commondb/services/upload.py`
- **BaseOmopService** (10 connections) — `gen_epix/omopdb/services/omop/base.py`
- *... and 93 more nodes in this community*

## Relationships

- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (30 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (29 shared connections)
- [Person Upload Command](Person_Upload_Command.md) (12 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (12 shared connections)
- [Case Batch Upload](Case_Batch_Upload.md) (11 shared connections)
- [OMOP Domain CRUD Commands](OMOP_Domain_CRUD_Commands.md) (9 shared connections)
- [Seqdb Upload Test Suite](Seqdb_Upload_Test_Suite.md) (9 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (9 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (5 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (5 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (5 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/services/case/upload.py`
- `gen_epix/commondb/domain/command/base.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/commondb/services/upload.py`
- `gen_epix/omopdb/services/omop/base.py`
- `gen_epix/omopdb/services/omop/person_validator.py`
- `gen_epix/omopdb/services/omop/retrieve_person.py`
- `gen_epix/omopdb/services/omop/service.py`
- `gen_epix/omopdb/services/omop/upload.py`

## Audit Trail

- EXTRACTED: 433 (99%)
- INFERRED: 5 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*