# Gen-EpiX Backend Product Manual

## 1. Introduction

Gen-EpiX is the backend of a genomic epidemiology platform. It is delivered not as a single monolith, but as a small family of closely related API services that share a common “control plane” for configuration, composition, security, and request handling.

At its core, the system is built around a **command-centric execution model**: HTTP endpoints are deliberately kept thin, acting mostly as transport adapters that translate requests into commands. The real work—along with the most important security decisions—happens as those commands move through a well-defined execution pipeline.

What this manual *doesn’t* claim: the documentation set does not fully specify production deployment topology, ingress hardening, rollout/rollback strategy, or complete OpenAPI coverage for all app variants. Where the source documentation explicitly marks gaps, this manual preserves them as `<TBF elsewhere>`.

---

## 2. System Overview

### Core components

Think of Gen-EpiX as four “siblings” built from the same blueprint:

- **COMMONDB**: the shared foundation. It provides common routers (including `auth`, `rbac`, `organization`, `system`) and shared service configuration baseline.
- **CASEDB**: extends the common surface with case-focused domains (e.g., `case`, `geo`, `ontology`, `subject`, `abac`).
- **SEQDB**: extends the common surface with sequence/file domains (e.g., `seq`, `file`).
- **OMOPDB**: extends the common surface with OMOP-oriented domains (e.g., `omop`).

All four are FastAPI applications that follow the same assembly pattern: build configuration, compose runtime dependencies, then expose routers under a versioned prefix.

### Service boundaries

The key boundary in the architecture is **composition time**—the moment when the service decides what it is, what it trusts, and what policies will govern it. Each app variant constructs an app configuration (`AppCfg`), then uses a composer (`AppComposer`) to create and register:

- repositories (bounded to a small set of supported types),
- services,
- identity/user dependencies,
- policy registrations (RBAC/ABAC and system policies),
- role maps and permission sets.

Only after that does the FastAPI “shell” get assembled and begin accepting requests.

### High-level runtime flow

The runtime experience is intentionally uniform across app variants:

- Requests are routed under `/v1`.
- The root path `/` does not behave like a typical API root; it is redirect-driven to a configured default route.
- In non-debug mode, the API shell applies a set of HTTP hardening behaviors (rate limiting, gzip, response header hardening, and auth exception handling middleware). In debug mode, those hardening behaviors are disabled, changing the protection posture.

### Request lifecycle (ASCII diagram)

```text
Process start
  -> AppCfg (logging + settings)
  -> AppComposer (repositories + services + user dependencies + policies)
  -> FastAPI shell (middleware + routers mounted under /v1 + root redirect)
  -> endpoint function (transport adapter)
  -> app.handle(command)
  -> policy phases: BEFORE / DURING / AFTER
  -> response serialization
```

---

## 3. Security Model

Gen-EpiX treats security less like a single gate and more like a **pipeline with handoffs**. First it establishes identity using external trust anchors, then it applies internal authority through policy decisions.

### Authentication model (OIDC-based)

Authentication is implemented through FastAPI security dependencies that parse bearer tokens and delegate validation to identity provider (IDP) clients.

The documented token validation path is:

1. Parse the `Authorization` header and require a bearer scheme.
2. Decode/verify JWT against OIDC metadata and keys.
3. Enforce issuer and required claims.
4. Optionally introspect the token when introspection is enabled.

A claim mapping mechanism (`claim_map`) can remap provider claim names into the local claim keys expected by the system before user resolution occurs.

**Hard constraint:** OIDC is the only implemented authentication protocol in the IDP client initialization path. Any non-OIDC protocol configuration raises `NotImplementedError`.

### User resolution and identity outcomes

After claims are accepted, the system resolves them into a local user model. The documented user resolution behavior follows a staged approach:

1. Generate a user key from mapped claims (with optional userinfo fallback).
2. Retrieve an existing user by key.
3. If not found, branch to root creation or automatic user creation when configured.
4. If no valid path exists, fail unauthorized.

