# Organization Model Validation

> 6 nodes

## Key Concepts

- **._validate_model()** (4 connections) — `gen_epix/commondb/domain/model/organization.py`
- **._validate_issuer_fields()** (4 connections) — `gen_epix/commondb/domain/model/organization.py`
- **model_validator** (2 connections)
- **Self** (2 connections)
- **Derive the id, if not provided, or otherwise verify that it is correctly…** (1 connections) — `gen_epix/commondb/domain/model/organization.py`
- **Ensure that either identifier_issuer_id or identifier_issuer_code is set.** (1 connections) — `gen_epix/commondb/domain/model/organization.py`

## Relationships

- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (1 shared connections)
- [IdentifierForUpload](IdentifierForUpload.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/organization.py`

## Audit Trail

- EXTRACTED: 8 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*