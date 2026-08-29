# RetrieveGeneticSequenceFastaByCaseCommand

> 8 nodes

## Key Concepts

- **RetrieveGeneticSequenceFastaByCaseCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **.retrieve_genetic_sequence_fasta_by_case()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_genetic_sequence_fasta_by_case()** (3 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_genetic_sequence_fasta_by_case()** (3 connections) — `gen_epix/casedb/services/remote_app.py`
- **Retrieve a set of genetic sequences in FASTA format based on a set of case IDs…** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Retrieve genetic sequence data in FASTA format for case.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Return a streaming iterable of FASTA formatted lines. Path: HTTP client ->…** (1 connections) — `gen_epix/casedb/services/case/service.py`
- **Stream genetic sequence FASTA data for cases.** (1 connections) — `gen_epix/casedb/services/remote_app.py`

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

- EXTRACTED: 15 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*