# BaseSeqdbService

> 23 nodes

## Key Concepts

- **BaseSeqdbService** (12 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **CreateFileCommand** (9 connections) — `gen_epix/seqdb/domain/command/file.py`
- **RetrieveGeneticSequenceFastaByIdCommand** (6 connections) — `gen_epix/casedb/domain/command/seqdb.py`
- **RetrieveGeneticSequenceByIdCommand** (4 connections) — `gen_epix/casedb/domain/command/seqdb.py`
- **.create_file()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **.retrieve_phylogenetic_tree()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **.retrieve_similar_profiles()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **.upload_samples()** (4 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **.retrieve_genetic_sequence_fasta_by_id()** (3 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **UUID** (3 connections)
- **.retrieve_genetic_sequence_fasta_by_id()** (2 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **Command** (2 connections)
- **.register_handlers()** (1 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **PhylogeneticTree** (1 connections)
- **Command** (1 connections)
- **Retrieve a genetic sequence by its ID.** (1 connections) — `gen_epix/casedb/domain/command/seqdb.py`
- **Retrieve a set of genetic sequences in FASTA format based on a set of sequence…** (1 connections) — `gen_epix/casedb/domain/command/seqdb.py`
- **Retrieve phylogenetic tree for specified profiles.** (1 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **Retrieve genetic sequence data in FASTA format by ID.** (1 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **Upload samples in batch.** (1 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **Create file and return file UUID.** (1 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **Retrieve UUIDs of profiles similar to specified profile.** (1 connections) — `gen_epix/casedb/domain/service/seqdb.py`
- **Create a file. The given expected format and compression are used to verify the…** (1 connections) — `gen_epix/seqdb/domain/command/file.py`

## Relationships

- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (7 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (4 shared connections)
- [OrganizationService](OrganizationService.md) (3 shared connections)
- [FileCompression](FileCompression.md) (2 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)
- [BaseService](BaseService.md) (1 shared connections)
- [Seqdb RemoteApp Client Methods](Seqdb_RemoteApp_Client_Methods.md) (1 shared connections)
- [SeqService](SeqService.md) (1 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)
- [commondb/domain/literal.py](commondb-domain-literal.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/seqdb.py`
- `gen_epix/casedb/domain/service/seqdb.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/seqdb/domain/command/file.py`

## Audit Trail

- EXTRACTED: 44 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*