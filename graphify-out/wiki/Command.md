# Command

> 32 nodes · cohesion 0.10

## Key Concepts

- **Command** (18 connections)
- **CaseRights** (14 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseSetRights** (14 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **RetrieveCasesByIdCommand** (12 connections) — `gen_epix/casedb/domain/command/case.py`
- **RetrieveCaseRightsCommand** (10 connections) — `gen_epix/casedb/domain/command/case.py`
- **._get_case_or_set_rights()** (9 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **._get_case_or_set_rights_without_full_access()** (9 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **RetrieveCaseSetRightsCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **.retrieve_case_or_set_rights()** (8 connections) — `gen_epix/casedb/services/case/service.py`
- **._get_case_or_set_rights_with_full_access()** (6 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.retrieve_case_or_set_rights()** (6 connections) — `gen_epix/casedb/domain/service/case.py`
- **.get_case_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_case_set_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **UUID** (4 connections)
- **.retrieve_case_rights()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.retrieve_case_set_rights()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **.retrieve_cases_by_id()** (4 connections) — `gen_epix/casedb/services/remote_app.py`
- **field_validator** (3 connections)
- **._validate_case_ids()** (3 connections) — `gen_epix/casedb/domain/command/case.py`
- **._validate_case_ids()** (3 connections) — `gen_epix/casedb/domain/command/case.py`
- **._validate_case_set_ids()** (3 connections) — `gen_epix/casedb/domain/command/case.py`
- **Create a CaseRights or CaseSetRights object for the case/case set for a user…** (3 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **Retrieve access rights for a set of cases.** (2 connections) — `gen_epix/casedb/domain/command/case.py`
- **Retrieve access rights for cases.** (2 connections) — `gen_epix/casedb/services/remote_app.py`
- **Retrieve cases by their IDs.** (1 connections) — `gen_epix/casedb/domain/command/case.py`
- *... and 7 more nodes in this community*

## Relationships

- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (10 shared connections)
- [CaseTypeAccessAbac](CaseTypeAccessAbac.md) (10 shared connections)
- [CaseAbac](CaseAbac.md) (7 shared connections)
- [case/non_persistable.py](case-non_persistable.py.md) (5 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (4 shared connections)
- [BaseCaseService](BaseCaseService.md) (3 shared connections)
- [CasedbRemoteApp](CasedbRemoteApp.md) (3 shared connections)
- [case_service_create_file_for_read_set_or_seq](case_service_create_file_for_read_set_or_seq.md) (2 shared connections)
- [TypedDatetimeRangeFilter](TypedDatetimeRangeFilter.md) (2 shared connections)
- [TestcasedbEdgeCasesRefDataAccess](TestcasedbEdgeCasesRefDataAccess.md) (2 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [CaseService](CaseService.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/abac/rights.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 113 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*