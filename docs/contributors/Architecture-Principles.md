# Architecture Principles

## 1. Layer Boundaries

### Evidenced in Repository
- HTTP shell is assembled in `create_fast_api(...)`: middleware, router mounting, and root redirect are all configured there. (Source: `gen_epix/commondb/app_setup.py#L27-L35`; Source: `gen_epix/commondb/app_setup.py#L74-L126`)
- Endpoint functions mostly translate HTTP calls to commands and invoke `app.handle(cmd)`. (Source: `gen_epix/commondb/api/auth.py#L24-L36`; Source: `gen_epix/commondb/api/system.py#L82-L90`)
- Services execute command behavior and call repositories through unit-of-work patterns. (Source: `gen_epix/fastapp/service.py#L184-L240`; Source: `gen_epix/fastapp/service.py#L302-L375`)

### Inferred from Code Structure
- This separation keeps HTTP transport concerns in API/setup files and execution/data logic in service/repository layers. (Source: `gen_epix/commondb/app_setup.py#L27-L35`; Source: `gen_epix/commondb/api/system.py#L82-L90`; Source: `gen_epix/fastapp/service.py#L184-L240`)

## 2. Command-Based Execution Model

### Evidenced in Repository
- `App.handle(...)` is the command execution entrypoint and is used by endpoints and services. (Source: `gen_epix/fastapp/app.py#L309-L327`; Source: `gen_epix/commondb/api/auth.py#L32-L34`; Source: `gen_epix/fastapp/service.py#L507-L517`)
- Commands and permissions are registered in the domain model, including CRUD command wiring. (Source: `gen_epix/fastapp/domain/domain.py#L658-L721`; Source: `gen_epix/fastapp/domain/domain.py#L72-L85`)

### Inferred from Code Structure
- The command object is the stable integration surface across transport, policy, and service execution. (Source: `gen_epix/commondb/api/auth.py#L32-L34`; Source: `gen_epix/fastapp/app.py#L309-L327`; Source: `gen_epix/fastapp/service.py#L507-L517`)

## 3. Policy Enforcement Timing: BEFORE / DURING / AFTER

### Evidenced in Repository
- The PDP defines three timings and behavior. (Source: `gen_epix/fastapp/pdp.py#L12-L17`; Source: `gen_epix/fastapp/pdp.py#L85-L112`)
  - `BEFORE`: deny/allow gate
  - `DURING`: inject policies into command context
  - `AFTER`: filter/transform return value
- `App.handle` applies these phases for initial commands. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`; Source: `gen_epix/fastapp/app.py#L417-L429`)

### Inferred from Code Structure
- Centralized policy timing reduces route-level authorization drift. (Source: `gen_epix/fastapp/pdp.py#L12-L17`; Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`)

## 4. Authentication vs Authorization Separation

### Evidenced in Repository
- Authentication dependencies are created by `AuthService` and injected into endpoints. (Source: `gen_epix/fastapp/services/auth/service.py#L84-L91`; Source: `gen_epix/commondb/env.py#L163-L168`)
- Authorization decisions are enforced by command policies in `App.handle`/PDP. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L406-L419`; Source: `gen_epix/fastapp/pdp.py#L97-L112`)

### Inferred from Code Structure
- Passing dependency-based authentication does not by itself grant command authorization. (Source: `gen_epix/fastapp/services/auth/service.py#L84-L91`; Source: `gen_epix/fastapp/app.py#L406-L419`)

## 5. OIDC-Only Identity Provider Support

### Evidenced in Repository
- `AuthService._init_idp_client` initializes `OauthIdpClient` only when `protocol == OIDC`; other protocols raise `NotImplementedError`. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L694`)
- Auth protocol enum includes values beyond OIDC, but implementation path is explicitly constrained as above. (Source: `gen_epix/fastapp/enum.py#L285-L289`)

### Inferred from Code Structure
- Non-OIDC provider onboarding requires code changes, not config-only changes. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L694`; Source: `gen_epix/fastapp/enum.py#L285-L289`)

## 6. Root Fallback and No-IDP Implications

### Evidenced in Repository
- If no IDP clients are configured, auth dependencies switch to `_create_no_auth_dependencies()`. (Source: `gen_epix/fastapp/services/auth/service.py#L88-L90`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L424`)
- No-IDP mode is a real config path (`config/no_identity_providers.toml`). (Source: `config/no_identity_providers.toml#L1-L1`; Source: `gen_epix/commondb/domain/util.py#L83-L85`)
- Root user creation and root role assignment are implemented in user manager and RBAC policy checks. (Source: `gen_epix/commondb/services/user_manager.py#L46-L59`; Source: `gen_epix/commondb/services/user_manager.py#L125-L178`; Source: `gen_epix/fastapp/services/rbac/policy.py#L51-L66`)

### Inferred from Code Structure
- Running with no configured IDP materially changes trust posture and should be treated as a constrained mode. (Source: `gen_epix/fastapp/services/auth/service.py#L88-L90`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L424`; Source: `gen_epix/commondb/services/user_manager.py#L125-L178`)

## Evidence Sources
- `gen_epix/commondb/app_setup.py#L27-L35`
- `gen_epix/commondb/app_setup.py#L74-L126`
- `gen_epix/commondb/api/auth.py#L24-L36`
- `gen_epix/commondb/api/system.py#L82-L90`
- `gen_epix/commondb/env.py#L163-L168`
- `gen_epix/fastapp/app.py#L309-L327`
- `gen_epix/fastapp/app.py#L314-L320`
- `gen_epix/fastapp/app.py#L347-L360`
- `gen_epix/fastapp/app.py#L406-L429`
- `gen_epix/fastapp/pdp.py#L12-L17`
- `gen_epix/fastapp/pdp.py#L85-L112`
- `gen_epix/fastapp/domain/domain.py#L72-L85`
- `gen_epix/fastapp/domain/domain.py#L658-L721`
- `gen_epix/fastapp/service.py#L184-L240`
- `gen_epix/fastapp/service.py#L302-L375`
- `gen_epix/fastapp/service.py#L507-L517`
- `gen_epix/fastapp/services/auth/service.py#L84-L91`
- `gen_epix/fastapp/services/auth/service.py#L376-L424`
- `gen_epix/fastapp/services/auth/service.py#L675-L694`
- `gen_epix/fastapp/services/rbac/policy.py#L51-L66`
- `gen_epix/fastapp/enum.py#L285-L289`
- `gen_epix/commondb/domain/util.py#L83-L85`
- `gen_epix/commondb/services/user_manager.py#L46-L59`
- `gen_epix/commondb/services/user_manager.py#L125-L178`
- `config/no_identity_providers.toml#L1-L1`
