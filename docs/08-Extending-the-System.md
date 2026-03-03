Creation Date: March 1, 2026

# Extending the System

This chapter documents the five primary extension patterns evidenced in the codebase. Each pattern includes the observable wiring steps and source references.

For a full worked example of app assembly, see [08a-App-Composition-Walkthrough](./08a-App-Composition-Walkthrough.md).

---

## 1. Add a New Module/Service

### Evidenced in Repository

- Service and repository classes are loaded from settings (`module` + `class_name`) during app config validation. (Source: `gen_epix/commondb/config/cfg.py#L235-L263`)
- App composition iterates service types, creates repository instances, then service instances. (Source: `gen_epix/commondb/env.py#L126-L137`; Source: `gen_epix/commondb/env.py#L245-L295`)
- Service types are defined as enums per app domain. (Source: `gen_epix/casedb/domain/enum.py#L9-L20`; Source: `gen_epix/seqdb/domain/enum.py#L23-L31`; Source: `gen_epix/omopdb/domain/enum.py#L23-L30`)
- Domain entities/commands are registered through `register_domain_entities(...)` using sorted service/model/command maps. (Source: `gen_epix/casedb/domain/__init__.py#L12-L20`; Source: `gen_epix/seqdb/domain/__init__.py#L12-L20`; Source: `gen_epix/commondb/domain/__init__.py#L11-L17`)

### Observable Extension Pattern

1. Add service type enum entry.
2. Add domain command/model mappings for that service type.
3. Add settings entries for service and repository class resolution.
4. Implement service class and handler registrations.
5. Add router wiring if HTTP exposure is needed.

(Source: `gen_epix/casedb/domain/enum.py#L9-L20`; Source: `gen_epix/commondb/domain/command/__init__.py#L106-L158`; Source: `gen_epix/commondb/config/cfg.py#L235-L263`; Source: `gen_epix/commondb/domain/service/system.py#L17-L21`; Source: `gen_epix/commondb/api/router.py#L23-L48`)

A formal maintainer-approved checklist is not documented: `<TBF elsewhere>`.

---

## 2. Add a New Command

### Evidenced in Repository

- Commands are defined as subclasses of `Command`/`CrudCommand`. (Source: `gen_epix/commondb/domain/command/base.py#L18-L46`)
- Commands are assigned to service types in `COMMANDS_BY_SERVICE_TYPE`. (Source: `gen_epix/commondb/domain/command/__init__.py#L106-L158`; Source: `gen_epix/casedb/domain/command/__init__.py#L248-L337`)
- Services bind command classes to handlers with `app.register_handler(...)`. (Source: `gen_epix/commondb/domain/service/system.py#L17-L21`; Source: `gen_epix/casedb/domain/service/case.py#L129-L187`; Source: `gen_epix/seqdb/domain/service/seq.py#L13-L36`)
- Domain registration creates command permissions from `PERMISSION_TYPE_SET`. (Source: `gen_epix/fastapp/domain/domain.py#L72-L85`; Source: `gen_epix/fastapp/domain/domain.py#L658-L676`)

### Observable Wiring

For non-CRUD commands, the minimum observed wiring is:
1. Command class definition (subclass of `Command`).
2. Inclusion in `COMMANDS_BY_SERVICE_TYPE`.
3. Service handler registration (`app.register_handler(...)`).
4. Optional endpoint exposure.

(Source: `gen_epix/commondb/domain/command/base.py#L18-L46`; Source: `gen_epix/commondb/domain/command/__init__.py#L106-L158`; Source: `gen_epix/commondb/domain/service/system.py#L17-L21`; Source: `gen_epix/commondb/api/system.py#L60-L141`)

---

## 3. Register New RBAC Rules

### Evidenced in Repository

- RBAC permissions are declared in `RoleGenerator.ROLE_PERMISSION_SETS` and `ROLE_HIERARCHY`, then expanded to `ROLE_PERMISSIONS`. (Source: `gen_epix/commondb/domain/policy/permission.py#L35-L139`)
- Domain-specific apps extend the common role generator and add app-specific command permissions. (Source: `gen_epix/casedb/domain/policy/permission.py#L15-L27`; Source: `gen_epix/seqdb/domain/policy/permission.py#L21-L33`; Source: `gen_epix/omopdb/domain/policy/permission.py#L20-L27`)
- Composition registers roles and RBAC policies during startup. (Source: `gen_epix/commondb/env.py#L147-L150`; Source: `gen_epix/commondb/env.py#L175-L177`; Source: `gen_epix/fastapp/services/rbac/service.py#L327-L375`)
- No-RBAC exceptions are explicit via `NO_RBAC_PERMISSIONS`. (Source: `gen_epix/commondb/domain/policy/permission.py#L10-L26`)

### Key Insight

Adding a new RBAC rule is primarily a `RoleGenerator` change. No separate declarative RBAC config file is evidenced; the permission model is code-driven.

