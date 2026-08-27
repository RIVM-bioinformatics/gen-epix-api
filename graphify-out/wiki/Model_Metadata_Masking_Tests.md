# Model Metadata Masking Tests

> 15 nodes · cohesion 0.25

## Key Concepts

- **TestModelMetadataPolicy** (14 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **_make_cmd()** (13 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **._obj_with_metadata()** (7 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **_make_user()** (4 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.setup_method()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_app_admin_fields_are_not_nulled()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_non_model_noid_objects_in_list_are_skipped()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_none_user_bypasses_masking()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_regular_user_gets_fields_nulled_list()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_regular_user_gets_fields_nulled_single()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **.test_root_user_fields_are_not_nulled()** (3 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **User** (2 connections)
- **.test_none_retval_passes_through()** (2 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`
- **scenario_ids** (1 connections)
- **Build a UserCrudCommand bypassing field validation.** (1 connections) — `test/commondb/unit/policies/test_model_process_metadata_policy.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (5 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (2 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (2 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (1 shared connections)
- [Read User Policy Tests](Read_User_Policy_Tests.md) (1 shared connections)

## Source Files

- `test/commondb/unit/policies/test_model_process_metadata_policy.py`

## Audit Trail

- EXTRACTED: 36 (92%)
- INFERRED: 3 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*