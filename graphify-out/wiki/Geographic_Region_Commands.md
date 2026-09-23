# Geographic Region Commands

> 132 nodes · cohesion 0.04

## Key Concepts

- **CrudCommand** (187 connections) — `gen_epix/commondb/domain/command/base.py`
- **omopdb/domain/command/__init__.py** (116 connections) — `gen_epix/omopdb/domain/command/__init__.py`
- **command/omop.py** (67 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **Represents a request to perform a CRUD operation on OMOP care-site records.** (54 connections) — `gen_epix/omopdb/domain/command/omop.py`
- **command/organization.py** (34 connections) — `gen_epix/commondb/domain/command/organization.py`
- **command/base.py** (19 connections) — `gen_epix/commondb/domain/command/base.py`
- **command/geo.py** (10 connections) — `gen_epix/casedb/domain/command/geo.py`
- **commondb/domain/command/abac.py** (10 connections) — `gen_epix/commondb/domain/command/abac.py`
- **UserCrudCommand** (10 connections) — `gen_epix/commondb/domain/command/organization.py`
- **RetrieveOrganizationsUnderAdminCommand** (9 connections) — `gen_epix/commondb/domain/command/abac.py`
- **OrganizationAdminPolicyCrudCommand** (8 connections) — `gen_epix/commondb/domain/command/abac.py`
- **ContactCrudCommand** (8 connections) — `gen_epix/commondb/domain/command/organization.py`
- **DataCollectionSetDataCollectionUpdateAssociationCommand** (8 connections) — `gen_epix/commondb/domain/command/organization.py`
- **OrganizationSetOrganizationUpdateAssociationCommand** (8 connections) — `gen_epix/commondb/domain/command/organization.py`
- **SiteCrudCommand** (8 connections) — `gen_epix/commondb/domain/command/organization.py`
- **UserInvitationCrudCommand** (8 connections) — `gen_epix/commondb/domain/command/organization.py`
- **DataCollectionCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **DataCollectionSetCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **DataCollectionSetMemberCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **IdentifierIssuerCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **OrganizationCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **OrganizationSetCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **OrganizationSetMemberCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/organization.py`
- **OutageCrudCommand** (7 connections) — `gen_epix/commondb/domain/command/system.py`
- **RetrieveSpecimenIdsByCohortIdsCommand** (6 connections) — `gen_epix/omopdb/domain/command/omop.py`
- *... and 107 more nodes in this community*

## Relationships

- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (50 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (42 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (41 shared connections)
- [CRUD Command Base](CRUD_Command_Base.md) (13 shared connections)
- [User Invitation & Management](User_Invitation_&_Management.md) (11 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (10 shared connections)
- [Case CRUD Service Operations](Case_CRUD_Service_Operations.md) (9 shared connections)
- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (9 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (8 shared connections)
- [User & Person Commands](User_&_Person_Commands.md) (7 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (6 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (5 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/geo.py`
- `gen_epix/casedb/services/case/crud_common.py`
- `gen_epix/commondb/domain/command/abac.py`
- `gen_epix/commondb/domain/command/base.py`
- `gen_epix/commondb/domain/command/organization.py`
- `gen_epix/commondb/domain/command/system.py`
- `gen_epix/fastapp/domain/domain.py`
- `gen_epix/fastapp/service.py`
- `gen_epix/omopdb/domain/command/__init__.py`
- `gen_epix/omopdb/domain/command/omop.py`
- `gen_epix/omopdb/domain/service/omop.py`
- `test/fastapp/integration/api/test_fastapp_api.py`
- `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- `test/fastapp/unit/api/test_crud_endpoint_set.py`

## Audit Trail

- EXTRACTED: 601 (99%)
- INFERRED: 4 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*