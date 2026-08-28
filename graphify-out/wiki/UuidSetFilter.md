# UuidSetFilter

> 63 nodes · cohesion 0.05

## Key Concepts

- **UuidSetFilter** (59 connections) — `gen_epix/filter/uuid_set.py`
- **EqualsUuidFilter** (27 connections) — `gen_epix/filter/equals_uuid.py`
- **calculate_phylogenetic_tree.py** (27 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **RefDataAccess** (21 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **AbacService** (18 connections) — `gen_epix/casedb/services/abac.py`
- **seq_service_calculate_phylogenetic_tree()** (14 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **._get_filter()** (12 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **._get_case_abac_cached()** (10 connections) — `gen_epix/casedb/services/abac.py`
- **._get_ref_data_access_cached()** (9 connections) — `gen_epix/casedb/services/abac.py`
- **UUID** (7 connections)
- **._get_access_dict()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._get_access_intersect()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.get_case_type_share_abac_dict()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._get_share_dict()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._get_share_intersect()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **.update_user_own_organization()** (5 connections) — `gen_epix/casedb/services/abac.py`
- **._compose_id_filter()** (5 connections) — `gen_epix/casedb/services/case/service.py`
- **.get_case_type_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_case_type_set_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_col_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_col_set_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_dim_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_ref_col_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_ref_dim_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_case_abac()** (4 connections) — `gen_epix/casedb/services/abac.py`
- *... and 38 more nodes in this community*

## Relationships

- [composite.py](composite.py.md) (18 shared connections)
- [CompositeFilter](CompositeFilter.md) (12 shared connections)
- [CrudOperation](CrudOperation.md) (10 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (7 shared connections)
- [BaseSeqService](BaseSeqService.md) (6 shared connections)
- [BaseCaseService](BaseCaseService.md) (5 shared connections)
- [CaseTypeAccessAbac](CaseTypeAccessAbac.md) (5 shared connections)
- [CaseService](CaseService.md) (5 shared connections)
- [case/non_persistable.py](case-non_persistable.py.md) (4 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (4 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (3 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (3 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/services/abac.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/filter/equals_uuid.py`
- `gen_epix/filter/uuid_set.py`
- `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`

## Audit Trail

- EXTRACTED: 218 (94%)
- INFERRED: 13 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*