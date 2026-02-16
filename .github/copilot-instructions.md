# Gen-EpiX — Copilot Chat Instructions

Gen-EpiX is a **multi-service genomic epidemiology platform** with strict access controls and a consistent architectural style. These instructions tell Copilot Chat how to reason about the repo, where to look first, and what patterns to follow.

---

## 0) Evidence & Freshness Rules (read this first)

1. **Docs guide, code decides**
   - Use docs to navigate and understand intent.
   - If docs conflict with implementation, **trust the code/config** and call out the mismatch:  
     *“Docs say X, code shows Y.”* Then recommend whether docs should be updated.

2. **Docs freshness**
   - Each documentation file begins with a **creation date on the first line**. Treat this as a **freshness hint**, not a guarantee.
   - Prefer newer docs when they disagree, and verify important behavior in code.

3. **No guessing**
   - Don’t invent endpoints, ports, config keys, roles, or domain responsibilities.
   - When unsure, **search the workspace** and cite evidence: **file paths + symbols** (and line ranges if possible).

4. **Preferred answer format**
   When asked to implement or change something, respond as:
   1) **What I consulted** (docs + key code paths)
   2) **Plan**
   3) **Patch** (minimal diff-style snippet + where it goes) — only if requested or clearly needed
   4) **Risks / assumptions**

---

## 1) Where to start in docs

Always begin with the system index and follow links to deep dives:

- `0_System-Documentation-Index.md` (entrypoint / map of the system)
- Use deep dives only as needed, and always keep the creation date in mind.

---

## 2) Architecture Overview

### Service domains
Gen-EpiX is organized around **four service domains**:

- `casedb`
- `seqdb`
- `omopdb`
- `commondb`

Typically:
- `casedb`, `seqdb`, and `omopdb` run as independent FastAPI services on different ports with their own database/auth/domain logic.
- `commondb` contains shared models and cross-cutting components used across services (not usually run as a standalone API unless explicitly configured in this repo).

### Hexagonal architecture (strict layering)
Each service follows a consistent structure:

- `domain/` — pure business logic (models, commands, policies)
- `services/` — application layer (orchestration, CRUD operations)
- `repositories/` — data access (SQLAlchemy or in-memory dict)
- `api/` — FastAPI endpoints and HTTP concerns

**Rule of thumb:** API should be thin; business rules live in domain/policies; data access stays in repositories.

### Command–Query pattern (central mediator)
Operations flow through `Command` objects handled by the central `App` mediator. This ensures policies/auth/logging are consistently applied.

**Default rule:** For normal application flows, trigger operations via:

- `result = app.handle(SomeCommand(...))`

**Exceptions (allowed but must be justified):**
- tests
- ETL/CLI scripts
- bootstrapping / migrations / one-off admin routines

If bypassing commands, keep it localized and explain why.

---

## 3) Key Patterns to Follow

### 3.1 Unit of Work for transactions
Use Unit of Work boundaries for DB transactions.

```python
with self.repository.uow() as uow:
    result = self.repository.crud(
        uow, user_id, Model, obj, None, CrudOperation.CREATE_ONE
    )
```

### 3.2 Command-driven operations
Commands are the preferred way to trigger domain operations so policies/auth/logging apply.

```python
from gen_epix.casedb.domain.command import CreateCaseCommand

cmd = CreateCaseCommand(user=user, case_data=data)
result = app.handle(cmd)
```

### 3.3 Authorization model: RBAC + ABAC
- **RBAC roles** (examples): `ROOT`, `APP_ADMIN`, `ORG_ADMIN`, `ORG_USER`, `GUEST`
- **ABAC policies** live in `policies/` directories
- Policies are applied during command execution via a `PolicyDecisionPoint`-style mechanism

**Instruction:** When changing or adding behavior, always consider:
- required role(s)
- required attributes / policy checks
- how user context is passed into commands

### 3.4 Multi-repository support (SQLAlchemy + in-memory)
Services support both SQLAlchemy and in-memory dict repositories:

