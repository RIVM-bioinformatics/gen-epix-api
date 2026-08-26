# Seqdb Service CRUD

> 17 nodes · cohesion 0.15

## Key Concepts

- **SeqdbService** (16 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **UUID** (4 connections)
- **.crud()** (4 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **.create_file()** (3 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **.__init__()** (3 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **.retrieve_phylogenetic_tree()** (3 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **._retrieve_seq_objects_by_ids()** (3 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **.retrieve_similar_profiles()** (3 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **Any** (2 connections)
- **App** (2 connections)
- **.seqdb_app()** (2 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **.seqdb_user()** (2 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **CrudCommand** (1 connections)
- **PhylogeneticTree** (1 connections)
- **Seq** (1 connections)
- **Generic CRUD operation handler that forwards the command to seqdb while setting…** (1 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **SeqdbUser** (1 connections)

## Relationships

- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (4 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (2 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (1 shared connections)
- [File Creation Command](File_Creation_Command.md) (1 shared connections)
- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/seqdb/service.py`

## Audit Trail

- EXTRACTED: 30 (94%)
- INFERRED: 2 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*