# Migration operations and troubleshooting

This runbook is for first deployment, environment promotion, and recovery. A
schema change can be irreversible even when Alembic supplies a `downgrade()`;
take and verify a database backup before baselining or applying a migration that
rewrites existing data.

## Pre-deployment checks

For every affected service:

1. identify the exact application image and Gen-EpiX commit being promoted;
2. inspect the revision chain and confirm it has one head;
3. read every pending revision between the environment's current revision and
   that head;
4. confirm the application remains compatible while old and new pods overlap;
5. rehearse slow or data-changing migrations against a recent isolated backup;
6. estimate lock duration and choose a maintenance window when required; and
7. confirm a tested backup/restore path and name the person making the go/no-go
   decision.

Useful read-only commands are:

```sh
export SERVICE=seqdb
export ALEMBIC_URL='<SQLAlchemy SQL Server URL>'

alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" current
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" heads
alembic -c "gen_epix/$SERVICE/repositories/alembic.ini" history --verbose
```

You can also inspect the database marker directly:

```sql
SELECT version_num FROM alembic.alembic_version;
```

Do not update that table with ad-hoc SQL. Use Alembic's `stamp` command only
after validating the schema as described below.

## Empty database

An empty database should have no Alembic version row. Run `upgrade head`; the
initial revision creates the service schemas and tables, later revisions run in
order, and Alembic records the resulting head.

For Azure environments, the `lsp-api` migration Job performs this operation.
The database itself and the Key Vault connection-string secret must already
exist. After the pipeline succeeds, compare `current` with the head bundled in
the deployed image and smoke-test the API before loading reference or
operational data.

## Existing database without Alembic history

Never run an initial revision blindly against a populated legacy database. It
will attempt to create objects that already exist. `stamp` is the adoption tool,
but it records a revision without running DDL or proving that the schema matches
that revision.

The initial revisions that captured the pre-Alembic schemas are:

| Database | Initial baseline |
| --- | --- |
| CommonDB | `b9c5e10bf42c` |
| CaseDB | `bbc386e12a58` |
| SeqDB | `973d81851aeb` |
| OMOPDB | `252f23d99c89` |

Use the following adoption procedure separately for each database:

1. stop writers and take a verified backup;
2. compare tables, columns, nullability, defaults, indexes, foreign keys, and
   constraints with the selected baseline revision;
3. resolve any drift deliberately—do not assume a similarly named schema is
   equivalent;
4. stamp the matching revision from a secured operator environment; and
5. run `upgrade head`, verify the new marker, and test the application.

If the legacy database matches the captured initial schemas exactly, the
commands are:

```sh
ALEMBIC_URL='<CommonDB URL>' \
  alembic -c gen_epix/commondb/repositories/alembic.ini stamp b9c5e10bf42c
ALEMBIC_URL='<CaseDB URL>' \
  alembic -c gen_epix/casedb/repositories/alembic.ini stamp bbc386e12a58
ALEMBIC_URL='<SeqDB URL>' \
  alembic -c gen_epix/seqdb/repositories/alembic.ini stamp 973d81851aeb
ALEMBIC_URL='<OMOPDB URL>' \
  alembic -c gen_epix/omopdb/repositories/alembic.ini stamp 252f23d99c89
```

Then run `upgrade head` for **all** deployed service databases. This matters
because CaseDB, SeqDB, and OMOPDB now have post-baseline revisions. Do not copy
these stamp commands to a database that was changed manually after the initial
snapshot; determine and verify the revision it actually matches.

The Azure migration runner intentionally cannot stamp. Baselining is a
one-time, supervised operation and must not be hidden in a repeatable deployment
pipeline.

## Promotion rules

- Promote the same reviewed revision files with the application code that uses
  them.
- Prefer expand-and-contract changes: add compatible schema first, deploy code
  that tolerates both forms, migrate/backfill data, then remove the old schema
  in a later release.
- Never remove or rewrite a revision that has reached a shared environment.
- Serialize deployments that target the same environment and service. The
  `lsp-api` Job name is stable (`alembic-<service>`), and a concurrent pipeline
  can delete or replace another run's Job.
- Do not run Alembic manually while the pipeline migration for the same database
  is active.
- Treat a pipeline rerun as safe only after establishing what the failed run
  committed. Alembic does not automatically execute `downgrade()` on failure.

## Failure triage

Start with the failed migration stage, service, environment, image build ID,
and revision. Preserve the pipeline logs before rerunning because the next run
deletes the stable Kubernetes Job.

