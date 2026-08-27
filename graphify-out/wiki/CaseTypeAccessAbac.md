# CaseTypeAccessAbac

> 52 nodes · cohesion 0.08

## Key Concepts

- **CaseTypeAccessAbac** (45 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **CaseRight** (33 connections) — `gen_epix/casedb/domain/enum.py`
- **UUID** (26 connections)
- **CaseTypeShareAbac** (23 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **rights.py** (18 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **test_rights.py** (13 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **._check_access_or_share()** (10 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._get_has_right_function()** (10 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **TestHelperFunctions** (10 connections) — `test/casedb/unit/domain/model/abac/test_rights.py`
- **._is_add_allowed()** (9 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._is_remove_allowed()** (8 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._get_get_share_from_data_collections_function()** (7 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.is_allowed()** (7 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.is_content_allowed()** (7 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._validate_private_creation_or_deletion()** (7 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._get_from_data_collections_for_right_function()** (6 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._update_access_rights()** (6 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_addable_data_collections_ids()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_case_types_with_access_right()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_cols_with_access_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_combinations_with_access_right()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_removable_data_collections_ids()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._update_data_collections_with_share_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_data_collections_with_access_right_for_col()** (4 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_case_types_with_any_rights()** (3 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- *... and 27 more nodes in this community*

## Relationships

- [CaseAbac](CaseAbac.md) (41 shared connections)
- [CaseService](CaseService.md) (11 shared connections)
- [Command](Command.md) (10 shared connections)
- [BaseCaseAbacTestCase](BaseCaseAbacTestCase.md) (9 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (7 shared connections)
- [BaseCaseService](BaseCaseService.md) (6 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (5 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (5 shared connections)
- [abac/__init__.py](abac-__init__.py.md) (3 shared connections)
- [BaseIsOwnCasesTestCase](BaseIsOwnCasesTestCase.md) (3 shared connections)
- [TestRetrieveCompleteCaseType](TestRetrieveCompleteCaseType.md) (3 shared connections)
- [.create_case_for_upload](create_case_for_upload.md) (3 shared connections)

## Source Files

- `gen_epix/casedb/domain/enum.py`
- `gen_epix/casedb/domain/model/abac/rights.py`
- `test/casedb/unit/domain/model/abac/test_rights.py`

## Audit Trail

- EXTRACTED: 203 (91%)
- INFERRED: 19 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*