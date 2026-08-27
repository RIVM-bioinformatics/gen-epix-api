# case_validator.py

> 41 nodes · cohesion 0.08

## Key Concepts

- **case_validator.py** (44 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **IntervalTransformer** (21 connections) — `gen_epix/transform/transformers/interval.py`
- **interval.py** (18 connections) — `gen_epix/transform/transformers/interval.py`
- **transform/enum.py** (13 connections) — `gen_epix/transform/enum.py`
- **test_transform_interval.py** (13 connections) — `test/transform/unit/test_transform_interval.py`
- **iso_time.py** (12 connections) — `gen_epix/transform/transformers/iso_time.py`
- **TestIntervalTransformer** (12 connections) — `test/transform/unit/test_transform_interval.py`
- **test_transform_iso_time.py** (8 connections) — `test/transform/unit/test_transform_iso_time.py`
- **TimeUnit** (7 connections) — `gen_epix/transform/enum.py`
- **IntervalTransformStrategy** (6 connections) — `gen_epix/transform/enum.py`
- **Enum** (6 connections)
- **TimeUnitTransformStrategy** (6 connections) — `gen_epix/transform/enum.py`
- **TransformResultType** (6 connections) — `gen_epix/transform/enum.py`
- **.test_basic_interval_mapping()** (4 connections) — `test/transform/unit/test_transform_interval.py`
- **.test_decimal_values()** (4 connections) — `test/transform/unit/test_transform_interval.py`
- **.test_none_values()** (4 connections) — `test/transform/unit/test_transform_interval.py`
- **.test_on_no_match_raise()** (4 connections) — `test/transform/unit/test_transform_interval.py`
- **.test_on_no_match_set_none()** (4 connections) — `test/transform/unit/test_transform_interval.py`
- **.result_type()** (3 connections) — `gen_epix/transform/transform_result.py`
- **.test_is_transformable()** (3 connections) — `test/transform/unit/test_transform_interval.py`
- **.test_transform_value_direct()** (3 connections) — `test/transform/unit/test_transform_interval.py`
- **TransformType** (2 connections) — `gen_epix/transform/enum.py`
- **scenario_ids** (2 connections)
- **# TODO: transform any other col_types** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- **# TODO: replace by pre-calculated interval_relation_map for efficiency** (1 connections) — `gen_epix/casedb/services/case/case_validator.py`
- *... and 16 more nodes in this community*

## Relationships

- [IntervalToIntervalTransformer](IntervalToIntervalTransformer.md) (15 shared connections)
- [Transformer](Transformer.md) (15 shared connections)
- [ObjectAdapter](ObjectAdapter.md) (12 shared connections)
- [CrudOperation](CrudOperation.md) (7 shared connections)
- [IsoTimeTransformer](IsoTimeTransformer.md) (7 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (4 shared connections)
- [composite.py](composite.py.md) (3 shared connections)
- [CaseValidator](CaseValidator.md) (3 shared connections)
- [TransformResult](TransformResult.md) (3 shared connections)
- [BaseCaseService](BaseCaseService.md) (2 shared connections)
- [case_date.py](case_date.py.md) (2 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)

## Source Files

- `gen_epix/casedb/services/case/case_validator.py`
- `gen_epix/transform/enum.py`
- `gen_epix/transform/transform_result.py`
- `gen_epix/transform/transformers/interval.py`
- `gen_epix/transform/transformers/iso_time.py`
- `test/transform/unit/test_transform_interval.py`
- `test/transform/unit/test_transform_iso_time.py`

## Audit Trail

- EXTRACTED: 152 (98%)
- INFERRED: 3 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*