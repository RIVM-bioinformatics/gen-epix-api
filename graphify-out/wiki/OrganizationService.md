# OrganizationService

> 78 nodes · cohesion 0.04

## Key Concepts

- **OrganizationService** (24 connections) — `gen_epix/commondb/services/organization.py`
- **RbacService** (21 connections) — `gen_epix/commondb/services/rbac.py`
- **casedb/services/__init__.py** (19 connections) — `gen_epix/casedb/services/__init__.py`
- **commondb/services/__init__.py** (19 connections) — `gen_epix/commondb/services/__init__.py`
- **SystemService** (19 connections) — `gen_epix/commondb/services/system.py`
- **SeqdbService** (16 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **seqdb/services/__init__.py** (15 connections) — `gen_epix/seqdb/services/__init__.py`
- **omopdb/services/__init__.py** (14 connections) — `gen_epix/omopdb/services/__init__.py`
- **PackageMetadata** (8 connections) — `gen_epix/commondb/domain/model/system.py`
- **model/system.py** (7 connections) — `gen_epix/commondb/domain/model/system.py`
- **Outage** (7 connections) — `gen_epix/commondb/domain/model/system.py`
- **._parse_and_get_package_metadata()** (7 connections) — `gen_epix/commondb/services/system.py`
- **RetrieveLicensesCommand** (6 connections) — `gen_epix/commondb/domain/command/system.py`
- **services/seqdb/__init__.py** (5 connections) — `gen_epix/casedb/services/seqdb/__init__.py`
- **RbacService** (5 connections) — `gen_epix/omopdb/services/rbac.py`
- **seqdb/services/abac.py** (5 connections) — `gen_epix/seqdb/services/abac.py`
- **UUID** (4 connections)
- **.crud()** (4 connections) — `gen_epix/casedb/services/seqdb/service.py`
- **.retrieve_licenses()** (4 connections) — `gen_epix/commondb/domain/service/system.py`
- **.retrieve_licenses()** (4 connections) — `gen_epix/commondb/services/remote_app.py`
- **._extract_homepage_from_project_urls()** (4 connections) — `gen_epix/commondb/services/system.py`
- **.retrieve_licenses()** (4 connections) — `gen_epix/commondb/services/system.py`
- **omopdb/services/organization.py** (4 connections) — `gen_epix/omopdb/services/organization.py`
- **OrganizationService** (4 connections) — `gen_epix/omopdb/services/organization.py`
- **omopdb/services/rbac.py** (4 connections) — `gen_epix/omopdb/services/rbac.py`
- *... and 53 more nodes in this community*

## Relationships

- [CrudOperation](CrudOperation.md) (20 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (12 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (10 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (5 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (5 shared connections)
- [UserManager](UserManager.md) (4 shared connections)
- [AuthService](AuthService.md) (4 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (4 shared connections)
- [AppCfg](AppCfg.md) (4 shared connections)
- [.anonymize_user](anonymize_user.md) (4 shared connections)
- [SeqdbRemoteApp](SeqdbRemoteApp.md) (3 shared connections)
- [BaseSeqdbService](BaseSeqdbService.md) (3 shared connections)

## Source Files

- `gen_epix/casedb/services/__init__.py`
- `gen_epix/casedb/services/seqdb/__init__.py`
- `gen_epix/casedb/services/seqdb/service.py`
- `gen_epix/commondb/domain/command/system.py`
- `gen_epix/commondb/domain/model/system.py`
- `gen_epix/commondb/domain/service/system.py`
- `gen_epix/commondb/services/__init__.py`
- `gen_epix/commondb/services/organization.py`
- `gen_epix/commondb/services/rbac.py`
- `gen_epix/commondb/services/remote_app.py`
- `gen_epix/commondb/services/system.py`
- `gen_epix/omopdb/services/__init__.py`
- `gen_epix/omopdb/services/organization.py`
- `gen_epix/omopdb/services/rbac.py`
- `gen_epix/seqdb/services/__init__.py`
- `gen_epix/seqdb/services/abac.py`

## Audit Trail

- EXTRACTED: 207 (95%)
- INFERRED: 11 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*