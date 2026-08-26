# Dict Model Modifier Tests

> 20 nodes · cohesion 0.17

## Key Concepts

- **TestCommondbDictModelModifier** (15 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **_make_obj()** (14 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **test_dict_modifier.py** (10 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **_fixed_factory()** (3 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **datetime** (3 connections)
- **.setup_method()** (3 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
- **.test_default_factory_produces_utc_aware_datetime()** (3 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`
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
- **scenario_ids** (1 connections)
- **Unit tests for CommondbDictModelModifier. Verifies that: - on_create stamps…** (1 connections) — `test/commondb/unit/repositories/test_dict_modifier.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (6 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (2 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (1 shared connections)

## Source Files

- `test/commondb/unit/conftest.py`
- `test/commondb/unit/repositories/test_dict_modifier.py`

## Audit Trail

- EXTRACTED: 40 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*