# Audit Timestamp Model Tests

> 32 nodes · cohesion 0.10

## Key Concepts

- **ModelNoId** (32 connections) — `gen_epix/commondb/domain/model/base.py`
- **TestModelMetadataPolicy** (16 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **_make_cmd()** (13 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **TestSetCreated** (7 connections) — `test/commondb/unit/logging/test_model.py`
- **TestSetModified** (7 connections) — `test/commondb/unit/logging/test_model.py`
- **._obj_with_metadata()** (7 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **logging/test_model.py** (6 connections) — `test/commondb/unit/logging/test_model.py`
- **.set_created()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **.set_modified()** (3 connections) — `gen_epix/commondb/domain/model/base.py`
- **UUID** (3 connections)
- **.test_app_admin_fields_are_not_nulled()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_non_model_noid_objects_in_list_are_skipped()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_none_user_bypasses_masking()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_regular_user_gets_fields_nulled_list()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_regular_user_gets_fields_nulled_single()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_root_user_fields_are_not_nulled()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **Record the current UTC time and user as the latest modification.** (2 connections) — `gen_epix/commondb/domain/model/base.py`
- **scenario_ids** (2 connections)
- **.setup_method()** (2 connections) — `test/commondb/unit/logging/test_model.py`
- **.setup_method()** (2 connections) — `test/commondb/unit/logging/test_model.py`
- **.test_none_retval_passes_through()** (2 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **Represents creation and modification metadata to a FastApp domain model. This…** (1 connections) — `gen_epix/commondb/domain/model/base.py`
- **Unit tests for ModelNoId.set_modified and ModelNoId.set_created. Test coverage:…** (1 connections) — `test/commondb/unit/logging/test_model.py`
- **# TODO: check scenario ids, how are they determined?** (1 connections) — `test/commondb/unit/logging/test_model.py`
- **.test_created_at_and_modified_at_are_equal()** (1 connections) — `test/commondb/unit/logging/test_model.py`
- *... and 7 more nodes in this community*

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [System Outage & License Models](System_Outage_&_License_Models.md) (4 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (4 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (4 shared connections)
- [OMOP Model Base & Validation](OMOP_Model_Base_&_Validation.md) (3 shared connections)
- [Commondb Dict Modifier](Commondb_Dict_Modifier.md) (2 shared connections)
- [OmopDB Enums & Base Model](OmopDB_Enums_&_Base_Model.md) (2 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (2 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (2 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (1 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/base.py`
- `test/commondb/unit/logging/test_model.py`
- `test/commondb/unit/policies/test_model_process_metadata_policy.py`

## Audit Trail

- EXTRACTED: 75 (88%)
- INFERRED: 10 (12%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*