# Commondb Repository Interfaces

> 46 nodes · cohesion 0.06

## Key Concepts

- **BaseOrganizationRepository** (16 connections) — `gen_epix/commondb/domain/repository/organization.py`
- **BaseAbacRepository** (11 connections) — `gen_epix/commondb/domain/repository/abac.py`
- **commondb/repositories/organization_dict.py** (11 connections) — `gen_epix/commondb/repositories/organization_dict.py`
- **commondb/domain/repository/__init__.py** (10 connections) — `gen_epix/commondb/domain/repository/__init__.py`
- **repository/organization.py** (9 connections) — `gen_epix/commondb/domain/repository/organization.py`
- **seqdb/domain/repository/__init__.py** (9 connections) — `gen_epix/seqdb/domain/repository/__init__.py`
- **omopdb/domain/repository/__init__.py** (8 connections) — `gen_epix/omopdb/domain/repository/__init__.py`
- **BaseFileRepository** (8 connections) — `gen_epix/seqdb/domain/repository/file.py`
- **repository/file.py** (7 connections) — `gen_epix/seqdb/domain/repository/file.py`
- **file_dict.py** (7 connections) — `gen_epix/seqdb/repositories/file_dict.py`
- **file_sa.py** (7 connections) — `gen_epix/seqdb/repositories/file_sa.py`
- **.__init__()** (6 connections) — `gen_epix/commondb/domain/repository/organization.py`
- **.__init__()** (6 connections) — `gen_epix/commondb/services/abac.py`
- **commondb/domain/repository/abac.py** (5 connections) — `gen_epix/commondb/domain/repository/abac.py`
- **FileDictRepository** (5 connections) — `gen_epix/seqdb/repositories/file_dict.py`
- **FileSARepository** (5 connections) — `gen_epix/seqdb/repositories/file_sa.py`
- **.retrieve_user_by_key()** (4 connections) — `gen_epix/commondb/domain/repository/organization.py`
- **BaseAbacRepository** (4 connections) — `gen_epix/omopdb/domain/repository/abac.py`
- **.is_existing_user_by_key()** (3 connections) — `gen_epix/commondb/domain/repository/organization.py`
- **omopdb/domain/repository/abac.py** (3 connections) — `gen_epix/omopdb/domain/repository/abac.py`
- **User** (2 connections)
- **CommonBaseAbacRepository** (1 connections)
- **Define the repository interface for commondb ABAC persistence.** (1 connections) — `gen_epix/commondb/domain/repository/abac.py`
- **Encapsulates the persistence boundary for organization-administration policies.** (1 connections) — `gen_epix/commondb/domain/repository/abac.py`
- **Re-export commondb repository interfaces. ABAC, organization, and system…** (1 connections) — `gen_epix/commondb/domain/repository/__init__.py`
- *... and 21 more nodes in this community*

## Relationships

- [System & ABAC Repositories](System_&_ABAC_Repositories.md) (13 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (7 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (7 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (6 shared connections)
- [Casedb Repository Contracts](Casedb_Repository_Contracts.md) (4 shared connections)
- [Organization SQL Repository](Organization_SQL_Repository.md) (4 shared connections)
- [Case Date Derivation](Case_Date_Derivation.md) (2 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (2 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (2 shared connections)
- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (2 shared connections)
- [User Dictionary Repository](User_Dictionary_Repository.md) (1 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/repository/__init__.py`
- `gen_epix/commondb/domain/repository/abac.py`
- `gen_epix/commondb/domain/repository/organization.py`
- `gen_epix/commondb/repositories/organization_dict.py`
- `gen_epix/commondb/services/abac.py`
- `gen_epix/omopdb/domain/repository/__init__.py`
- `gen_epix/omopdb/domain/repository/abac.py`
- `gen_epix/seqdb/domain/repository/__init__.py`
- `gen_epix/seqdb/domain/repository/file.py`
- `gen_epix/seqdb/repositories/file_dict.py`
- `gen_epix/seqdb/repositories/file_sa.py`

## Audit Trail

- EXTRACTED: 111 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*