# Sequence Format Enums

> 20 nodes · cohesion 0.11

## Key Concepts

- **._validate_seq_format()** (5 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_format()** (5 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._validate_qc_result()** (5 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._serialize_seq_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._serialize_format()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **.qc_result()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **._serialize_qc_result()** (4 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **field_serializer** (3 connections)
- **field_validator** (3 connections)
- **QualityControlResult** (3 connections)
- **FormatType** (2 connections)
- **SeqFormat** (2 connections)
- **computed_field** (1 connections)
- **Serialize the format enum to its integer value.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Convert a supplied quality result, defaulting missing values to pending.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Serialize the quality result as its stable integer representation.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Return the manual quality result if provided, otherwise the automated one.…** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Convert a supplied value to a supported sequence representation format.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Serialize the seq_format enum to its integer value.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Convert the supplied value to the content format enum used by the subclass.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`

## Relationships

- [Commondb Base Models](Commondb_Base_Models.md) (8 shared connections)
- [Base Sequence Model](Base_Sequence_Model.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/base.py`

## Audit Trail

- EXTRACTED: 31 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*