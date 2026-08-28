# SeqService

> 54 nodes · cohesion 0.04

## Key Concepts

- **SeqService** (48 connections) — `gen_epix/seqdb/services/seq/service.py`
- **UUID** (36 connections)
- **crud_ast_measurement.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_ast_measurement.py`
- **crud_seq.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_seq.py`
- **RetrieveSimilarProfilesCommand** (9 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **seq_service_crud_ast_measurement()** (8 connections) — `gen_epix/seqdb/services/seq/crud_ast_measurement.py`
- **seq_service_crud_seq()** (8 connections) — `gen_epix/seqdb/services/seq/crud_seq.py`
- **RetrieveSeqFastaCommand** (7 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **AstMeasurementCrudCommand** (6 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **SeqCrudCommand** (6 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **.crud_ast_measurement()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_seq()** (5 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.crud_ast_measurement()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.crud_protocol_set()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.crud_protocol_set_member()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.crud_seq()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.crud_seq_category_set()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.crud_tree_algorithm()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.crud_tree_algorithm_class()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.retrieve_seq_fasta()** (3 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.retrieve_genetic_sequence_fasta_by_id()** (3 connections) — `gen_epix/seqdb/services/remote_app.py`
- **.retrieve_similar_profiles()** (3 connections) — `gen_epix/seqdb/services/seq/service.py`
- **UUID** (2 connections)
- **UUID** (2 connections)
- **.retrieve_seq_fasta()** (2 connections) — `gen_epix/seqdb/services/seq/service.py`
- *... and 29 more nodes in this community*

## Relationships

- [BaseSeqService](BaseSeqService.md) (26 shared connections)
- [command/seq.py](command-seq.py.md) (20 shared connections)
- [test_seqdb_retrieve_best.py](test_seqdb_retrieve_best.py.md) (8 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (6 shared connections)
- [SeqdbEndpointTestClient](SeqdbEndpointTestClient.md) (3 shared connections)
- [OrganizationService](OrganizationService.md) (2 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (2 shared connections)
- [crud_allele.py](crud_allele.py.md) (2 shared connections)
- [crud_ast_prediction.py](crud_ast_prediction.py.md) (2 shared connections)
- [crud_locus_code_map.py](crud_locus_code_map.py.md) (2 shared connections)
- [crud_pcr_measurement.py](crud_pcr_measurement.py.md) (2 shared connections)
- [crud_read_set.py](crud_read_set.py.md) (2 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/remote_app.py`
- `gen_epix/seqdb/services/seq/crud_ast_measurement.py`
- `gen_epix/seqdb/services/seq/crud_seq.py`
- `gen_epix/seqdb/services/seq/service.py`

## Audit Trail

- EXTRACTED: 173 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*