| Symptom | Likely cause | First checks/action |
| --- | --- | --- |
| Key Vault authentication error | AKS identity integration, client ID, or vault access is wrong | Check `AZURE_CLIENT_ID`, vault URL, identity assignment, and secret `get` permission. |
| Secret not found/empty | Service-to-secret mapping or environment vault is wrong | Check the exact secret name from the Azure pipeline guide; never print its value. |
| SQL login/network error | Bad connection string, firewall/DNS, driver, or database identity | Test connectivity from the same AKS/network context and verify ODBC Driver 18 settings. |
| `object already exists` on the initial revision | Populated database was never baselined, or points to the wrong database | Stop; inspect the target and follow the stamping procedure. Do not mark the pipeline green manually. |
| `Can't locate revision` | Database marker is newer than, or absent from, the image's revision chain | Compare build/source refs and history. Deploy an image containing the revision; do not edit the marker directly. |
| Multiple heads | Concurrent branches added revisions from the same parent | Coordinate ordering or create a reviewed merge revision before deployment. |
| Constraint/index error | Production shape or data differs from the tested schema | Inspect catalog objects and violating rows on an isolated copy; make the revision handle the known shape. |
| `alembic check` reports operations after upgrade | Metadata and revision are out of sync, or comparison normalization is missing | Review generated diff; add the missing operation or a narrowly justified metadata normalization. |
| Ten-minute timeout | Long DDL/data update, blocking transaction, or AKS command problem | Inspect Job/pod state and SQL blocking before retrying; split or redesign work that cannot fit the window. |
| API deployment skipped | Its prerequisite migration job/stage failed | Fix or safely correct the migration, rerun it, and let the dependency gate deploy the API. |

In the `lsp-api` job, failure handling already requests the last 200 pod log
lines and `kubectl describe job/...`. If more investigation is needed before
the next pipeline replaces the Job, operators with cluster access can use:

```sh
kubectl get job,pod -n lsp-seqdb -l job-name=alembic-seqdb
kubectl logs -n lsp-seqdb -l job-name=alembic-seqdb \
  --all-containers=true --prefix=true
kubectl describe job/alembic-seqdb -n lsp-seqdb
```

Use the matching namespace and service name for CaseDB or OMOPDB.

## Recovery choices

Prefer a forward corrective revision after a migration has been deployed. A
downgrade is appropriate only when its SQL and data-loss implications were
reviewed and tested for the exact database state.

1. Stop the deployment and application writers if continued writes increase
   damage or make recovery ambiguous.
2. Determine the live schema and `alembic.alembic_version`; do not infer either
   only from the pipeline result.
3. Decide among a safe rerun, a forward corrective revision, a tested
   downgrade, or restoring the backup.
4. Rehearse the chosen recovery on a copy when time and incident severity allow.
5. Apply one controlled recovery path, verify schema and data invariants, then
   re-enable deployment/writers.
6. Record the environment, image, revisions, commands, timestamps, and outcome
   in the incident or release notes without including secrets.

## Handover status in `lsp-api`

Before enabling migrations in the deployment pipeline, successors should close
these items:

- The implementation is on `LSP-3503-alembic-dev-migrations`, not
  `lsp-api/dev`; rebase or merge it deliberately and validate the compiled
  Azure YAML.
- The branch contains other deployment, reference-data, and seed-user work.
  Separate or review that scope rather than assuming every branch change is
  required for Alembic.
- Confirm the snapshot and release pipelines fetch the intended
  `gen-epix-api` ref and that the built image contains the expected heads.
- Exercise empty-database creation and legacy-database stamping in DEV before
  the first environment promotion.
- Verify AKS identity access to Key Vault and database DDL permissions for each
  environment without logging connection strings.
- Prove the migration-to-deployment dependency for both automatic and manual
  `SA_SQL` paths, including a deliberately failing revision in a disposable
  environment.
- Decide whether the standalone all-service manual migration stages should
  remain in addition to migration-before-service-deploy stages; document the
  operator-facing choice in Azure DevOps.
- Add serialization or an operational lock so two pipeline runs cannot replace
  the same `alembic-<service>` Job.
- Confirm whether a separately deployed CommonDB will ever be part of LSP. If
  so, extend the runner, Key Vault mapping, manifest invocation, and stages; do
  not assume the existing three-service pipeline covers it.
- Validate the build agent's Azure CLI behavior. The branch history contains a
  reverted workaround for `az aks command invoke`; reproduce the final form on
  the agent version that will run production migrations.

## Post-deployment evidence

Keep the following with the release record:

- Gen-EpiX commit and container build ID;
- previous and resulting Alembic revision for each database;
- migration stage/Job result and duration;
- backup identifier for data-changing releases;
- smoke-test outcome; and
- any approved drift, manual intervention, or deferred cleanup.
