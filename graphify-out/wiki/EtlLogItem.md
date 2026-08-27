# EtlLogItem

> 17 nodes · cohesion 0.12

## Key Concepts

- **EtlLogItem** (25 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_errors()** (3 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.add_info()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_infos()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **._serialize_severity()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **._validate_severity()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_errors()** (3 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.get_errors()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.test_add_logs_single_non_error_item_keeps_status()** (2 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`
- **Get all data issues that are errors.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **field_serializer** (1 connections)
- **field_validator** (1 connections)
- **Append an INFO-severity log item.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return a list of log items with INFO severity.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Represents a log item for an ETL result accumulator, containing a timestamp,…** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Get all data issues that are errors.** (1 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **Get all data issues that are errors.** (1 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`

## Relationships

- [BaseEtlResult](BaseEtlResult.md) (7 shared connections)
- [TestUploadResult](TestUploadResult.md) (4 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (2 shared connections)
- [test_omopdb_upload_base_result.py](test_omopdb_upload_base_result.py.md) (2 shared connections)
- [model/omop/upload.py](model-omop-upload.py.md) (2 shared connections)
- [entity.py](entity.py.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (2 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (1 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/commondb/domain/model/base.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `test/omopdb/unit/services/omop/upload/test_omopdb_upload_base_result.py`

## Audit Trail

- EXTRACTED: 40 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*