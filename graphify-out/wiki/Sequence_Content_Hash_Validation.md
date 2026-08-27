# Sequence Content Hash Validation

> 6 nodes · cohesion 0.40

## Key Concepts

- **._validate_model()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_content()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **model_validator** (2 connections)
- **Self** (2 connections)
- **Derive the sequence hash as the first 128 bits of the SHA256 hash of the lower…** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Validate that the content hash matches the content.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`

## Relationships

- [Entity Key Generation](Entity_Key_Generation.md) (1 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/base.py`

## Audit Trail

- EXTRACTED: 8 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*