This is where many operational “mysteries” become explainable: a request can fail *after* token validation if user resolution can’t complete, because authentication and authorization are intentionally separate controls.

### Authorization model (policy-based, command-centric)

Authorization is modeled around **commands**, not routes.

Endpoints submit commands, and the application core acts as the policy enforcement point around command execution. This is the architectural move that prevents authorization logic from scattering across dozens of route handlers—and it means the same command path tends to have consistent authorization behavior regardless of which endpoint invoked it.

Policy enforcement timing is explicit and standardized:

- **BEFORE**: allow/deny gate for command execution.
- **DURING**: attach/inject policies into the command context for handler use.
- **AFTER**: filter or transform the returned data.

RBAC registration is command-policy based and wired through service registration at startup rather than hardcoded per route.

Some commands are explicitly marked as **no-RBAC** (including identity provider listing).

### Trust boundaries

The system carries two kinds of authority at once:

- **External authority**: the OIDC provider ecosystem (discovery metadata, signing keys, issuer expectations, token semantics).
- **Internal authority**: the repository-backed user model plus the policy engine that governs commands.

Operationally, it helps to think of the handoff like a passport checkpoint: the IDP says “this token is valid,” but the system still has to decide “what does this identity mean *here*, and what is it allowed to do *now*?”

### Root fallback behavior

Root privilege behavior is structural in RBAC: root can satisfy authorization checks even when regular role intersection would fail.

There is also an explicit **no-IDP fallback mode**. When no IDP clients are configured, auth dependencies intentionally switch to a fallback that can resolve requests as a root user through dependency behavior. This is implemented behavior, not an accidental failure mode.

### Security risk modes

The documentation calls out several modes that are intentionally supported but change operational risk:

1. **No-IDP fallback mode** can resolve requests as root user via dependency behavior.  
   Operational implication: treat as restricted mode, not a default internet-exposed posture.

2. **Public provider listing without RBAC** exists: `GetIdentityProvidersCommand` is no-RBAC and invoked with `user=None`.  
   Operational implication: provider metadata exposure is intentional and should be reviewed as part of external interface hardening.

3. **Root privilege behavior is structural** (role hierarchy + root checks).  
   Operational implication: compromise of root identity path has system-wide effect by design.

4. **Pending IDP retry model** favors availability by queueing failed IDPs and retrying later.  
   Operational implication: operators must monitor pending/retry logs to catch degraded auth surface.

5. **Security dependency generation is capped at five IDP variants**.  
   Operational implication: higher IDP counts fail initialization and require code change, not config-only change.

---

## 4. Runtime Behavior

### Service startup model

Local bootstrap is controlled by `run.py`, which orchestrates:

- selecting the app variant,
- selecting the IDP mode,
- selecting the repository mode,
- building an environment-driven settings stack,
- starting the service via uvicorn (with reload support and optional local TLS files when present).

Per-app settings define host/port/debug and a `/v1` route prefix. The documented defaults include:
- `CASEDB: 8000`
- `SEQDB: 8001`
- `OMOPDB: 8002`
- `COMMONDB: 8010`

Composition is the “moment of truth” during startup: policies, roles, repositories, and services are created and registered before business requests can be served. If startup fails at composition time, the system logs setup failure and re-raises, so deployment logs should clearly reflect composition-stage failures.

### Configuration loading model

Configuration loading is staged and environment-driven:

- Logging configuration is loaded from `<APP>_LOG_CONFIG_FILE`.
- Settings are loaded from `<APP>_SETTINGS_FILES` via a settings manager.
- Dynaconf nested overrides are supported using the `__` separator.
- Missing settings files fail fast (e.g., `FileNotFoundError`).

A practical consequence: configuration errors tend to appear early and loudly, rather than degrading silently.

### Request handling lifecycle

Once the app is running, the lifecycle is designed to be predictable:

- Requests enter through `/v1/*`.
- The endpoint function is mostly a transport adapter that constructs a command and passes it into `app.handle(...)`.
- The command runs through policy enforcement phases (BEFORE/DURING/AFTER).
- The response is serialized back through the FastAPI route schema.

