# Region Containment Command

> 7 nodes · cohesion 0.29

## Key Concepts

- **RetrieveContainingRegionCommand** (6 connections) — `gen_epix/casedb/domain/command/geo.py`
- **.retrieve_containing_region()** (3 connections) — `gen_epix/casedb/domain/service/geo.py`
- **.retrieve_containing_region()** (3 connections) — `gen_epix/casedb/services/geo.py`
- **Command** (1 connections)
- **Retrieve the regions that contain the specified regions.** (1 connections) — `gen_epix/casedb/domain/command/geo.py`
- **Region** (1 connections)
- **Region** (1 connections)

## Relationships

- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (2 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/geo.py`
- `gen_epix/casedb/domain/service/geo.py`
- `gen_epix/casedb/services/geo.py`

## Audit Trail

- EXTRACTED: 10 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*