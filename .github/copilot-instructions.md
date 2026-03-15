# Gen-EpiX --- Copilot Architectural Invariants

This file defines architectural constraints and security invariants.

The canonical golden prompt (evidence + output format) lives in:

.github/prompts/base_prompt.md

Both must be applied together.

If they conflict: - The golden prompt defines procedural evidence
requirements. - This file defines architecture and security rules.

------------------------------------------------------------------------

## 0) Evidence & Freshness (Hard Rules)

1.  **Docs guide, code decides.** If docs conflict with implementation:
    \> "Docs say X, code shows Y." Then recommend updating docs or code.

2.  **Freshness hint.** Each doc starts with a creation date. Prefer
    newer docs but always verify in code.

3.  **No guessing.** Never invent:

    -   endpoints
    -   ports
    -   config keys
    -   roles
    -   module ownership

4.  **Stale-doc detection (required).** If a referenced
    path/symbol/config cannot be found:

    -   Add a `### Suspected Stale Documentation` section
    -   Cite search evidence
    -   Do not invent replacements

5.  **No silent assumptions.** If evidence is missing:

    -   Search workspace
    -   Report findings
    -   State assumptions explicitly

------------------------------------------------------------------------

## 1) Architectural Core

### 1.1 Command-First Rule (Non-Negotiable)

Business logic must not live in API routes.

Endpoints must: - Parse request - Construct a `Command` - Call
`app.handle(command)` - Return result

Do NOT: - Call repositories directly from routes - Enforce RBAC/ABAC in
routes - Add domain rules in FastAPI handlers

Exceptions (must justify): - tests - ETL/CLI - bootstrapping/migrations

------------------------------------------------------------------------

### 1.2 Strict Layering

    api/         → transport only
    domain/      → domain objects, commands, permissions and base
                   classes for services, policies, repositories
    policies/    → implementations of policies (auth, validation, etc.)
    services/    → implementations of services
    repositories/→ implementations of repositories (persistence)

API must stay thin. Policies execute in command lifecycle (BEFORE /
DURING / AFTER).

------------------------------------------------------------------------

### 1.3 Policy Enforcement Model

Authorization is command-based.

When changing behavior, explicitly state:

1.  Which command is involved?
2.  Required role(s)?
3.  RBAC/ABAC impact?
4.  BEFORE/DURING/AFTER implications?

If this is not addressed, the answer is incomplete.

------------------------------------------------------------------------

## 2) Security Posture Constraints

### 2.1 IDP Modes

The system supports:

-   `IDPS` (real OIDC)
-   `MOCK`
-   `NONE` (root fallback)

`NONE` mode changes trust posture.

If modifying: - auth dependencies - user resolution - IDP
configuration - root behavior

You must state: - NONE-mode implications - Root-user implications -
Whether OIDC-only assumptions are introduced

Never weaken security implicitly.

------------------------------------------------------------------------

## 3) Multi-Repository Guarantee (repository pattern)

All behavior must work in:

-   DICT
-   SA_SQLITE
-   SA_SQL

If modifying repositories: - Update both DICT + SQL implementations -
Keep domain behavior identical

Do not introduce SQL-only logic without justification.

------------------------------------------------------------------------

## 4) Router & API Integrity

When modifying routers:

-   No duplicate router registrations
-   Must mount under `/v1`
-   OpenAPI must reflect change
-   Endpoint must delegate to command

------------------------------------------------------------------------

## 5) Application Domains

Four application domains:

-   casedb

-   seqdb

-   omopdb

-   commondb

-   commondb provides shared models + cross-cutting services.

-   Cross-application communication occurs via HTTP in production, not direct
    imports.

Before adding new HTTP patterns: - Search for existing client
abstractions - Reuse precedent - Cite file paths + symbols - Label truly
new patterns as such

------------------------------------------------------------------------

## 6) Configuration Constraints

-   Config is Dynaconf-based.
-   Settings auto-discovered via environment stack.
-   Never hardcode config paths.
-   Repository type is config-driven.

------------------------------------------------------------------------

## 7) Operational Commands (Reference)

Startup:

    python run.py api <APP> <IDP_MODE> <REPO_MODE>

Testing:

    python run.py test_all

Data loading:

    python run.py etl_load_demo_data <scope>

Do not assume ports --- verify in config.

------------------------------------------------------------------------

## 8) Common Failure Points

-   Repository mappers must be registered before SQL use.
-   Commands require user context.
-   casedb may depend on seqdb running.