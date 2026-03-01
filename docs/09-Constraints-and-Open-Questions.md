Creation Date: March 1, 2026

# Constraints & Open Questions

This chapter consolidates all architectural constraints, security guardrails, documented consistency issues, and open `<TBF elsewhere>` items scattered across the documentation set into a single reference.

---

## 1. Security Constraints

| Constraint | Source |
|------------|--------|
| Auth initialization supports OIDC only; non-OIDC raises `NotImplementedError`. | `gen_epix/fastapp/services/auth/service.py#L675-L694` |
| IDP dependency generation is capped at 5 IDP bases. Adding more requires code changes. | `gen_epix/fastapp/services/auth/service.py#L346-L366`; `#L442-L449` |
| Duplicate IDP `name` or `label` values are rejected at startup. | `gen_epix/fastapp/services/auth/service.py#L753-L775` |
| IDP introspection interval is limited to configured bounds. | `gen_epix/fastapp/services/auth/service.py` |
| `NONE` mode falls back to root user dependencies — materially changes trust posture. | `gen_epix/fastapp/services/auth/service.py#L90`; `config/no_identity_providers.toml` |
| In debug mode, middleware hardening (rate limiting, security headers, gzip, auth exception handling) is disabled. | `gen_epix/commondb/app_setup.py#L75-L109` |
| Publishing to PyPI is configured with `id-token: write` and a named `PyPI` environment; permissions are tied to GitHub environment governance. | `.github/workflows/release.yaml#L11-L23` |

---

## 2. Architectural Constraints

| Constraint | Source |
|------------|--------|
| Repository types are bounded to `DICT`, `SA_SQLITE`, and `SA_SQL`. Unsupported modes fail at composition time with `NotImplementedError`. | `gen_epix/commondb/base_env.py#L66-L93` |
| Root route (`/`) is redirect-driven — redirects to `api.default_route` (defaults to `/openapi.json`). | `gen_epix/commondb/app_setup.py#L119-L126` |
| All routers must be mounted under `/v1`. | `gen_epix/commondb/app_setup.py#L119-L120` |
| Policy enforcement is centralized through `App.handle()` command dispatch — RBAC/ABAC must not be enforced in routes. | `.github/copilot-instructions.md` §1.1 |
| Business logic must live in commands/services, not in API route handlers. | `.github/copilot-instructions.md` §1.1 |
| Repository implementations must exist for both Dict and SQL backends with identical domain behavior. | `.github/copilot-instructions.md` §3 |
| Cross-application communication occurs via HTTP in production, not direct imports. | `.github/copilot-instructions.md` §5 |
| CI and release logic are GitHub Actions-specific; alternate CD systems are not evidenced. | `.github/workflows/main.yml`; `.github/workflows/release.yaml` |

---

## 3. Contract Limitations

| Limitation | Source |
|------------|--------|
| OpenAPI schema is expressly bounded to the CASEDB artifact in the current Dockerfile/documentation. Other apps serve their own schemas but only CASEDB is explicitly documented as the reference. | `Dockerfile`; `docs/general/Product-Manual.md` |
| `CrudEndpointGenerator` suppresses `ValueError` exceptions and maps them to HTTP 422 rather than bubbling them through the standard exception hierarchy. | `gen_epix/fastapp/api/crud_endpoint_generator.py` |

---

## 4. Documented Consistency Issues

| Issue | Source |
|-------|--------|
| License mismatch: `pyproject.toml` specifies EUPL-1.2; `LICENSE` file and OpenAPI output reference MIT. | `pyproject.toml#L12`; `LICENSE`; Product-Manual observations |
| Manifest and `pyproject.toml` version values can diverge (`7.1.2` vs `7.1.1`); the release workflow has a version-bump step to reconcile them. | `.release-please-manifest.json#L2`; `pyproject.toml#L7`; `.github/workflows/release.yaml#L51-L77` |

---

## 5. Open Questions / `<TBF elsewhere>` (Consolidated)

### Security & Auth
- Environment protection rules, required reviewers, and secret governance for the `PyPI` environment.
- SAML / non-OIDC protocol support.
- Production IDP secret governance and operational rollout process.

### Operational
- Formal rollback process for a bad PyPI/GitHub release.
- Runtime infrastructure rollout/rollback strategy (not implemented in current workflows).
- Branch protection and force-push policy alignment with automated version bumping.

### Governance
- Code review policy (required approvals, reviewer roles, merge policy).
- Issue triage and prioritization process.
- A formal branching model policy (beyond `dev`/`test`/`main` as CI targets).
- A formal maintainer-approved checklist for adding new modules/services.

### Architecture
- ABAC enforcement scope beyond org-admin checks.
- Whether the OpenAPI contract should be broadened beyond CASEDB as the reference artifact.
- Whether middleware should be hardened in debug mode (currently disabled).

---

## Evidence Sources

- `gen_epix/fastapp/services/auth/service.py#L90`, `#L346-L449`, `#L675-L775`
- `gen_epix/commondb/app_setup.py#L75-L126`
- `gen_epix/commondb/base_env.py#L66-L93`
- `.github/copilot-instructions.md` §1-5
- `.github/workflows/main.yml#L1-L197`
- `.github/workflows/release.yaml#L1-L118`
- `.release-please-manifest.json#L2`
- `pyproject.toml#L5-L12`
- `LICENSE`
- `Dockerfile`
- `config/no_identity_providers.toml`
- `gen_epix/fastapp/api/crud_endpoint_generator.py`
