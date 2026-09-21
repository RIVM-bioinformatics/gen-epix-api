# Case Data Validation

> 34 nodes · cohesion 0.12

## Key Concepts

- **CaseValidator** (39 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **UUID** (16 connections)
- **CaseDataIssue** (14 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **.transform_value_pairs()** (9 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.validate_and_transform()** (9 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._set_derived_value()** (8 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.calculate_case_date()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._get_content_references()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_decimal_to_interval()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_interval_to_interval()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_number_value_pairs()** (7 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_geo_value_pairs()** (6 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.transform_individual_values()** (6 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_time_value_pairs()** (6 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **.validate_unknown_columns()** (5 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._get_col_pairs()** (4 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **._transform_decimal()** (4 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **Represents a case-content issue associated with a column.** (1 connections) — `gen_epix/casedb/domain/model/case/upload.py`
- **NoReturn** (1 connections)
- **Generate all pairs of column IDs in both directions.** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **Normalize a decimal string or return the invalid-value sentinel. Args: value:…** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **Validate and transform the cases in a batch upload command. Where applicable,…** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **Return mutable content and issue-list references for all batch cases. The…** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **Append issues for unknown columns without removing their content. Args:…** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **Normalize individual values into validated content in place. Invalid values…** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- *... and 9 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (13 shared connections)
- [Case Type Validation Metadata](Case_Type_Validation_Metadata.md) (7 shared connections)
- [Case Validator Tests](Case_Validator_Tests.md) (6 shared connections)
- [Region Metadata Loading](Region_Metadata_Loading.md) (3 shared connections)
- [Concept Metadata Loading](Concept_Metadata_Loading.md) (3 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (2 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (2 shared connections)
- [Complete Case Type Models](Complete_Case_Type_Models.md) (1 shared connections)
- [Composite Filters](Composite_Filters.md) (1 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (1 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/casedb/services/case/case_validator.py`

## Audit Trail

- EXTRACTED: 100 (92%)
- INFERRED: 9 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*