---

## 4. Add New Endpoints (Router Pattern)

### Evidenced in Repository

- Each app router is built from `router_data` entries (`name`, `create_endpoints_fn`, optional kwargs). (Source: `gen_epix/commondb/api/router.py#L23-L48`; Source: `gen_epix/casedb/api/router.py#L26-L72`; Source: `gen_epix/seqdb/api/router.py#L26-L64`)
- Endpoint modules combine explicit routes with generated CRUD families. (Source: `gen_epix/commondb/api/auth.py#L24-L46`; Source: `gen_epix/commondb/api/system.py#L60-L141`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L54-L58`; Source: `gen_epix/fastapp/api/crud_endpoint_generator.py#L702-L757`)
- All routers are mounted under `/v1` by shared setup. (Source: `gen_epix/commondb/app_setup.py#L119-L120`)

### Observable Path

1. Create `create_<domain>_endpoints(...)` function.
2. Add entry to `router_data` list.
3. Routes are auto-mounted under `/v1`.

---

## 5. Add New IDP Configuration

### Evidenced in Repository

- IDP entries use `[[service.auth.props.idps_cfg]]` structures in config files. (Source: `config/identity_providers.toml#L1-L34`; Source: `config/mock_identity_provider.toml#L1-L16`)
- Local mode selection maps `IDPS`, `MOCK`, `NONE` to concrete files. (Source: `gen_epix/commondb/domain/util.py#L78-L85`)
- `protocol` is read from each IDP config entry during auth client initialization; OIDC server config includes fields such as `name`, `label`, and `claim_map`. (Source: `config/identity_providers.toml#L1-L4`; Source: `gen_epix/fastapp/services/auth/service.py#L675-L684`; Source: `gen_epix/fastapp/services/auth/model.py#L100-L112`)
- Auth initialization supports OIDC only; non-OIDC raises `NotImplementedError`. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L694`)
- Duplicate IDP `name`/`label` values are rejected. (Source: `gen_epix/fastapp/services/auth/service.py#L753-L775`)
- Security dependency generation is capped at five IDP bases. (Source: `gen_epix/fastapp/services/auth/service.py#L346-L366`; Source: `gen_epix/fastapp/services/auth/service.py#L442-L449`)

### Constraints

- Adding more than five active IDPs requires code changes in auth dependency generation.
- Production IDP secret governance and operational rollout process are not defined here: `<TBF elsewhere>`.

---

## Evidence Sources

- `gen_epix/commondb/config/cfg.py#L235-L263`
- `gen_epix/commondb/env.py#L126-L177`, `#L245-L295`
- `gen_epix/casedb/domain/enum.py#L9-L20`
- `gen_epix/seqdb/domain/enum.py#L23-L31`
- `gen_epix/omopdb/domain/enum.py#L23-L30`
- `gen_epix/commondb/domain/__init__.py#L11-L17`
- `gen_epix/casedb/domain/__init__.py#L12-L20`
- `gen_epix/seqdb/domain/__init__.py#L12-L20`
- `gen_epix/commondb/domain/command/base.py#L18-L46`
- `gen_epix/commondb/domain/command/__init__.py#L106-L158`
- `gen_epix/casedb/domain/command/__init__.py#L248-L337`
- `gen_epix/commondb/domain/service/system.py#L17-L21`
- `gen_epix/casedb/domain/service/case.py#L129-L187`
- `gen_epix/seqdb/domain/service/seq.py#L13-L36`
- `gen_epix/fastapp/domain/domain.py#L72-L85`, `#L658-L676`
- `gen_epix/commondb/domain/policy/permission.py#L10-L139`
- `gen_epix/casedb/domain/policy/permission.py#L15-L27`
- `gen_epix/seqdb/domain/policy/permission.py#L21-L33`
- `gen_epix/omopdb/domain/policy/permission.py#L20-L27`
- `gen_epix/fastapp/services/rbac/service.py#L327-L375`
- `gen_epix/commondb/api/router.py#L23-L48`
- `gen_epix/casedb/api/router.py#L26-L72`
- `gen_epix/seqdb/api/router.py#L26-L64`
- `gen_epix/commondb/api/auth.py#L24-L46`
- `gen_epix/commondb/api/system.py#L60-L141`
- `gen_epix/fastapp/api/crud_endpoint_generator.py#L54-L58`, `#L702-L757`
- `gen_epix/commondb/app_setup.py#L119-L120`
- `gen_epix/commondb/domain/util.py#L78-L85`
- `gen_epix/fastapp/services/auth/model.py#L100-L112`, `#L299-L317`
- `gen_epix/fastapp/services/auth/service.py#L346-L366`, `#L442-L449`, `#L675-L694`, `#L753-L775`
- `config/identity_providers.toml#L1-L34`
- `config/mock_identity_provider.toml#L1-L16`
