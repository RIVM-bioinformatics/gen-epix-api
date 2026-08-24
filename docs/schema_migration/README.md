# Schema migrations

Each service database has its own Alembic environment next to its SQLAlchemy
models. Although the service models include the shared CommonDB models, every
database has an independent Alembic revision chain:

| Database | Alembic configuration |
| --- | --- |
| CommonDB | `gen_epix/commondb/repositories/alembic.ini` |
| CaseDB | `gen_epix/casedb/repositories/alembic.ini` |
| SeqDB | `gen_epix/seqdb/repositories/alembic.ini` |
| OMOPDB | `gen_epix/omopdb/repositories/alembic.ini` |

The version table is stored in an application-owned `alembic` schema. Do not
put it in SQL Server's protected `sys` schema.

## Local clean bootstrap

The SQL Server Compose stacks create four empty databases and run a one-shot
`migrate-*` service for each of them before starting the APIs:

```sh
docker compose -f docker-compose.sql.yml down -v
docker compose -f docker-compose.sql.yml build
docker compose -f docker-compose.sql.yml up -d --wait lsp_sql
docker compose -f docker-compose.sql.yml run --rm init-db
docker compose -f docker-compose.sql.yml run --rm migrate-commondb
docker compose -f docker-compose.sql.yml run --rm migrate-casedb
docker compose -f docker-compose.sql.yml run --rm migrate-seqdb
docker compose -f docker-compose.sql.yml run --rm migrate-omopdb
docker compose -f docker-compose.sql.yml up -d --wait seqdb omopdb casedb
```

Use `docker-compose.sql.idp.yml` instead when testing with the mock OIDC
provider. The explicit job commands avoid Docker Compose's `--wait` behaviour
that treats an unreferenced, successfully completed one-shot service as a
failure. Inspect a migration job with, for example:

```sh
docker compose -f docker-compose.sql.yml logs migrate-seqdb
```

## PRD deployment

Run one short-lived migration Job per database before its API Deployment. The
Job must use the same release image, an `ALEMBIC_URL` secret that points to the
same Azure SQL database as the API, and this command pattern:

```sh
alembic -c gen_epix/seqdb/repositories/alembic.ini upgrade head
```

Create corresponding jobs for `commondb`, `casedb`, and `omopdb`. Make each API
Deployment wait for its own Job to complete successfully. This is the intended
Chartreuse/Kubernetes arrangement: a release-time Job, not an API-startup
sidecar. A failed migration leaves the API Deployment unstarted.

The API no longer runs `metadata.create_all()` for SQL Server, so this
pre-deployment step is required. SQLite remains automatically initialised for
tests and fixtures.

## Existing databases

Do not run the initial revision against a database that already contains the
unmanaged production schema: it attempts to create tables that are already
there. Take a backup, inspect the current schema, then record the matching
baseline with `stamp`.

For an existing current deployment, stamp CommonDB, CaseDB and OMOPDB at their
initial revisions. SeqDB must be stamped at its initial revision and then
upgraded so that the LSP-3497 compatibility revision removes the historical
unique constraints on `sample.code`, `read_set.code`, and `seq.code`:

```sh
alembic -c gen_epix/commondb/repositories/alembic.ini stamp b9c5e10bf42c
alembic -c gen_epix/casedb/repositories/alembic.ini stamp bbc386e12a58
alembic -c gen_epix/omopdb/repositories/alembic.ini stamp 252f23d99c89
alembic -c gen_epix/seqdb/repositories/alembic.ini stamp 973d81851aeb
alembic -c gen_epix/seqdb/repositories/alembic.ini upgrade head
```

Run the commands with `ALEMBIC_URL` set to the relevant database connection.
`stamp` records a revision but does not validate or change the tables, so it
must only be used after confirming the existing schema matches that baseline.

## Developing a migration

1. Change the SQLAlchemy models for one service.
2. Start an empty SQL Server database and provide its URL through `ALEMBIC_URL`.
3. Generate and inspect the candidate revision:

   ```sh
   alembic -c gen_epix/seqdb/repositories/alembic.ini revision --autogenerate -m "describe change"
   ```

4. Add hand-written SQL Server operations when autogeneration cannot express
   the operation, then run `upgrade head` and `alembic check` against Azure SQL.
5. Commit the model and revision together. The `test/general/migrations` test
   is part of `run.py test_all` and prevents model tables or columns from being
   added without a migration operation.

Generate the current revision-history pages with:

```sh
make generate-schema-migration-docs
```

## SQL Server-specific choices

- Initial revisions create service schemas explicitly because Alembic
  autogeneration creates tables but does not create their schemas.
- The Alembic version table uses the `alembic` schema; Azure SQL rejects use of
  the system `sys` schema for this purpose.
- `GETUTCDATE()` defaults are excluded from automatic default comparison,
  because SQL Server reflects that expression differently from the project's
  custom SQLAlchemy default type.
- OMOP migration metadata normalizes primary-key columns to `NOT NULL`, which
  is the SQL Server invariant and avoids false nullable-change revisions from
  legacy ORM annotations.
- SeqDB's historical code constraints are removed with guarded, hand-written
  SQL Server operations. The migration works whether the old object is a unique
  constraint or a unique index, and it is safe for already-correct databases.
