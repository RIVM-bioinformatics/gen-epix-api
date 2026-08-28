# TestRetrieveCompleteCaseType

> 19 nodes · cohesion 0.15

## Key Concepts

- **TestRetrieveCompleteCaseType** (12 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **RetrieveCompleteCaseTypeCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **.retrieve()** (8 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **.retrieve_complete_case_type()** (5 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_complete_case_type()** (4 connections) — `gen_epix/casedb/domain/service/case.py`
- **.retrieve_complete_case_type()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.create_command()** (4 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **User** (3 connections)
- **.create_access_abac()** (3 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **.repository_crud()** (3 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **.test_full_access_characterizes_generated_access_and_exclusions()** (3 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **.test_non_full_access_characterizes_complete_case_type()** (3 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **Any** (2 connections)
- **.app_handle()** (2 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **.setup_method()** (2 connections) — `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`
- **Retrieve a complete CaseType.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- **Retrieve complete case type with all associated data.** (1 connections) — `gen_epix/casedb/domain/service/case.py`
- **cached** (1 connections)
- **Retrieve the full definition of a case type.** (1 connections) — `gen_epix/casedb/services/remote_app.py`

## Relationships

- [BaseCaseService](BaseCaseService.md) (6 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (4 shared connections)
- [CaseTypeAccessAbac](CaseTypeAccessAbac.md) (3 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (2 shared connections)
- [Command](Command.md) (1 shared connections)
- [CaseService](CaseService.md) (1 shared connections)
- [CasedbRemoteApp](CasedbRemoteApp.md) (1 shared connections)
- [Role](Role.md) (1 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)
- [CaseAbac](CaseAbac.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`
- `test/casedb/unit/services/case/retrieve_case/test_retrieve_complete_case_type.py`

## Audit Trail

- EXTRACTED: 43 (93%)
- INFERRED: 3 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*