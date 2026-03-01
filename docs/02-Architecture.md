Creation Date: March 1, 2026

# Architecture

This chapter defines the architectural principles, system composition model, and command-centric execution pipeline that all Gen-EpiX app variants share.

For framework internals (domain metadata, model layer, repositories, services, middleware), see [02a-Fastapp-Framework](./02a-Fastapp-Framework.md).

---

## 1. Architectural Principles

Six evidence-grounded invariants govern the system's design:

### 1.1 Layer Boundaries

- The HTTP shell is assembled in `create_fast_api(...)`: middleware, router mounting, and root redirect. (Source: `gen_epix/commondb/app_setup.py#L27-L35`; Source: `gen_epix/commondb/app_setup.py#L74-L126`)
- Endpoint functions translate HTTP calls to commands and invoke `app.handle(cmd)`. (Source: `gen_epix/commondb/api/auth.py#L24-L36`; Source: `gen_epix/commondb/api/system.py#L82-L90`)
- Services execute command behavior and call repositories through unit-of-work patterns. (Source: `gen_epix/fastapp/service.py#L184-L240`; Source: `gen_epix/fastapp/service.py#L302-L375`)

This separation keeps HTTP transport in API/setup files and execution/data logic in service/repository layers.

### 1.2 Command-Based Execution Model

- `App.handle(...)` is the command execution entrypoint used by endpoints and services. (Source: `gen_epix/fastapp/app.py#L309-L327`)
- Commands and permissions are registered in the domain model, including CRUD command wiring. (Source: `gen_epix/fastapp/domain/domain.py#L658-L721`)
- The command object is the stable integration surface across transport, policy, and service execution. (Source: `gen_epix/commondb/api/auth.py#L32-L34`; Source: `gen_epix/fastapp/app.py#L309-L327`)

### 1.3 Policy Enforcement Timing: BEFORE / DURING / AFTER

The PDP defines three timing phases: (Source: `gen_epix/fastapp/pdp.py#L12-L17`; Source: `gen_epix/fastapp/pdp.py#L85-L112`)

| Phase | Purpose |
|-------|---------|
| `BEFORE` | Deny/allow gate for command execution |
| `DURING` | Inject policies into command context for handler use |
| `AFTER` | Filter or transform the return value |

`App.handle` applies these phases for initial commands. Centralized policy timing reduces route-level authorization drift. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`; Source: `gen_epix/fastapp/app.py#L417-L429`)

### 1.4 Authentication vs Authorization Separation

- Authentication dependencies are created by `AuthService` and injected into endpoints. (Source: `gen_epix/fastapp/services/auth/service.py#L84-L91`; Source: `gen_epix/commondb/env.py#L163-L168`)
- Authorization decisions are enforced by command policies in `App.handle`/PDP. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L406-L419`)
- Passing dependency-based authentication does not by itself grant command authorization.

### 1.5 OIDC-Only Identity Provider Support

- `AuthService._init_idp_client` initializes `OauthIdpClient` only when `protocol == OIDC`; other protocols raise `NotImplementedError`. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L694`)
- Non-OIDC provider onboarding requires code changes, not config-only changes.

### 1.6 Root Fallback and No-IDP Implications

