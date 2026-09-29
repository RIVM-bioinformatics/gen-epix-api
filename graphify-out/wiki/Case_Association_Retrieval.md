# Case Association Retrieval

> 29 nodes · cohesion 0.07

## Key Concepts

- **UUID** (10 connections)
- **._retrieve_case_sets_with_content_right()** (8 connections) — `gen_epix/casedb/services/case/base.py`
- **._retrieve_cases_with_content_right()** (8 connections) — `gen_epix/casedb/services/case/base.py`
- **._read_association_with_valid_ids()** (7 connections) — `gen_epix/casedb/services/case/base.py`
- **._retrieve_seq_column_data()** (7 connections) — `gen_epix/casedb/services/case/base.py`
- **._retrieve_association_map()** (5 connections) — `gen_epix/casedb/services/case/base.py`
- **._compose_id_filter()** (4 connections) — `gen_epix/casedb/services/case/base.py`
- **._retrieve_case_case_sets_map()** (4 connections) — `gen_epix/casedb/services/case/base.py`
- **._retrieve_case_data_collections_map()** (4 connections) — `gen_epix/casedb/services/case/base.py`
- **._retrieve_case_set_data_collections_map()** (4 connections) — `gen_epix/casedb/services/case/base.py`
- **._verify_case_set_member_case_type()** (4 connections) — `gen_epix/casedb/services/case/base.py`
- **User** (3 connections)
- **Model** (2 connections)
- **Case** (1 connections)
- **CaseSet** (1 connections)
- **CaseSetMember** (1 connections)
- **Col** (1 connections)
- **CrudCommand** (1 connections)
- **RefCol** (1 connections)
- **Read association entities constrained by valid endpoint identifiers. Args:…** (1 connections) — `gen_epix/casedb/services/case/base.py`
- **Retrieve case sets for which a user has a content right. Args: uow: Unit of…** (1 connections) — `gen_epix/casedb/services/case/base.py`
- **Retrieve cases for which a user has a content right. Args: uow: Unit of work…** (1 connections) — `gen_epix/casedb/services/case/base.py`
- **Retrieve the data collections linked to cases. Args: uow: Unit of work used for…** (1 connections) — `gen_epix/casedb/services/case/base.py`
- **Retrieve the data collections linked to case sets. Args: uow: Unit of work used…** (1 connections) — `gen_epix/casedb/services/case/base.py`
- **Retrieve the case sets linked to cases. Args: uow: Unit of work used for…** (1 connections) — `gen_epix/casedb/services/case/base.py`
- *... and 4 more nodes in this community*

## Relationships

- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (10 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (8 shared connections)
- [Case Access Rights ABAC](Case_Access_Rights_ABAC.md) (4 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (2 shared connections)
- [Case Statistics Tests](Case_Statistics_Tests.md) (1 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/services/case/base.py`

## Audit Trail

- EXTRACTED: 56 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*