### Health and error behavior

- A health endpoint exists at `/health`, and because routers are mounted under `/v1`, it is available at `/v1/health`.
- In non-debug mode, auth exception handling is part of the middleware posture; debugging a `401` should distinguish **middleware/auth exceptions** from **policy denials** (`NOT_AUTHORIZED`), because they represent different layers and different fixes.

---

## 5. Deployment & Release

### Container model

A documented container baseline exists:

- Python slim base image
- ODBC driver installation
- dependency installation
- non-root runtime user
- exposed port `8000`
- healthcheck at `/v1/health`

However, the inspected Dockerfile contains **no active runtime `CMD`** (examples are commented). The final production start command is therefore:

`<TBF elsewhere>`

Cloud provider topology, infrastructure-as-code, network segmentation, and rollout model are also not evidenced:

`<TBF elsewhere>`

### CI/CD behavior

Delivery is implemented as two connected pipelines:

1. **CI quality pipeline** (GitHub Actions):  
   - triggers on push and PR activity across `dev`, `test`, and `main`
   - uses concurrency cancellation to prevent redundant in-flight runs
   - sets up Python 3.14, installs dependencies, and source-builds `pyodbc` (with ODBC headers)
   - runs formatting gates (`isort`, `black`)
   - runs linting (`pylint`)
   - runs strict type checking (`mypy` with strict flags)
   - runs tests via `python run.py test_all`
   - uploads coverage (`test/output/coverage.xml`) as an artifact
   - runs SonarCloud analysis using that coverage artifact

2. **Release publication pipeline** (GitHub Actions, release-please-driven):  
   - anchored to `main` activity and release-please outputs
   - can bump `pyproject.toml`, commit, and push with `--force`
   - if a release is created: builds distributions, zips artifacts, uploads to GitHub Release, and publishes `dist` to PyPI
   - publishing uses `id-token: write` and a named `PyPI` environment (tying release posture to GitHub environment governance)

A documented operational note: repository state shows a version mismatch (`pyproject.toml` `7.1.1` vs manifest `7.1.2`), which explains why the release pipeline contains a version synchronization step.

### Release automation

Release-please is the authority source for release intent in the automation; downstream publish steps are intentionally conditional on release-please outputs (e.g., `release_created`).

### Known unknowns

- Runtime infrastructure rollout/rollback strategy: `<TBF elsewhere>`
- Environment protection rules and secret governance for the `PyPI` environment: `<TBF elsewhere>`
- Formal rollback process for a bad PyPI/GitHub release: `<TBF elsewhere>`
- Branch protection alignment with force-push version bumping: `<TBF elsewhere>`

---

## 6. Operating the System

Operating Gen-EpiX is less about memorizing endpoints and more about understanding the system’s few, strong control knobs—because those knobs determine posture.

### Configuration surfaces

The primary configuration surfaces are:

- `<APP>_SETTINGS_FILES`: stacked settings files used by the settings manager
- `<APP>_LOG_CONFIG_FILE`: logging configuration input
- Dynaconf environment overrides using nested keys with `__`

The system fails fast when settings files are missing, which is helpful in production—misconfiguration becomes a startup failure rather than a silent foot-gun.

### IDP configuration

The system supports multiple IDP “modes,” especially visible in local operation:

- `IDPS`: configured OIDC providers (including a public provider entry and claim mapping configuration)
- `MOCK`: local mock OIDC settings
- `NONE`: explicit no-provider path (reduced security posture)

Important operational guidance in the docs: before exposing any instance beyond a trusted environment, verify both **IDP mode** and **repository mode**—these two switches define authentication posture and persistence behavior.

### Logging behavior

Logging is JSON-formatted to stdout with scoped namespaces (including `commondb.setup`, `service`, `app`, `api`, `external`) and a root default at `INFO`.

The most useful operational logs are the ones that mark phase transitions or control points, such as:

- IDP initialization/retry logs (trust anchors available vs degraded),
- user-verification warnings (auth dependency failures before command execution),
- `NOT_AUTHORIZED` events (policy denials after identity resolution).

