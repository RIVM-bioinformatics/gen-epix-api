Creation Date: February 16, 2026

# High-Level Architecture Deep Dive

## 1. System Architecture Overview
The system is built around a repeatable app composition pattern: each app module (`casedb`, `seqdb`, `omopdb`, `commondb`) creates `AppCfg`, composes runtime dependencies through `AppComposer`, then builds the FastAPI shell with shared setup logic. This gives a consistent control plane for services that have different domain routers. (Source: `gen_epix/casedb/app.py#L28-L45`; Source: `gen_epix/seqdb/app.py#L28-L45`; Source: `gen_epix/omopdb/app.py#L28-L45`; Source: `gen_epix/commondb/app.py#L26-L42`)

**The core architectural decision is command-centric execution.** Endpoints are transport adapters; commands are the execution unit, and policy enforcement happens in the command lifecycle. (Source: `gen_epix/commondb/api/auth.py#L30-L34`; Source: `gen_epix/fastapp/app.py#L309-L327`; Source: `gen_epix/fastapp/app.py#L314-L360`)

```text
Process/bootstrap
  -> AppCfg (logging + settings)
  -> AppComposer (repositories + services + policies + user dependencies)
  -> create_fast_api (middleware + routers + /v1 mount)
  -> endpoint function
  -> app.handle(command)
  -> policy phases: BEFORE / DURING / AFTER
```
(Source: `gen_epix/commondb/config/cfg.py#L155-L177`; Source: `gen_epix/commondb/env.py#L103-L177`; Source: `gen_epix/commondb/app_setup.py#L74-L126`; Source: `gen_epix/fastapp/app.py#L314-L360`)

## 2. Composition Boundaries and Responsibilities
Composition is the boundary where runtime authority is established. `AppComposer` creates role maps, service/repository instances, user manager dependencies, and registers system/RBAC/ABAC policies before the API starts handling business requests. (Source: `gen_epix/commondb/env.py#L73-L85`; Source: `gen_epix/commondb/env.py#L147-L177`; Source: `gen_epix/commondb/env.py#L198-L205`)

FastAPI assembly is centralized in `create_fast_api`, which applies middleware, mounts routers under `/v1`, and defines root redirect behavior. This keeps HTTP-level behavior uniform across all app variants. (Source: `gen_epix/commondb/app_setup.py#L27-L35`; Source: `gen_epix/commondb/app_setup.py#L74-L109`; Source: `gen_epix/commondb/app_setup.py#L119-L126`)

Router boundaries are app-specific but follow the same pattern: shared common routers plus app-domain routers (`case`, `seq/file`, `omop`). (Source: `gen_epix/commondb/api/router.py#L23-L48`; Source: `gen_epix/casedb/api/router.py#L26-L72`; Source: `gen_epix/seqdb/api/router.py#L26-L64`; Source: `gen_epix/omopdb/api/router.py#L25-L55`)

Developer Note: this separation is why endpoint modules stay thin while composition modules carry most of the architectural complexity. (Source: `gen_epix/commondb/api/system.py#L47-L58`; Source: `gen_epix/commondb/env.py#L97-L177`)

## 3. Boot and Request Lifecycle
Local bootstrap is controlled by `run.py`: it maps app type to import URI/host/port, sets environment-driven settings stack, then runs uvicorn (with optional TLS files if present). (Source: `run.py#L17-L38`; Source: `run.py#L82-L107`; Source: `gen_epix/commondb/util.py#L74-L119`)

Configuration load is staged: logging config is loaded from `<APP>_LOG_CONFIG_FILE`, then settings are loaded via `SettingsManager` from `<APP>_SETTINGS_FILES`, then service/repository classes/defaults are resolved. (Source: `gen_epix/commondb/config/cfg.py#L188-L215`; Source: `gen_epix/commondb/config/settings_manager.py#L43-L77`; Source: `gen_epix/commondb/config/cfg.py#L218-L269`)

