Creation Date: March 1, 2026

# App Composition Walkthrough — COMMONDB

This document traces every component that participates in building the COMMONDB FastAPI application, from the entry point in `app.py` down to the lowest-level helpers. The structure is intentionally top-down: each section describes *what* a component does and *why* it exists, followed by a pointer to the next layer it hands control to.

For the general extension patterns, see [08-Extending-the-System](./08-Extending-the-System.md). For configuration detail, see [05-Configuration-and-Runtime](./05-Configuration-and-Runtime.md).

---

## 1. Entry Point — `app.py`

**File:** `gen_epix/commondb/app.py`

The module-level code executes exactly four statements at import time. Everything that follows is triggered by those statements.

| Statement | What it produces |
|-----------|-----------------|
| `SCHEMA_KWARGS` | A plain dict that feeds the OpenAPI/Swagger documentation metadata (title, version, contact, license). `get_package_version()` reads the version string from `pyproject.toml`. |
| `APP_CFG = AppCfg(...)` | Loads and validates all configuration and sets up logging. See §2. |
| `APP_COMPOSER = AppComposer(APP_CFG)` | Wires together the domain, repositories, services, and auth pipeline into a single `App` object. See §3. |
| `FAST_API = create_fast_api(...)` | Takes the composed `App` and produces the final `FastAPI` instance with middleware, routers, and a custom OpenAPI schema. See §4. |

The trailing `app = FAST_API` alias exists only for backwards compatibility with boot scripts that `import app`.

---

## 2. Configuration — `AppCfg`

**Files:** `config/cfg.py`, `config/settings_manager.py`, `config/factory.py`

`AppCfg` is the first thing constructed. Its `__init__` runs three phases in order:

### 2a. Logger Initialisation (`_init_configure_loggers`)
1. Reads the path to a YAML logging-config file from the environment variable `COMMONDB_LOG_CONFIG_FILE`.
2. Feeds that YAML to `logging.config.dictConfig`, which creates all handlers and loggers in one call.
3. Stores four named loggers that the rest of the stack uses:
   - `setup` — startup/shutdown lifecycle events.
   - `api` — per-request HTTP-layer events.
   - `app` — application-level events (command dispatch, policy checks).
   - `service` — service-layer events (business logic, repository calls).

### 2b. Settings Loading (`_init_load_settings`)
1. Constructs a `SettingsManager` with the env-var prefix `COMMONDB_`.
2. `SettingsManager.load_settings()` reads the list of TOML settings files from the env var `COMMONDB_SETTINGS_FILES`, then initialises a `Dynaconf` object. Dynaconf merges the files in order, so later files override earlier ones. Runtime env vars (e.g. `COMMONDB__LOG__LEVEL`) override everything via the `__` separator convention.

   The settings files that ship with COMMONDB are:
   - `settings.toml` — base config (host, port, HTTP headers, service class names, default factories).
   - `settings.repository.dict.toml` or `settings.repository.sa.toml` — swaps in the Dict or SQLAlchemy repository classes for each service type.
   - Secret/overlay files (prefixed `.example.secrets.*`) — connection strings, file paths, IdP tokens. These are never checked in; they are supplied per environment.

### 2c. Settings Validation (`_init_validate_settings`)
Dynaconf returns plain strings for class references and factory names. This phase resolves them into actual Python objects:

1. **Factory resolution** — The strings `"DATETIME_NOW"` and `"ULID"` in `service.defaults.props` are replaced by the corresponding callables from `TimestampFactory` and `IdFactory` (both simple `Enum` classes wrapping `datetime.now(UTC)` and `ulid.new().uuid`).
2. **Service class resolution** — For every `ServiceType`, the `module` + `class_name` pair in `service.<type>` is turned into an actual class via `importlib.import_module`.
3. **Repository class resolution** — Same treatment for every entry in `repository.<type>`.
4. **Default merging** — The `service.defaults` and `repository.defaults` blocks are shallow-merged into each per-type block so that every service and repository inherits the common `timestamp_factory` / `id_factory` without repeating them.

---

## 3. Application Composition — `AppComposer`

**Files:** `env.py` (defines `AppComposer`), `base_env.py` (defines `BaseAppComposer`), `app_impl_details.py`

`AppComposer` is the Composition Root. It owns the single call that builds the entire runtime object graph. The class accepts optional overrides for almost every injectable (service classes, policy classes, model/command class maps) so that downstream apps (CASEDB, SEQDB, OMOPDB) can reuse the same wiring logic while substituting their own domain classes.

