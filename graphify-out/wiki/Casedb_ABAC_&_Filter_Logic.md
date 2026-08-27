# Casedb ABAC & Filter Logic

> 184 nodes · cohesion 0.03

## Key Concepts

- **CompositeFilter** (93 connections) — `gen_epix/filter/composite.py`
- **composite.py** (62 connections) — `gen_epix/filter/composite.py`
- **UuidSetFilter** (62 connections) — `gen_epix/filter/uuid_set.py`
- **filter/__init__.py** (59 connections) — `gen_epix/filter/__init__.py`
- **crud_endpoint_generator.py** (48 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **test_casedb_retrieve_case.py** (37 connections) — `test/casedb/unit/services/case/retrieve_case/test_casedb_retrieve_case.py`
- **StringSetFilter** (34 connections) — `gen_epix/filter/string_set.py`
- **filter/enum.py** (33 connections) — `gen_epix/filter/enum.py`
- **EqualsUuidFilter** (30 connections) — `gen_epix/filter/equals_uuid.py`
- **TypedCompositeFilter** (29 connections) — `gen_epix/filter/composite.py`
- **LogicalOperator** (27 connections) — `gen_epix/filter/enum.py`
- **calculate_phylogenetic_tree.py** (27 connections) — `gen_epix/seqdb/services/seq/calculate_phylogenetic_tree.py`
- **commondb/policies/read_user_policy.py** (25 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **FilterType** (25 connections) — `gen_epix/filter/enum.py`
- **casedb/services/abac.py** (23 connections) — `gen_epix/casedb/services/abac.py`
- **EqualsBooleanFilter** (22 connections) — `gen_epix/filter/equals_boolean.py`
- **filter/base.py** (19 connections) — `gen_epix/filter/base.py`
- **retrieve_best.py** (19 connections) — `gen_epix/seqdb/services/seq/retrieve_best.py`
- **test_filter_base_filter.py** (19 connections) — `test/filter/unit/test_filter_base_filter.py`
- **ExistsFilter** (18 connections) — `gen_epix/filter/exists.py`
- **retrieve_stats.py** (17 connections) — `gen_epix/casedb/services/case/retrieve_stats.py`
- **uuid_set.py** (17 connections) — `gen_epix/filter/uuid_set.py`
- **EqualsStringFilter** (16 connections) — `gen_epix/filter/equals_string.py`
- **NumberRangeFilter** (16 connections) — `gen_epix/filter/number_range.py`
- **RangeFilter** (16 connections) — `gen_epix/filter/range.py`
- *... and 159 more nodes in this community*

## Relationships

- [Casedb Retrieve Case Query Logic](Casedb_Retrieve_Case_Query_Logic.md) (40 shared connections)
- [Query Filter Engine](Query_Filter_Engine.md) (36 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (33 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (31 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (22 shared connections)
- [Log Parsing & User Journey Analysis](Log_Parsing_&_User_Journey_Analysis.md) (21 shared connections)
- [Case Query & Rights Retrieval](Case_Query_&_Rights_Retrieval.md) (15 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (13 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (13 shared connections)
- [Case Stats Retrieval](Case_Stats_Retrieval.md) (12 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (12 shared connections)
- [Best Seq Per Sample](Best_Seq_Per_Sample.md) (12 shared connections)

## Source Files

- `gen_epix/casedb/services/abac.py`
- `gen_epix/casedb/services/case/retrieve_stats.py`
- `gen_epix/commondb/policies/read_user_policy.py`
- `gen_epix/commondb/services/abac.py`
- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `gen_epix/fastapp/remote_app.py`
- `gen_epix/filter/__init__.py`
- `gen_epix/filter/base.py`
- `gen_epix/filter/composite.py`
- `gen_epix/filter/date_range.py`
- `gen_epix/filter/datetime_range.py`
- `gen_epix/filter/enum.py`
- `gen_epix/filter/equals.py`
- `gen_epix/filter/equals_boolean.py`
- `gen_epix/filter/equals_number.py`
- `gen_epix/filter/equals_string.py`
- `gen_epix/filter/equals_uuid.py`
- `gen_epix/filter/exists.py`
- `gen_epix/filter/hashable_set.py`
- `gen_epix/filter/no_filter.py`

## Audit Trail

- EXTRACTED: 899 (92%)
- INFERRED: 78 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*