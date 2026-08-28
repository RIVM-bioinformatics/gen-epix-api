# BaseEtlResult

> 21 nodes · cohesion 0.10

## Key Concepts

- **BaseEtlResult** (19 connections) — `gen_epix/commondb/domain/model/base.py`
- **.add_error()** (4 connections) — `gen_epix/commondb/domain/model/base.py`
- **.add_warning()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_errors()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.get_warnings()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.set_error_status()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_errors()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_infos()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_log_code()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **.has_warnings()** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **BaseModel** (2 connections)
- **Append an ERROR-severity log item and update the status.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Override to set the concrete class's error status value.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Append a WARN-severity log item.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return True if any log item has ERROR severity.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return True if any log item has WARN severity.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return True if any log item has INFO severity.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return True if any log item carries the given code.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return a list of log items with ERROR severity.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Return a list of log items with WARN severity.** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Pydantic BaseModel that declares ``logs`` and provides log accumulation and…** (1 connections) — `gen_epix/commondb/domain/model/base.py`

## Relationships

- [EtlLogItem](EtlLogItem.md) (7 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (2 shared connections)
- [test_omopdb_upload_base_result.py](test_omopdb_upload_base_result.py.md) (2 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (1 shared connections)
- [entity.py](entity.py.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/base.py`

## Audit Trail

- EXTRACTED: 34 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*