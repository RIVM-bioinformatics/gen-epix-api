# Case Data Validator

> 45 nodes · cohesion 0.09

## Key Concepts

- **CaseValidator** (45 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **UUID** (16 connections)
- **CaseDataIssue** (14 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **._transform_interval_to_interval()** (9 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_time_value_pairs()** (9 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.transform_value_pairs()** (9 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.validate_and_transform()** (9 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_decimal_to_interval()** (8 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.calculate_case_date()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._get_content_references()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._init_metadata()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._retrieve_concept_data()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._set_derived_value()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_number_value_pairs()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._retrieve_region_data()** (6 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_geo_value_pairs()** (6 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.transform_individual_values()** (6 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.__init__()** (5 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.validate_unknown_columns()** (5 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._get_col_pairs()** (4 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._init_concept_metadata()** (4 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._init_organization_metadata()** (3 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._init_region_metadata()** (3 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._retrieve_organization_data()** (3 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_decimal()** (3 connections) — `gen_epix/casedb/services/case/case_validator.py`
- *... and 20 more nodes in this community*

## Relationships

- [Case Batch Upload](Case_Batch_Upload.md) (9 shared connections)
- [Case Validator Tests](Case_Validator_Tests.md) (7 shared connections)
- [Case Domain Enums](Case_Domain_Enums.md) (6 shared connections)
- [Transform Framework Registry & Pipeline](Transform_Framework_Registry_&_Pipeline.md) (4 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (4 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (3 shared connections)
- [Data Transform Strategies](Data_Transform_Strategies.md) (3 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (2 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (2 shared connections)
- [Interval Transformation](Interval_Transformation.md) (2 shared connections)
- [Casedb Test Client Helpers](Casedb_Test_Client_Helpers.md) (2 shared connections)
- [Case Date Calculation Utils](Case_Date_Calculation_Utils.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/casedb/services/case/case_validator.py`

## Audit Trail

- EXTRACTED: 125 (90%)
- INFERRED: 14 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*