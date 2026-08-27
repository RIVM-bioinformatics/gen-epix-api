# AppComposer (Composition Root)

> 10 nodes · cohesion 0.22

## Key Concepts

- **AppComposer (Composition Root)** (6 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **Entry Point app.py (SCHEMA_KWARGS, APP_CFG, APP_COMPOSER, FAST_API)** (3 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **Repository + Service Loop (compose_application/_initialize_repository)** (3 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **AppImplDetails (state bag)** (2 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **create_fast_api Assembly (lifespan, middleware, routers, OpenAPI)** (2 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **User Dependencies (registered_user/new_user/idp_user FastAPI Depends)** (2 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **System Composition (four FastAPI apps sharing a model)** (1 connections) — `docs/02-Architecture.md`
- **AppCfg (logger init, settings load, settings validation)** (1 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **Exception Handling (api/exc.py, handle_exception/handle_command)** (1 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **Role Derivation (RoleGenerator: role_map, role_set_map, role_permissions_map)** (1 connections) — `docs/08a-App-Composition-Walkthrough.md`

## Relationships

- [BaseRepository (abstract)](BaseRepository_abstract.md) (1 shared connections)
- [IdpClient hierarchy](IdpClient_hierarchy.md) (1 shared connections)

## Source Files

- `docs/02-Architecture.md`
- `docs/08a-App-Composition-Walkthrough.md`

## Audit Trail

- EXTRACTED: 11 (92%)
- INFERRED: 1 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*