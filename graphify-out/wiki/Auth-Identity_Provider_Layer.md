# Auth/Identity Provider Layer

> 13 nodes · cohesion 0.17

## Key Concepts

- **IdpClient hierarchy** (7 connections) — `docs/02a-Fastapp-Framework.md`
- **AuthService (concrete)** (4 connections) — `docs/02a-Fastapp-Framework.md`
- **OauthIdpClient (real OIDC)** (2 connections) — `docs/02a-Fastapp-Framework.md`
- **BaseUserManager** (2 connections) — `docs/02a-Fastapp-Framework.md`
- **Authentication (Identity Resolution Layer)** (2 connections) — `docs/03-Security.md`
- **Add New IDP Configuration** (2 connections) — `docs/08-Extending-the-System.md`
- **User Dependencies (registered_user/new_user/idp_user FastAPI Depends)** (2 connections) — `docs/08a-App-Composition-Walkthrough.md`
- **IdentityProvider entity** (2 connections) — `docs/erm/casedb.auth.detailed.md`
- **MockIDPClient (no-auth dev/CI)** (1 connections) — `docs/02a-Fastapp-Framework.md`
- **User Resolution (claims -> local User)** (1 connections) — `docs/03-Security.md`
- **IDP Modes (IDPS / MOCK / NONE)** (1 connections) — `docs/05-Configuration-and-Runtime.md`
- **Security Constraints table** (1 connections) — `docs/09-Constraints-and-Open-Questions.md`
- **IDPUser entity** (1 connections) — `docs/erm/casedb.auth.detailed.md`

## Relationships

- [Documentation Index](Documentation_Index.md) (1 shared connections)
- [FastAPI App Composition Root](FastAPI_App_Composition_Root.md) (1 shared connections)

## Source Files

- `docs/02a-Fastapp-Framework.md`
- `docs/03-Security.md`
- `docs/05-Configuration-and-Runtime.md`
- `docs/08-Extending-the-System.md`
- `docs/08a-App-Composition-Walkthrough.md`
- `docs/09-Constraints-and-Open-Questions.md`
- `docs/erm/casedb.auth.detailed.md`

## Audit Trail

- EXTRACTED: 13 (87%)
- INFERRED: 2 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*