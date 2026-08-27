# ParentUploadResult

> 17 nodes · cohesion 0.15

## Key Concepts

- **ParentUploadResult** (17 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_status_count()** (6 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_child_results_field_names()** (5 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_parent_results()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.convert_status()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.get_status_count()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.propagate_child_failures()** (4 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.resolve_status()** (3 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.update_status_with_data_issues()** (2 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Count the number of occurrences of each EtlStatus in this result (if…** (2 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Represents the upload result for a Parent model upload. This class must be…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Mark this result, and each of its own children, as FAILED if any nested child…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Update the upload status of this result based on the data issues found, adding…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Convert all occurrences of from_status to to_status in this result and all its…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Get the list of field names in this result class that contain lists of child…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Get the list of parent upload results in this batch upload result.** (1 connections) — `gen_epix/commondb/domain/model/upload.py`
- **Set this batch result's status based on the aggregate of its children. Only has…** (1 connections) — `gen_epix/commondb/domain/model/upload.py`

## Relationships

- [BaseUnitOfWork](BaseUnitOfWork.md) (8 shared connections)
- [model/omop/upload.py](model-omop-upload.py.md) (2 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (1 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (1 shared connections)
- [entity.py](entity.py.md) (1 shared connections)
- [test_commondb_upload.py](test_commondb_upload.py.md) (1 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (1 shared connections)
- [test_seqdb_upload.py](test_seqdb_upload.py.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/upload.py`

## Audit Trail

- EXTRACTED: 37 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*