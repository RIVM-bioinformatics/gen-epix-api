# App Configuration & Startup

> 11 nodes · cohesion 0.25

## Key Concepts

- **Runtime dependencies (requirements.txt)** (8 connections) — `requirements.txt`
- **run.py CLI entrypoint** (6 connections) — `AGENTS.md`
- **Dynaconf-based configuration** (3 connections) — `AGENTS.md`
- **Local Development Model** (3 connections) — `docs/06-Development-Guide.md`
- **Staged startup troubleshooting** (3 connections) — `docs/06-Development-Guide.md`
- **SQLAlchemy** (3 connections) — `requirements.txt`
- **uvicorn** (3 connections) — `requirements.txt`
- **IDP modes (IDPS, MOCK, NONE)** (2 connections) — `AGENTS.md`
- **Repository mode parity (DICT, SA_SQLITE, SA_SQL)** (2 connections) — `AGENTS.md`
- **Alembic** (2 connections) — `requirements.txt`
- **Dynaconf** (2 connections) — `requirements.txt`

## Relationships

- [Agent Conventions & Guides](Agent_Conventions_&_Guides.md) (5 shared connections)
- [Identity Provider Authentication](Identity_Provider_Authentication.md) (1 shared connections)
- [Service & Docs Overview](Service_&_Docs_Overview.md) (1 shared connections)
- [OAuth Provider Test Harness](OAuth_Provider_Test_Harness.md) (1 shared connections)
- [Domain Package Layout](Domain_Package_Layout.md) (1 shared connections)

## Source Files

- `AGENTS.md`
- `docs/06-Development-Guide.md`
- `requirements.txt`

## Audit Trail

- EXTRACTED: 19 (83%)
- INFERRED: 4 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*