# Seqdb Locus & Protocol CRUD

> 64 nodes · cohesion 0.03

## Key Concepts

- **seq/service.py** (52 connections) — `gen_epix/seqdb/services/seq/service.py`
- **crud_protocol.py** (13 connections) — `gen_epix/seqdb/services/seq/crud_protocol.py`
- **crud_locus.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_locus.py`
- **crud_read_set.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_read_set.py`
- **crud_seq_profile_identifier.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile_identifier.py`
- **crud_taxon.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_taxon.py`
- **crud_taxon_set.py** (11 connections) — `gen_epix/seqdb/services/seq/crud_taxon_set.py`
- **seq_service_crud_protocol()** (8 connections) — `gen_epix/seqdb/services/seq/crud_protocol.py`
- **seq_service_crud_locus()** (6 connections) — `gen_epix/seqdb/services/seq/crud_locus.py`
- **seq_service_crud_read_set()** (6 connections) — `gen_epix/seqdb/services/seq/crud_read_set.py`
- **seq_service_crud_seq_profile_identifier()** (6 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile_identifier.py`
- **seq_service_crud_taxon()** (6 connections) — `gen_epix/seqdb/services/seq/crud_taxon.py`
- **seq_service_crud_taxon_set()** (6 connections) — `gen_epix/seqdb/services/seq/crud_taxon_set.py`
- **services/seq/__init__.py** (6 connections) — `gen_epix/seqdb/services/seq/__init__.py`
- **.retrieve_seq_distance_last_modified()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **UUID** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **UUID** (2 connections)
- **datetime** (2 connections)
- **Locus** (1 connections)
- **Implement seqdb CRUD service operations for services.seq.crud_locus.** (1 connections) — `gen_epix/seqdb/services/seq/crud_locus.py`
- **Handle CRUD operations for locus entities. Args: self: Sequence service…** (1 connections) — `gen_epix/seqdb/services/seq/crud_locus.py`
- *... and 39 more nodes in this community*

## Relationships

- [Seq Service Interface](Seq_Service_Interface.md) (14 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (14 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (7 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (5 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (4 shared connections)
- [Best Sequence Retrieval](Best_Sequence_Retrieval.md) (4 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (3 shared connections)
- [Range Filters](Range_Filters.md) (2 shared connections)
- [Protocol & Profile Type Enums](Protocol_&_Profile_Type_Enums.md) (2 shared connections)
- [Sequence Format Conversion](Sequence_Format_Conversion.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/__init__.py`
- `gen_epix/seqdb/services/seq/crud_locus.py`
- `gen_epix/seqdb/services/seq/crud_protocol.py`
- `gen_epix/seqdb/services/seq/crud_read_set.py`
- `gen_epix/seqdb/services/seq/crud_seq_profile_identifier.py`
- `gen_epix/seqdb/services/seq/crud_taxon.py`
- `gen_epix/seqdb/services/seq/crud_taxon_set.py`
- `gen_epix/seqdb/services/seq/service.py`

## Audit Trail

- EXTRACTED: 155 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*