# FASTAPP — Shared Framework Overview

`fastapp` is the reusable framework that every Gen-EpiX app (`commondb`, `casedb`,
`seqdb`, `omopdb`) is built on.  It provides all of the scaffolding that sits
between a FastAPI route and a database row: domain metadata, command dispatch,
policy enforcement, two repository backends, authentication, RBAC, CRUD-endpoint
generation, and middleware.

Nothing in `fastapp` is app-specific.  It imports only `filter` and standard /
third-party libraries.

---

## Directory layout

```
gen_epix/fastapp/
├── __init__.py                          # public re-exports
├── app.py                               # App (command dispatcher / PEP)
├── enum.py                              # all framework enumerations
├── exc.py                               # domain & service exceptions
├── log.py                               # structured log-item model
├── model.py                             # base Model, Command, Policy, Permission, Role 
├── pdp.py                               # PolicyDecisionPoint
├── remote_app.py                        # RemoteApp (HTTP-client variant of App)
├── repository.py                        # BaseRepository (abstract)
├── service.py                           # BaseService (abstract)
├── unit_of_work.py                      # BaseUnitOfWork (abstract)
├── user_manager.py                      # BaseUserManager (abstract)
├── util.py                              # serialize_id, SSL context helpers
│
├── api/                                 # CRUD-endpoint generation & HTTP exceptions
│   ├── crud_endpoint_generator.py
│   ├── crud_endpoint_set.py
│   ├── exc.py                           # typed HTTP exceptions (400-503)
│   └── openapi.py                       # OpenAPI schema post-processing
│
├── domain/                              # entity / key / link metadata registry
│   ├── domain.py                        # Domain (central registry)
│   ├── entity.py                        # Entity descriptor
│   ├── key.py                           # Key (unique constraint)
│   ├── link.py                          # Link (foreign key)
│   └── util.py                          # create_keys / create_links helpers
│
├── middleware/                           # ASGI middleware
│   ├── handle_auth_exception.py         # AuthException → 401
│   ├── handle_no_response.py            # client-disconnect → 204
│   ├── limiter.py                       # rate limiting (10 req/s default)
│   └── update_response_header.py        # version & custom headers
│
├── repositories/
│   ├── dict/                            # in-memory backend (dev / testing)
│   │   ├── repository.py                # DictRepository
│   │   └── unit_of_work.py              # DictUnitOfWork (no-op)
│   └── sa/                              # SQLAlchemy backend (production)
│       ├── engine_factory.py            # thread-safe engine cache
│       ├── mapper.py                    # Pydantic ↔ ORM row mapping
│       ├── repository.py                # SARepository
│       ├── unit_of_work.py              # SAUnitOfWork (real transactions)
│       └── util.py                      # Python → SA type mapping
│
└── services/
    ├── auth/                            # authentication pipeline
    │   ├── base.py                      # BaseAuthService
    │   ├── command.py                   # GetIdentityProvidersCommand
    │   ├── idp_client.py                # IdpClient (abstract)
    │   ├── literal.py                   # type literals
    │   ├── mock_idp_client.py           # MockIDPClient (no-auth)
    │   ├── model.py                     # Claims, IdentityProvider, IDPUser, OidcServerCfg
    │   ├── oauth_idp_client.py          # OauthIdpClient (real OIDC)
    │   ├── service.py                   # AuthService (concrete)
    │   ├── token_introspection_manager.py
    │   └── util.py
    ├── rbac/                            # role-based access control
    │   ├── policy.py                    # RbacPolicy
    │   └── service.py                   # BaseRbacService
    └── remote/                          # cross-service HTTP calls
        └── service.py                   # BaseRemoteService
```

---

## Layered responsibilities

```
HTTP request
    │
    ▼
FastAPI route  ──►  CrudEndpointGenerator builds these at startup
    │
    ▼
Command object  ──►  CrudCommand (or custom Command subclass)
    │
    ▼
App.handle()  ──►  dispatcher + Policy Enforcement Point (PEP)
    │                   ├─ BEFORE policies  (RBAC, outage checks …)
    │                   ├─ DURING policies  (attach filter policies)
    │                   └─ AFTER  policies  (result filtering)
    │
    ▼
Handler  ──►  registered by a BaseService subclass
    │           └─ default: service.crud()
    │
    ▼
BaseRepository  ──►  DictRepository  or  SARepository
    │                  (chosen at startup via config)
    │
    ▼
Database  (in-memory dict  or  SQL via SQLAlchemy)
```

