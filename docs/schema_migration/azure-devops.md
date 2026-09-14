# Azure DevOps migration flow in `lsp-api`

The Azure deployment implementation is owned by the separate `lsp-api`
repository. At the time of this handover, the migration work is on its
`LSP-3503-alembic-dev-migrations` branch; `lsp-api/dev` does not contain the
migration job, runner, or stage wiring. Verify that branch has been reviewed
and merged before relying on the behavior described here.

The pipeline migrates the three API databases deployed by `lsp-api`: `casedb`,
`seqdb`, and `omopdb`. It does not run the standalone `commondb` chain. Shared
CommonDB tables stored in those three databases are already part of their own
service-specific revision chains.

## End-to-end sequence

```text
Azure pipeline selects a gen-epix-api ref
                 │
                 ▼
BUILD checks out lsp-api + gen-epix-api
                 │
                 ├── builds lsp-api:<Build.BuildId>
                 ├── embeds Alembic code and the migration runner
                 ├── publishes the image tar
                 └── publishes migration-manifest.yml
                 │
                 ▼
Migration job publishes/signs the same image in the target ACR
                 │
                 ▼
envsubst renders one short-lived AKS Job for one service
                 │
                 ▼
AKS Job reads its database URL from Azure Key Vault
                 │
                 ▼
python -m alembic -c <service>/repositories/alembic.ini upgrade head
                 │
          success┴failure
             │       │
             ▼       └── pipeline prints Job logs/description and fails
      API deployment may run
```

The migration is a pre-deployment Kubernetes Job, not an API init container or
sidecar. The API image and migration image are the same build, which keeps the
revision files aligned with the application being deployed.

## Entry pipelines and source refs

| Pipeline | Trigger/source | `gen-epix-api` ref | Automatic target |
| --- | --- | --- | --- |
| `cicd/azure-lsp-api-snapshot.yml` | non-`main`, non-`hotfix/*` snapshot flow | `remoteRef`, default `refs/heads/dev` | DEV / `SA_SQL` |
| `cicd/azure-lsp-api-release.yml` | `main` and `hotfix/*` | `main` | ACC / `SA_SQL` |
| `cicd/azure-lsp-api-webhook.yml` | GitHub webhook | forwards the received branch as `remoteRef` to the snapshot pipeline | determined by snapshot pipeline |

For a feature-branch deployment, check the pipeline run's `remoteRef`. A
successful `lsp-api` build against the wrong `gen-epix-api` ref can deploy an
image without the revision you expected.

Both entry pipelines expand `cicd/templates/stages/cicd.yml`. The migration
branch provides two ways to execute migrations:

- Automatic `MIGRATE_CASEDB_AUTO`, `MIGRATE_SEQDB_AUTO`, and
  `MIGRATE_OMOPDB_AUTO` stages run after `BUILD`. Each corresponding automatic
  API deployment depends on its migration stage.
- Manual `MIGRATE_TST`, `MIGRATE_ACC`, and `MIGRATE_PRD` stages run all three
  service migrations without deploying an API. The three jobs in one stage are
  independent and can run in parallel.
- Manual per-service `SA_SQL` deployment stages in
  `cicd/templates/stages/deploy-service.yml` run that service's migration job
  first; the API deployment job has an explicit dependency on it.
- Manual `DICT_DEMO` deployments do not need SQL migrations.

Running `upgrade head` on an already-current database is expected to be a
no-op. This makes a normal pipeline rerun safe as long as the revision itself
is safe and the previous attempt did not leave partially applied manual SQL.

## Build-time pieces

The following `lsp-api` files form the migration path:

| File | Responsibility |
| --- | --- |
| `Dockerfile` | Installs Alembic through the Gen-EpiX requirements, plus `pyodbc`, Azure Identity, and Key Vault clients; copies the migration runner into `/app/cicd/scripts/`. |
| `cicd/templates/jobs/build.yml` | Builds and saves `lsp-api:<Build.BuildId>`, then publishes the image tar and migration manifest as pipeline artifacts. |
| `cicd/azure/migration-manifest.yml` | Defines the hardened, short-lived Kubernetes Job and passes only Key Vault/identity settings to it. |
| `cicd/scripts/run_alembic_migration.py` | Maps a service to its Alembic configuration and Key Vault secret, sets `ALEMBIC_URL` only in the child process environment, and executes `upgrade head`. |
| `cicd/templates/jobs/run-alembic-migration.yml` | Pushes/signs the image, renders the manifest, replaces the previous named Job, waits for completion, and emits diagnostics. |
| `cicd/templates/stages/cicd.yml` | Wires automatic and standalone manual migration stages into the pipeline. |
| `cicd/templates/stages/deploy-service.yml` | Makes each manual `SA_SQL` service deployment wait for its migration job. |
| `cicd/templates/jobs/deploy-app.yml` | Accepts the dependency that gates API deployment on migration success. |

## Identity and secret flow

The rendered Job receives these non-secret settings:

- `AZURE_KEY_VAULT_URL`, selected from the target environment configuration;
- `AZURE_CLIENT_ID`, set to the AKS user-assigned identity client ID; and
- the service name (`casedb`, `seqdb`, or `omopdb`) as the runner argument.

`DefaultAzureCredential` uses the AKS identity setup to access Key Vault. The
runner requests exactly one secret:

| Service | Key Vault secret |
| --- | --- |
| CaseDB | `CASEDB---REPOSITORY--DEFAULTS--PROPS--CONNECTION-STRING` |
| SeqDB | `SEQDB---REPOSITORY--DEFAULTS--PROPS--CONNECTION-STRING` |
| OMOPDB | `OMOPDB---REPOSITORY--DEFAULTS--PROPS--CONNECTION-STRING` |

The secret value is assigned to `ALEMBIC_URL` in the environment of the
Alembic subprocess. The runner announces which service it is migrating but
does not print the URL. Preserve this property when changing diagnostics.

The database identity in each connection string needs permission to create and
alter the service schemas and to create/read/update
`alembic.alembic_version`. The AKS identity separately needs `get` access to the
three Key Vault secrets. A failure in either permission path blocks deployment.

## AKS Job behavior

For each service, the pipeline:

1. creates the namespace if needed;
2. deletes the previous Job with the stable name `alembic-<service>`;
3. renders and applies a Job using the current `Build.BuildId` image;
4. waits up to ten minutes for `condition=complete`;
5. prints the last 200 log lines on success; and
6. prints logs plus `kubectl describe job/...` and fails on error or timeout.

The Job uses `backoffLimit: 0`, so Kubernetes does not retry a failing
migration pod automatically. It runs as UID/GID 1001, drops Linux capabilities,
uses a read-only root filesystem with explicit temporary volumes, and is kept
for up to 24 hours by `ttlSecondsAfterFinished` unless the next run replaces it.

## Deployment guarantees and limits

- A service API deployment is gated on its own migration, not on all service
  migrations. CaseDB can deploy after CaseDB succeeds even if SeqDB fails in a
  separate automatic stage.
- A failed migration prevents the dependent API deployment, but it does not
  roll back database work already committed by the revision.
- The runner supports only `upgrade head`; it deliberately cannot stamp or
  downgrade an existing database.
- The pipeline does not create an Azure SQL database itself. The database,
  identity permissions, Key Vault secret, and AKS identity integration must
  already exist.
- Removing a revision from a newer image does not reverse it in the database.
  Once deployed, use a new corrective revision or an explicitly planned
  downgrade.

See [Operations and troubleshooting](operations.md) before baselining an
existing database or recovering a failed deployment.
