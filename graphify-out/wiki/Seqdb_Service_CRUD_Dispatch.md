# Seqdb Service CRUD Dispatch

> 123 nodes · cohesion 0.02

## Key Concepts

- **BaseSeqService** (135 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **UUID** (36 connections)
- **.crud_allele()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ast_measurement()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ast_prediction()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_locus()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_locus_code_map()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_locus_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_pcr_measurement()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_protocol()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_protocol_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_protocol_set_member()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_read_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_read_set_identifier()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ref_allele()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ref_seq()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_sample()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_sample_data_collection_link()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_sample_identifier()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq_category()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq_category_set()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq_classification()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq_distance()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq_identifier()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- *... and 98 more nodes in this community*

## Relationships

- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (42 shared connections)
- [Sample Query Retrieval](Sample_Query_Retrieval.md) (26 shared connections)
- [Seqdb Distance Calculation Tests](Seqdb_Distance_Calculation_Tests.md) (7 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (6 shared connections)
- [Best Seq Per Sample](Best_Seq_Per_Sample.md) (5 shared connections)
- [RefSeq/Taxon CRUD Stubs](RefSeq-Taxon_CRUD_Stubs.md) (4 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (3 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (2 shared connections)
- [Allele CRUD](Allele_CRUD.md) (2 shared connections)
- [AstPrediction CRUD](AstPrediction_CRUD.md) (2 shared connections)
- [PcrMeasurement CRUD](PcrMeasurement_CRUD.md) (2 shared connections)
- [ProtocolSet CRUD](ProtocolSet_CRUD.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/seq/upload.py`

## Audit Trail

- EXTRACTED: 293 (100%)
- INFERRED: 1 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*