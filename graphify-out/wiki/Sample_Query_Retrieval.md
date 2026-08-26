# Sample Query Retrieval

> 127 nodes · cohesion 0.02

## Key Concepts

- **seq/service.py** (86 connections) — `gen_epix/seqdb/services/seq/service.py`
- **BaseSeqRepository** (24 connections) — `gen_epix/seqdb/domain/repository/seq.py`
- **UUID** (13 connections)
- **crud_protocol.py** (12 connections) — `gen_epix/seqdb/services/seq/crud_protocol.py`
- **crud_seq_profile.py** (12 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **crud_ast_measurement.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_ast_measurement.py`
- **crud_locus.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_locus.py`
- **crud_locus_code_map.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_locus_code_map.py`
- **crud_locus_set.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_locus_set.py`
- **crud_ref_allele.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_ref_allele.py`
- **crud_seq_category_set.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_seq_category_set.py`
- **crud_seq_identifier.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_seq_identifier.py`
- **seq_service_crud_seq_profile()** (10 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **crud_seq_taxonomy.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_seq_taxonomy.py`
- **RetrieveSamplesByQueryCommand** (9 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **seq_service_crud_protocol()** (9 connections) — `gen_epix/seqdb/services/seq/crud_protocol.py`
- **retrieve_sample.py** (9 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **seq_service_crud_ast_measurement()** (8 connections) — `gen_epix/seqdb/services/seq/crud_ast_measurement.py`
- **seq_service_crud_locus_code_map()** (8 connections) — `gen_epix/seqdb/services/seq/crud_locus_code_map.py`
- **seq_service_crud_locus()** (8 connections) — `gen_epix/seqdb/services/seq/crud_locus.py`
- **seq_service_crud_locus_set()** (8 connections) — `gen_epix/seqdb/services/seq/crud_locus_set.py`
- **seq_service_crud_ref_allele()** (8 connections) — `gen_epix/seqdb/services/seq/crud_ref_allele.py`
- **seq_service_crud_seq_category_set()** (8 connections) — `gen_epix/seqdb/services/seq/crud_seq_category_set.py`
- **seq_service_crud_seq_identifier()** (8 connections) — `gen_epix/seqdb/services/seq/crud_seq_identifier.py`
- **seq_service_crud_seq_taxonomy()** (8 connections) — `gen_epix/seqdb/services/seq/crud_seq_taxonomy.py`
- *... and 102 more nodes in this community*

## Relationships

- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (46 shared connections)
- [Seqdb Service CRUD Dispatch](Seqdb_Service_CRUD_Dispatch.md) (26 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (14 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (12 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (11 shared connections)
- [Seqdb Distance Calculation Tests](Seqdb_Distance_Calculation_Tests.md) (8 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (7 shared connections)
- [RefSeq/Taxon CRUD Stubs](RefSeq-Taxon_CRUD_Stubs.md) (4 shared connections)
- [Seq Dict Repository](Seq_Dict_Repository.md) (3 shared connections)
- [Seq SA Repository](Seq_SA_Repository.md) (3 shared connections)
- [Seqdb Enums](Seqdb_Enums.md) (3 shared connections)
- [Best Seq Per Sample](Best_Seq_Per_Sample.md) (3 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/repository/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/seq/crud_ast_measurement.py`
- `gen_epix/seqdb/services/seq/crud_common.py`
- `gen_epix/seqdb/services/seq/crud_locus.py`
- `gen_epix/seqdb/services/seq/crud_locus_code_map.py`
- `gen_epix/seqdb/services/seq/crud_locus_set.py`
- `gen_epix/seqdb/services/seq/crud_protocol.py`
- `gen_epix/seqdb/services/seq/crud_ref_allele.py`
- `gen_epix/seqdb/services/seq/crud_seq_category_set.py`
- `gen_epix/seqdb/services/seq/crud_seq_identifier.py`
- `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- `gen_epix/seqdb/services/seq/crud_seq_taxonomy.py`
- `gen_epix/seqdb/services/seq/retrieve_sample.py`
- `gen_epix/seqdb/services/seq/service.py`

## Audit Trail

- EXTRACTED: 348 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*