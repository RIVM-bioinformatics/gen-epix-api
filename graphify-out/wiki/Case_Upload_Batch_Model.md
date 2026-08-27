# Case Upload Batch Model

> 66 nodes · cohesion 0.04

## Key Concepts

- **BaseBatchForUpload** (22 connections) — `gen_epix/commondb/domain/model/upload.py`
- **ParentForUpload** (17 connections) — `gen_epix/commondb/domain/model/upload.py`
- **SampleBatchForUpload** (17 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **CaseBatchForUpload** (8 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.get_parents_for_upload()** (8 connections) — `gen_epix/commondb/domain/model/upload.py`
- **computed_field** (7 connections)
- **Model** (6 connections)
- **model_validator** (6 connections)
- **Self** (6 connections)
- **._serialize_id_fields()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_child_ids()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_intra_parent_links()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_parent_ids()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_all_children_for_upload()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.replace_child_id()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.validate_child_parent_id()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **._validate_id_field()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.validate_parent_id()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **UUID** (4 connections)
- **._validate_upload_result()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.has_read_sets()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.has_seqs()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.get_n_parents()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_parent_class()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_identifiers()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- *... and 41 more nodes in this community*

## Relationships

- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (6 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (4 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (3 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (3 shared connections)
- [Seq Distance Generation Script](Seq_Distance_Generation_Script.md) (3 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (2 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (2 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (2 shared connections)
- [Identifiers Validation Mixin](Identifiers_Validation_Mixin.md) (2 shared connections)
- [Seqdb Upload Test Suite](Seqdb_Upload_Test_Suite.md) (2 shared connections)
- [Person Upload Batch Model](Person_Upload_Batch_Model.md) (1 shared connections)
- [Commondb Upload Test Suite](Commondb_Upload_Test_Suite.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`

## Audit Trail

- EXTRACTED: 124 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*