# File Creation & Case Ownership

> 7 nodes · cohesion 0.29

## Key Concepts

- **.create_file_for_read_set()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.create_file_for_seq()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.retrieve_is_own_cases()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **UUID** (4 connections)
- **Create a file associated with a read set column.** (1 connections) — `gen_epix/casedb/services/remote_app.py`
- **Create a file associated with a sequence column.** (1 connections) — `gen_epix/casedb/services/remote_app.py`
- **Check whether the user owns each of the given cases.** (1 connections) — `gen_epix/casedb/services/remote_app.py`

## Relationships

- [Casedb Remote App Client](Casedb_Remote_App_Client.md) (3 shared connections)
- [Case File Upload Commands](Case_File_Upload_Commands.md) (2 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 13 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*