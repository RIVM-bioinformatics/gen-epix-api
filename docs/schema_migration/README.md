# Database schema migrations

Alembic is the source of truth for SQL Server schema creation and evolution in
Gen-EpiX. API startup does **not** call `metadata.create_all()` for SQL Server;
the database must be migrated before an `SA_SQL` API starts. SQLite repositories
still create their schema automatically for tests and local fixtures.

Use this documentation as a map:

- [Developing migrations](development.md) explains the file layout, commands,
  review rules, and local validation loop.
- The generated history pages list every revision for
  [CommonDB](commondb.md), [CaseDB](casedb.md), [SeqDB](seqdb.md), and
  [OMOPDB](omopdb.md).

## One revision chain per database

Each service owns an Alembic environment beside its SQLAlchemy repository:

| Database | Configuration | Migration metadata | Revisions |
| --- | --- | --- | --- |
| CommonDB | `gen_epix/commondb/repositories/alembic.ini` | `gen_epix/commondb/repositories/sa_alembic/metadata.py` | `gen_epix/commondb/repositories/sa_alembic/versions/` |
| CaseDB | `gen_epix/casedb/repositories/alembic.ini` | `gen_epix/casedb/repositories/sa_alembic/metadata.py` | `gen_epix/casedb/repositories/sa_alembic/versions/` |
| SeqDB | `gen_epix/seqdb/repositories/alembic.ini` | `gen_epix/seqdb/repositories/sa_alembic/metadata.py` | `gen_epix/seqdb/repositories/sa_alembic/versions/` |
| OMOPDB | `gen_epix/omopdb/repositories/alembic.ini` | `gen_epix/omopdb/repositories/sa_alembic/metadata.py` | `gen_epix/omopdb/repositories/sa_alembic/versions/` |

These are independent revision chains even though CaseDB, SeqDB, and OMOPDB
also persist shared CommonDB models in their own databases. A change to a
shared model can therefore require a new revision in more than one chain. Run
the migration tests to discover every affected database; do not assume that a
CommonDB revision updates the copies embedded in the other service databases.

Each database records its current revision in
`alembic.alembic_version`. The environment creates the application-owned
`alembic` schema on SQL Server before running a migration. Do not move this
table to SQL Server's protected `sys` schema.

## Runtime flow

```text
SQLAlchemy models
      │
      ▼
sa_alembic/metadata.py ──► Alembic autogenerate comparison
      │
      ▼
sa_alembic/versions/<revision>.py
      │
      ▼
alembic upgrade head ──► service schemas/tables ──► alembic.alembic_version
      │
      ▼
SA_SQL API starts
```

The URL is deliberately absent from `alembic.ini`. Every Alembic invocation
must receive it through either:

1. `-x url='<SQLAlchemy URL>'`; or
2. the `ALEMBIC_URL` environment variable.

The `-x` value wins when both are set. Prefer `ALEMBIC_URL` in automation so
credentials do not appear in process arguments, and never paste a production
connection string into logs, documentation, or source control.

## Command quick reference

Set `SERVICE` to `commondb`, `casedb`, `seqdb`, or `omopdb`:

```sh
export SERVICE=seqdb
export ALEMBIC_URL='<SQLAlchemy SQL Server URL>'

alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" current
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" heads
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" history --verbose
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" upgrade head
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" check
```

`current` reports the database state, while `heads` reports the latest revision
available in the checked-out code. They should agree after deployment.

Regenerate the committed history pages after adding a revision:

```sh
make generate-schema-migration-docs
```

## Ownership boundaries

- SQLAlchemy models describe the desired schema.
- Each service's `sa_alembic/metadata.py` selects the metadata compared by
  Alembic.
- Revision files are the reviewed, ordered deployment instructions. Generated
  output is only a draft and must be inspected.
- Local Compose and the deployment repository are responsible for running
  `upgrade head` before an API starts.
- Application startup must not be used as a second schema-management path.

If documentation and executable behavior disagree, trust the models, Alembic
environment, revision chain, and deployment pipeline in that order, then update
the documentation in the same change.
