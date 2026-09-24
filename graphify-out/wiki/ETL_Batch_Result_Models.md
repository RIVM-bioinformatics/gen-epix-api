# ETL Batch Result Models

> 147 nodes · cohesion 0.03

## Key Concepts

- **UploadResult** (65 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Result** (46 connections) — `gen_epix/etl/model.py`
- **BatchResult** (43 connections) — `gen_epix/etl/model.py`
- **LoadResult** (27 connections) — `gen_epix/etl/model.py`
- **etl/model.py** (24 connections) — `gen_epix/etl/model.py`
- **TestBatchEtlResult** (23 connections) — `test/etl/test_model.py`
- **TestEtlResult** (23 connections) — `test/etl/test_model.py`
- **JobResult** (21 connections) — `gen_epix/etl/model.py`
- **etl/test_model.py** (21 connections) — `test/etl/test_model.py`
- **TestRunEtlResult** (13 connections) — `test/etl/test_model.py`
- **gen_epix/etl/__init__.py** (12 connections) — `gen_epix/etl/__init__.py`
- **ExtractResult** (11 connections) — `gen_epix/etl/model.py`
- **TransformResult** (11 connections) — `gen_epix/etl/model.py`
- **TestPolymorphicRoundTrip** (10 connections) — `test/etl/test_model.py`
- **.update_status_from_loads()** (8 connections) — `gen_epix/etl/model.py`
- **.update_status_from_transforms()** (8 connections) — `gen_epix/etl/model.py`
- **.set_failed()** (7 connections) — `gen_epix/etl/model.py`
- **.update_status_from_extractions()** (6 connections) — `gen_epix/etl/model.py`
- **.update_status_from_batches()** (6 connections) — `gen_epix/etl/model.py`
- **.set_success()** (6 connections) — `gen_epix/etl/model.py`
- **parametrize** (6 connections)
- **.add_results()** (5 connections) — `gen_epix/etl/model.py`
- **.set_completed()** (5 connections) — `gen_epix/etl/model.py`
- **Any** (5 connections)
- **._deserialize()** (5 connections) — `gen_epix/etl/model.py`
- *... and 122 more nodes in this community*

## Relationships

- [Case Upload Results](Case_Upload_Results.md) (30 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (25 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (19 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (8 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (7 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [Sequence Sample Upload Models](Sequence_Sample_Upload_Models.md) (6 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (4 shared connections)
- [Batch Upload Validation](Batch_Upload_Validation.md) (2 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (2 shared connections)
- [Case Data Collection Updates](Case_Data_Collection_Updates.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/etl/__init__.py`
- `gen_epix/etl/model.py`
- `test/etl/test_model.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`

## Audit Trail

- EXTRACTED: 347 (88%)
- INFERRED: 49 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*