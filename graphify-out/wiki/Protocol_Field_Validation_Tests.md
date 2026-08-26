# Protocol Field Validation Tests

> 53 nodes · cohesion 0.07

## Key Concepts

- **_make_protocol()** (28 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **ProtocolType** (13 connections) — `gen_epix/seqdb/domain/enum.py`
- **TestProtocolProps** (12 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **_minimal_protocol_data()** (10 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **TestProtocolGitCommitHash** (10 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **TestProtocolSerializers** (9 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_extra_field_set_when_not_required_raises()** (7 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **parametrize** (6 connections)
- **Protocol** (6 connections)
- **scenario_ids** (6 connections)
- **TestProtocolGitRepositoryUri** (6 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **TestProtocolHappyPaths** (6 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **TestProtocolTypeDependencies** (6 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_missing_required_field_raises()** (6 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_valid_instantiation_for_all_protocol_types()** (5 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **_create_field_description()** (3 connections) — `gen_epix/seqdb/domain/model/seq/protocol.py`
- **Any** (3 connections)
- **.test_hex_wrong_length_raises()** (3 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_invalid_uris_raise()** (3 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_valid_uris_accepted()** (3 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_optional_metadata_fields_accepted()** (3 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_locus_set_id_serialized_as_string()** (3 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_ref_seq_id_serialized_as_string()** (3 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_hex_string_with_0x_prefix_raises()** (2 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- **.test_non_hex_40_char_string_raises()** (2 connections) — `test/seqdb/unit/domain/test_seqdb_model.py`
- *... and 28 more nodes in this community*

## Relationships

- [Seqdb Enums](Seqdb_Enums.md) (12 shared connections)
- [Seq Format Validation](Seq_Format_Validation.md) (6 shared connections)
- [Entity Key Generation](Entity_Key_Generation.md) (2 shared connections)
- [Sample Query Retrieval](Sample_Query_Retrieval.md) (1 shared connections)
- [Seqdb Test Client](Seqdb_Test_Client.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/enum.py`
- `gen_epix/seqdb/domain/model/seq/protocol.py`
- `test/seqdb/unit/domain/test_seqdb_model.py`

## Audit Trail

- EXTRACTED: 111 (97%)
- INFERRED: 4 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*