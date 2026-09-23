# Base Case Service Interface

> 78 nodes · cohesion 0.04

## Key Concepts

- **BaseCaseService** (63 connections) — `gen_epix/casedb/domain/service/case.py`
- **UUID** (26 connections)
- **.crud_case()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_data_collection_link()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_identifier()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_category()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_data_collection_link()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_member()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_set_status()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type_set()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type_set_category()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_type_set_member()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_col()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_col_set()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_col_set_member()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_dim()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_genetic_distance_protocol()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_ref_col()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_ref_dim()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_tree_algorithm()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_tree_algorithm_class()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **Handle a CRUD command for case entities. Args: cmd: Case CRUD command to…** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.create_case_set()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- *... and 53 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (23 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (15 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (9 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (8 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (4 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (2 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (2 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (2 shared connections)
- [Case Type Validation Metadata](Case_Type_Validation_Metadata.md) (1 shared connections)
- [Genetic Distance Protocol CRUD](Genetic_Distance_Protocol_CRUD.md) (1 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (1 shared connections)
- [Case Query Retrieval](Case_Query_Retrieval.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/service/case.py`

## Audit Trail

- EXTRACTED: 182 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*