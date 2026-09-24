# Case Query Retrieval

> 29 nodes · cohesion 0.10

## Key Concepts

- **validate_concept_or_region()** (12 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_verify_case_filter()** (11 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **case_service_retrieve_cases_by_query()** (10 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **CaseQueryResult** (9 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **_verify_filter_validity()** (9 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **RetrieveCasesByQueryCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **_verify_case_set_access()** (8 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **RefCol** (7 connections)
- **_get_map_functions_for_filters()** (6 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **User** (6 connections)
- **_get_map_function_for_col()** (5 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **_validate_filter_members()** (5 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **.retrieve_cases_by_query()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_cases_by_query()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_cases_by_query()** (3 connections) — `gen_epix/casedb/services/client.py`
- **Any** (2 connections)
- **Col** (2 connections)
- **Represents a request to retrieve cases matching a case query.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Represents the case identifiers returned for an executed query.** (1 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Retrieve access-filtered cases matching query criteria. Args: cmd: Case query…** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **Normalize and validate content-filter keys and members. Args: self: Case…** (1 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **Ensure the user can read or write every requested case set. Args: self: Case…** (1 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **Retrieve case IDs for a query after ABAC, set, and content filtering. The…** (1 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **Resolve filter metadata and validate concept and region members. Args: self:…** (1 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- **Validate a StringSet filter against the ref column's concept or region set.** (1 connections) — `gen_epix/casedb/services/case/retrieve_case.py`
- *... and 4 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (21 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (5 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (3 shared connections)
- [Range Filters](Range_Filters.md) (3 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (3 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (1 shared connections)
- [Exists Filters](Exists_Filters.md) (1 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (1 shared connections)
- [Composite Filters](Composite_Filters.md) (1 shared connections)
- [Case Access Rights ABAC](Case_Access_Rights_ABAC.md) (1 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/retrieve_case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/client.py`

## Audit Trail

- EXTRACTED: 69 (83%)
- INFERRED: 14 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*