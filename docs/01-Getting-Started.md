Creation Date: March 1, 2026

# Getting Started

## Prerequisites

- **Python ≥ 3.14.1** (Source: `pyproject.toml#L17-L24`; Source: `.github/workflows/main.yml#L30-L33`).
- **Preferred environment manager: `uv`**. For new contributors, use the
  dedicated guide: [01a-UV-Getting-Started](./01a-UV-Getting-Started.md).
- **ODBC driver** — CI installs `unixodbc-dev` and builds `pyodbc` from source. On Windows, install the Microsoft ODBC Driver for SQL Server. (Source: `.github/workflows/main.yml#L34-L37`)
- **Dependencies**:
  ```
  pip install -r requirements.txt
  pip install -r dev-requirements.txt
  ```
  Runtime and development dependencies are split between these two files. (Source: `requirements.txt#L3-L35`; Source: `dev-requirements.txt#L6-L16`)

---

## Quickstart

### Start a single service

```
python run.py api <app_type> <idp_mode> <repo_mode>
```

| Argument | Choices | Description |
|----------|---------|-------------|
| `app_type` | `commondb`, `casedb`, `seqdb`, `omopdb` | Which app variant to boot |
| `idp_mode` | `idps`, `mock`, `none` | Identity provider configuration |
| `repo_mode` | `dict_demo`, `dict_empty`, `sa_sqlite_demo`, `sa_sqlite_empty`, `sa_sql` | Repository backend |

(Source: `run.py#L82-L107`; Source: `gen_epix/commondb/domain/enum.py#L82-L113`)

**Recommended first run** — start COMMONDB with mock auth and in-memory demo data:

```
python run.py api commondb mock dict_demo
```

### Default ports

| App | Port | Swagger | ReDoc |
|-----|------|---------|-------|
| COMMONDB | 8010 | `https://127.0.0.1:8010/docs` | `https://127.0.0.1:8010/redoc` |
| CASEDB | 8000 | `https://127.0.0.1:8000/docs` | `https://127.0.0.1:8000/redoc` |
| SEQDB | 8001 | `https://127.0.0.1:8001/docs` | `https://127.0.0.1:8001/redoc` |
| OMOPDB | 8002 | `https://127.0.0.1:8002/docs` | `https://127.0.0.1:8002/redoc` |

All API routes are prefixed with `/v1`. (Source: `run.py#L17-L38`)

### Self-signed certificates

`cert/` ships in the repo, so the app serves over HTTPS. Browsers show an "untrusted certificate" warning — click through to proceed. With curl, pass `-k`. (Source: `run.py#L40-L41`)

---

## Verify Health

After starting a service, call the health endpoint:

```
curl -k https://127.0.0.1:<port>/v1/health
```

Expected response: `HEALTHY`. (Source: `gen_epix/commondb/api/system.py#L60-L73`; Source: `gen_epix/commondb/app_setup.py#L119-L120`)

---

## Run Tests

```
python run.py test_all
```

This runs the curated test suite and writes coverage reports to `test/output/`. (Source: `run.py#L163-L200`; Source: `.github/workflows/main.yml#L167-L170`)

For more test commands and options, see [06-Development-Guide](./06-Development-Guide.md) and [06a-CLI-Reference](./06a-CLI-Reference.md).

---

## Verify Logs

Application logs go to stdout in JSON format. Logger namespaces include `setup`, `app`, `service`, `api`, and `external`. (Source: `gen_epix/commondb/config/logging.yaml#L7-L32`)

---

## Next Steps

- Understand the architecture: [02-Architecture](./02-Architecture.md)
- Learn about configuration and modes: [05-Configuration-and-Runtime](./05-Configuration-and-Runtime.md)
- Set up your development workflow: [06-Development-Guide](./06-Development-Guide.md)