### 3a. Role Derivation
Before any services exist, the `RoleGenerator` (from `domain/policy/permission.py`) is consulted for three static maps:

| Map | Purpose |
|-----|---------|
| `role_map` | `Role` enum → prefixed string (e.g. `Role.ROOT` → `"COMMONDB_ROOT"`). |
| `role_set_map` | `RoleSet` enum → frozenset of role strings for permission checks. |
| `role_permissions_map` | role string → set of `(Command, PermissionType)` tuples that the role is allowed to execute. |

These maps are handed into `AppImplDetails`, the shared state bag that all subsequent steps read from.

### 3b. `AppImplDetails` — The State Bag
A Pydantic `BaseModel` that holds every piece of state produced during composition. It does *not* contain any logic; it is purely a validated container. Key fields:

- `sorted_service_types` — the order in which services are initialised (matters because some services depend on others).
- `services` / `repositories` — dicts keyed by `ServiceType`, populated during the loop in §3c.
- `model_class_map` / `command_class_map` / `policy_class_map` — substitution maps that allow child apps to replace base classes with their own subclasses without changing the wiring code. `get_mapped_class()` is the single lookup point.
- Three user-dependency slots — see §3e.

### 3c. Repository + Service Loop
`compose_application()` iterates over `sorted_service_types` and, for each one, calls `_initialize_repository()`. That method:

1. Reads `service.<type>` and `repository.<type>` from the already-validated `Dynaconf` config.
2. If a repository config exists, calls `repository_class.create_repository()`. The base class (`BaseRepository`) already knows how to create either a `DictRepository` (pickle-backed in-memory store) or an `SARepository` (SQLAlchemy, targeting SQLite or SQL Server) depending on the `RepositoryType`. It receives the list of domain entities for the service type so it can set up tables / in-memory buckets automatically.
3. Instantiates the service class, injecting the `App`, the repository (or `None` for services like AUTH that have no local store), the loggers, and any per-service props from config.
4. Stores both in `AppImplDetails`.

Services that ship with COMMONDB:

| ServiceType | Service class | Has repository? |
|-------------|---------------|-----------------|
| AUTH | `AuthService` | No — delegates to the external IdP. |
| RBAC | `RbacService` | No — permission data is derived in memory from `role_permissions_map`. |
| ABAC | `AbacService` | Yes — persists `OrganizationAdminPolicy` records. |
| ORGANIZATION | `OrganizationService` | Yes — persists all organization-domain entities. |
| SYSTEM | `SystemService` | Yes — persists `Outage` records. |

### 3d. Post-Loop Wiring
After every service exists, three cross-cutting concerns are completed:

1. **Role registration** — `RbacService.register_roles()` receives the `role_permissions_map` and the root-role string. It pre-computes the transitive permission closure that every subsequent permission check uses.
2. **User Manager** — `UserManager` is constructed with a reference to both `OrganizationService` and `RbacService`. It sits between the IdP token validation and the application's command layer: it maps raw IdP claims to internal `User` objects, handles root-user bootstrap (a shared secret in config), and optionally auto-creates users for first-time claims.
3. **Policy registration** — `SystemService`, `RbacService`, and `AbacService` each call `register_policies()`. This attaches the authorization guards (RBAC permission checks, ABAC org-admin checks, system-outage blocks) to the `App`'s command-dispatch table.

### 3e. User Dependencies (FastAPI DI)
`AuthService.create_user_dependencies()` returns three FastAPI `Depends` callables:

| Dependency | When it resolves |
|------------|-----------------|
| `registered_user` | The caller holds a valid token *and* has an existing `User` record. |
| `new_user` | The caller holds a valid token but is *not* yet registered (invitation flow). |
| `idp_user` | The caller is known to the IdP but registration status is unknown. |

These are stored on `AppImplDetails` and injected into route handlers so that each endpoint can declare exactly the authentication level it needs as a function parameter.

How it works internally: the method generates one set of `get_current_user` / `get_new_user` / `get_idp_user` async functions per number of configured IdP clients (up to 5). Each function declares one `Depends(idp_client)` parameter per IdP. FastAPI resolves those dependencies at request time — whichever IdP returns valid claims first wins. If no IdP is configured at all, it falls back to `_create_no_auth_dependencies()`, which just returns a hard-coded root user for local development.

