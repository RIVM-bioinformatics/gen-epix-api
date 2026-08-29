# IdpClient hierarchy

> 11 nodes

## Key Concepts

- **IdpClient hierarchy** (7 connections) — `docs/02a-Fastapp-Framework.md`
- **AuthService (concrete)** (4 connections) — `docs/02a-Fastapp-Framework.md`
- **OauthIdpClient (real OIDC)** (2 connections) — `docs/02a-Fastapp-Framework.md`
- **BaseUserManager** (2 connections) — `docs/02a-Fastapp-Framework.md`
- **Authentication (Identity Resolution Layer)** (2 connections) — `docs/03-Security.md`
- **IdentityProvider entity** (2 connections) — `docs/erm/casedb.auth.detailed.md`
- **MockIDPClient (no-auth dev/CI)** (1 connections) — `docs/02a-Fastapp-Framework.md`
- **User Resolution (claims -> local User)** (1 connections) — `docs/03-Security.md`
- **Add New IDP Configuration** (1 connections) — `docs/08-Extending-the-System.md`
- **IDPUser entity** (1 connections) — `docs/erm/casedb.auth.detailed.md`
- **Security Constraints table** (1 connections) — `docs/09-Constraints-and-Open-Questions.md`

## Relationships

- [AppComposer (Composition Root)](AppComposer_Composition_Root.md) (1 shared connections)
- [fastapp shared application framework](fastapp_shared_application_framework.md) (1 shared connections)

## Source Files

- `docs/02a-Fastapp-Framework.md`
- `docs/03-Security.md`
- `docs/08-Extending-the-System.md`
- `docs/09-Constraints-and-Open-Questions.md`
- `docs/erm/casedb.auth.detailed.md`

## Audit Trail

- EXTRACTED: 12 (92%)
- INFERRED: 1 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*