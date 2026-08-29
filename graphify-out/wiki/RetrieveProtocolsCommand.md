# RetrieveProtocolsCommand

> 10 nodes

## Key Concepts

- **RetrieveProtocolsCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **Protocol** (1 connections)
- **Protocol** (1 connections)
- **Protocol** (1 connections)
- **Retrieve the protocols registered in seqdb for downstream sequence processing…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Retrieve available protocols.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Retrieve sequencing or assembly protocols.** (1 connections) — `gen_epix/casedb/services/remote_app.py`

## Relationships

- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (2 shared connections)
- [Command](Command.md) (1 shared connections)
- [Casedb Case Service Domain Interface](Casedb_Case_Service_Domain_Interface.md) (1 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [CasedbRemoteApp](CasedbRemoteApp.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 17 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*