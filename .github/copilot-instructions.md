# Gen-EpiX Copilot Instructions

Always preserve these repository invariants. Use task prompts for output
format, planning style, and detailed workflow guidance.

## Source of Truth

- Docs guide; code decides.
- If task-relevant docs and code conflict, report both: "Docs say X, code shows Y."
  Recommend whether docs or code should change.
- Treat doc creation dates only as hints for which docs to inspect first.
  Verify claims in code or config before relying on them.
- Do not invent endpoints, ports, config keys, roles, module ownership,
  domain rules, or replacements for missing symbols.
- If a referenced path, symbol, config key, endpoint, role, or command is
  missing, use targeted search and report it under
  `### Suspected Stale Documentation` with concise search evidence.

## Architecture

- Business logic must not live in API routes.
- API routes are transport only: parse requests, construct a `Command`,
  call `app.handle(command)`, and return the result.
- Do not call repositories directly from routes.
- Do not enforce RBAC or ABAC in FastAPI handlers.
- Do not add domain rules in API handlers.
- Justify exceptions for tests, ETL/CLI code, bootstrapping, or migrations.

Layer ownership:

- `api/`: transport only
- `domain/`: domain objects, commands, permissions, and base classes
- `policies/`: policy implementations
- `services/`: service implementations
- `repositories/`: persistence implementations

Policies run in the command lifecycle: BEFORE, DURING, or AFTER.

When changing behavior, identify the command involved. State role, RBAC/ABAC,
and BEFORE/DURING/AFTER impact only when changed or when a risk exists.

## Security

- Supported IDP modes are `IDPS`, `MOCK`, and `NONE`.
- `NONE` mode changes trust posture through root fallback.
- When changing auth dependencies, user resolution, IDP configuration, or root
  behavior, state the implications for `NONE`, root users, and OIDC-only
  assumptions.
- Never weaken security implicitly.

## Repositories

- Repository behavior must remain equivalent across `DICT`, `SA_SQLITE`, and
  `SA_SQL`.
- If repository logic changes, update the relevant DICT and SQL
  implementations or justify why parity is unaffected.
- Do not introduce SQL-only behavior without justification.

## Routers

- Routers must mount under `/v1`.
- Avoid duplicate router registration.
- Ensure OpenAPI reflects router changes.
- Endpoints must delegate to commands.

## Application Domains

- Application domains are `casedb`, `seqdb`, `omopdb`, and `commondb`.
- `commondb` provides shared models and cross-cutting services.
- In production, cross-domain communication uses HTTP, not direct imports.
- Before adding a new HTTP pattern, use targeted search for existing client
  abstractions and reuse precedent where it exists.

## Configuration

- Configuration is Dynaconf-based.
- Settings are discovered through the environment stack.
- Repository type is config-driven.
- Do not hardcode config paths.
- Do not assume ports; verify them in config.

## Agent Workflow

- Optimize for correctness first and token efficiency second.
- Prefer Ask or Plan mode before Agent mode for unclear investigations.
- Read targeted files first; expand to related commands, policies,
  repositories, routers, config, and tests when the change crosses those
  boundaries.
- Avoid broad workspace scans when file, symbol, or path searches suffice.
- Keep diffs focused and avoid unrelated refactors.
- Use targeted tests before full suites when appropriate.
- When a command failure blocks or materially affects the result, report the
  command, exit code, first error block, and last relevant lines instead of
  full logs.
