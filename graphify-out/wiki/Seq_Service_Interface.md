# Seq Service Interface

> 115 nodes · cohesion 0.02

## Key Concepts

- **BaseSeqService** (135 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **UUID** (37 connections)
- **crud_seq_identifier.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_seq_identifier.py`
- **crud_seq_taxonomy.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_seq_taxonomy.py`
- **SeqIdentifierCrudCommand** (7 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **SeqTaxonomyCrudCommand** (7 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **Handle a CRUD command for sequence entities. Args: cmd: Typed sequence CRUD…** (6 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **seq_service_crud_seq_identifier()** (6 connections) — `gen_epix/seqdb/services/seq/crud_seq_identifier.py`
- **seq_service_crud_seq_taxonomy()** (6 connections) — `gen_epix/seqdb/services/seq/crud_seq_taxonomy.py`
- **.crud_allele()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ast_measurement()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ast_prediction()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_locus()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_locus_code_map()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_locus_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_pcr_measurement()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_protocol()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_protocol_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_read_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_read_set_identifier()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ref_allele()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ref_seq()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_sample()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_sample_data_collection_link()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_sample_identifier()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- *... and 90 more nodes in this community*

## Relationships

- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (37 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (14 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (14 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (7 shared connections)
- [Sample Retrieval Commands](Sample_Retrieval_Commands.md) (6 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (5 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (5 shared connections)
- [Phylogenetic Tree Calculation](Phylogenetic_Tree_Calculation.md) (4 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (3 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/seq/crud_seq_identifier.py`
- `gen_epix/seqdb/services/seq/crud_seq_taxonomy.py`
- `gen_epix/seqdb/services/seq/upload.py`

## Audit Trail

- EXTRACTED: 317 (98%)
- INFERRED: 5 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*