---

## 4. FastAPI Assembly — `create_fast_api`

**File:** `app_setup.py`

Takes the fully-composed `App` and produces a `FastAPI` instance. The steps are:

### 4a. Lifespan
An `asynccontextmanager` that logs `STARTED_APP` on startup and `STOPPING_APP` on shutdown. This is the standard FastAPI lifespan hook; no background tasks or resource cleanup happen here for COMMONDB.

### 4b. Middleware Stack (production only, skipped in debug mode)
Middleware is added in the order FastAPI processes them (last-added runs first on the way *in*, first-added runs first on the way *out*):

| Middleware | Purpose |
|------------|---------|
| `SlowAPIMiddleware` | Global rate limiting. Per-route limits can be added with `@limiter.limit`. |
| `GZipMiddleware` | Compresses responses ≥ 1000 bytes at compression level 5. |
| `UpdateResponseHeaderMiddleware` | Injects security headers (CSP, HSTS, X-Frame-Options, etc.) on every response. Certain paths (e.g. `/docs`, the OAuth2 redirect) get a reduced set. |
| `HandleAuthExceptionMiddleware` | Catches authentication exceptions that escape the route handler and turns them into proper HTTP 401/403 responses with logging. |

### 4c. Routers
`create_routers()` (`api/router.py`) builds one `APIRouter` per logical group:

| Tag | Factory function | ServiceType it serves |
|-----|------------------|-----------------------|
| `auth` | `create_auth_endpoints` | AUTH |
| `rbac` | `create_rbac_endpoints` | RBAC |
| `organization` | `create_organization_endpoints` | ORGANIZATION |
| `system` | `create_system_endpoints` | SYSTEM |

Each factory receives the `App` and the `handle_exception` callable. Inside, it registers individual route functions that:
1. Declare the appropriate user dependency (`registered_user`, `new_user`, etc.) as a FastAPI parameter.
2. Construct a *command object* from the request body.
3. Call `handle_command(app, user, error_code, command, handle_exception)`.
4. Return the result.

All routers are mounted under the `/v1` prefix (from `api.route.v1` in config).

### 4d. Root Redirect
A single `GET /` route that redirects to `api.default_route` (defaults to `/openapi.json`, i.e. the raw schema JSON).

### 4e. Custom OpenAPI Schema
`create_custom_openapi_function()` replaces the default `FastAPI.openapi` method. It:
- Injects the `SCHEMA_KWARGS` metadata (title, contact, license, etc.).
- Optionally applies a `fix_schema` pass that cleans up generated JSON Schema.
- Wires in the `auth_service` so that the OpenAPI document correctly describes the OAuth2 / OIDC security schemes.

---

## 5. Exception Handling — `api/exc.py`

**File:** `gen_epix/commondb/api/exc.py`

Every route delegates its `except` clause to `handle_exception`, which is produced by `generate_handle_exception_function` — a `functools.partial` that binds the `App` and the logger at composition time.

The function classifies exceptions into a hierarchy and maps them to HTTP status codes:

| Exception base | HTTP code | Behaviour |
|----------------|-----------|-----------|
| `AuthException` | 401 / 403 | Logged at INFO (expected rejections). |
| `IdsError` | 422 or 409 | Extracts the offending IDs from the exception and includes them in the response detail. |
| `ServiceException` | per-exception | Logged at ERROR; detail is generic ("System unavailable"). |
| Other `DomainException` | 422 | Logged at WARN. |
| Any other `Exception` | 500 | Logged at ERROR; detail is suppressed. |

The `handle_command` wrapper in the same file is the single call site used by every route handler. It calls `app.handle(command)` and catches any exception to route it through the handler above.

---

## 6. Domain Registration — `domain/__init__.py`

**File:** `gen_epix/commondb/domain/__init__.py`

Before the app can dispatch commands, it needs to know which models and commands exist. The `Domain` object (from `fastapp`) is a registry. `register_domain_entities()` walks `SORTED_MODELS_BY_SERVICE_TYPE` and `COMMANDS_BY_SERVICE_TYPE` (both defined in the domain sub-packages) and registers every entity and its associated commands into the `Domain`. The `set_schema_to_service_type=True` flag groups them by `ServiceType` in the generated OpenAPI schema.

---

## Key Patterns and Frameworks

