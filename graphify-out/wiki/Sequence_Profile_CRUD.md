# Sequence Profile CRUD

> 11 nodes · cohesion 0.22

## Key Concepts

- **crud_seq_profile.py** (13 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **seq_service_crud_seq_profile()** (8 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **_get_not_implemented_message()** (5 connections) — `gen_epix/seqdb/services/seq/crud_common.py`
- **UUID** (2 connections)
- **CrudCommand** (1 connections)
- **Format an unsupported CRUD-operation message including the caller's roles.** (1 connections) — `gen_epix/seqdb/services/seq/crud_common.py`
- **SeqProfile** (1 connections)
- **Implement seqdb CRUD service operations for services.seq.crud_seq_profile.** (1 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **Handle CRUD operations for sequence-profile entities. Args: self: Sequence…** (1 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **# TODO: 3034 Check if seq_profile.seq_profile_type and…** (1 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`
- **# TODO: 3428 Delete all distances for these allele profiles as well** (1 connections) — `gen_epix/seqdb/services/seq/crud_seq_profile.py`

## Relationships

- [Filter Base Abstractions](Filter_Base_Abstractions.md) (2 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (2 shared connections)
- [New Profile Distance Tests](New_Profile_Distance_Tests.md) (2 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (2 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (1 shared connections)
- [Seqdb Locus & Protocol CRUD](Seqdb_Locus_&_Protocol_CRUD.md) (1 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/services/seq/crud_common.py`
- `gen_epix/seqdb/services/seq/crud_seq_profile.py`

## Audit Trail

- EXTRACTED: 23 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*