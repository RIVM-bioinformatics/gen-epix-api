# App Composition & Service Wiring

> 85 nodes · cohesion 0.03

## Key Concepts

- **SeqdbRemoteApp** (41 connections) — `gen_epix/seqdb/services/remote_app.py`
- **OrganizationService** (24 connections) — `gen_epix/commondb/services/organization.py`
- **RbacService** (21 connections) — `gen_epix/commondb/services/rbac.py`
- **seqdb/service.py** (20 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **casedb/services/__init__.py** (19 connections) — `gen_epix/casedb/services/__init__.py`
- **commondb/services/__init__.py** (19 connections) — `gen_epix/commondb/services/__init__.py`
- **SystemService** (19 connections) — `gen_epix/commondb/services/system.py`
- **services/system.py** (17 connections) — `gen_epix/commondb/services/system.py`
- **seqdb/services/__init__.py** (15 connections) — `gen_epix/seqdb/services/__init__.py`
- **commondb/services/rbac.py** (14 connections) — `gen_epix/commondb/services/rbac.py`
- **omopdb/services/__init__.py** (14 connections) — `gen_epix/omopdb/services/__init__.py`
- **ModelMetadataPolicy** (13 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **model_metadata_policy.py** (11 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **UUID** (7 connections)
- **services/seqdb/__init__.py** (5 connections) — `gen_epix/casedb/services/seqdb/__init__.py`
- **.filter()** (5 connections) — `gen_epix/commondb/policies/model_metadata_policy.py`
- **omopdb/services/abac.py** (5 connections) — `gen_epix/omopdb/services/abac.py`
- **RbacService** (5 connections) — `gen_epix/omopdb/services/rbac.py`
- **._extract_homepage_from_project_urls()** (4 connections) — `gen_epix/commondb/services/system.py`
- **AbacService** (4 connections) — `gen_epix/omopdb/services/abac.py`
- **omopdb/services/organization.py** (4 connections) — `gen_epix/omopdb/services/organization.py`
- **OrganizationService** (4 connections) — `gen_epix/omopdb/services/organization.py`
- **omopdb/services/rbac.py** (4 connections) — `gen_epix/omopdb/services/rbac.py`
- **AbacService** (4 connections) — `gen_epix/seqdb/services/abac.py`
- **.create_file()** (4 connections) — `gen_epix/seqdb/services/remote_app.py`
- *... and 60 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (33 shared connections)
- [Seqdb Remote App Tests](Seqdb_Remote_App_Tests.md) (16 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (13 shared connections)
- [Seqdb Domain CRUD Commands](Seqdb_Domain_CRUD_Commands.md) (10 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (10 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (8 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (6 shared connections)
- [Organization Service](Organization_Service.md) (6 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (5 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (5 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (5 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/services/__init__.py`
- `gen_epix/casedb/services/seqdb/__init__.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/policies/model_metadata_policy.py`
- `gen_epix/commondb/services/__init__.py`
- `gen_epix/commondb/services/organization.py`
- `gen_epix/commondb/services/rbac.py`
- `gen_epix/commondb/services/system.py`
- `gen_epix/omopdb/services/__init__.py`
- `gen_epix/omopdb/services/abac.py`
- `gen_epix/omopdb/services/organization.py`
- `gen_epix/omopdb/services/rbac.py`
- `gen_epix/seqdb/services/__init__.py`
- `gen_epix/seqdb/services/abac.py`
- `gen_epix/seqdb/services/remote_app.py`

## Audit Trail

- EXTRACTED: 277 (96%)
- INFERRED: 13 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*