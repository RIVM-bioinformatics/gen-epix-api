# RBAC Command Execution Model

> 13 nodes · cohesion 0.17

## Key Concepts

- **App (command dispatcher / PEP)** (6 connections) — `docs/02a-Fastapp-Framework.md`
- **CrudEndpointGenerator** (3 connections) — `docs/02a-Fastapp-Framework.md`
- **PolicyDecisionPoint** (3 connections) — `docs/02a-Fastapp-Framework.md`
- **RbacPolicy** (3 connections) — `docs/02a-Fastapp-Framework.md`
- **Authorization (Policy Decision Layer)** (3 connections) — `docs/03-Security.md`
- **Security Contract Interpretation (OIDC scopes, public routes)** (2 connections) — `docs/04-API-Surface.md`
- **Command-Based Execution Model** (1 connections) — `docs/02-Architecture.md`
- **Policy Enforcement Timing (BEFORE/DURING/AFTER)** (1 connections) — `docs/02-Architecture.md`
- **BaseRbacService** (1 connections) — `docs/02a-Fastapp-Framework.md`
- **Policy (is_allowed/get_content/filter hooks)** (1 connections) — `docs/02a-Fastapp-Framework.md`
- **RemoteApp (HTTP-client variant of App)** (1 connections) — `docs/02a-Fastapp-Framework.md`
- **Endpoint Family Generation Pattern (/batch,/query,/{object_id})** (1 connections) — `docs/04-API-Surface.md`
- **Add New Endpoints (Router Pattern)** (1 connections) — `docs/08-Extending-the-System.md`

## Relationships

- [Repository Architecture Docs](Repository_Architecture_Docs.md) (1 shared connections)

## Source Files

- `docs/02-Architecture.md`
- `docs/02a-Fastapp-Framework.md`
- `docs/03-Security.md`
- `docs/04-API-Surface.md`
- `docs/08-Extending-the-System.md`

## Audit Trail

- EXTRACTED: 12 (86%)
- INFERRED: 2 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*