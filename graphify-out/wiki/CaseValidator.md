# CaseValidator

> 47 nodes

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
- *... and 22 more nodes in this community*

## Relationships

- [UploadCasesCommand](UploadCasesCommand.md) (9 shared connections)
- [test_casedb_case_validator.py](test_casedb_case_validator.py.md) (7 shared connections)
- [casedb/domain/model/__init__.py](casedb-domain-model-__init__.py.md) (6 shared connections)
- [ObjectAdapter](ObjectAdapter.md) (4 shared connections)
- [case_validator.py](case_validator.py.md) (3 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (3 shared connections)
- [IsoTimeTransformer](IsoTimeTransformer.md) (3 shared connections)
- [IntervalToIntervalTransformer](IntervalToIntervalTransformer.md) (2 shared connections)
- [CompositeFilter](CompositeFilter.md) (2 shared connections)
- [UuidSetFilter](UuidSetFilter.md) (2 shared connections)
- [CasedbTestClient](CasedbTestClient.md) (2 shared connections)
- [model/omop/upload.py](model-omop-upload.py.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/case/upload.py`
- `gen_epix/casedb/services/case/case_validator.py`
- `test/casedb/unit/services/case/upload/test_casedb_case_validator.py`

## Audit Trail

- EXTRACTED: 129 (90%)
- INFERRED: 14 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*