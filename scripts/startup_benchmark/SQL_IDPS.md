# Casedb startup benchmark with SQL Server and IDPS

The benchmark cannot attach to an existing Compose API. `runner.launch_command`
starts `python run.py api casedb IDPS SA_SQL --noreload` for every attempt,
checks that port 8000 is free, verifies an instance-specific response header on
`/v1/health`, then terminates its child process group. There is no external URL
or Docker-launch option. The benchmark itself could run inside a Linux container
and launch its own child there, but that measures that container environment;
it still cannot measure an independently running Compose API.

The database-only approach below uses the existing Compose jobs. It deliberately
uses casedb's default **LOCAL** seqdb collaborator: an embedded seqdb application,
not a separate HTTP server. Consequently both casedb and seqdb need migrations
and SQL configuration. This measures casedb **including embedded seqdb startup**.
For production's REMOTE topology, an independently provisioned reachable seqdb
API and its OAuth client configuration would also be required. Selecting NONE
would change the measured workload and is not used here.

## Prerequisites and configuration

Run all commands in the **same Bash session in Linux/WSL**, from this checkout:

```bash
cd /home/streevdm/gen-epix/gen-epix-api
source .venv/bin/activate
set -euo pipefail
set +x
umask 077
python --version
python -m scripts.startup_benchmark benchmark --help
docker compose version
docker info >/dev/null 2>&1 || { echo 'Start Docker and enable access from this WSL distribution.'; exit 1; }
python - <<'PY'
import sys
import pyodbc
assert sys.platform.startswith('linux') and sys.version_info >= (3, 14)
assert 'ODBC Driver 18 for SQL Server' in pyodbc.drivers()
print('Linux, Python and ODBC prerequisites OK')
PY
```

If the environment is missing, install Python 3.14+, create `.venv`, and install
`requirements.txt` and `dev-requirements.txt` per the repository development guide.
The host also needs unixODBC, Microsoft's ODBC Driver 18, and `pyodbc` (the Docker
image installs these separately; installing a Python package alone is insufficient).
Docker must be able to pull the pinned SQL image and build `Dockerfile.dev`.

IDPS reads `config/identity_providers.toml`. As inspected, this includes
`rivm_signicat` at
`https://pre-login.rivm.nl/broker/sp/oidc/.well-known/openid-configuration`
and `mock` at `https://127.0.0.1:5443/.well-known/openid-configuration`.
Neither is supplied by `docker-compose.sql.yml`. Supply the intended reachable
OIDC providers before proceeding; do not silently benchmark with a failed provider.
The separate `docker-compose.sql.idp.yml` uses MOCK and an HTTP provider on 8080;
it is not a drop-in implementation of this IDPS configuration.

You may maintain the existing TOML locally, or supply a private JSON file containing
the complete `idps_cfg` list (same keys as the TOML: name, label, protocol,
discovery_url, client_id, client_secret, scope, claim_map, and applicable options).
To replace the list for both apps without editing tracked configuration:

```bash
# Optional: use this only if replacing the checked-in provider list.
read -r -p 'Absolute path to your private IDP JSON list: ' benchmark_idp_file
export CASEDB_SERVICE__AUTH__PROPS__IDPS_CFG="@json $(python -c 'import json,sys; print(json.dumps(json.load(open(sys.argv[1]))))' "$benchmark_idp_file")"
export SEQDB_SERVICE__AUTH__PROPS__IDPS_CFG="$CASEDB_SERVICE__AUTH__PROPS__IDPS_CFG"
unset benchmark_idp_file
```

Use actual registered client settings; this guide supplies no secrets. Keep shell
tracing disabled. Discovery/JWKS checks below establish startup connectivity, not
a successful user login or token grant. The health probe does not require a token.

## Start only the database and migration jobs

```bash
compose=(sudo docker compose -f docker-compose.sql.yml)
"${compose[@]}" config --services
"${compose[@]}" build migrate-casedb migrate-seqdb
"${compose[@]}" up -d --no-deps --wait --wait-timeout 180 lsp_sql
"${compose[@]}" run --rm --no-deps -T init-db >/dev/null 2>&1
"${compose[@]}" run --rm --no-deps -T migrate-casedb >/dev/null 2>&1
"${compose[@]}" run --rm --no-deps -T migrate-seqdb >/dev/null 2>&1
echo 'Initialization and migration jobs exited successfully.'
```

The sequence is intentional: SQL health first, then synchronous one-shot jobs;
`set -e` stops on a nonzero exit. `--no-deps` prevents implicit service startup.
Only `lsp_sql`, `init-db`, `migrate-casedb`, and `migrate-seqdb` are invoked.
Initialization also creates the empty commondb and omopdb databases because the
existing job does so; their migrations are unnecessary for this topology.
The shared commondb models are included in each application's own migration tree.
No application service is requested, even if the commented API services are later
restored. Existing containers are not stopped by these commands.

Job output is suppressed to avoid accidentally displaying connection details on
failure. A failure stops this session; investigate privately before rerunning.
The existing init job does not use sqlcmd's `-b` option, so its exit code alone
is insufficient evidence of SQL statement success. The authenticated database
and Alembic-head checks below are therefore required.