---

## 1. Domain metadata layer (`domain/`)

This sub-package is a pure metadata registry.  No I/O or business logic lives here.

### Entity

`Entity` is the central descriptor for a persistable model.  Every Pydantic model
that maps to a database table carries one as a `ClassVar`:

```python
class MyModel(Model):
    ENTITY: ClassVar = Entity(
        table_name="my_table",
        keys=create_keys({"name_key": ("name",)}),
        links=create_links({"organization": Link("organization_id", Organization)}),
    )
```

When the model class is registered with the `Domain`, `Entity` introspects all
fields and classifies each one:

| FieldType | Meaning |
|-----------|---------|
| `ID` | Primary-key field (`id`) |
| `LINK` | Foreign-key ID field (e.g. `organization_id`) |
| `RELATIONSHIP` | Optional back-populated object (e.g. `organization: Organization \| None`) |
| `VALUE` | Regular data field |
| `COMPUTED` | Derived / read-only field |
| `SERVICE_METADATA` | Framework-managed metadata (e.g. created_by) |
| `DB_METADATA` | Database-managed metadata (e.g. row_version) |

### Key

A `Key` represents a unique constraint.  It stores a tuple of field names and a
callable `key_generator` that extracts the composite key value from a model
instance.  Used by `DictRepository` to enforce uniqueness in memory.

### Link

A `Link` binds a foreign-key field (`link_field_name`) to the target model class
(`link_model_class`) and optionally names the back-populated relationship field.
The repository layer uses links to validate referential integrity and to
cascade-load related objects.

### Domain (registry)

`Domain` is the single source of truth for the relationship graph.  It tracks:

| What | How it is stored |
|------|------------------|
| Service types → entities | `_entities_by_service_type` |
| Model class → Entity | `_entity_by_model_class` |
| Model class → CrudCommand class | `_crud_command_by_model_class` |
| Command class → Permission set | derived at register time |
| Entity dependency order | DAG sorted by Link edges |

Every `App` owns exactly one `Domain`.  Services and repositories query it during
startup and at runtime.

---

## 2. Model layer (`model.py`)

All domain objects in the project inherit from classes defined here.

### Model

Thin Pydantic `BaseModel` subclass.  Adds the optional `ENTITY` class-var slot
that links the model to its metadata.  Every persistable entity across all four
apps ultimately inherits from this (or from a per-app intermediate like
`commondb.Model` which adds an `id` field).

### User

Represents the authenticated caller.  Carries a hashable `id` and a `get_key()`
method (returns email by default) used for cross-system identity matching.

### Command / CrudCommand

`Command` is the base unit of work.  Every mutation and non-trivial read is
represented as a command object.

`CrudCommand` is the generic specialisation for standard CRUD.  Its `operation`
field (a `CrudOperation` enum value) plus `objs` / `obj_ids` / `query_filter`
fields fully describe what the repository should do.  A `@model_validator` ensures
the combination is consistent (e.g. `CREATE_ONE` requires exactly one object).

`UpdateAssociationCommand` handles many-to-many join tables by replacing the full
set of rows atomically.

### Permission

A frozen (hashable) `(command_name, permission_type)` pair.  The set of permissions
a command requires is computed once at registration time from its
`PERMISSION_TYPE_SET` class-var.

### Policy

Abstract base for all authorization and filtering rules.  Three hooks match the
three timing stages used by `App.handle()`:

| Method | Timing | Purpose |
|--------|--------|---------|
| `is_allowed(cmd)` | BEFORE | Return `False` to deny the command outright |
| `get_content(cmd)` | DURING | Attach runtime state (e.g. an access filter) to the command |
| `filter(cmd, retval)` | AFTER | Rewrite the return value (e.g. strip rows the user may not see) |

### Role

A named set of `Permission` objects.  Roles are registered with `BaseRbacService`
and form a hierarchy (see commondb `DOMAIN.md` for the concrete tree).

---

## 3. App — the command dispatcher (`app.py`)

`App` is the mediator that every service, repository, and policy plugs into.  It
owns a `Domain`, a `PolicyDecisionPoint`, and a registry of command → handler
mappings.

### Registering with the App

