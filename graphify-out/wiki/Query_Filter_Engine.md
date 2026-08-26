# Query Filter Engine

> 50 nodes · cohesion 0.08

## Key Concepts

- **Filter** (91 connections) — `gen_epix/filter/base.py`
- **Any** (12 connections)
- **.filter_rows()** (9 connections) — `gen_epix/filter/base.py`
- **._is_row_match_with_na_values()** (9 connections) — `gen_epix/filter/base.py`
- **._is_row_match_without_na_values()** (9 connections) — `gen_epix/filter/base.py`
- **Hashable** (9 connections)
- **._match()** (8 connections) — `gen_epix/filter/base.py`
- **.match_row()** (8 connections) — `gen_epix/filter/base.py`
- **.match_rows()** (8 connections) — `gen_epix/filter/base.py`
- **._get_row_value()** (7 connections) — `gen_epix/filter/base.py`
- **BaseModel** (7 connections)
- **Any** (7 connections)
- **._initialize_mapping()** (6 connections) — `gen_epix/filter/base.py`
- **CompositeFilter** (6 connections) — `test/filter/unit/test_filter_base_filter.py`
- **validate_filter_behavior()** (6 connections) — `test/filter/unit/util.py`
- **._split_filter_recursion()** (5 connections) — `gen_epix/fastapp/repositories/sa/repository.py`
- **.__call__()** (5 connections) — `gen_epix/filter/base.py`
- **.filter_column()** (5 connections) — `gen_epix/filter/base.py`
- **AlwaysTrueFilter** (5 connections) — `test/filter/unit/test_filter_base_filter.py`
- **.setup_method()** (5 connections) — `test/filter/unit/test_filter_base_filter.py`
- **EqualsFilter** (5 connections) — `test/filter/unit/test_filter_base_filter.py`
- **.match_column()** (4 connections) — `gen_epix/filter/base.py`
- **.match_value()** (4 connections) — `gen_epix/filter/base.py`
- **.set_key()** (3 connections) — `gen_epix/filter/base.py`
- **_default_validate_query_filter()** (2 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- *... and 25 more nodes in this community*

## Relationships

- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (36 shared connections)
- [Log Parsing & User Journey Analysis](Log_Parsing_&_User_Journey_Analysis.md) (7 shared connections)
- [Repository Query Helpers](Repository_Query_Helpers.md) (6 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (6 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (4 shared connections)
- [Repository CRUD Base](Repository_CRUD_Base.md) (4 shared connections)
- [Filter Framework Tests](Filter_Framework_Tests.md) (4 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (3 shared connections)
- [CRUD Endpoint Generation Helpers](CRUD_Endpoint_Generation_Helpers.md) (2 shared connections)
- [CRUD Endpoint Generator](CRUD_Endpoint_Generator.md) (2 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (2 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (2 shared connections)

## Source Files

- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `gen_epix/fastapp/repositories/sa/repository.py`
- `gen_epix/filter/base.py`
- `test/filter/unit/test_filter_base_filter.py`
- `test/filter/unit/util.py`

## Audit Trail

- EXTRACTED: 178 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*