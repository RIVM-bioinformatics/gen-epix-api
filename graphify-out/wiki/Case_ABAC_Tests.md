# Case ABAC Tests

> 53 nodes · cohesion 0.10

## Key Concepts

- **CaseAbac** (91 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **TestCaseAbac** (45 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.make_access()** (38 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.make_share()** (19 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **TestCaseTypeAccessAbac** (7 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **TestCaseTypeShareAbac** (7 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **scenario_ids** (4 connections)
- **.test_get_case_rights_non_full_access()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_case_rights_not_own_private_share_only_can_delete_false()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_case_set_rights_non_full_access()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_case_types_with_access_right()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_case_types_with_any_rights()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_cols_with_any_rights_filtered_includes_all()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_cols_with_any_rights_unfiltered()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_combinations_with_any_rights()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_data_collections_with_access_right_for_col()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_data_collections_with_any_rights()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_data_collections_with_any_rights_share_no_rights_ignored()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_is_allowed_add_to_private_target_false()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_is_allowed_add_with_share_true()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_is_allowed_content_read_false()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_is_allowed_remove_with_share_true()** (4 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **UUID** (3 connections)
- **.test_get_case_set_rights_can_delete_false()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_case_types_with_any_rights_share_only()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- *... and 28 more nodes in this community*

## Relationships

- [Case Access Rights](Case_Access_Rights.md) (53 shared connections)
- [Case Query & Rights Retrieval](Case_Query_&_Rights_Retrieval.md) (6 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (3 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (3 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (3 shared connections)
- [Case Policy ABAC Definitions](Case_Policy_ABAC_Definitions.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)
- [Case File Upload Commands](Case_File_Upload_Commands.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Casedb Retrieve Case Query Logic](Casedb_Retrieve_Case_Query_Logic.md) (1 shared connections)
- [Complete Case Type Retrieval Tests](Complete_Case_Type_Retrieval_Tests.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/abac/rights.py`
- `test/casedb/unit/domain/model/abac/test_rights.py`

## Audit Trail

- EXTRACTED: 203 (95%)
- INFERRED: 11 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*