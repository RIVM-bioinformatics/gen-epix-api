# BaseUnitOfWork

> 146 nodes

## Key Concepts

- **BaseUnitOfWork** (241 connections) — `gen_epix/fastapp/unit_of_work.py`
- **BatchUploader** (59 connections) — `gen_epix/commondb/services/upload.py`
- **UploadResult** (52 connections) — `gen_epix/commondb/domain/model/upload.py`
- **fastapp/unit_of_work.py** (52 connections) — `gen_epix/fastapp/unit_of_work.py`
- **UploadBatchCommandMixin** (42 connections) — `gen_epix/commondb/domain/command/base.py`
- **model/upload.py** (41 connections) — `gen_epix/commondb/domain/model/upload.py`
- **BaseBatchUploadResult** (40 connections) — `gen_epix/commondb/domain/model/upload.py`
- **services/upload.py** (34 connections) — `gen_epix/commondb/services/upload.py`
- **services/case/upload.py** (32 connections) — `gen_epix/casedb/services/case/upload.py`
- **UploadSamplesCommand** (31 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **EtlStatus** (24 connections) — `gen_epix/commondb/domain/enum.py`
- **services/omop/upload.py** (24 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **services/seq/upload.py** (23 connections) — `gen_epix/seqdb/services/seq/upload.py`
- **upload_upsert_batch.py** (16 connections) — `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- **.is_null()** (14 connections) — `gen_epix/commondb/services/upload.py`
- **.upsert_batch()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_identifiers()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_link_id()** (13 connections) — `gen_epix/commondb/services/upload.py`
- **PersonBatchUploader** (12 connections) — `gen_epix/omopdb/services/omop/upload.py`
- **SampleBatchUploader** (12 connections) — `gen_epix/seqdb/services/seq/upload.py`
- **.create_identifiers()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.create_objects()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.get_parents_for_upload()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.verify_children()** (12 connections) — `gen_epix/commondb/services/upload.py`
- **.create_child_identifiers()** (11 connections) — `gen_epix/commondb/services/upload.py`
- *... and 121 more nodes in this community*

## Relationships

- [commondb/domain/literal.py](commondb-domain-literal.py.md) (37 shared connections)
- [CrudOperation](CrudOperation.md) (31 shared connections)
- [_crud_cascade_delete](_crud_cascade_delete.md) (24 shared connections)
- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (23 shared connections)
- [SeqSARepository](SeqSARepository.md) (23 shared connections)
- [UploadCasesCommand](UploadCasesCommand.md) (19 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (19 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (18 shared connections)
- [get_case_abac_from_command](get_case_abac_from_command.md) (12 shared connections)
- [SeqDictRepository](SeqDictRepository.md) (12 shared connections)
- [CaseService](CaseService.md) (12 shared connections)
- [test_commondb_upload.py](test_commondb_upload.py.md) (10 shared connections)

## Source Files

- `gen_epix/casedb/services/case/upload.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/domain/command/base.py`
- `gen_epix/commondb/domain/enum.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/commondb/services/upload.py`
- `gen_epix/fastapp/unit_of_work.py`
- `gen_epix/fastapp/user_manager.py`
- `gen_epix/omopdb/services/omop/upload.py`
- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/services/seq/__init__.py`
- `gen_epix/seqdb/services/seq/service.py`
- `gen_epix/seqdb/services/seq/upload.py`
- `gen_epix/seqdb/services/seq/upload_upsert_batch.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `test/commondb/unit/upload/test_commondb_upload.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`

## Audit Trail

- EXTRACTED: 891 (99%)
- INFERRED: 5 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*