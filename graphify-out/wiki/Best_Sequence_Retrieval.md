# Best Sequence Retrieval

> 71 nodes · cohesion 0.08

## Key Concepts

- **_get_best_id_per_sample()** (37 connections) — `gen_epix/seqdb/services/seq/retrieve_best.py`
- **test_seqdb_retrieve_best.py** (34 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **_mock_service()** (28 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **_row()** (25 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **retrieve_best.py** (17 connections) — `gen_epix/seqdb/services/seq/retrieve_best.py`
- **_profile_cmd()** (16 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **TestRankingLogic** (11 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **RetrieveBestSeqClassificationPerSampleCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **RetrieveBestSeqPerSampleCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **RetrieveBestSeqProfilePerSampleCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **seq_service_retrieve_best_seq_classification_per_sample()** (10 connections) — `gen_epix/seqdb/services/seq/retrieve_best.py`
- **seq_service_retrieve_best_seq_per_sample()** (10 connections) — `gen_epix/seqdb/services/seq/retrieve_best.py`
- **seq_service_retrieve_best_seq_profile_per_sample()** (10 connections) — `gen_epix/seqdb/services/seq/retrieve_best.py`
- **_classification_cmd()** (9 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **TestFilterConstruction** (8 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **_seq_cmd()** (7 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **.test_user_id_passed_to_read_fields()** (6 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **TestReturnPrimaryCategoryId** (6 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **UUID** (5 connections)
- **.retrieve_best_seq_classification_per_sample()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.retrieve_best_seq_per_sample()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.retrieve_best_seq_profile_per_sample()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.test_none_user_passes_none_user_id()** (5 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **.test_with_protocol_ids_passes_composite_filter()** (5 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- **.test_without_protocol_ids_passes_uuid_set_filter()** (5 connections) — `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`
- *... and 46 more nodes in this community*

## Relationships

- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (7 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (7 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (6 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (4 shared connections)
- [Composite Filters](Composite_Filters.md) (4 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (4 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (4 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (4 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (3 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (3 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (3 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (3 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/services/seq/retrieve_best.py`
- `gen_epix/seqdb/services/seq/service.py`
- `test/seqdb/unit/services/seq/retrieve_best/test_seqdb_retrieve_best.py`

## Audit Trail

- EXTRACTED: 245 (98%)
- INFERRED: 5 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*