Services call these methods during initialisation:

```
app.register_command(CommandClass)          # tell Domain about the command
app.register_handler(CommandClass, fn)      # wire command → handler function
app.register_policy(CommandClass, policy, timing)  # attach a policy
```

### Executing a command — `App.handle(cmd)`

```
1.  Push cmd onto the internal command stack
2.  BEFORE policies   → pdp.apply(cmd, BEFORE)
      • Each policy's is_allowed() is checked.
      • First denial raises the policy's exception (typically UnauthorizedAuthError).
3.  Resolve handler   → app._handler_by_command[type(cmd)]
4.  DURING policies   → pdp.apply(cmd, DURING)
      • Policies' get_content() results are attached to cmd._policies.
5.  Call handler       → retval = handler(cmd)
6.  AFTER policies    → pdp.apply(cmd, AFTER, retval)
      • Each policy's filter() can transform retval (e.g. mask rows).
7.  Pop cmd from the stack
8.  Return retval
```

All exceptions are caught, logged with an 8-character hex error code, and
re-raised (or converted to an HTTP exception by the endpoint layer).

### RemoteApp (`remote_app.py`)

`RemoteApp` extends `App` for cross-service communication.  Instead of calling a
local handler, it sends an HTTP request to another Gen-EpiX instance.  It has no
policies — authorisation is the responsibility of the receiving service.  Used by
`casedb` to call `seqdb` for phylogenetic-tree data.

---

## 4. PolicyDecisionPoint (`pdp.py`)

`PolicyDecisionPoint` is the sole owner of the policy registry.  It is the only
place policies are stored, looked up, and applied.  `App` delegates all policy
operations to it.

Policies are keyed by `(command_class, EventTiming)`.  Multiple policies can be
registered for the same key; they are evaluated in order.

---

## 5. Service layer (`service.py`)

`BaseService` is the abstract base for every business-logic service in the project.
Each concrete service (e.g. `OrganizationService`) lives in the app's `services/`
directory.

Key responsibilities:

- **Register handlers.**  `register_handlers()` is called once at startup.  The
  default implementation calls `register_default_crud_handlers()`, which wires the
  generic `service.crud()` method as the handler for all CRUD operations on every
  entity the service owns.
- **Default CRUD handler.**  `crud(cmd)` opens a Unit of Work, delegates to the
  repository, and optionally cascade-reads linked objects from other services.
- **Association updates.**  `update_association()` replaces join-table rows
  atomically inside a single UoW.

### Specialised service bases

| Class | Location | Role |
|-------|----------|------|
| `BaseRbacService` | `services/rbac/service.py` | Manages the role → permission mapping and sub-role hierarchy |
| `BaseAuthService` | `services/auth/base.py` | Registers the `GetIdentityProvidersCommand` handler |
| `AuthService` | `services/auth/service.py` | Concrete auth: validates JWTs, creates user dependencies for FastAPI |
| `BaseRemoteService` | `services/remote/service.py` | Base for services that talk to another Gen-EpiX app over HTTP |

---

## 6. Repository layer

### Abstract interface (`repository.py`)

`BaseRepository` defines the contract every backend must honour:

| Method | What it does |
|--------|--------------|
| `crud(uow, …)` | Generic CRUD dispatcher keyed on `CrudOperation` |
| `read_fields(uow, …)` | Read only specific columns |
| `split_filter(model_class, filter)` | Partition a composite filter into a *db* part (pushed to SQL) and a *service* part (applied in Python) |
| `update_association(uow, …)` | Replace all rows in a join table for a given parent |

All methods receive a `BaseUnitOfWork` as their first argument.

### DictRepository (`repositories/dict/`)

In-memory storage backed by nested dicts: `_db[ModelClass][id] = instance`.

- Loaded at startup from a `.pkl` / `.pkl.gz` snapshot or a `.zip` of JSON files.
- Enforces unique keys and foreign-key constraints in Python.
- `DictUnitOfWork` is a no-op (commit and rollback do nothing) — changes are
  visible immediately.  Suitable only for dev / testing.

### SARepository (`repositories/sa/`)

Production backend built on SQLAlchemy Core (not ORM sessions in the traditional
sense).

- `EngineFactory` caches engines by connection string, so multiple services sharing
  the same database reuse the same pool.
