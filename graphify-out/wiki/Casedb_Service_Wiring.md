# Casedb Service Wiring

> 126 nodes · cohesion 0.02

## Key Concepts

- **UserManager** (30 connections) — `gen_epix/commondb/services/user_manager.py`
- **RbacService** (22 connections) — `gen_epix/commondb/services/rbac.py`
- **SeqdbService** (19 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **casedb/services/__init__.py** (17 connections) — `gen_epix/casedb/services/__init__.py`
- **omopdb/services/__init__.py** (15 connections) — `gen_epix/omopdb/services/__init__.py`
- **seqdb/services/__init__.py** (12 connections) — `gen_epix/seqdb/services/__init__.py`
- **RetrieveOwnPermissionsCommand** (10 connections) — `gen_epix/commondb/domain/command/rbac.py`
- **command/rbac.py** (9 connections) — `gen_epix/commondb/domain/command/rbac.py`
- **RetrieveSubRolesCommand** (9 connections) — `gen_epix/commondb/domain/command/rbac.py`
- **User** (9 connections)
- **.create_new_user_from_token()** (8 connections) — `gen_epix/commondb/services/user_manager.py`
- **Any** (7 connections)
- **services/seqdb/__init__.py** (6 connections) — `gen_epix/casedb/services/seqdb/__init__.py`
- **.auto_create_new_user()** (6 connections) — `gen_epix/commondb/services/user_manager.py`
- **.construct_user_instance_from_claims()** (6 connections) — `gen_epix/commondb/services/user_manager.py`
- **.create_root_user_from_claims()** (5 connections) — `gen_epix/commondb/services/user_manager.py`
- **.generate_id()** (5 connections) — `gen_epix/commondb/services/user_manager.py`
- **.get_user_name_from_claims()** (5 connections) — `gen_epix/commondb/services/user_manager.py`
- **.retrieve_user_by_id()** (5 connections) — `gen_epix/commondb/services/user_manager.py`
- **omopdb/services/organization.py** (5 connections) — `gen_epix/omopdb/services/organization.py`
- **OrganizationService** (5 connections) — `gen_epix/omopdb/services/organization.py`
- **omopdb/services/rbac.py** (5 connections) — `gen_epix/omopdb/services/rbac.py`
- **RbacService** (5 connections) — `gen_epix/omopdb/services/rbac.py`
- **services/case/__init__.py** (4 connections) — `gen_epix/casedb/services/case/__init__.py`
- **OntologyService** (4 connections) — `gen_epix/casedb/services/ontology.py`
- *... and 101 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (27 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (13 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (7 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (5 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (5 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (5 shared connections)
- [System Outage & License Models](System_Outage_&_License_Models.md) (3 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (3 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (2 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (2 shared connections)
- [Auth Claim Utilities](Auth_Claim_Utilities.md) (2 shared connections)
- [User Auto-Creation Tests](User_Auto-Creation_Tests.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/__init__.py`
- `gen_epix/casedb/services/case/__init__.py`
- `gen_epix/casedb/services/ontology.py`
- `gen_epix/casedb/services/rbac.py`
- `gen_epix/casedb/services/seqdb/__init__.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/domain/command/rbac.py`
- `gen_epix/commondb/domain/service/rbac.py`
- `gen_epix/commondb/services/rbac.py`
- `gen_epix/commondb/services/user_manager.py`
- `gen_epix/omopdb/services/__init__.py`
- `gen_epix/omopdb/services/abac.py`
- `gen_epix/omopdb/services/organization.py`
- `gen_epix/omopdb/services/rbac.py`
- `gen_epix/seqdb/services/__init__.py`

## Audit Trail

- EXTRACTED: 243 (97%)
- INFERRED: 8 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*