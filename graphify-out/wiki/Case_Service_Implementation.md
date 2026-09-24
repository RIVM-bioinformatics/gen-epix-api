# Case Service Implementation

> 127 nodes · cohesion 0.03

## Key Concepts

- **CaseService** (67 connections) — `gen_epix/casedb/services/case/service.py`
- **UUID** (45 connections)
- **._retrieve_cases_with_content_right()** (15 connections) — `gen_epix/casedb/services/case/service.py`
- **._retrieve_case_sets_with_content_right()** (12 connections) — `gen_epix/casedb/services/case/service.py`
- **._filter_cases_by_access_and_content()** (11 connections) — `gen_epix/casedb/services/case/service.py`
- **._retrieve_association_map()** (10 connections) — `gen_epix/casedb/services/case/service.py`
- **._resolve_case_date_mappers_and_limits()** (9 connections) — `gen_epix/casedb/services/case/service.py`
- **._retrieve_cases_by_ids_or_case_type_filter()** (9 connections) — `gen_epix/casedb/services/case/service.py`
- **CaseRight** (8 connections)
- **._filter_case_content()** (7 connections) — `gen_epix/casedb/services/case/service.py`
- **._read_association_with_valid_ids()** (7 connections) — `gen_epix/casedb/services/case/service.py`
- **._resolve_case_type_access()** (7 connections) — `gen_epix/casedb/services/case/service.py`
- **._retrieve_seq_column_data()** (7 connections) — `gen_epix/casedb/services/case/service.py`
- **Case** (7 connections)
- **._compose_id_filter()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_case_identifier()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_case_set_category()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_case_set_status()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_case_type_set_category()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_tree_algorithm()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **.crud_tree_algorithm_class()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **._load_case_type()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **._retrieve_case_data_collections_map()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **._retrieve_case_set_data_collections_map()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- **._validate_case_set_access()** (6 connections) — `gen_epix/casedb/services/case/service.py`
- *... and 102 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (19 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (19 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (12 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (6 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (6 shared connections)
- [Composite Filters](Composite_Filters.md) (4 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (3 shared connections)
- [Case Statistics Tests](Case_Statistics_Tests.md) (3 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (3 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (2 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (2 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/case/service.py`

## Audit Trail

- EXTRACTED: 304 (99%)
- INFERRED: 3 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*