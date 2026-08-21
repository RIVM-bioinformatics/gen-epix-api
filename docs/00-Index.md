Creation Date: March 1, 2026

# Gen-EpiX Contributor Documentation

Gen-EpiX is the backend of a genomic epidemiology platform. It includes four FastAPI app variants (`CASEDB`, `SEQDB`, `OMOPDB`, `COMMONDB`) that share a common composition model, command-centric execution, and policy-based authorization. (Source: `README.md#L7-L14`; Source: `run.py#L17-L38`)

---

## Table of Contents

| # | Chapter | Description |
|---|---------|-------------|
| 01 | [Getting Started](./01-Getting-Started.md) | Prerequisites, quickstart, first API call, health check |
| 02 | [Architecture](./02-Architecture.md) | Principles, system composition, app variants, layering, command model |
| 02a | [Fastapp Framework](./02a-Fastapp-Framework.md) | Full framework internals reference (domain, model, app, services, repositories) |
| 03 | [Security](./03-Security.md) | Authentication pipeline, authorization model, trust boundaries, risk modes |
| 04 | [API Surface](./04-API-Surface.md) | Endpoint families, contracts, CRUD generation, OpenAPI |
| 05 | [Configuration & Runtime](./05-Configuration-and-Runtime.md) | Settings model, Dynaconf, IDP/repo modes, startup lifecycle, logging |
| 06 | [Development Guide](./06-Development-Guide.md) | Local development, testing workflows, linting, docstring convention |
| 06s | [Python Docstring Standard](./standards/google-python-style-guide-3.8-comments-and-docstrings.md) | Canonical Google-style Python docstring guidance |
| 06a | [CLI Reference](./06a-CLI-Reference.md) | `run.py` full subcommand catalog and design notes |
| 06b | [Mutation Testing](./06b-Mutation-Testing.md) | `pytest-gremlins` guide including WSL setup |
| 07 | [CI/CD & Release](./07-CI-CD-and-Release.md) | CI pipeline, quality gates, release-please, containers |
| 08 | [Extending the System](./08-Extending-the-System.md) | Adding modules, commands, RBAC rules, endpoints, IDP config |
| 08a | [App Composition Walkthrough](./08a-App-Composition-Walkthrough.md) | Full COMMONDB assembly trace (top-down) |
| 09 | [Constraints & Open Questions](./09-Constraints-and-Open-Questions.md) | All hard limits and consolidated `<TBF elsewhere>` items |
| 10 | [Logging](./10-Logging.md) | Logging architecture, JSON formatter behavior, runtime level precedence, overwrite/debug modes |

---

## Recommended Reading Order

1. **[Getting Started](./01-Getting-Started.md)** — Run the system locally and verify health/logging.
2. **[Architecture](./02-Architecture.md)** — Understand boundaries and invariants before changing code.
3. **[Security](./03-Security.md)** — Trust boundaries and policy enforcement points.
4. **[API Surface](./04-API-Surface.md)** — Map the exposed contract to architecture and security.
5. **[Configuration & Runtime](./05-Configuration-and-Runtime.md)** — Settings model, modes, startup lifecycle.
6. **[Logging](./10-Logging.md)** — Logging setup, JSON structure, and load/overwrite behavior.
7. **[Development Guide](./06-Development-Guide.md)** — Local workflows, testing, linting.
8. **[CI/CD & Release](./07-CI-CD-and-Release.md)** — Align with CI gates before opening a PR.
9. **[Extending the System](./08-Extending-the-System.md)** — Use before adding modules, commands, RBAC rules, routers, or IDP config.
10. **[Constraints & Open Questions](./09-Constraints-and-Open-Questions.md)** — Review hard limits and known documentation gaps.

For framework internals, read [02a-Fastapp-Framework](./02a-Fastapp-Framework.md) after chapter 02.
For a full app assembly walkthrough, read [08a-App-Composition-Walkthrough](./08a-App-Composition-Walkthrough.md) after chapter 08.

---

## Documentation Policy

- **Evidenced in repository**: directly supported by source code, config, or workflow files.
- **Inferred from code structure**: conservative interpretation of repeated implementation patterns.
- If evidence is missing, the docs use `<TBF elsewhere>`.
- Each document starts with a creation date. Prefer newer docs but always verify against code.
- `(Source: file#lines)` citations trace claims to primary evidence.
