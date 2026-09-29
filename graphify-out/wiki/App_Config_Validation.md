# App Config Validation

> 22 nodes · cohesion 0.11

## Key Concepts

- **.rev_role_map()** (5 connections) — `gen_epix/commondb/app_impl_details.py`
- **._validate_role_map()** (5 connections) — `gen_epix/commondb/app_impl_details.py`
- **._validate_role_set_map()** (5 connections) — `gen_epix/commondb/app_impl_details.py`
- **Enum** (5 connections)
- **.idp_user_dependency()** (4 connections) — `gen_epix/commondb/app_impl_details.py`
- **.new_user_dependency()** (4 connections) — `gen_epix/commondb/app_impl_details.py`
- **.registered_user_dependency()** (4 connections) — `gen_epix/commondb/app_impl_details.py`
- **._validate_sorted_service_types()** (4 connections) — `gen_epix/commondb/app_impl_details.py`
- **computed_field** (4 connections)
- **field_validator** (4 connections)
- **._validate_model_class_map()** (3 connections) — `gen_epix/commondb/app_impl_details.py`
- **Role** (2 connections)
- **User** (2 connections)
- **Any** (1 connections)
- **Return the new-user dependency. Returns: Dependency that resolves a newly…** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Return the identity-provider user dependency. Returns: Dependency that resolves…** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Normalize role enum input and reject duplicate mapped values.** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Normalize a role-set enum class to its value mapping.** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Normalize service types to a unique list in dependency order.** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Validate implementation classes against their mapped base classes.** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Return a reverse lookup map from role string to role enum value.** (1 connections) — `gen_epix/commondb/app_impl_details.py`
- **Return the registered-user dependency. Returns: Dependency that resolves a…** (1 connections) — `gen_epix/commondb/app_impl_details.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (10 shared connections)

## Source Files

- `gen_epix/commondb/app_impl_details.py`

## Audit Trail

- EXTRACTED: 35 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*