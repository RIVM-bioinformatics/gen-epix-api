# Case Query & Rights Retrieval

> 55 nodes · cohesion 0.05

## Key Concepts

- **case/non_persistable.py** (22 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **RefDataAccess** (21 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseRights** (14 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseSetRights** (14 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **._get_filter()** (12 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseCohortLink** (10 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **CaseQueryResult** (10 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **._get_case_or_set_rights()** (9 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **RetrieveCasesByQueryCommand** (8 connections) — `gen_epix/casedb/domain/command/case.py`
- **BaseCaseRights** (8 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.retrieve_case_or_set_rights()** (8 connections) — `gen_epix/casedb/services/case/service.py`
- **._get_case_or_set_rights_with_full_access()** (6 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **CaseQuery** (6 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **Model** (6 connections)
- **.retrieve_case_or_set_rights()** (6 connections) — `gen_epix/casedb/domain/service/case.py`
- **.get_case_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **.get_case_set_rights()** (5 connections) — `gen_epix/casedb/domain/model/abac/rights.py`
- **CaseSetQuery** (5 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **SimilarCase** (5 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_case_type_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_case_type_set_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_col_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_col_set_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_dim_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- **.get_ref_col_filter()** (4 connections) — `gen_epix/casedb/domain/model/case/non_persistable.py`
- *... and 30 more nodes in this community*

## Relationships

- [Case Data Serialization](Case_Data_Serialization.md) (19 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (15 shared connections)
- [Case Access Rights](Case_Access_Rights.md) (10 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (7 shared connections)
- [Casedb Retrieve Case Query Logic](Casedb_Retrieve_Case_Query_Logic.md) (7 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (7 shared connections)
- [Case ABAC Tests](Case_ABAC_Tests.md) (6 shared connections)
- [Casedb Remote App Client](Casedb_Remote_App_Client.md) (4 shared connections)
- [Case Service CRUD](Case_Service_CRUD.md) (3 shared connections)
- [Casedb Domain Enums & Policy](Casedb_Domain_Enums_&_Policy.md) (3 shared connections)
- [Case Stats Retrieval](Case_Stats_Retrieval.md) (2 shared connections)
- [Casedb Case Service](Casedb_Case_Service.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/domain/model/abac/rights.py`
- `gen_epix/casedb/domain/model/case/non_persistable.py`
- `gen_epix/casedb/domain/service/case.py`
- `gen_epix/casedb/services/case/service.py`
- `gen_epix/casedb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 160 (94%)
- INFERRED: 10 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*