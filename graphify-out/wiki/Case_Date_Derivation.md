# Case Date Derivation

> 73 nodes · cohesion 0.04

## Key Concepts

- **EqualsUuidFilter** (31 connections) — `gen_epix/filter/equals_uuid.py`
- **case_date.py** (27 connections) — `gen_epix/casedb/services/case/case_date.py`
- **ReadUserPolicy** (25 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **commondb/policies/read_user_policy.py** (22 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **AbacService** (20 connections) — `gen_epix/commondb/services/abac.py`
- **EqualsBooleanFilter** (20 connections) — `gen_epix/filter/equals_boolean.py`
- **case_service_get_case_date_col_mappers()** (12 connections) — `gen_epix/casedb/services/case/case_date.py`
- **RetrieveOrganizationAdminNameEmailsCommand** (11 connections) — `gen_epix/commondb/domain/command/organization.py`
- **UserNameEmail** (11 connections) — `gen_epix/commondb/domain/model/organization.py`
- **equals_uuid.py** (11 connections) — `gen_epix/filter/equals_uuid.py`
- **case_service_get_case_date_col_mappers_from_cols()** (9 connections) — `gen_epix/casedb/services/case/case_date.py`
- **datetime** (9 connections)
- **.filter()** (9 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **.get_admin_user_ids_own_organization()** (8 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **User** (7 connections)
- **._get_org_and_user_ids()** (7 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **.retrieve_organizations_under_admin()** (7 connections) — `gen_epix/commondb/services/abac.py`
- **UUID** (6 connections)
- **._get_admin_user_ids()** (6 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **.update_user_own_organization()** (6 connections) — `gen_epix/commondb/services/abac.py`
- **omopdb/domain/service/abac.py** (6 connections) — `gen_epix/omopdb/domain/service/abac.py`
- **._filter_read_one()** (5 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **._filter_read_some()** (5 connections) — `gen_epix/commondb/policies/read_user_policy.py`
- **._get_user_by_id_cached()** (5 connections) — `gen_epix/commondb/services/abac.py`
- **.retrieve_organization_admin_name_emails()** (5 connections) — `gen_epix/commondb/services/abac.py`
- *... and 48 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (24 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (20 shared connections)
- [Filter Base Abstractions](Filter_Base_Abstractions.md) (15 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (9 shared connections)
- [Case Operational Data Models](Case_Operational_Data_Models.md) (8 shared connections)
- [Composite Filters](Composite_Filters.md) (7 shared connections)
- [Reference Data Access Filters](Reference_Data_Access_Filters.md) (6 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (5 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (4 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (3 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (2 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/case/case_date.py`
- `gen_epix/commondb/domain/command/organization.py`
- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/commondb/domain/service/abac.py`
- `gen_epix/commondb/policies/read_user_policy.py`
- `gen_epix/commondb/services/abac.py`
- `gen_epix/commondb/services/client.py`
- `gen_epix/filter/equals_boolean.py`
- `gen_epix/filter/equals_uuid.py`
- `gen_epix/omopdb/domain/service/abac.py`

## Audit Trail

- EXTRACTED: 231 (92%)
- INFERRED: 21 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*