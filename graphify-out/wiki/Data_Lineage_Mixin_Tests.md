# Data Lineage Mixin Tests

> 18 nodes · cohesion 0.14

## Key Concepts

- **TestDataLineageMixin** (11 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **._field_info()** (7 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_provenance_id_annotation_is_optional_uuid()** (3 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_provenance_id_field_default_is_none()** (3 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_source_traceback_annotation_is_optional_str()** (3 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_source_traceback_field_default_is_none()** (3 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_source_traceback_max_length()** (3 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_provenance_id_annotation_exists()** (2 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_source_traceback_annotation_exists()** (2 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **FieldInfo** (1 connections)
- **Tests for the DataLineageMixin class. DataLineageMixin is a plain mixin (not a…** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **DataLineageMixin should declare a provenance_id annotation.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **DataLineageMixin should declare a source_traceback annotation.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **The provenance_id Field should have a default of None.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **The source_traceback Field should have a default of None.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **The source_traceback Field should enforce max_length=255.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **The provenance_id annotation should allow UUID | None.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **The source_traceback annotation should allow str | None.** (1 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`

## Relationships

- [OMOP Model Validators](OMOP_Model_Validators.md) (2 shared connections)

## Source Files

- `test/omopdb/unit/domain/test_omopdb_model_validators.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*