Request execution follows command handling with three policy enforcement points:
1. `BEFORE`: authorization gate
2. `DURING`: inject policies for handler use
3. `AFTER`: transform/filter returned data
(Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`; Source: `gen_epix/fastapp/app.py#L406-L418`)

## 4. Configuration Model
Per-app `settings.toml` files define runtime host/port/debug, API defaults, and route prefix. The same structural keys are used across app variants. (Source: `gen_epix/casedb/config/settings.toml#L1-L4`; Source: `gen_epix/seqdb/config/settings.toml#L1-L4`; Source: `gen_epix/omopdb/config/settings.toml#L1-L4`; Source: `gen_epix/commondb/config/settings.toml#L1-L4`; Source: `gen_epix/commondb/config/settings.toml#L42-L43`)

Repository implementation is configuration-driven by module/class mapping, and runtime repository type handling is bounded to `DICT`, `SA_SQLITE`, and `SA_SQL`. (Source: `gen_epix/casedb/config/settings.repository.dict.toml#L1-L27`; Source: `gen_epix/casedb/config/settings.repository.sa.toml#L1-L27`; Source: `gen_epix/seqdb/config/settings.repository.sa.toml#L1-L19`; Source: `gen_epix/omopdb/config/settings.repository.sa.toml#L1-L15`; Source: `gen_epix/commondb/base_env.py#L66-L93`)

Environment override behavior is explicit: settings files are stacked via env vars and Dynaconf supports nested key overrides using `__`. (Source: `gen_epix/commondb/util.py#L114-L119`; Source: `gen_epix/commondb/config/settings_manager.py#L15-L17`; Source: `gen_epix/commondb/config/settings_manager.py#L71-L77`)

## 5. Runtime Risk Modes and Design Tradeoffs
Some runtime behaviors are intentional flexibility points with operational implications.

1. Middleware hardening (rate limit, gzip, auth exception handling, response headers) is disabled when `debug=True`.
Operational implication: debug mode changes HTTP protection posture. (Source: `gen_epix/commondb/app_setup.py#L75-L109`; Source: `gen_epix/casedb/config/settings.toml#L4-L4`)

2. Repository type support is deliberately finite.
Operational implication: unsupported repository modes fail at composition time (`NotImplementedError`) rather than silently degrading. (Source: `gen_epix/commondb/base_env.py#L66-L93`)

3. `SEQDB` router data includes `file` twice.
Operational implication: duplicate registration attempts are possible and should be treated as a guardrail issue in router maintenance. (Source: `gen_epix/seqdb/api/router.py#L57-L63`)

4. `CASEDB` environment setup also triggers `SEQDB` environment setup.
Operational implication: local/runtime configuration changes for casedb can implicitly alter seqdb settings context. (Source: `gen_epix/commondb/util.py#L61-L64`)

Security Note: command-level authorization remains active regardless of router shape, so transport expansion does not automatically imply permission expansion. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L406-L418`)

## 6. Operational Interpretation
Operators should reason about architecture in three stages: configuration loading, composition/startup, and request execution. Most incidents can be localized quickly by identifying the failing stage first. (Source: `gen_epix/commondb/config/settings_manager.py#L58-L67`; Source: `gen_epix/commondb/env.py#L185-L197`; Source: `gen_epix/fastapp/app.py#L366-L387`)

When startup fails, `AppComposer` prints traceback and logs setup failure before re-raising, which means deployment logs should show composition-stage failures explicitly. (Source: `gen_epix/commondb/env.py#L185-L197`)

Developer Note: because routers are mounted through one shared function, cross-app HTTP behavior changes should usually be made in `app_setup.py` rather than app-specific router modules. (Source: `gen_epix/casedb/app.py#L33-L39`; Source: `gen_epix/seqdb/app.py#L33-L39`; Source: `gen_epix/omopdb/app.py#L33-L40`; Source: `gen_epix/commondb/app.py#L31-L37`; Source: `gen_epix/commondb/app_setup.py#L27-L35`)

## 7. Constraints & Guardrails
1. Repository creation is hard-coded to `DICT`, `SA_SQLITE`, or `SA_SQL`. (Source: `gen_epix/commondb/base_env.py#L66-L93`)
2. The API root route is always redirect-driven through shared setup logic. (Source: `gen_epix/commondb/app_setup.py#L123-L126`)
3. Policy enforcement for user-initiated command execution is centralized in `App.handle` lifecycle hooks. (Source: `gen_epix/fastapp/app.py#L314-L320`; Source: `gen_epix/fastapp/app.py#L347-L360`; Source: `gen_epix/fastapp/app.py#L406-L418`)

## 8. Open Questions / <TBF elsewhere>
1. End-to-end infra topology (ingress, load balancing, service mesh) beyond app process boundaries: `<TBF elsewhere>`.
2. Formal SLO/SLA targets and scaling strategy per app type: `<TBF elsewhere>`.
3. Full endpoint-level contract deep dives for each app-specific router family: `<TBF elsewhere>`.

## 9. Evidence Index
- `run.py#L17-L38`
- `run.py#L82-L107`
- `gen_epix/casedb/app.py#L28-L45`
- `gen_epix/seqdb/app.py#L28-L45`
- `gen_epix/omopdb/app.py#L28-L45`
- `gen_epix/commondb/app.py#L26-L42`
- `gen_epix/commondb/env.py#L73-L205`
- `gen_epix/commondb/base_env.py#L66-L93`
- `gen_epix/commondb/app_setup.py#L74-L126`
- `gen_epix/commondb/config/cfg.py#L188-L269`
- `gen_epix/commondb/config/settings_manager.py#L43-L77`
- `gen_epix/commondb/util.py#L61-L119`
- `gen_epix/commondb/api/router.py#L23-L48`
- `gen_epix/casedb/api/router.py#L26-L72`
- `gen_epix/seqdb/api/router.py#L26-L64`
- `gen_epix/omopdb/api/router.py#L25-L55`
- `gen_epix/fastapp/app.py#L309-L418`
