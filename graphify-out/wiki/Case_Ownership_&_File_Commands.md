# Case Ownership & File Commands

> 7 nodes · cohesion 0.29

## Key Concepts

- **RetrieveIsOwnCasesCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **UUID** (5 connections)
- **.create_file_for_read_set()** (3 connections) — `gen_epix/casedb/services/client.py`
- **.create_file_for_seq()** (3 connections) — `gen_epix/casedb/services/client.py`
- **.retrieve_is_own_cases()** (3 connections) — `gen_epix/casedb/services/client.py`
- **.update_case_created_in_data_collection()** (3 connections) — `gen_epix/casedb/services/client.py`
- **Represents a request to retrieve cases owned by or accessible to the user. The…** (1 connections) — `gen_epix/casedb/domain/command/case.py`

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (4 shared connections)
- [Casedb Client Handlers](Casedb_Client_Handlers.md) (4 shared connections)
- [Own-Cases Retrieval Tests](Own-Cases_Retrieval_Tests.md) (2 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (2 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (1 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (1 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/client.py`

## Audit Trail

- EXTRACTED: 21 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*