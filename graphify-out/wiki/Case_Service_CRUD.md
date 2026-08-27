# Case Service CRUD

> 72 nodes · cohesion 0.04

## Key Concepts

- **BaseCaseService** (45 connections) — `gen_epix/casedb/domain/service/case.py`
- **UUID** (25 connections)
- **.crud_case_data_collection_link()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
- **.crud_case_identifier()** (5 connections) — `gen_epix/casedb/domain/service/case.py`
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
- **.create_file_for_read_set()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.create_file_for_seq()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_case_cohort_links_by_case_type()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_complete_case_type()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_is_own_cases()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- *... and 47 more nodes in this community*

## Relationships

- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (14 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (8 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (4 shared connections)
- [Case CRUD](Case_CRUD.md) (3 shared connections)
- [CaseSet CRUD](CaseSet_CRUD.md) (3 shared connections)
- [Case Query & Rights Retrieval](Case_Query_&_Rights_Retrieval.md) (3 shared connections)
- [Tree Algorithm CRUD](Tree_Algorithm_CRUD.md) (2 shared connections)
- [Case File Upload Commands](Case_File_Upload_Commands.md) (2 shared connections)
- [Case Date Calculation Utils](Case_Date_Calculation_Utils.md) (1 shared connections)
- [Case Batch Upload](Case_Batch_Upload.md) (1 shared connections)
- [Case Stats Retrieval](Case_Stats_Retrieval.md) (1 shared connections)
- [Phylogenetic Tree Retrieval](Phylogenetic_Tree_Retrieval.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/service/case.py`

## Audit Trail

- EXTRACTED: 139 (99%)
- INFERRED: 1 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*