Creation Date: March 1, 2026

# Security

This chapter covers the end-to-end security architecture: authentication pipeline, authorization model, trust boundaries, and security risk modes.

---

## 1. Security Architecture Overview

The system treats security as a pipeline with a clear handoff: external identity is established first, then internal authority is applied to commands. **Authentication establishes who the caller is**, while **authorization decides what that caller can do**. These are intentionally separate layers tied together in app composition and command handling. (Source: `gen_epix/commondb/env.py#L154-L177`; Source: `gen_epix/fastapp/services/auth/service.py#L84-L91`; Source: `gen_epix/fastapp/app.py#L314-L360`)

Trust enters through FastAPI security dependencies that parse bearer tokens and delegate claim validation to IDP clients. After claims are accepted, the system resolves them into a local user model (existing user, root user, or automatic new user path) and only then executes commands under policy control. (Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L621-L648`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L595`)

Policy enforcement physically occurs in the app command lifecycle, not directly in endpoint code:

```text
Request
  -> FastAPI dependency
  -> IDP validation
  -> user resolution
  -> command execution
  -> policy phases: BEFORE / DURING / AFTER
```

(Source: `gen_epix/fastapp/services/auth/service.py#L450-L470`; Source: `gen_epix/fastapp/app.py#L314-L360`)

---

## 2. Trust Boundaries and Authority Model

The system has two authorities by design:

