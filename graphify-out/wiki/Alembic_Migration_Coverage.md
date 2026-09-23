# Alembic Migration Coverage

> 16 nodes · cohesion 0.13

## Key Concepts

- **test_alembic_migrations.py** (9 connections) — `test/general/migrations/test_alembic_migrations.py`
- **test_drop_legacy_seq_code_constraints()** (8 connections) — `test/general/migrations/test_alembic_migrations.py`
- **_migration_tables()** (4 connections) — `test/general/migrations/test_alembic_migrations.py`
- **test_models_have_migration_operations()** (4 connections) — `test/general/migrations/test_alembic_migrations.py`
- **execute()** (2 connections) — `test/general/migrations/test_alembic_migrations.py`
- **parametrize** (1 connections)
- **Path** (1 connections)
- **Verify that Alembic revisions cover the SQLAlchemy database models.** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **Fail CI when a persistable model table or column has no revision DDL.** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **The LSP-3497 revision drops constraints and legacy unique indexes safely.** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **Collect table and column names created by all revisions for one service.** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **drop_constraint()** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **drop_index()** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **get_bind()** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **__init__()** (1 connections) — `test/general/migrations/test_alembic_migrations.py`
- **scalar()** (1 connections) — `test/general/migrations/test_alembic_migrations.py`

## Relationships

- [Error Code Uniqueness Check](Error_Code_Uniqueness_Check.md) (1 shared connections)
- [CaseDB Alembic Migrations](CaseDB_Alembic_Migrations.md) (1 shared connections)
- [CommonDB Alembic Migrations](CommonDB_Alembic_Migrations.md) (1 shared connections)
- [OmopDB Alembic Migrations](OmopDB_Alembic_Migrations.md) (1 shared connections)
- [SeqDB Alembic Migrations](SeqDB_Alembic_Migrations.md) (1 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (1 shared connections)

## Source Files

- `test/general/migrations/test_alembic_migrations.py`

## Audit Trail

- EXTRACTED: 21 (95%)
- INFERRED: 1 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*