```python
enum.RepositoryType.SA_SQL  # SQLAlchemy + real database
enum.RepositoryType.DICT    # In-memory for testing
```

**Instruction:** When writing code, keep repository implementations consistent (same domain behavior; different persistence).

---

## 4) Project Conventions

### File organization
- Domain logic: `gen_epix/{service}/domain/`
- Service implementations: `gen_epix/{service}/services/`
- Repository models: `gen_epix/{service}/repositories/sa_model/`
- API endpoints: `gen_epix/{service}/api/`

### Configuration system (Dynaconf-based)
- Settings: `gen_epix/{service}/config/settings.toml`
- Secrets: `gen_epix/{service}/config/.secrets.{component}.toml`
- Auth configs: `gen_epix/{service}/config/idp/`
- Repository configs: service-specific TOML files (connection strings, file paths, etc.)
- Environment variables: auto-discovery via `set_env_variables()`

Example structure:

```toml
[service.auth.props.root.organization]
id = "018d074d-ea0c-e942-07db-a3cc0ba1d653"
name = "DUMMY"
legal_entity_code = "DUMMY"

[service.auth.props.root.user]
key = "root@dummy.org"
email = "root@dummy.org"

[repository.defaults]
type = "DICT"

[repository.defaults.props]
dir = "./data/casedb/demo"
```

### Transform framework
The `gen_epix.transform` module provides stream-processing pipelines:

```python
from gen_epix.transform import FieldTransformer, TransformerPipeline

pipeline = TransformerPipeline([FieldTransformer("name", str.title)])
```

---

## 5) Critical Development Commands

### Starting services
Standard format:

```bash
# SERVICE_NAME IDP_CONFIG REPOSITORY_CONFIG
python run.py api CASEDB IDPS DICT_DEMO
python run.py api CASEDB MOCK DICT_DEMO
python run.py api SEQDB  IDPS SA_SQLITE_DEMO
python run.py api OMOPDB MOCK DICT_EMPTY
```

Typical ports:
- CASEDB: 8000
- SEQDB: 8001
- OMOPDB: 8002

> If `commondb` runs as an API in this repo, find its port in code/config and document it (do not guess).

### Testing
```bash
python run.py test_all
python run.py test_all_unit
```

### Data loading
```bash
python run.py etl_load_demo_data all
python run.py etl_load_demo_data casedb
```

---

## 6) Common Gotchas (do not ignore)

1. **Environment variables / discovery**
   - Services auto-discover configs via `ConfigDiscovery.get_config_path()` — don’t hardcode paths.

2. **Repository registration**
   - Always call `repository.register_mappers()` before using SQLAlchemy repos.

3. **Service dependencies**
   - `casedb` depends on `seqdb` — start `seqdb` when working with `casedb`.

4. **Command IDs**
   - Commands auto-generate UUIDs — don’t manually set `id` fields.

5. **User context is mandatory**
   - Commands require a `user` parameter for authorization. Use test fixtures where appropriate.

---

## 7) Cross-Service Discovery (HTTP boundaries)

Services communicate via **HTTP APIs**, not direct imports.

When generating or modifying cross-service calls:
1) **Search the workspace for existing patterns first** (e.g., `RemoteApp`, `httpx`, “client”, “base_url”, “external”, “gateway`).
2) **Reuse existing client abstractions/config patterns** instead of introducing new ones.
3) **Cite precedent**: include file paths + symbols (and line ranges if possible) that match the pattern you used.
4) If no client pattern exists, propose a minimal client design and label it as a **new pattern** (include risks and where to document it).

---

## 8) Integration Points

- **Cross-service communication**: via HTTP APIs (not direct imports)
- **Remote service support**: can connect to remote instances via a `RemoteApp` pattern (verify exact location in repo)
- **Shared models**: common models live in `gen_epix.commondb` (User, Organization, etc.)
- **Auth tokens**: JWT tokens shared across services via `gen_epix.fastapp.services.auth` (verify exact usage in repo)

---