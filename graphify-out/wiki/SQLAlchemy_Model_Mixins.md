# SQLAlchemy Model Mixins

> 76 nodes · cohesion 0.11

## Key Concepts

- **Base** (143 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **omopdb/repositories/sa_model/__init__.py** (83 connections) — `gen_epix/omopdb/repositories/sa_model/__init__.py`
- **sa_model/omop.py** (64 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Encapsulates a SQLAlchemy model for the corresponding persistable domain model.** (55 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **NoIdRowMetadataMixin** (44 connections) — `gen_epix/commondb/repositories/sa_model/base.py`
- **IdentifierMixin** (29 connections) — `gen_epix/commondb/repositories/sa_model/organization.py`
- **DataLineageMixin** (25 connections) — `gen_epix/omopdb/repositories/sa_model/base.py`
- **ConditionEra** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **ConditionOccurrence** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Cost** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Death** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **DeviceExposure** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **DoseEra** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **DrugEra** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **DrugExposure** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Episode** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **EpisodeEvent** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Measurement** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Note** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **NoteNlp** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Observation** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **ObservationPeriod** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **PayerPlanPeriod** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **Person** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- **ProcedureOccurrence** (6 connections) — `gen_epix/omopdb/repositories/sa_model/omop.py`
- *... and 51 more nodes in this community*

## Relationships

- [Organization SQL Repository](Organization_SQL_Repository.md) (38 shared connections)
- [Seq Upload & SQL Models](Seq_Upload_&_SQL_Models.md) (36 shared connections)
- [Case SQLAlchemy Tables](Case_SQLAlchemy_Tables.md) (33 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (6 shared connections)
- [Casedb ABAC SQL Models](Casedb_ABAC_SQL_Models.md) (6 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (4 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (3 shared connections)
- [Organization Column Mixins](Organization_Column_Mixins.md) (1 shared connections)
- [System & ABAC Repositories](System_&_ABAC_Repositories.md) (1 shared connections)
- [OmopDB Alembic Migrations](OmopDB_Alembic_Migrations.md) (1 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (1 shared connections)
- [Database Session Isolation](Database_Session_Isolation.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/repositories/sa_model/base.py`
- `gen_epix/commondb/repositories/sa_model/organization.py`
- `gen_epix/omopdb/repositories/sa_model/__init__.py`
- `gen_epix/omopdb/repositories/sa_model/base.py`
- `gen_epix/omopdb/repositories/sa_model/omop.py`
- `test/fastapp/integration/api/test_fastapp_api.py`

## Audit Trail

- EXTRACTED: 445 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*