Do not use `scripts/start-sql-stack.sh`: it explicitly starts APIs after running
all migrations. Do not run a bare `compose up` for this workflow.

## Configure and verify connections from the benchmark environment

The Compose database publishes **127.0.0.1:1433**. `lsp_sql` is a Compose-network
DNS name and is not the host connection address. Enter the local SQL login and
password configured in your existing Compose stack (or existing volume).
The checked-in Compose stack contains development credentials; they are not
repeated here. An existing volume may retain an older password; editing the
Compose environment does not reset it. Do not delete the volume to fix login.

```bash
read -r -p 'SQL login configured for this local stack: ' benchmark_sql_user
read -r -s -p 'SQL password: ' benchmark_sql_password; printf '\n'
for prefix in CASEDB SEQDB; do
    export "${prefix}_REPOSITORY__DEFAULTS__PROPS__SERVER=127.0.0.1,1433"
    export "${prefix}_REPOSITORY__DEFAULTS__PROPS__UID=@str $benchmark_sql_user"
    export "${prefix}_REPOSITORY__DEFAULTS__PROPS__PWD=@str $benchmark_sql_password"
    export "${prefix}_REPOSITORY__DEFAULTS__PROPS__DRIVER=ODBC Driver 18 for SQL Server"
    export "${prefix}_REPOSITORY__DEFAULTS__PROPS__OTHER=;TrustServerCertificate=yes"
    export "${prefix}_APP__DEBUG=false"
done
unset benchmark_sql_user benchmark_sql_password
export CASEDB_REPOSITORY__DEFAULTS__PROPS__DATABASE=casedb
export SEQDB_REPOSITORY__DEFAULTS__PROPS__DATABASE=seqdb
export CASEDB_SERVICE__SEQDB__PROPS__SEQDB_CLIENT_TYPE=LOCAL

python - <<'PY'
import sys
import httpx
import sqlalchemy as sa
from alembic.config import Config
from alembic.script import ScriptDirectory
from gen_epix.commondb.domain.util import set_env_variables, get_app_cfg_class
from scripts.startup_benchmark.runner import port_available

stage = 'configuration'
try:
    set_env_variables('casedb', 'IDPS', 'SA_SQL')
    assert port_available(8000), 'Port occupied'
    for app in ('casedb', 'seqdb'):
        stage = f'{app} configuration'
        cfg = get_app_cfg_class(app)(log_setup=False, log_any=False).cfg
        assert not cfg['app']['debug']
        if app == 'casedb':
            assert cfg['service']['seqdb']['props']['seqdb_client_type'] == 'LOCAL'
        heads = set(ScriptDirectory.from_config(Config(
            f'gen_epix/{app}/repositories/alembic.ini')).get_heads())
        checked = set()
        for name, repo in cfg['repository'].items():
            if name == 'defaults':
                continue
            stage = f'{app} repository {name}'
            assert str(repo['type']).split('.')[-1] == 'SA_SQL'
            url = repo['props']['connection_string']
            parsed = sa.engine.make_url(url)
            assert parsed.drivername == 'mssql+pyodbc'
            assert 'SERVER=127.0.0.1,1433;' in parsed.query['odbc_connect']
            if url in checked:
                continue
            checked.add(url)
            engine = sa.create_engine(url, connect_args={'timeout': 10})
            try:
                with engine.connect() as connection:
                    assert connection.scalar(sa.text('SELECT DB_NAME()')) == app
                    actual = set(connection.execute(sa.text(
                        'SELECT version_num FROM alembic.alembic_version')).scalars())
                    assert actual == heads, 'Migration heads differ'
            finally:
                engine.dispose()
        assert checked
        providers = cfg['service']['auth']['props']['idps_cfg']
        assert 1 <= len(providers) <= 5
        for index, provider in enumerate(providers):
            stage = f'{app} IDP {index + 1} discovery/JWKS'
            assert provider['protocol'] == 'OIDC'
            with httpx.Client(verify=provider.get('ssl_context', True), timeout=15) as client:
                response = client.get(provider['discovery_url'])
                response.raise_for_status()
                doc = response.json()
                assert doc['issuer'] and doc['authorization_endpoint'] and doc['token_endpoint']
                response = client.get(doc['jwks_uri'])
                response.raise_for_status()
                assert response.json()['keys']
        print(f'{app}: SQL connection, migration heads and IDP endpoints verified')
except Exception:
    # Do not print exceptions: DB errors can include connection credentials.
    print(f'Preflight failed at {stage}; inspect configuration privately.', file=sys.stderr)
    sys.exit(1)
PY
```

This loads the same configuration utility as the launcher, including optional
`gen_epix/{casedb,seqdb}/config/secrets.repository.sa_sql.toml` files. Review any
per-repository overrides in those files: they can override defaults. Do not set
`CASEDB_SETTINGS_FILES` to inject another file: the launcher overwrites that list.
The checks inspect every effective repository connection, rather than assuming
the default connection is used everywhere.

