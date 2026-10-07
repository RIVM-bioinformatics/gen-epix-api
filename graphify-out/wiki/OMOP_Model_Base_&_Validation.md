# OMOP Model Base & Validation

> 108 nodes · cohesion 0.04

## Key Concepts

- **omop/ontology.py** (26 connections) — `gen_epix/omopdb/domain/model/omop/ontology.py`
- **_uuid_field_name()** (25 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **validate_str_key_args()** (21 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **validate_int_key_args()** (20 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **validate_str_for_uuid_field()** (20 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **test_omopdb_model_validators.py** (18 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **model/omop/base.py** (17 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **TestValidateIntPrimaryKeyArgs** (17 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **TestValidateStrPrimaryKeyArgs** (15 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **health_system.py** (14 connections) — `gen_epix/omopdb/domain/model/omop/health_system.py`
- **int_to_uuid()** (14 connections) — `gen_epix/util.py`
- **str_to_uuid()** (14 connections) — `gen_epix/util.py`
- **_int_field_name()** (14 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **TestValidateStrForUuidField** (14 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **omop/metadata.py** (12 connections) — `gen_epix/omopdb/domain/model/omop/metadata.py`
- **_str_field_name()** (12 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_provided_uuid_id_absent_derives_uuid()** (7 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_bool_int_id_treated_as_int()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_as_uuid_field_int_id_absent_switches()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_as_uuid_field_switches_and_derives()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_int_id_provided_uuid_id_none_derives_uuid()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_matching_uuid_and_int_id_passes()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_non_dict_types_raise_value_error()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_uuid_id_as_matching_string_passes()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- **.test_zero_int_id()** (6 connections) — `test/omopdb/unit/domain/test_omopdb_model_validators.py`
- *... and 83 more nodes in this community*

## Relationships

- [OMOP Concept Validators](OMOP_Concept_Validators.md) (18 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (16 shared connections)
- [OMOP Concept Key Validation](OMOP_Concept_Key_Validation.md) (15 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [Provider & Location Models](Provider_&_Location_Models.md) (4 shared connections)
- [Data Lineage Mixin Tests](Data_Lineage_Mixin_Tests.md) (4 shared connections)
- [Audit Timestamp Model Tests](Audit_Timestamp_Model_Tests.md) (3 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (3 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (3 shared connections)
- [OMOP CDM Metadata](OMOP_CDM_Metadata.md) (3 shared connections)
- [OmopDB Enums & Base Model](OmopDB_Enums_&_Base_Model.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/domain/model/omop/base.py`
- `gen_epix/omopdb/domain/model/omop/health_system.py`
- `gen_epix/omopdb/domain/model/omop/metadata.py`
- `gen_epix/omopdb/domain/model/omop/ontology.py`
- `gen_epix/util.py`
- `test/omopdb/unit/domain/test_omopdb_model_validators.py`

## Audit Trail

- EXTRACTED: 298 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*