- `SAMapper` handles the translation between Pydantic models and SQLAlchemy `Row`
  objects.  Custom field-name mappings and service-/db-metadata generation hooks are
  supported.
- `SAUnitOfWork` wraps a real `Session`.  On exception it converts
  `IntegrityError` into the appropriate domain exception
  (`UniqueConstraintViolationError`, `LinkConstraintViolationError`, etc.) before
  re-raising.
- `repositories/sa/util.py` maps Python / Pydantic types to SQLAlchemy column
  types automatically (including dialect-specific UTC timestamp handling).

### Unit of Work (`unit_of_work.py`)

`BaseUnitOfWork` is a context-manager that guarantees commit-on-success /
rollback-on-exception semantics.  Both `DictUnitOfWork` and `SAUnitOfWork`
implement this interface.

---

## 7. Authentication (`services/auth/`)

### IdpClient hierarchy

| Class | When it is used |
|-------|-----------------|
| `IdpClient` (ABC) | — |
| `OauthIdpClient` | Real OIDC identity provider; fetches JWKS from the discovery URL and validates JWT signatures |
| `MockIDPClient` | Development / CI; bypasses real token validation entirely |

### AuthService

The concrete service that orchestrates authentication end-to-end:

1. An HTTP request arrives with a bearer token.
2. `AuthService` tries each registered `IdpClient` in order until one validates
   the token and produces a `Claims` object.
3. The `Claims` are handed to `BaseUserManager.get_user_instance_from_claims()`,
   which looks up (or creates) the internal `User`.
4. The `User` is injected into the FastAPI route as a dependency.

`AuthService.create_user_dependencies()` dynamically generates the FastAPI
dependency functions (`get_current_user`, `get_new_user`, `get_idp_user`) based on
how many identity providers are configured.

### UserManager (`user_manager.py`)

`BaseUserManager` is the bridge between IdP claims and internal `User` objects.
Concrete implementations live in each app's `services/` directory.  Key
responsibilities:

- Map the IdP claim identified by `key_claim` (typically email) to the internal
  user `key`.
- Determine whether the user is a *root* user (bootstrapped from config).
- Retrieve or create `User` records.
- Expose `retrieve_user_permissions()` so that RBAC can check authorisation.

---

## 8. RBAC (`services/rbac/`)

### BaseRbacService

Maintains the live role → permission mapping.  At startup each app registers its
role hierarchy via `register_role()`.  The service pre-computes:

- `roles_by_permission` — which roles grant a given permission.
- `sub_roles_by_role` — transitive closure down the hierarchy.
- `permissions_without_rbac` — permissions that bypass role checks entirely.

### RbacPolicy

A `Policy` subclass registered in the BEFORE timing on every command.  Its
`is_allowed()` logic:

1. Derive the permission the command requires.
2. If the permission is in `permissions_without_rbac`, allow unconditionally.
3. Otherwise check whether the user holds any role that grants the permission.
4. Optionally check root-user status as a last resort.

---

## 9. CRUD endpoint generation (`api/`)

`CrudEndpointGenerator` is a class full of static methods, each of which returns a
fully-formed async FastAPI route function.  It is called once per entity at startup.

`CrudEndpointSet` is the configuration object that drives generation:

| Field | Purpose |
|-------|---------|
| `model_class` | The domain model |
| `crud_command_class` | Command class to instantiate |
| `endpoint_basename` | URL path segment (e.g. `"organization"`) |
| `endpoint_types` | Which of the 12 endpoint types to expose |
| `user_dependency` | FastAPI `Depends()` that supplies the authenticated user |
| `query_filter_validator` | Optional callable to validate / rewrite query filters |

The generated endpoints:
- use the 8-character error-code convention for structured logging,
- call `app.handle(cmd)` as their single business-logic step, and
- automatically convert domain exceptions to the appropriate HTTP status codes
  via the typed exceptions in `api/exc.py`.

---

## 10. Middleware

| Middleware | What it does |
|-----------|--------------|
| `HandleAuthExceptionMiddleware` | Catches `AuthException` (including nested exception groups) and returns a 401 JSON response |
| `HandleNoResponseMiddleware` | Detects client disconnects (RuntimeError "No response returned") and returns 204 |
| `UpdateResponseHeaderMiddleware` | Adds an `X-API-Version` header (from `version.txt`) and any app-specific headers |
| Rate limiter (`limiter.py`) | 10 requests / second per bearer token (falls back to IP).  Built on `slowapi` |

