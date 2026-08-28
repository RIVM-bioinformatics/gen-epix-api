# Policy

> 56 nodes · cohesion 0.06

## Key Concepts

- **Policy** (37 connections) — `gen_epix/fastapp/model.py`
- **commondb/domain/policy/__init__.py** (16 connections) — `gen_epix/commondb/domain/policy/__init__.py`
- **commondb/domain/policy/abac.py** (13 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **PolicyDecisionPoint** (12 connections) — `gen_epix/fastapp/pdp.py`
- **casedb/domain/policy/__init__.py** (10 connections) — `gen_epix/casedb/domain/policy/__init__.py`
- **BaseIsOrganizationAdminPolicy** (10 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **BaseReadOrganizationResultsOnlyPolicy** (9 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **seqdb/domain/policy/__init__.py** (9 connections) — `gen_epix/seqdb/domain/policy/__init__.py`
- **.get_mapped_class()** (8 connections) — `gen_epix/commondb/app_impl_details.py`
- **BaseAbacPolicy** (8 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **BaseReadSelfResultsOnlyPolicy** (8 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **BaseUpdateUserPolicy** (8 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **omopdb/domain/policy/__init__.py** (8 connections) — `gen_epix/omopdb/domain/policy/__init__.py`
- **.apply()** (6 connections) — `gen_epix/fastapp/pdp.py`
- **.get_policies()** (6 connections) — `gen_epix/fastapp/pdp.py`
- **BaseReadUserPolicy** (5 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **BaseIsPermissionSubsetNewRolePolicy** (5 connections) — `gen_epix/commondb/domain/policy/rbac.py`
- **.register_policy()** (5 connections) — `gen_epix/fastapp/pdp.py`
- **.unregister_policy()** (5 connections) — `gen_epix/fastapp/pdp.py`
- **.register_retrieve_organization_ids_handler()** (4 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **.retrieve_organization_ids()** (4 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **Command** (4 connections)
- **Command** (4 connections)
- **.__init__()** (3 connections) — `gen_epix/commondb/domain/policy/abac.py`
- **UUID** (3 connections)
- *... and 31 more nodes in this community*

## Relationships

- [CrudOperation](CrudOperation.md) (21 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (15 shared connections)
- [App](App.md) (6 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (5 shared connections)
- [BaseCaseService](BaseCaseService.md) (4 shared connections)
- [RemoteApp](RemoteApp.md) (3 shared connections)
- [Permission](Permission.md) (2 shared connections)
- [omopdb/domain/enum.py](omopdb-domain-enum.py.md) (2 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (1 shared connections)
- [AppCfg](AppCfg.md) (1 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (1 shared connections)
- [ReadUserPolicy](ReadUserPolicy.md) (1 shared connections)

## Source Files

- `gen_epix/casedb/domain/policy/__init__.py`
- `gen_epix/commondb/app_impl_details.py`
- `gen_epix/commondb/domain/policy/__init__.py`
- `gen_epix/commondb/domain/policy/abac.py`
- `gen_epix/commondb/domain/policy/rbac.py`
- `gen_epix/fastapp/app.py`
- `gen_epix/fastapp/model.py`
- `gen_epix/fastapp/pdp.py`
- `gen_epix/omopdb/domain/policy/__init__.py`
- `gen_epix/seqdb/domain/policy/__init__.py`

## Audit Trail

- EXTRACTED: 156 (97%)
- INFERRED: 5 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*