# RetrieveProtocolsCommand

> 10 nodes · cohesion 0.20

## Key Concepts

- **RetrieveProtocolsCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_protocols()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **Retrieve the protocols registered in seqdb for downstream sequence processing…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Protocol** (1 connections)
- **Retrieve available protocols.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Protocol** (1 connections)
- **Protocol** (1 connections)
- **Retrieve sequencing or assembly protocols.** (1 connections) — `gen_epix/casedb/services/remote_app.py`

## Relationships

- [BaseCaseService](BaseCaseService.md) (3 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [Command](Command.md) (1 shared connections)
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