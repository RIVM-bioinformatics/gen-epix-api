# Tracking Unit Of Work

> 8 nodes · cohesion 0.29

## Key Concepts

- **TrackingUnitOfWork** (8 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **.__init__()** (4 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **Seq** (2 connections)
- **.uow()** (2 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **.__init__()** (2 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **Track the transaction outcome for the conversion service test.** (1 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **.commit()** (1 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **.rollback()** (1 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`

## Relationships

- [Sequence Format Conversion](Sequence_Format_Conversion.md) (4 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`

## Audit Trail

- EXTRACTED: 13 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*