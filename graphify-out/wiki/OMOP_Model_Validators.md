# OMOP Model Validators

> 110 nodes · cohesion 0.04

## Key Concepts

- **_uuid_field_name()** (25 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **validate_str_key_args()** (22 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **validate_int_key_args()** (21 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **validate_str_for_uuid_field()** (21 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **str_to_uuid()** (19 connections) — `gen_epix/util.py`
- **model/omop/base.py** (18 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **test_omopdb_model_validators.py** (18 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **int_to_uuid()** (17 connections) — `gen_epix/util.py`
- **TestValidateIntPrimaryKeyArgs** (17 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **TestValidateStrPrimaryKeyArgs** (15 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **_int_field_name()** (14 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **TestValidateIntForUuidField** (14 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **TestValidateStrForUuidField** (14 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **_str_field_name()** (12 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **parametrize** (8 connections)
- **.test_int_id_provided_uuid_id_absent_derives_uuid()** (7 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_bool_int_id_treated_as_int()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_as_uuid_field_int_id_absent_switches()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_as_uuid_field_switches_and_derives()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_provided_uuid_id_none_derives_uuid()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_matching_uuid_and_int_id_passes()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_non_dict_types_raise_value_error()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_uuid_id_as_matching_string_passes()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_zero_int_id()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_matching_uuid_and_str_id_passes()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- *... and 85 more nodes in this community*

## Relationships

- [UUID Field Validation](UUID_Field_Validation.md) (24 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (13 shared connections)
- [Project Utility Functions](Project_Utility_Functions.md) (6 shared connections)
- [Data Lineage Mixin Tests](Data_Lineage_Mixin_Tests.md) (2 shared connections)
- [Base User Manager & RBAC](Base_User_Manager_&_RBAC.md) (1 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/model/omop/base.py`
- `gen_epix/util.py`
- `test/omopdb/unit/domain/test_omopdb_model_validators.py`

## Audit Trail

- EXTRACTED: 283 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*