---

## 11. Enumerations and exceptions

### Key enumerations (`enum.py`)

| Enum | Notable values |
|------|----------------|
| `PermissionType` | CREATE, READ, UPDATE, DELETE, EXECUTE |
| `CrudOperation` | 20 variants: CREATE_ONE, READ_ALL, UPSERT_SOME, DELETE_ALL … |
| `CrudEndpointType` | 12 HTTP endpoint shapes (POST_ONE, GET_ALL, POST_QUERY …) |
| `FieldType` / `FieldTypeSet` | ID, LINK, VALUE, COMPUTED, RELATIONSHIP … |
| `IsolationLevel` | Maps to SQL isolation levels for SAUnitOfWork |
| `AuthProtocol` | NONE, OAUTH2, OIDC |
| `HttpProtocol` | HTTP, HTTPS — used by RemoteApp |

### Exception hierarchy (`exc.py`)

```
DomainException
├── DataException                        (carries `ids`)
│   ├── InvalidArgumentsError
│   ├── IdsError / InvalidIdsError / DuplicateIdsError
│   ├── InvalidModelIdsError / InvalidLinkIdsError / AlreadyExistingIdsError
│   ├── LinkConstraintViolationError     (carries `linked_ids`)
│   ├── UniqueConstraintViolationError   (carries `duplicate_key_ids`)
│   ├── NotNullConstraintViolationError  (carries `column_names`)
│   └── NoResultsError
└── ServiceException                     (carries `http_props` for status code)
    ├── InitializationServiceError
    ├── RepositoryServiceError
    ├── AuthException
    │   ├── CredentialsAuthError         (401)
    │   ├── UnauthorizedAuthError        (403)
    │   ├── UserNotFoundAuthError        (404)
    │   └── UserAlreadyExistsAuthError   (409)
    ├── ServiceUnavailableError          (503)
    └── RequestLimitExceededAuthError    (429)
```

`SAUnitOfWork` catches SQLAlchemy `IntegrityError` and converts it into the
correct `DataException` subclass before it propagates.

---

## 12. Initialisation sequence

The sketch below shows the order in which the pieces wire together when an app
starts.  Each app's `env.py` orchestrates this via an `AppComposer`.

```
1.  Create Domain
2.  Create App (owns Domain + PolicyDecisionPoint)
3.  Create Repository (Dict or SA, depending on config)
4.  Create each Service, injecting App + Repository
        └─ service.__init__  →  register_handlers()
               ├─ app.register_command(…)
               ├─ app.register_handler(…)
               └─ app.register_policy(…)
5.  Create AuthService
        └─ load IdpClients from config
        └─ create FastAPI user-dependency functions
6.  Create UserManager, injecting App
7.  Build FastAPI application
        ├─ add middleware
        ├─ include routers  →  CrudEndpointGenerator produces routes
        └─ mount OpenAPI schema overrides
8.  Uvicorn starts serving
```

---

## 13. How the pieces fit together — a worked example

A `GET /v1/organization` request against `commondb`:

| # | What happens | Where |
|---|--------------|-------|
| 1 | FastAPI matches the route | Generated by `CrudEndpointGenerator.generate_get_all()` |
| 2 | `get_current_user` dependency runs | Created by `AuthService.create_user_dependencies()` |
| 3 | JWT is validated by `OauthIdpClient` | `services/auth/oauth_idp_client.py` |
| 4 | `UserManager` resolves claims → `User` | App-specific `user_manager.py` |
| 5 | Endpoint creates `OrganizationCrudCommand(operation=READ_ALL, user=…)` | Route function body |
| 6 | `app.handle(cmd)` is called | `app.py` |
| 7 | BEFORE: `RbacPolicy.is_allowed()` checks the user's roles | `services/rbac/policy.py` |
| 8 | DURING: `ReadOrganizationResultsOnlyPolicy` attaches an access filter | Per-app policy |
| 9 | Handler `service.crud(cmd)` runs | `service.py` |
| 10 | `DictRepository.crud()` or `SARepository.crud()` executes the read | Chosen repository |
| 11 | AFTER: the access filter strips rows outside the user's org | Per-app policy |
| 12 | Result is returned as JSON | FastAPI serialisation |