| Pattern / Framework | Where it appears | Role |
|---------------------|------------------|------|
| **Composition Root** | `AppComposer` | Single place that constructs and wires the entire object graph. Nothing is built elsewhere. |
| **Strategy (via config)** | `settings.toml` + `AppCfg._init_validate_settings` | Repository *type* (Dict vs SA_SQLite vs SA_SQL) and service *class* are selected at runtime from config, not hard-coded. |
| **Repository Pattern** | `BaseRepository` → `DictRepository` / `SARepository` | All persistence is behind an interface; the concrete store is invisible to services. |
| **Command Pattern** | Every mutation and non-trivial read is a command object | Routes construct commands; `App.handle()` dispatches them to the correct service handler. |
| **Unit of Work** | Inside `App.handle()` | Each command runs inside a transaction that is committed on success and rolled back on failure. |
| **RBAC + ABAC** | Policies registered in §3d | RBAC checks permissions derived from the role hierarchy. ABAC narrows results to the user's own organization or enforces org-admin status. |
| **FastAPI Dependency Injection** | User dependencies from §3e | The three `Depends` callables plug the authentication layer directly into route signatures with zero boilerplate in each handler. |
| **Dynaconf** | `SettingsManager` | Provides layered, env-var-overridable configuration. Multiple TOML files are merged; env vars with `__` separators can override any nested key. |
| **Lifespan (ASGI)** | `create_fast_api` lifespan context manager | Replaces the deprecated `on_startup` / `on_shutdown` events with the modern ASGI lifespan protocol. |

---

## Dependency Flow (summary)

```
Environment variables + TOML files
        │
        ▼
   AppCfg  ──► Dynaconf settings object
        │         (service classes, repo classes, factories, loggers)
        ▼
   AppComposer
        ├── creates  App  (holds Domain, cfg, logger, impl details)
        ├── creates  Repositories  (one per ServiceType that needs one)
        ├── creates  Services      (one per ServiceType, injected with repo)
        ├── registers Roles + Policies onto App
        ├── creates  UserManager   (auth pipeline glue)
        └── produces user Depends  (registered / new / idp)
                │
                ▼
        create_fast_api
                ├── attaches Middleware stack
                ├── attaches Routers  (auth, rbac, organization, system)
                ├── attaches root redirect
                └── replaces OpenAPI schema function
                        │
                        ▼
                  FAST_API  (the live FastAPI instance, ready to serve)
                        │
                        ▼
              uvicorn.run() / gunicorn  (ASGI server)
```

---

## Serving the App

`FAST_API` is a standard ASGI application object. There are two paths to actually serving it:

### Local development — `run.py` + uvicorn

```
python run.py api COMMONDB <idp_config> <repository_config>
```

Before uvicorn starts, `Run.api()` calls `set_env_variables()`. That helper assembles the ordered list of TOML settings files for the chosen combination and writes them into the `COMMONDB_SETTINGS_FILES` env var. Uvicorn is then called with `reload=True` (hot-reload on file changes) and optional TLS. The app string is `"gen_epix.commondb.app:FAST_API"`. See [06a-CLI-Reference](./06a-CLI-Reference.md) for full CLI detail.

### Container / production — Dockerfile + gunicorn

The intended production `CMD` is:

```
gunicorn --preload -k uvicorn.workers.UvicornWorker gen_epix.casedb.app:FAST_API
```

`--preload` runs the app module once in the master process before forking workers, so `AppCfg` + `AppComposer` execute only once and the resulting `FAST_API` object is shared via copy-on-write. See [07-CI-CD-and-Release](./07-CI-CD-and-Release.md) for container detail.

---

## Evidence Sources

- `gen_epix/commondb/app.py`
- `gen_epix/commondb/config/cfg.py#L155-L269`
- `gen_epix/commondb/config/settings_manager.py#L15-L77`
- `gen_epix/commondb/env.py#L103-L295`
- `gen_epix/commondb/base_env.py#L66-L140`
- `gen_epix/commondb/app_impl_details.py`
- `gen_epix/commondb/app_setup.py#L1-L126`
- `gen_epix/commondb/api/router.py#L23-L48`
- `gen_epix/commondb/api/exc.py`
- `gen_epix/commondb/domain/__init__.py#L11-L17`
- `gen_epix/commondb/domain/policy/permission.py#L35-L139`
- `gen_epix/fastapp/services/auth/service.py#L346-L449`
- `run.py#L82-L117`
- `Dockerfile`
