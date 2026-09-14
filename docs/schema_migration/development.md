# Developing Alembic migrations

This guide covers the normal workflow for changing a SQL Server schema. Use a
disposable database first; repeat the validation on an environment-like SQL
Server or Azure SQL database before promotion.

## Before editing

Identify every database that contains the changed model. Service migration
metadata is assembled from the classes exported by that service's `sa_model`
package, and service databases can include CommonDB tables. For each affected
database:

1. inspect `sa_alembic/metadata.py`;
2. inspect the current head in `sa_alembic/versions/`;
3. confirm that there is one head; and
4. create a separate revision in that database's chain.

Do not edit or renumber a revision that may already have run outside your local
environment. Add a follow-up revision instead. Do not create a merge revision
merely to hide two accidental heads; first establish whether both branches
have been deployed and coordinate the ordering with the other author.

## Prepare a baseline database

Create an empty service database, check out the code before your model change,
and apply the existing chain:

```sh
export SERVICE=seqdb
export ALEMBIC_URL='<SQLAlchemy SQL Server URL>'

alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" upgrade head
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" current
```

Then apply the model change. Autogenerate compares the checked-out metadata
with the live schema, so generating against a completely empty, unmigrated
database would incorrectly propose the whole schema again.

The repository Compose stack can provide disposable SQL Server databases:

```sh
docker compose -f docker-compose.sql.yml down -v
docker compose -f docker-compose.sql.yml build
docker compose -f docker-compose.sql.yml up -d --wait lsp_sql
docker compose -f docker-compose.sql.yml run --rm init-db
```

The `down -v` command deletes the local SQL Server volume. Never use it against
a Compose project containing data you need to keep.

## Generate and review the revision

Generate a candidate with a short description:

```sh
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" \
  revision --autogenerate -m "describe schema change"
```

Treat the new file as hand-written production code. Check all of the following:

- `revision` is new, `down_revision` is the previous single head, and the file
  is in the correct service directory;
- schema names are explicit for tables, foreign keys, indexes, and constraints;
- operations are ordered so referenced schemas and tables exist first;
- existing rows can satisfy new `NOT NULL`, unique, check, and foreign-key
  constraints;
- renames remain renames instead of destructive drop-and-create pairs;
- index and constraint names match what SQL Server actually created;
- both `upgrade()` and `downgrade()` express the intended behavior;
- any data migration is bounded, restart-safe where practical, and reviewed for
  lock duration; and
- no unrelated metadata drift was swept into the revision.

Autogenerate cannot infer intent. Renames, data backfills, constraint changes,
and SQL Server-specific catalog checks commonly require manual operations.

## Validate locally

At minimum, run the migration-focused tests once:

```sh
python run.py run_test "test/general/migrations"
```

The coverage test statically verifies that every mapped table and column occurs
in a migration operation. It is a guard against omissions, not proof that SQL
executes successfully or preserves data.

Run the candidate against SQL Server:

```sh
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" upgrade head
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" current
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" check
```

When the downgrade is safe and meaningful, also exercise a round trip on a
disposable copy:

```sh
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" downgrade -1
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" upgrade head
```

Do not test a destructive downgrade on shared or production data. For a risky
change, restore a production-like backup to an isolated database and measure
the upgrade there. Verify row counts, critical constraints/indexes, and the API
paths that use the changed objects.

Finally run the normal repository checks appropriate to the change, including
the affected unit/integration tests and formatting checks. Commit the model,
revision, focused tests, and regenerated history page together.

## Local full-stack bootstrap

The SQL Compose files model the required deployment order with one-shot
`migrate-*` services. To bootstrap all four databases explicitly:

```sh
docker compose -f docker-compose.sql.yml run --rm migrate-commondb
docker compose -f docker-compose.sql.yml run --rm migrate-casedb
docker compose -f docker-compose.sql.yml run --rm migrate-seqdb
docker compose -f docker-compose.sql.yml run --rm migrate-omopdb
docker compose -f docker-compose.sql.yml up -d --wait seqdb omopdb casedb
```

Use `docker-compose.sql.idp.yml` for the mock OIDC stack. The API services depend
on their migration job completing successfully. Inspect a failed job with, for
example:

```sh
docker compose -f docker-compose.sql.yml logs migrate-seqdb
```

## SQL Server-specific behavior

- Initial revisions create service schemas explicitly because Alembic creates
  tables but does not automatically create their schemas.
- The version table is stored in the application-owned `alembic` schema.
- `compare_type=True` detects type drift.
- Server-default comparison is disabled because SQL Server reflects expressions
  such as `GETUTCDATE()` differently from the project's SQLAlchemy types. Review
  server defaults manually.
- OMOP migration metadata normalizes primary-key columns to `NOT NULL`, matching
  SQL Server and preventing false nullable-change revisions from legacy model
  annotations.
- Some historical SeqDB unique objects can exist as either constraints or
  indexes. The compatibility revision queries SQL Server's catalog and drops
  the object by its actual type.

## Review checklist

- [ ] All databases containing the model have a revision.
- [ ] `alembic heads` shows one expected head in each affected chain.
- [ ] Upgrade succeeds from the previously deployed revision on SQL Server.
- [ ] Upgrade succeeds on a restored production-like database when the change
      transforms existing data.
- [ ] Downgrade was tested on disposable data or explicitly documented as
      intentionally unsafe.
- [ ] `alembic check` reports no pending model operations after the upgrade.
- [ ] Migration-focused and affected application tests pass.
- [ ] The revision does not log secrets or sensitive row data.
- [ ] Generated history pages are refreshed.
- [ ] Deployment order and backward compatibility with the currently running
      application were considered.
