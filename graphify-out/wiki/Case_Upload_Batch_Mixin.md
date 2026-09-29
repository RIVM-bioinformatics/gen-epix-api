# Case Upload Batch Mixin

> 109 nodes · cohesion 0.04

## Key Concepts

- **BatchUploader** (67 connections) — `gen_epix/commondb/services/upload.py`
- **BaseBatchUploadResult** (45 connections) — `gen_epix/commondb/domain/model/upload.py`
- **UploadBatchCommandMixin** (44 connections) — `gen_epix/commondb/domain/command/base.py`
- **PersonBatchUploader** (19 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **.is_null()** (15 connections) — `gen_epix/commondb/services/upload.py`
- **.upsert_batch()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_identifiers()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.create_identifiers()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.get_parents_for_upload()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_children()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_link_id()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **UploadResultWithIdentifiers** (11 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.create_child_identifiers()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.create_children()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.create_objects()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.parent_result_items()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.update_children()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_batch()** (11 connections) — `gen_epix/commondb/services/upload.py`
- **._get_parents_and_children()** (10 connections) — `gen_epix/commondb/services/upload.py`
- **.update_objects()** (10 connections) — `gen_epix/commondb/services/upload.py`
- **.create_parent_identifiers()** (9 connections) — `gen_epix/commondb/services/upload.py`
- **.get_parent_results()** (9 connections) — `gen_epix/commondb/services/upload.py`
- **.retrieve_parent_id_by_intra_parent_linked_child_id()** (9 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_children_identifiers()** (9 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_parents()** (9 connections) — `gen_epix/commondb/services/upload.py`
- *... and 84 more nodes in this community*

## Relationships

- [Sample Batch Upload](Sample_Batch_Upload.md) (24 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (24 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (24 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (20 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (8 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (6 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (4 shared connections)
- [Case Upload Results](Case_Upload_Results.md) (3 shared connections)
- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (3 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (3 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/case/upload.py`
- `gen_epix/commondb/domain/command/base.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/commondb/services/upload.py`
- `gen_epix/omopdb/services/omop/upload.py`

## Audit Trail

- EXTRACTED: 359 (95%)
- INFERRED: 20 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*