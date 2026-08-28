# services/user_manager.py

> 56 nodes · cohesion 0.05

## Key Concepts

- **services/user_manager.py** (24 connections) — `gen_epix/commondb/services/user_manager.py`
- **BaseOrganizationService** (23 connections) — `gen_epix/commondb/domain/service/organization.py`
- **BaseRbacService** (16 connections) — `gen_epix/commondb/domain/service/rbac.py`
- **commondb/domain/service/__init__.py** (15 connections) — `gen_epix/commondb/domain/service/__init__.py`
- **BaseSystemService** (15 connections) — `gen_epix/commondb/domain/service/system.py`
- **service/organization.py** (14 connections) — `gen_epix/commondb/domain/service/organization.py`
- **seqdb/domain/service/__init__.py** (13 connections) — `gen_epix/seqdb/domain/service/__init__.py`
- **service/rbac.py** (11 connections) — `gen_epix/commondb/domain/service/rbac.py`
- **omopdb/domain/service/__init__.py** (11 connections) — `gen_epix/omopdb/domain/service/__init__.py`
- **service/system.py** (10 connections) — `gen_epix/commondb/domain/service/system.py`
- **service/user_manager.py** (10 connections) — `gen_epix/commondb/domain/service/user_manager.py`
- **BaseUserManager** (10 connections) — `gen_epix/commondb/domain/service/user_manager.py`
- **policy/system.py** (8 connections) — `gen_epix/commondb/domain/policy/system.py`
- **BaseAbacService** (8 connections) — `gen_epix/seqdb/domain/service/abac.py`
- **.__init__()** (7 connections) — `gen_epix/commondb/domain/service/user_manager.py`
- **ServiceType** (5 connections) — `gen_epix/commondb/domain/enum.py`
- **policy/rbac.py** (5 connections) — `gen_epix/commondb/domain/policy/rbac.py`
- **.anonymize_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.register_invited_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **.update_user()** (4 connections) — `gen_epix/commondb/domain/service/organization.py`
- **User** (4 connections)
- **.retrieve_own_permissions()** (4 connections) — `gen_epix/commondb/domain/service/rbac.py`
- **seqdb/policies/update_user_policy.py** (4 connections) — `gen_epix/seqdb/policies/update_user_policy.py`
- **.__init__()** (3 connections) — `gen_epix/commondb/domain/policy/system.py`
- **.retrieve_user_by_key()** (3 connections) — `gen_epix/commondb/domain/service/organization.py`
- *... and 31 more nodes in this community*

## Relationships

- [CrudOperation](CrudOperation.md) (22 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (17 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (10 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (7 shared connections)
- [Permission](Permission.md) (6 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (6 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (5 shared connections)
- [Policy](Policy.md) (5 shared connections)
- [OrganizationService](OrganizationService.md) (5 shared connections)
- [casedb/repositories/__init__.py](casedb-repositories-__init__.py.md) (4 shared connections)
- [UserManager](UserManager.md) (4 shared connections)
- [App](App.md) (3 shared connections)

## Source Files

- `gen_epix/commondb/domain/enum.py`
- `gen_epix/commondb/domain/policy/rbac.py`
- `gen_epix/commondb/domain/policy/system.py`
- `gen_epix/commondb/domain/service/__init__.py`
- `gen_epix/commondb/domain/service/organization.py`
- `gen_epix/commondb/domain/service/rbac.py`
- `gen_epix/commondb/domain/service/system.py`
- `gen_epix/commondb/domain/service/user_manager.py`
- `gen_epix/commondb/services/user_manager.py`
- `gen_epix/omopdb/domain/service/__init__.py`
- `gen_epix/seqdb/domain/service/__init__.py`
- `gen_epix/seqdb/domain/service/abac.py`
- `gen_epix/seqdb/policies/update_user_policy.py`

## Audit Trail

- EXTRACTED: 187 (95%)
- INFERRED: 9 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*