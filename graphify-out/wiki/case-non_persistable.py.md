# case/non_persistable.py

> 21 nodes

## Key Concepts

- **case/non_persistable.py** (22 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseCohortLink** (10 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseQueryResult** (10 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **RetrieveCasesByQueryCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **BaseCaseRights** (8 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseQuery** (6 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Model** (6 connections)
- **CaseSetQuery** (5 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **SimilarCase** (5 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.retrieve_cases_by_query()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_cases_by_query()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_cases_by_query()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.is_null()** (2 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **BaseModel** (1 connections)
- **Retrieve cases based on a query.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Whether the link is a null link, i.e. the case has no linked cohort. This is…** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Represents a "similar case" search result with its ID, date, and ownership flag.** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **# TODO: add data_collection_id** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Base class describing all the rights that a user has on one particular item,…** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Retrieve cases matching query criteria.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Retrieve cases matching the given query.** (1 connections) — `gen_epix/casedb/services/remote_app.py`

## Relationships

- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (18 shared connections)
- [Command](Command.md) (5 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (5 shared connections)
- [BaseRetrieveCaseTestCase](BaseRetrieveCaseTestCase.md) (4 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (4 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [composite.py](composite.py.md) (2 shared connections)
- [entity.py](entity.py.md) (2 shared connections)
- [Casedb Case Service Domain Interface](Casedb_Case_Service_Domain_Interface.md) (1 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [CasedbRemoteApp](CasedbRemoteApp.md) (1 shared connections)
- [TypedDatetimeRangeFilter](TypedDatetimeRangeFilter.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 71 (93%)
- INFERRED: 5 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*