# App Lifecycle & Boot Docs

> 6 nodes · cohesion 0.33

## Key Concepts

- **Startup Lifecycle (run.py -> AppCfg -> AppComposer -> create_fast_api)** (3 connections) — `docs/05-Configuration-and-Runtime.md`
- **Boot Sequence (AppCfg -> AppComposer -> create_fast_api)** (2 connections) — `docs/02-Architecture.md`
- **Container Model (Dockerfile, gunicorn --preload)** (2 connections) — `docs/07-CI-CD-and-Release.md`
- **Load and Overwrite Precedence (env var > Dynaconf > YAML pinned)** (2 connections) — `docs/10-Logging.md`
- **Request Lifecycle (endpoint -> app.handle -> policies -> handler)** (1 connections) — `docs/02-Architecture.md`
- **Logger Namespaces and Default Levels** (1 connections) — `docs/10-Logging.md`

## Relationships

- [Documentation Index](Documentation_Index.md) (1 shared connections)

## Source Files

- `docs/02-Architecture.md`
- `docs/05-Configuration-and-Runtime.md`
- `docs/07-CI-CD-and-Release.md`
- `docs/10-Logging.md`

## Audit Trail

- EXTRACTED: 4 (67%)
- INFERRED: 2 (33%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*