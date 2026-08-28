# BaseSeqService

> 115 nodes · cohesion 0.03

## Key Concepts

- **BaseSeqService** (135 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **seq/service.py** (86 connections) — `gen_epix/seqdb/services/seq/service.py`
- **crud_protocol.py** (12 connections) — `gen_epix/seqdb/services/seq/crud_protocol.py`
- **RetrieveSamplesByIdCommand** (10 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **crud_protocol_set.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_protocol_set.py`
- **crud_protocol_set_member.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_protocol_set_member.py`
- **crud_sample.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_sample.py`
- **crud_seq_category_set.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_seq_category_set.py`
- **crud_taxon.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_taxon.py`
- **seq/crud_tree_algorithm.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_tree_algorithm.py`
- **seq/crud_tree_algorithm_class.py** (10 connections) — `gen_epix/seqdb/services/seq/crud_tree_algorithm_class.py`
- **RetrieveSamplesByQueryCommand** (9 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **seq_service_crud_protocol()** (9 connections) — `gen_epix/seqdb/services/seq/crud_protocol.py`
- **retrieve_sample.py** (9 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **RetrieveSeqDistanceLastModifiedCommand** (8 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **seq_service_crud_protocol_set_member()** (8 connections) — `gen_epix/seqdb/services/seq/crud_protocol_set_member.py`
- **seq_service_crud_protocol_set()** (8 connections) — `gen_epix/seqdb/services/seq/crud_protocol_set.py`
- **seq_service_crud_sample()** (8 connections) — `gen_epix/seqdb/services/seq/crud_sample.py`
- **seq_service_crud_seq_category_set()** (8 connections) — `gen_epix/seqdb/services/seq/crud_seq_category_set.py`
- **seq_service_crud_taxon()** (8 connections) — `gen_epix/seqdb/services/seq/crud_taxon.py`
- **seq_service_crud_tree_algorithm_class()** (8 connections) — `gen_epix/seqdb/services/seq/crud_tree_algorithm_class.py`
- **seq_service_crud_tree_algorithm()** (8 connections) — `gen_epix/seqdb/services/seq/crud_tree_algorithm.py`
- **seq_service_retrieve_sample_identifiers_by_id()** (8 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- **seq_service_retrieve_seq_distance_last_modified()** (7 connections) — `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- **seq_service_retrieve_samples_by_id()** (7 connections) — `gen_epix/seqdb/services/seq/retrieve_sample.py`
- *... and 90 more nodes in this community*

## Relationships

- [command/seq.py](command-seq.py.md) (40 shared connections)
- [SeqService](SeqService.md) (26 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (14 shared connections)
- [SeqdbEndpointTestClient](SeqdbEndpointTestClient.md) (11 shared connections)
- [test_seqdb_retrieve_best.py](test_seqdb_retrieve_best.py.md) (10 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (9 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (7 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (6 shared connections)
- [entity.py](entity.py.md) (6 shared connections)
- [calculate_seq_distance.py](calculate_seq_distance.py.md) (5 shared connections)
- [crud_allele.py](crud_allele.py.md) (5 shared connections)
- [crud_ast_prediction.py](crud_ast_prediction.py.md) (5 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/seq/calculate_seq_distance.py`
- `gen_epix/seqdb/services/seq/crud_protocol.py`
- `gen_epix/seqdb/services/seq/crud_protocol_set.py`
- `gen_epix/seqdb/services/seq/crud_protocol_set_member.py`
- `gen_epix/seqdb/services/seq/crud_sample.py`
- `gen_epix/seqdb/services/seq/crud_seq_category_set.py`
- `gen_epix/seqdb/services/seq/crud_taxon.py`
- `gen_epix/seqdb/services/seq/crud_tree_algorithm.py`
- `gen_epix/seqdb/services/seq/crud_tree_algorithm_class.py`
- `gen_epix/seqdb/services/seq/retrieve_sample.py`
- `gen_epix/seqdb/services/seq/service.py`
- `gen_epix/seqdb/services/seq/upload.py`

## Audit Trail

- EXTRACTED: 414 (100%)
- INFERRED: 1 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*