If localhost is not reachable from WSL, fix Docker's WSL integration/networking
first. A Windows-host IP is not automatically reachable for a port published only
on Windows loopback. The checks must pass in the same Linux environment as the
benchmark; Windows-only connectivity does not prove this.

## Run and verify

```bash
mkdir -p test/output
benchmark_output="$(mktemp -d "$PWD/test/output/startup-sql-idps-XXXXXXXX")"
tls_args=()
if [[ -f cert/key.pem && -f cert/cert.pem ]]; then
    read -r -p 'CA PEM path that validates the API certificate for 127.0.0.1: ' benchmark_ca
    tls_args=(--ca-file "$benchmark_ca")
fi
python -m scripts.startup_benchmark benchmark casedb \
    --idp-mode IDPS --repository-mode SA_SQL \
    --runs 30 --warmups 2 --readiness-timeout 180 \
    --output "$benchmark_output" "${tls_args[@]}"
python - "$benchmark_output/results.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
assert data['series_exit_code'] == 0
assert data['configuration_valid'] and data['series_completed']
assert len(data['records']) == 32
assert all(r['status'] == 'success' and r['cleanup'] == 'ok' for r in data['records'])
print('All warmup and measured runs succeeded; child processes cleaned up.')
PY
python -m scripts.startup_benchmark report \
    --input "$benchmark_output/results.json" --output "$benchmark_output/report.html"
printf 'Results directory: %s\n' "$benchmark_output"
```

Create `test/output` first if it does not exist (`mkdir -p test/output`). For an
initial smoke run use `--runs 1 --warmups 0` and change the record count assertion
to 1; choose a new output directory for the full series. With neither certificate
file present, the launcher uses HTTP. A partial certificate pair is rejected.
For local self-signed API certificates, `--insecure` is also supported instead of
`--ca-file`; it affects the benchmark's health probe, not IDP HTTPS verification.

The output contains `results.json`, `report.md`, configuration snapshots and logs,
and per-attempt stdout/stderr logs; the final command creates `report.html`.
Without `--output`, the default is
`test/output/startup_benchmark/casedb-<UTC timestamp>-<random suffix>/`.
Metadata/snapshots redact credentials, but raw application logs are not universally
redacted: keep artifacts private and review them before sharing. No commands here
print configuration, passwords, or raw logs.

Exit zero means successful execution, not that a performance target was met;
`--check-target` enables the benchmark's optional target gate. Results are fresh
process startup measurements with ordinary filesystem/SQL/IDP caches, not cold
database boots. Migrations/builds and preflight checks are outside the timing.
Repeated startup may initialize application data; use a local test database.
Health readiness does not prove login, authorization, or all API operations work.

## Cleanup without deleting data

The benchmark cleans up each API process. The `run --rm` jobs remove their own
temporary containers. When no other process needs this SQL instance:

```bash
docker compose -f docker-compose.sql.yml stop lsp_sql
for prefix in CASEDB SEQDB; do
    unset "${prefix}_REPOSITORY__DEFAULTS__PROPS__UID"
    unset "${prefix}_REPOSITORY__DEFAULTS__PROPS__PWD"
    unset "${prefix}_SERVICE__AUTH__PROPS__IDPS_CFG"
done
```

This leaves the named SQL volume and benchmark results intact. Close the dedicated
shell to discard the remaining overrides. Do not use `down -v`, volume prune,
or the Makefile teardown target. To resume, repeat the startup and preflight steps.

## Evidence and limitations

- `runner.py`: local child launch, fixed port, nonce, health probe, cleanup.
- `__main__.py`: Linux/Python requirement, exact CLI and result handling.
- `gen_epix/commondb/domain/util.py`: IDPS/settings-file selection and recursive
  seqdb setup for casedb.
- `gen_epix/{commondb,casedb,seqdb}/config/cfg.py`: SQL defaults and LOCAL seqdb.
- `gen_epix/fastapp/services/auth/service.py`: failed IDPs are queued for retry;
  readiness alone is not an IDP validation.
- `docker-compose.sql.yml`: database health, initialization, independent migrations.

Docs say SQL Server 2022 and API startup in the Compose header; code shows a pinned
SQL Server **2025** image and all API services commented out in this checkout.
The stack helper's help text also promises APIs and its code still requests those
now-commented services. Those comments/helper should be reconciled separately;
this guide preserves existing local edits. This is production-like SQL/Alembic
behavior, not a reproduction of production's authentication, permissions, data,
remote-service topology, or resource limits.

Validation on 2026-10-14: all Bash blocks passed `bash -n`; embedded Python
snippets compiled; the real benchmark CLI help ran under WSL Python 3.14.3.
Both apps' resolved repository configurations supported the preflight traversal.
ODBC Driver 18 was installed and Compose rendered the six expected SQL/job
services. The external configured IDP's discovery and JWKS were reachable.
Docker's daemon was unreachable; localhost ports 1433 and 5443 were unavailable
and 8000 was free. The local mock IDP discovery failed with ConnectError.
No image build, container startup, initialization, migration, authenticated SQL
connection, or full benchmark was executed. Start Docker and provision or replace
the unavailable mock IDP before running this guide.
