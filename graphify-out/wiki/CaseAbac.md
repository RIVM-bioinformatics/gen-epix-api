# CaseAbac

> 44 nodes

## Key Concepts

- **CaseAbac** (91 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **TestCaseAbac** (45 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.make_access()** (38 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.make_share()** (19 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
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
- **.test_get_case_set_rights_can_delete_false()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_case_types_with_any_rights_share_only()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_cols_with_access_rights_read_filtered()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_cols_with_access_rights_unfiltered()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_cols_with_access_rights_unfiltered_invalid_right_raises()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **.test_get_cols_with_any_rights_filtered_missing_case_type_returns_empty()** (3 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- *... and 19 more nodes in this community*

## Relationships

- [CaseTypeAccessAbac](CaseTypeAccessAbac.md) (41 shared connections)
- [BaseCaseAbacTestCase](BaseCaseAbacTestCase.md) (10 shared connections)
- [Command](Command.md) (7 shared connections)
- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (4 shared connections)
- [CaseService](CaseService.md) (3 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (2 shared connections)
- [abac/__init__.py](abac-__init__.py.md) (1 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (1 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (1 shared connections)
- [BaseCrudTestCase](BaseCrudTestCase.md) (1 shared connections)
- [retrieve_case.py](retrieve_case.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/abac/rights.py`
- `test/casedb/unit/domain/model/abac/test_rights.py`

## Audit Trail

- EXTRACTED: 190 (95%)
- INFERRED: 9 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*