- If no IDP clients are configured, auth dependencies switch to `_create_no_auth_dependencies()`. (Source: `gen_epix/fastapp/services/auth/service.py#L88-L90`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L424`)
- Running with no configured IDP materially changes trust posture and should be treated as a constrained mode. (Source: `config/no_identity_providers.toml#L1-L1`)
- Root user creation and root role assignment are implemented in user manager and RBAC policy checks. (Source: `gen_epix/commondb/services/user_manager.py#L46-L59`; Source: `gen_epix/fastapp/services/rbac/policy.py#L51-L66`)

---

## 2. System Composition

The platform is built as four FastAPI applications that share a common composition model. Each app constructs `AppCfg`, composes services/repositories/policies with `AppComposer`, and exposes HTTP routes through the shared `create_fast_api` assembly function:

| App | Purpose | Domain routers |
|-----|---------|---------------|
| **COMMONDB** | Shared foundation | `auth`, `rbac`, `organization`, `system` |
| **CASEDB** | Case management | Common + `case`, `geo`, `ontology`, `subject`, `abac` |
| **SEQDB** | Sequence/file data | Common + `seq`, `file` |
| **OMOPDB** | OMOP-oriented data | Common + `omop` |

(Source: `gen_epix/commondb/api/router.py#L23-L48`; Source: `gen_epix/casedb/api/router.py#L26-L72`; Source: `gen_epix/seqdb/api/router.py#L26-L64`; Source: `gen_epix/omopdb/api/router.py#L25-L55`)

**Architectural anchor:** endpoint code is mostly transport glue; authorization and policy enforcement are centralized at command execution time. (Source: `gen_epix/fastapp/app.py#L314-L360`)

---

## 3. Boot and Request Lifecycle

### Boot Sequence

```text
Process start
  -> AppCfg (logging + settings)
  -> AppComposer (repositories + services + user deps + policies)
  -> create_fast_api (middleware + /v1 routers + root redirect)
```

(Source: `gen_epix/commondb/config/cfg.py#L155-L177`; Source: `gen_epix/commondb/env.py#L103-L177`; Source: `gen_epix/commondb/app_setup.py#L74-L126`)

Composition is the "moment of truth" during startup: policies, roles, repositories, and services are created and registered before the system accepts business requests. If startup fails at composition time, the system logs setup failure and re-raises. (Source: `gen_epix/commondb/env.py#L185-L197`)

### Request Lifecycle

```text
  -> endpoint function (transport adapter)
  -> app.handle(command)
  -> BEFORE policies (allow/deny gate)
  -> DURING policies (inject context)
  -> handler execution
  -> AFTER policies (filter/transform)
  -> response serialization
```

(Source: `gen_epix/fastapp/app.py#L314-L360`; Source: `gen_epix/fastapp/app.py#L406-L418`)

Requests are routed under `/v1`. The root path `/` redirects to the configured default route. In non-debug mode, the API shell applies rate limiting, gzip, response header hardening, and auth exception handling middleware. (Source: `gen_epix/commondb/app_setup.py#L75-L109`; Source: `gen_epix/commondb/app_setup.py#L120-L126`)

---

## 4. Composition Boundaries

Composition is the boundary where runtime authority is established. `AppComposer` creates role maps, service/repository instances, user manager dependencies, and registers system/RBAC/ABAC policies before the API starts handling requests. (Source: `gen_epix/commondb/env.py#L73-L85`; Source: `gen_epix/commondb/env.py#L147-L177`)

FastAPI assembly is centralized in `create_fast_api`, keeping HTTP-level behavior uniform across all app variants. (Source: `gen_epix/commondb/app_setup.py#L27-L35`)

Router boundaries are app-specific but follow the same pattern: shared common routers plus app-domain routers. Because routers are mounted through one shared function, cross-app HTTP behavior changes should be made in `app_setup.py` rather than app-specific router modules. (Source: `gen_epix/casedb/app.py#L33-L39`; Source: `gen_epix/commondb/app_setup.py#L27-L35`)

Repository bindings are configuration-driven by module/class mappings, while runtime repository type handling is bounded to `DICT`, `SA_SQLITE`, and `SA_SQL`. (Source: `gen_epix/commondb/base_env.py#L66-L93`)

---

## 5. Operational Interpretation

Operators should reason about architecture in three stages: **configuration loading**, **composition/startup**, and **request execution**. Most incidents can be localized quickly by identifying the failing stage first. (Source: `gen_epix/commondb/config/settings_manager.py#L58-L67`; Source: `gen_epix/commondb/env.py#L185-L197`; Source: `gen_epix/fastapp/app.py#L366-L387`)

Command-level authorization remains active regardless of router shape, so transport expansion does not automatically imply permission expansion. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L406-L418`)

For guardrails and hard limits, see [09-Constraints-and-Open-Questions](./09-Constraints-and-Open-Questions.md).

---

## Evidence Sources

- `gen_epix/commondb/app_setup.py#L27-L126`
- `gen_epix/commondb/api/auth.py#L24-L36`
- `gen_epix/commondb/api/system.py#L82-L90`
- `gen_epix/commondb/env.py#L73-L205`
- `gen_epix/commondb/base_env.py#L66-L93`
- `gen_epix/commondb/config/cfg.py#L155-L177`
- `gen_epix/fastapp/app.py#L309-L429`
- `gen_epix/fastapp/pdp.py#L12-L112`
- `gen_epix/fastapp/service.py#L184-L375`
- `gen_epix/fastapp/domain/domain.py#L72-L721`
- `gen_epix/fastapp/services/auth/service.py#L84-L694`
- `gen_epix/fastapp/services/rbac/policy.py#L51-L66`
- `gen_epix/commondb/services/user_manager.py#L46-L178`
- `gen_epix/commondb/api/router.py#L23-L48`
- `gen_epix/casedb/api/router.py#L26-L72`
- `gen_epix/seqdb/api/router.py#L26-L64`
- `gen_epix/omopdb/api/router.py#L25-L55`
- `config/no_identity_providers.toml#L1-L1`
- `run.py#L17-L38`
