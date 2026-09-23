# Root User CRUD Guard

> 5 nodes · cohesion 0.40

## Key Concepts

- **.crud()** (4 connections) — `gen_epix/commondb/services/organization.py`
- **.__init__()** (4 connections) — `gen_epix/commondb/services/organization.py`
- **Any** (2 connections)
- **Initialize mapped user models and cache invalidation handlers. Args: app:…** (1 connections) — `gen_epix/commondb/services/organization.py`
- **Execute CRUD while preventing root users from deleting themselves or home.…** (1 connections) — `gen_epix/commondb/services/organization.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (1 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/services/organization.py`

## Audit Trail

- EXTRACTED: 8 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*