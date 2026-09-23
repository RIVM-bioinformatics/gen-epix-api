# Commondb Dict Modifier

> 28 nodes · cohesion 0.12

## Key Concepts

- **TestCommondbDictModelModifier** (15 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **CommondbDictModelModifier** (14 connections) — `gen_epix/commondb/repositories/dict_modifier.py`
- **_make_obj()** (14 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **test_dict_modifier.py** (10 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.on_create()** (4 connections) — `gen_epix/commondb/repositories/dict_modifier.py`
- **.on_update()** (4 connections) — `gen_epix/commondb/repositories/dict_modifier.py`
- **_fixed_factory()** (3 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **datetime** (3 connections)
- **.setup_method()** (3 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_default_factory_produces_utc_aware_datetime()** (3 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **Hashable** (2 connections)
- **Model** (2 connections)
- **unit/conftest.py** (2 connections) — `test/commondb/unit/conftest.py`
- **.test_on_create_created_at_and_modified_at_are_equal()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_create_sets_created_at()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_create_sets_modified_at()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_create_sets_modified_by()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_create_with_none_user_id()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_update_does_not_touch_stored_obj()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_update_preserves_created_at_from_stored_obj()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_update_sets_modified_at_to_now()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_update_sets_modified_by()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_on_update_with_none_user_id()** (2 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **Encapsulates a DictRepository modifier for all databases that use…** (1 connections) — `gen_epix/commondb/repositories/dict_modifier.py`
- **Stamp a new commondb model with creation and modification metadata. Args:…** (1 connections) — `gen_epix/commondb/repositories/dict_modifier.py`
- *... and 3 more nodes in this community*

## Relationships

- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (4 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [Audit Timestamp Model Tests](Audit_Timestamp_Model_Tests.md) (2 shared connections)
- [System & ABAC Repositories](System_&_ABAC_Repositories.md) (1 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/repositories/dict_modifier.py`
- `test/commondb/unit/conftest.py`
- `test/commondb/unit/repositories/test_dict_modifier.py`

## Audit Trail

- EXTRACTED: 55 (95%)
- INFERRED: 3 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*