### Observability

The documentation evidences:

- runtime logs as primary operational signals,
- CI observability through coverage artifact publication and SonarCloud analysis.

What is *not* evidenced in the documentation set:

- runtime metrics/tracing/alerting backend: `<TBF elsewhere>`
- formal SLO/SLA targets and scaling strategy: `<TBF elsewhere>`
- incident runbooks and monitoring definitions: `<TBF elsewhere>`

### Known operational gaps

- Production deployment instructions are not fully specified: `<TBF elsewhere>`
- Production ingress hardening and deployment guardrails are not evidenced by local convenience commands: `<TBF elsewhere>`
- Secret management architecture for IDP and repository credentials in production: `<TBF elsewhere>`

---

## 7. Extending the System

Extending Gen-EpiX is safest when you treat the architecture like a living organism with a skeleton: you can add new capabilities, but you do it by attaching to the same bones—composition, commands, and policies—rather than bypassing them.

### Module structure

The system is organized as app variants that share a common composition model. Extending behavior usually happens by adding domain-specific elements to an app variant while keeping the shared assembly and command execution pipeline intact.

### Policy registration model

RBAC is registered centrally during startup, not sprinkled across routes. Permissions are declared in role generators (permission sets and hierarchy), then expanded into role permissions used by policy checks. Domain-specific apps extend the common role generator to add app-specific command permissions.

No-RBAC exceptions are explicit through a defined exception list.

### Safe extension boundaries

Documented safe boundaries are consistent with the command-centric architecture:

- endpoints should remain transport adapters,
- authorization should remain centralized in the command lifecycle (BEFORE/DURING/AFTER),
- RBAC should remain registered at startup rather than hardcoded per route.

### Documented extension patterns only

**Adding RBAC rules**
- Primary change is in role generator definitions and hierarchy.
- There is no evidenced separate declarative RBAC config file; RBAC appears code-declared and composition-registered.

**Adding endpoints**
- Routers are built from `router_data` entries that register endpoint families.
- Endpoint modules often combine explicit routes with generated CRUD families.
- All routers remain mounted under `/v1` via shared setup.

**CRUD families**
- Many resource endpoints follow a generated pattern including `/batch`, `/query`, `/query/ids`, and `/{object_id}` suffixes, with consistent operation ID style.

**Adding IDP configuration**
- IDP entries use a `[[service.auth.props.idps_cfg]]` structure in config files.
- Local mode selection maps `IDPS`, `MOCK`, `NONE` to concrete config files.
- Security dependency generation is capped at five IDP bases; exceeding that requires code change.

---

## 8. Constraints & Limitations

This section gathers the system’s hard edges—the parts that are designed to stop you rather than bend.

### Security constraints

- **OIDC-only authentication support** in the IDP initialization path; non-OIDC config raises `NotImplementedError`.
- **Duplicate IDP `name` or `label` is rejected** at startup.
- **Security dependency variants are capped at five** IDP bases.
- **IDP visibility defaults to non-public** unless configured otherwise.
- **Token introspection interval > 1800 seconds is rejected** by validation.
- **No-IDP mode exists** and can map to root-user fallback dependencies; it is an explicit high-risk posture when externally exposed.

### Architectural and runtime constraints

- **Repository type support is bounded** to `DICT`, `SA_SQLITE`, and `SA_SQL`; unsupported modes fail at composition time (`NotImplementedError`) rather than degrading silently.
- **Root route behavior is always redirect-driven** through shared setup logic.
- **Policy enforcement is centralized** in the `App.handle` lifecycle for user-initiated command execution.

### HTTP posture constraints

- In **non-debug mode**, the API shell applies rate limiting, gzip, response header hardening, and auth exception handling middleware.
- In **debug mode**, that middleware hardening posture is disabled—so debug mode changes the HTTP protection posture.

### Contract and coverage limitations

- The documented OpenAPI contract authority in the deep-dive is bounded to one artifact (casedb).  
  Full OpenAPI coverage for `SEQDB` and `OMOPDB` is: `<TBF elsewhere>`

