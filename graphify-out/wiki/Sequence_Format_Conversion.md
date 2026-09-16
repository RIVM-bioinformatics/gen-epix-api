# Sequence Format Conversion

> 42 nodes · cohesion 0.09

## Key Concepts

- **test_seqdb_convert_seq_format.py** (27 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **seq_service_convert_seq_format()** (19 connections) — `gen_epix/seqdb/services/seq/convert_seq_format.py`
- **SequenceRepository** (16 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **encode_ascii_as_gzip_base64()** (13 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **create_seq()** (13 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **convert_seq_format.py** (11 connections) — `gen_epix/seqdb/services/seq/convert_seq_format.py`
- **SeqFormat** (8 connections) — `gen_epix/seqdb/domain/enum.py`
- **test_convert_seq_format_all_supported_directions()** (7 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **.crud()** (6 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_bidirectional_gzb64_to_plain()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_case_normalization()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_multiple_sequences()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_preserves_contig_identity()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_same_format_no_op()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_validates_batch_before_updating()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_with_gaps()** (5 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_empty_ids_no_op()** (4 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **test_convert_seq_format_rejects_invalid_format_pairs()** (4 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **UUID** (2 connections)
- **parametrize** (2 connections)
- **UUID** (2 connections)
- **test_convert_seq_format_rejects_duplicate_ids()** (2 connections) — `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`
- **Encapsulates supported serialized representations of sequence content.** (1 connections) — `gen_epix/seqdb/domain/enum.py`
- **Encode a string as a gzip-compressed base64 string.** (1 connections) — `gen_epix/seqdb/domain/model/seq/base.py`
- **Implement stored sequence representation conversion.** (1 connections) — `gen_epix/seqdb/services/seq/convert_seq_format.py`
- *... and 17 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (5 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (4 shared connections)
- [Tracking Unit Of Work](Tracking_Unit_Of_Work.md) (4 shared connections)
- [FASTA Retrieval Tests](FASTA_Retrieval_Tests.md) (3 shared connections)
- [Sequence Model Validation Tests](Sequence_Model_Validation_Tests.md) (3 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (3 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (2 shared connections)
- [File & Result Format Enums](File_&_Result_Format_Enums.md) (2 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (2 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (2 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/enum.py`
- `gen_epix/seqdb/domain/model/seq/base.py`
- `gen_epix/seqdb/services/seq/convert_seq_format.py`
- `test/seqdb/unit/services/seq/convert_seq_format/test_seqdb_convert_seq_format.py`

## Audit Trail

- EXTRACTED: 112 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*