- **External authority**: the OIDC provider ecosystem (discovery metadata, signing keys, issuer, token semantics). (Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L143-L199`)
- **Internal authority**: the repository-backed user model plus policy engine that governs commands. (Source: `gen_epix/commondb/services/user_manager.py#L46-L58`; Source: `gen_epix/fastapp/pdp.py#L12-L17`)

Operationally, the handoff works like a passport checkpoint: the IDP says "this token is valid," but the system still decides "what does this identity mean *here*, and what is it allowed to do *now*?"

**What the system trusts:**
1. Tokens that pass issuer, signature, audience, and required-claim checks.
2. Policy decisions produced by registered command policies.

**What the system does not trust:**
1. Missing or malformed authorization headers.
2. Tokens with mismatched issuer or invalid signature.

(Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L314-L388`)

Only OIDC is supported; any other configured auth protocol is rejected at initialization. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L704`)

---

## 3. Authentication (Identity Resolution Layer)

Authentication is a translation pipeline: provider config → token verification → normalized claims → local user identity. The goal is to convert external OIDC identity into an internal user object that command handlers can rely on. (Source: `gen_epix/fastapp/services/auth/service.py#L667-L690`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L595`)

### IDP Configuration

IDP configuration is loaded from runtime settings files and validated as OIDC server config, including claim mapping and optional introspection settings. (Source: `config/identity_providers.toml#L1-L34`; Source: `gen_epix/fastapp/services/auth/model.py#L100-L126`)

### Token Validation Path

1. Parse `Authorization` header and require bearer scheme.
2. Decode/verify JWT against OIDC metadata and keys.
3. Enforce issuer and required claims.
4. Optionally introspect token when enabled.

(Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L621-L648`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L279-L388`)

### Claim Mapping

`claim_map` can remap provider claim names into expected local claim keys before user resolution. (Source: `gen_epix/fastapp/services/auth/model.py#L109-L112`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L304-L312`)

### User Resolution

1. Generate user key from mapped claims, with optional userinfo fallback.
2. Retrieve existing user by key.
3. If not found, branch to root creation or automatic user creation when configured.
4. If no valid path exists, fail unauthorized.

(Source: `gen_epix/fastapp/services/auth/service.py#L635-L665`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L633`)

This is where many operational "mysteries" become explainable: a request can fail *after* token validation if user resolution can't complete, because authentication and authorization are intentionally separate controls.

### Fallback Behavior (No IDPs)

When no IDP clients are configured, auth dependencies intentionally switch to a fallback mode:
- Existing-user dependency can return root user.
- New-user dependency still requires claims and fails on missing claims.

(Source: `gen_epix/fastapp/services/auth/service.py#L384-L408`; Source: `config/no_identity_providers.toml#L1`)

---

## 4. Authorization (Policy Decision Layer)

Authorization is modeled around **commands**, not routes. Endpoints submit commands, and the app acts as policy enforcement point around command execution. This makes authorization behavior consistent across callers that invoke the same command path. (Source: `gen_epix/fastapp/app.py#L314-L360`)

### PDP Timing Model

| Phase | Purpose |
|-------|---------|
| `BEFORE` | Deny/allow command execution |
| `DURING` | Attach policies to the command context for handler use |
| `AFTER` | Filter or transform returned data |

(Source: `gen_epix/fastapp/pdp.py#L12-L17`; Source: `gen_epix/fastapp/pdp.py#L97-L112`)

### RBAC

RBAC is registered once at startup and applied broadly at `BEFORE` timing for commands subject to RBAC. Some commands are intentionally marked as no-RBAC (including identity provider listing). (Source: `gen_epix/fastapp/services/rbac/service.py#L364-L375`; Source: `gen_epix/commondb/domain/policy/permission.py#L10-L26`)

### Root Privilege

Root can satisfy authorization even when regular role intersection would fail. This is structural in RBAC. (Source: `gen_epix/fastapp/services/rbac/policy.py#L51-L66`; Source: `gen_epix/commondb/services/rbac.py#L48-L49`)

---

## 5. Security Risk Modes

These runtime modes are implemented intentionally but change operational risk. The architecture supports them for flexibility, not because they are equivalent in security posture.

| # | Risk mode | Operational implication |
|---|-----------|----------------------|
| 1 | **No-IDP fallback** — can resolve requests as root user via dependency behavior | Treat as restricted mode, not default internet-exposed posture. (Source: `gen_epix/fastapp/services/auth/service.py#L376-L395`) |
| 2 | **Public provider listing without RBAC** — `GetIdentityProvidersCommand` is no-RBAC and invoked with `user=None` | Provider metadata exposure is intentional; review as part of external interface hardening. (Source: `gen_epix/commondb/domain/policy/permission.py#L11-L17`) |
| 3 | **Root privilege is structural** — role hierarchy + root checks | Compromise of root identity path has system-wide effect by design. (Source: `gen_epix/commondb/domain/policy/permission.py#L112-L121`) |
| 4 | **Pending IDP retry model** — queues failed IDPs and retries later | Operators must monitor pending/retry logs to catch degraded auth surface. (Source: `gen_epix/fastapp/services/auth/service.py#L776-L819`) |
| 5 | **IDP variant cap** — security dependency generation supports up to five IDPs | Higher counts fail initialization, requiring code change. (Source: `gen_epix/fastapp/services/auth/service.py#L442-L449`) |

---

## 6. Operational Interpretation

At deployment time, operators need a stage-based model for incident triage:

1. **Configuration load** — settings file assembly and validation.
2. **IDP initialization** — provider discovery, JWKS fetch, retry/pending.
3. **Token validation** — JWT signature, issuer, claims.
4. **User resolution** — claim-to-user mapping, root bootstrap.
5. **Policy decision** — RBAC/ABAC enforcement at command level.

Most incidents can be localized to one stage quickly when analyzed in that order. (Source: `gen_epix/commondb/config/settings_manager.py#L45-L67`; Source: `gen_epix/fastapp/services/auth/service.py#L716-L744`)

A production-safe posture means running with explicit IDP configuration, avoiding no-IDP fallback, and keeping middleware-based auth exception handling active in non-debug mode. (Source: `config/identity_providers.toml#L1-L34`; Source: `gen_epix/commondb/app_setup.py#L75-L109`)

The most useful operational logs mark phase transitions:
- **IDP initialization/retry logs** — trust anchors available vs degraded.
- **User-verification warnings** — auth dependency failures before command execution.
- **`NOT_AUTHORIZED` events** — command policy denial after identity resolution.

(Source: `gen_epix/fastapp/services/auth/service.py#L697-L712`; Source: `gen_epix/fastapp/app.py#L408-L415`)

Developer Note: if requests return `401`, first distinguish middleware-auth exceptions from policy denials — they represent different layers and different fixes. (Source: `gen_epix/fastapp/middleware/handle_auth_exception.py#L37-L42`)

---

## Evidence Sources

- `gen_epix/fastapp/services/auth/service.py#L84-L825`
- `gen_epix/fastapp/services/auth/oauth_idp_client.py#L143-L648`
- `gen_epix/fastapp/services/auth/model.py#L100-L317`
- `gen_epix/fastapp/services/rbac/service.py#L327-L375`
- `gen_epix/fastapp/services/rbac/policy.py#L51-L66`
- `gen_epix/fastapp/app.py#L309-L418`
- `gen_epix/fastapp/pdp.py#L12-L112`
- `gen_epix/fastapp/middleware/handle_auth_exception.py#L37-L42`
- `gen_epix/commondb/env.py#L154-L177`
- `gen_epix/commondb/services/user_manager.py#L46-L178`
- `gen_epix/commondb/services/rbac.py#L41-L49`
- `gen_epix/commondb/domain/policy/permission.py#L10-L121`
- `gen_epix/commondb/app_setup.py#L75-L109`
- `config/identity_providers.toml#L1-L34`
- `config/mock_identity_provider.toml#L1-L16`
- `config/no_identity_providers.toml#L1-L1`