### Documented consistency issues

- Metadata mismatch exists: package license is `EUPL-1.2` while `seqdb`/`omopdb` OpenAPI metadata still uses placeholder `Apache-2.0`.

---

## 9. Open Questions / Missing Documentation

This is the consolidated list of `<TBF elsewhere>` items preserved from the source documentation set:

### Production topology and operations
- End-to-end infra topology (ingress, load balancing, service mesh) beyond app process boundaries: `<TBF elsewhere>`
- Cloud provider topology, infrastructure-as-code, network segmentation, and rollout model are also not evidenced: `<TBF elsewhere>`
- Stage/prod promotion, rollback, and environment isolation model beyond local + CI/release workflows: `<TBF elsewhere>`
- Runtime monitoring/alerting/SLO definitions and incident runbooks: `<TBF elsewhere>`
- Formal SLO/SLA targets and scaling strategy per app type: `<TBF elsewhere>`
- Runtime metrics/tracing/alerting backend: `<TBF elsewhere>`
- Production runtime process command and service manager contract for container deployments: `<TBF elsewhere>`
- Final production container start command (no active Dockerfile `CMD` evidenced): `<TBF elsewhere>`
- Production deployment instructions (not fully specified): `<TBF elsewhere>`

### Security, identity, and secrets
- Secret management architecture for IDP and repository credentials in production: `<TBF elsewhere>`
- Production-equivalent secret management flow for local-to-prod parity: `<TBF elsewhere>`
- Standardized runbook for local mode selection (`IDPS` vs `MOCK` vs `NONE`) beyond code-level options: `<TBF elsewhere>`

### API contracts and external exposure
- Full endpoint-level contract deep dives for each app-specific router family: `<TBF elsewhere>`
- Full OpenAPI coverage for `SEQDB` and `OMOPDB` endpoint contracts: `<TBF elsewhere>`
- External API deprecation/versioning policy beyond current `/v1` prefix and generated operation IDs: `<TBF elsewhere>`
- Gateway/ingress controls (WAF, IP allowlists, external rate-limit policy) not evidenced in artifact-level analysis: `<TBF elsewhere>`
- Production ingress hardening or deployment guardrails are not evidenced by local convenience commands: `<TBF elsewhere>`

### Authorization semantics and domain narratives
- Full ABAC semantics per command and data model: `<TBF elsewhere>`
- Human documentation claims automatic notifiable-disease sharing by RIVM; not evidenced in analyzed enforcement paths: `<TBF elsewhere>`
- End-to-end mapping of high-level sharing narratives to concrete casedb ABAC entities and policies: `<TBF elsewhere>`

### Delivery governance
- Environment protection rules, required reviewers, and secret governance for the `PyPI` environment: `<TBF elsewhere>`
- Formal rollback process for a bad PyPI/GitHub release: `<TBF elsewhere>`
- Branch protection and force-push policy alignment with automated version bumping: `<TBF elsewhere>`

### Project governance and contribution process
- Formal branching model policy beyond CI automation targets: `<TBF elsewhere>`
- Code review policy (required approvals, reviewer roles, merge policy): `<TBF elsewhere>`
- Issue triage and prioritization process: `<TBF elsewhere>`

### Local environment tooling
- Official local container orchestration profile (`docker-compose`/k8s dev profile): `<TBF elsewhere>`

---

## 10. Evidence Basis

This manual is a synthesis of the existing documentation set (no repository source code was used directly). The following documents were used:

- `README.md`
- `0_System-Documentation-Index.md`
- `High-Level-Architecture-Deep-Dive.md`
- `Authorization-Authentication-Deep-Dive.md`
- `API-Endpoints-Deep-Dive.md`
- `Local-Development-Deep-Dive.md`
- `Deployment-Release-Process-Deep-Dive.md`
- `Getting-Started.md`
- `Architecture-Principles.md`
- `Extending-the-System.md`
- `Contribution-Workflow.md`
