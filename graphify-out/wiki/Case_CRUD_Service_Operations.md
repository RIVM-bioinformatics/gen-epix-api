# Case CRUD Service Operations

> 74 nodes · cohesion 0.05

## Key Concepts

- **_crud_cascade_delete()** (44 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **case/crud_common.py** (43 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **is_app_admin_or_above()** (19 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **crud_case.py** (17 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **crud_case_data_collection_link.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **crud_case_set_data_collection_link.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **crud_case_set_member.py** (16 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **get_case_abac_from_command()** (16 connections) — `gen_epix/casedb/services/case/crud_common.py`
- **case_service_crud_case()** (10 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **_crud_case_with_abac()** (10 connections) — `gen_epix/casedb/services/case/crud_case.py`
- **case_service_crud_case_data_collection_link()** (10 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **case_service_crud_case_set_data_collection_link()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **case_service_crud_case_set_member()** (10 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **CaseDataCollectionLinkCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseSetDataCollectionLinkCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **CaseSetMemberCrudCommand** (9 connections) — `gen_epix/casedb/domain/command/case.py`
- **_crud_case_data_collection_link_with_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- **case_service_crud_case_set_category()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set_category.py`
- **_crud_case_set_data_collection_link_with_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **_crud_case_set_data_collection_link_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- **_crud_case_set_member_with_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **_crud_case_set_member_without_abac()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set_member.py`
- **case_service_crud_case_set_status()** (9 connections) — `gen_epix/casedb/services/case/crud_case_set_status.py`
- **case_service_crud_case_type_set_category()** (9 connections) — `gen_epix/casedb/services/case/crud_case_type_set_category.py`
- **_cascade_delete_linked_models()** (9 connections) — `gen_epix/casedb/services/case/crud_common.py`
- *... and 49 more nodes in this community*

## Relationships

- [Case Type & Column Commands](Case_Type_&_Column_Commands.md) (46 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (30 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (19 shared connections)
- [Base Case Service Interface](Base_Case_Service_Interface.md) (9 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (9 shared connections)
- [Sequence File Creation](Sequence_File_Creation.md) (8 shared connections)
- [Case Identifier CRUD](Case_Identifier_CRUD.md) (7 shared connections)
- [Case Set CRUD Handling](Case_Set_CRUD_Handling.md) (7 shared connections)
- [Case Service Implementation](Case_Service_Implementation.md) (6 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (3 shared connections)
- [Dimension CRUD Service](Dimension_CRUD_Service.md) (3 shared connections)

## Source Files

- `gen_epix/casedb/domain/command/case.py`
- `gen_epix/casedb/services/case/crud_case.py`
- `gen_epix/casedb/services/case/crud_case_data_collection_link.py`
- `gen_epix/casedb/services/case/crud_case_set_category.py`
- `gen_epix/casedb/services/case/crud_case_set_data_collection_link.py`
- `gen_epix/casedb/services/case/crud_case_set_member.py`
- `gen_epix/casedb/services/case/crud_case_set_status.py`
- `gen_epix/casedb/services/case/crud_case_type_set_category.py`
- `gen_epix/casedb/services/case/crud_common.py`

## Audit Trail

- EXTRACTED: 285 (93%)
- INFERRED: 22 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*