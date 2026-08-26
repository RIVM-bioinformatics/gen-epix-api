# OMOP Person/Specimen Retrieval

> 8 nodes · cohesion 0.25

## Key Concepts

- **BaseOmopService** (9 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_persons_by_id()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_persons_by_query()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.retrieve_specimen_ids_by_cohort_ids()** (4 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **.register_handlers()** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **Retrieve persons by their IDs.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **Retrieve persons matching query criteria.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`
- **Retrieve specimen IDs grouped by cohort ID.** (1 connections) — `gen_epix/omopdb/domain/service/omop.py`

## Relationships

- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (3 shared connections)
- [OMOP Domain CRUD Commands](OMOP_Domain_CRUD_Commands.md) (3 shared connections)
- [Organization Service](Organization_Service.md) (1 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (1 shared connections)
- [OMOP Repository](OMOP_Repository.md) (1 shared connections)
- [Person Upload Command](Person_Upload_Command.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/service/omop.py`

## Audit Trail

- EXTRACTED: 17 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*