# Case Access Rights

> 44 nodes · cohesion 0.06

## Key Concepts

- **case/non_persistable.py** (23 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **rights.py** (19 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **CaseRights** (13 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseSetRights** (13 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **._get_case_or_set_rights()** (9 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **CaseCohortLink** (9 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **RetrieveCaseSetRightsCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **.retrieve_case_or_set_rights()** (7 connections) — `gen_epix/casedb/services/case/service.py`
- **._get_case_or_set_rights_with_full_access()** (6 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **BaseCaseRights** (6 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseQuery** (6 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Model** (6 connections)
- **.retrieve_case_or_set_rights()** (6 connections) — `gen_epix/casedb/domain/service/case.py`
- **CaseRightSet** (5 connections) — `gen_epix/casedb/domain/enum.py`
- **.get_case_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_case_set_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **CaseSetQuery** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **SimilarCase** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.retrieve_case_cohort_links_by_case_type()** (4 connections) — `gen_epix/casedb/services/case/service.py`
- **.retrieve_case_cohort_links_by_case_type()** (3 connections) — `gen_epix/casedb/services/client.py`
- **.retrieve_case_set_rights()** (3 connections) — `gen_epix/casedb/services/client.py`
- **Represents a request to retrieve access rights to specified cases.** (2 connections) — `gen_epix/casedb/domain/command/case.py`
- **.is_null()** (2 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Group case access rights by protected resource and operation.** (1 connections) — `gen_epix/casedb/domain/enum.py`
- **Compute effective case and case-set rights from resolved ABAC records. Access…** (1 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- *... and 19 more nodes in this community*

## Relationships

- [Case Access Rights ABAC](Case_Access_Rights_ABAC.md) (20 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (11 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (9 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (5 shared connections)
- [Case Query Retrieval](Case_Query_Retrieval.md) (3 shared connections)
- [Casedb Client Handlers](Casedb_Client_Handlers.md) (3 shared connections)
- [Case Statistics Tests](Case_Statistics_Tests.md) (2 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (2 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [Case ID Validation](Case_ID_Validation.md) (1 shared connections)
- [Case Classification Enums](Case_Classification_Enums.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/enum.py`
- `gen_epix/casedb/domain/model/abac/rights.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/client.py`

## Audit Trail

- EXTRACTED: 126 (97%)
- INFERRED: 4 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*