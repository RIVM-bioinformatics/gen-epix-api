Creation Date: February 16, 2026

# Authorization & Authentication Deep Dive

## 1. Security Architecture Overview
This system treats security as a pipeline with a clear handoff: external identity is established first, then internal authority is applied to commands. **Authentication establishes who the caller is**, while **authorization decides what that caller can do**. These are intentionally separate layers tied together in app composition and command handling. (Source: `gen_epix/commondb/env.py#L154-L177`; Source: `gen_epix/fastapp/services/auth/service.py#L84-L91`; Source: `gen_epix/fastapp/app.py#L314-L360`)

Trust enters through FastAPI security dependencies that parse bearer tokens and delegate claim validation to IDP clients. After claims are accepted, the system resolves them into a local user model (existing user, root user, or automatic new user path) and only then executes commands under policy control. (Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L621-L648`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L279-L302`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L595`)

Policy enforcement physically occurs in the app command lifecycle, not directly in endpoint code: `BEFORE` deny/allow checks, `DURING` policy injection for handlers, and `AFTER` result filtering. (Source: `gen_epix/fastapp/app.py#L314-L360`; Source: `gen_epix/fastapp/pdp.py#L97-L112`)

```text
Request
  -> FastAPI dependency
  -> IDP validation
  -> user resolution
  -> command execution
  -> policy phases: BEFORE / DURING / AFTER
```
(Source: `gen_epix/fastapp/services/auth/service.py#L450-L470`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L621-L648`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L595`; Source: `gen_epix/fastapp/app.py#L314-L360`)

Developer Note: endpoint handlers mostly construct commands and call `app.handle(...)`; policy decisions are centralized in the command path. (Source: `gen_epix/commondb/api/auth.py#L32-L34`; Source: `gen_epix/commondb/api/system.py#L86-L88`; Source: `gen_epix/fastapp/app.py#L310-L327`)

## 2. Trust Boundaries and Authority Model
The system has two authorities by design. **External authority** is the OIDC provider ecosystem (discovery metadata, signing keys, issuer, token semantics). **Internal authority** is the repository-backed user model plus policy engine that governs commands. (Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L143-L199`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L336-L344`; Source: `gen_epix/commondb/services/user_manager.py#L46-L58`; Source: `gen_epix/fastapp/pdp.py#L12-L17`)

What the system trusts:
1. Tokens that pass issuer, signature, audience, and required-claim checks.
2. Policy decisions produced by registered command policies.
(Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L314-L370`; Source: `gen_epix/fastapp/services/rbac/service.py#L327-L375`; Source: `gen_epix/fastapp/pdp.py#L97-L112`)

What the system does not trust:
1. Missing or malformed authorization headers.
2. Tokens with mismatched issuer or invalid signature.
(Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L631-L638`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L374-L388`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L351-L370`)

Only OIDC is supported by this auth service path; any other configured auth protocol is rejected at initialization. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L704`)

If no IDP is configured, the service intentionally enters a fallback mode that can create and use a root user dependency path. This keeps the platform operable without external IDP wiring, but changes the trust posture substantially. (Source: `config/no_identity_providers.toml#L1`; Source: `gen_epix/fastapp/services/auth/service.py#L88-L90`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L395`)

Security Note: root fallback exists because the user manager can synthesize and persist a configured root organization/user model, and RBAC treats root as always authorized. (Source: `gen_epix/commondb/services/user_manager.py#L46-L58`; Source: `gen_epix/commondb/services/user_manager.py#L125-L178`; Source: `gen_epix/commondb/services/rbac.py#L41-L49`)

## 3. Authentication (Identity Resolution Layer)
Authentication in this system is a translation pipeline: provider config -> token verification -> normalized claims -> local user identity. The goal is to convert external OIDC identity into an internal user object that command handlers can rely on. (Source: `gen_epix/fastapp/services/auth/service.py#L667-L690`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L279-L312`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L595`)

IDP configuration is loaded from runtime settings files and validated as OIDC server config, including claim mapping and optional introspection settings. (Source: `gen_epix/commondb/util.py#L78-L83`; Source: `config/identity_providers.toml#L1-L34`; Source: `gen_epix/fastapp/services/auth/model.py#L100-L126`; Source: `gen_epix/fastapp/services/auth/model.py#L289-L317`)

Token validation path:
1. Parse `Authorization` header and require bearer scheme.
2. Decode/verify JWT against OIDC metadata and keys.
3. Enforce issuer and required claims.
4. Optionally introspect token when enabled.
(Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L621-L648`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L279-L302`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L314-L388`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L289-L290`)

Claim mapping is explicit: `claim_map` can remap provider claim names into expected local claim keys before user resolution. (Source: `gen_epix/fastapp/services/auth/model.py#L109-L112`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L304-L312`)

User resolution behavior:
1. Generate user key from mapped claims, with optional userinfo fallback.
2. Retrieve existing user by key.
3. If not found, branch to root creation or automatic user creation when configured.
4. If no valid path exists, fail unauthorized.
(Source: `gen_epix/fastapp/services/auth/service.py#L635-L665`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L595`; Source: `gen_epix/fastapp/services/auth/service.py#L597-L633`)

Fallback behavior with no IDPs:
1. Existing-user dependency can return root user.
2. New-user dependency still requires claims and fails on missing claims.
(Source: `gen_epix/fastapp/services/auth/service.py#L384-L408`)

Operator Note: in authentication failures, there are two useful boundaries to separate quickly: token/IDP validation problems versus user-resolution/persistence problems. (Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L351-L370`; Source: `gen_epix/fastapp/services/auth/service.py#L622-L633`)

## 4. Authorization (Policy Decision Layer)
Authorization is modeled around commands, not routes. Endpoints submit commands, and the app acts as policy enforcement point around command execution. This makes authorization behavior consistent across callers that invoke the same command path. (Source: `gen_epix/commondb/api/auth.py#L32-L34`; Source: `gen_epix/commondb/api/system.py#L86-L88`; Source: `gen_epix/fastapp/app.py#L314-L360`)

The PDP timing model is explicit:
1. `BEFORE`: deny/allow command execution.
2. `DURING`: attach policies to the command context for handler use.
3. `AFTER`: filter or transform returned data.
(Source: `gen_epix/fastapp/pdp.py#L12-L17`; Source: `gen_epix/fastapp/pdp.py#L97-L112`)

RBAC is registered once and applied broadly at `BEFORE` timing for commands subject to RBAC. Some commands are intentionally marked as no-RBAC (including identity provider listing). (Source: `gen_epix/fastapp/services/rbac/service.py#L364-L375`; Source: `gen_epix/commondb/domain/policy/permission.py#L10-L26`)

Root implications are explicit in RBAC logic: root can satisfy authorization even when regular role intersection would fail. (Source: `gen_epix/fastapp/services/rbac/policy.py#L51-L66`; Source: `gen_epix/commondb/services/rbac.py#L48-L49`)

Security Note: endpoint-level authentication and command-level authorization are deliberately separate controls. Passing dependency auth does not itself grant command permissions. (Source: `gen_epix/fastapp/services/auth/service.py#L450-L470`; Source: `gen_epix/fastapp/app.py#L406-L418`)

## 5. ⚠ Security Risk Modes
This section captures runtime modes that are implemented intentionally but change operational risk. The architecture supports them for flexibility and resilience, not because they are equivalent in security posture.

1. No-IDP fallback mode exists and can resolve requests as root user via dependency behavior.
Operational implication: this should be treated as restricted mode, not default internet-exposed posture. (Source: `config/no_identity_providers.toml#L1`; Source: `gen_epix/fastapp/services/auth/service.py#L376-L395`; Source: `gen_epix/commondb/services/rbac.py#L41-L49`)

2. Public provider listing without RBAC exists (`GetIdentityProvidersCommand` is no-RBAC and invoked with `user=None`).
Operational implication: provider metadata exposure is intentional and should be reviewed as part of external interface hardening. (Source: `gen_epix/commondb/domain/policy/permission.py#L11-L17`; Source: `gen_epix/commondb/api/auth.py#L30-L33`)

3. Root privilege behavior is structural (role hierarchy + root checks).
Operational implication: compromise of root identity path has system-wide effect by design. (Source: `gen_epix/commondb/domain/policy/permission.py#L112-L121`; Source: `gen_epix/commondb/services/rbac.py#L41-L49`)

4. Pending IDP retry model keeps startup and provider listing resilient by queueing failed IDPs and retrying later.
Operational implication: availability is favored over hard fail; operators must monitor pending/retry logs to catch degraded auth surface. (Source: `gen_epix/fastapp/services/auth/service.py#L732-L735`; Source: `gen_epix/fastapp/services/auth/service.py#L478-L493`; Source: `gen_epix/fastapp/services/auth/service.py#L776-L819`)

5. Security dependency generation is implemented up to five IDP variants.
Operational implication: higher IDP counts fail initialization and require code change, not config-only change. (Source: `gen_epix/fastapp/services/auth/service.py#L346-L352`; Source: `gen_epix/fastapp/services/auth/service.py#L442-L449`)

## 6. Operational Interpretation
At deployment time, operators need a stage-based model: configuration load, IDP initialization, token validation, user resolution, then policy decision. Most incidents can be localized to one stage quickly when analyzed in that order. (Source: `gen_epix/commondb/config/settings_manager.py#L45-L67`; Source: `gen_epix/fastapp/services/auth/service.py#L716-L744`; Source: `gen_epix/fastapp/services/auth/oauth_idp_client.py#L279-L388`; Source: `gen_epix/fastapp/services/auth/service.py#L532-L633`; Source: `gen_epix/fastapp/app.py#L406-L418`)

A production-safe posture, based on existing mechanisms, usually means running with explicit IDP configuration, avoiding no-IDP fallback, and keeping middleware-based auth exception handling active in non-debug mode. (Source: `config/identity_providers.toml#L1-L34`; Source: `config/no_identity_providers.toml#L1`; Source: `gen_epix/commondb/app_setup.py#L75-L76`; Source: `gen_epix/commondb/app_setup.py#L103-L109`)

The most useful logs are the ones that identify phase transitions or control points:
1. IDP initialization/retry logs indicate whether trust anchors are available.
2. User-verification warnings indicate authentication dependency failures before command execution.
3. `NOT_AUTHORIZED` indicates command policy denial after identity resolution.
(Source: `gen_epix/fastapp/services/auth/service.py#L697-L712`; Source: `gen_epix/fastapp/services/auth/service.py#L813-L818`; Source: `gen_epix/fastapp/services/auth/service.py#L425-L433`; Source: `gen_epix/fastapp/app.py#L408-L415`)

Developer Note: if requests return `401`, first distinguish middleware-auth exceptions from policy denials; they represent different layers and fixes. (Source: `gen_epix/fastapp/middleware/handle_auth_exception.py#L37-L42`; Source: `gen_epix/fastapp/app.py#L408-L418`)

## 7. Constraints & Guardrails
This design has explicit boundaries that should be treated as hard constraints unless code is changed.

1. Auth service supports OIDC only in IDP initialization path. (Source: `gen_epix/fastapp/services/auth/service.py#L675-L704`)
2. Duplicate IDP `name` or `label` is rejected at startup. (Source: `gen_epix/fastapp/services/auth/service.py#L753-L775`)
3. Security dependency variants are capped at five. (Source: `gen_epix/fastapp/services/auth/service.py#L442-L449`)
4. IDP visibility defaults to non-public unless configured otherwise. (Source: `gen_epix/fastapp/services/auth/service.py#L27-L27`; Source: `gen_epix/fastapp/services/auth/model.py#L118-L120`)
5. Introspection interval above 1800 seconds is rejected by validation. (Source: `gen_epix/fastapp/services/auth/token_introspection_manager.py#L74-L78`)

## 8. Open Questions / <TBF elsewhere>
These are conceptual gaps where architecture-level understanding requires evidence outside this document's scoped auth/authz layers.

1. Full ABAC semantics per command and data model are outside this rewrite scope: `<TBF elsewhere>`.
2. Human documentation claims automatic notifiable-disease sharing by RIVM; that behavior is not evidenced in the auth/authz enforcement paths analyzed here: `<TBF elsewhere>`. (Source: `docs/LSP - Authorization model.md#L207-L211`; Source: `gen_epix/fastapp/services/auth/service.py#L25-L56`; Source: `gen_epix/commondb/env.py#L154-L177`)
3. End-to-end mapping of high-level sharing narratives to concrete casedb ABAC entities and policies: `<TBF elsewhere>`.

