# Gen-EpiX Copilot Instructions

Follow [AGENTS.md](../AGENTS.md) for the shared repository-wide invariants.
That file is the source of truth; do not maintain a second copy here. When a
path-specific file under `.github/instructions/` applies, follow it in addition
to `AGENTS.md`.

## VS Code code-review compatibility

VS Code Copilot code review consumes this file but does not currently list
`AGENTS.md` as a supported instruction source. The following minimal fallback
is intentionally duplicated for that surface; `AGENTS.md` remains authoritative:

- Treat current source, configuration, tests, and workflows as stronger evidence
  than prose. Keep changes and review advice focused on the requested scope.
- Preserve the architecture boundaries: routes are transport adapters, business
  rules belong in commands, policies, or services, persistence stays behind
  repository interfaces, and authorization remains in `App.handle()` policy
  phases rather than FastAPI handlers.
- Preserve behavior across `DICT`, `SA_SQLITE`, and `SA_SQL` repositories unless
  a backend-specific difference is justified. Do not treat the no-IDP `NONE`
  mode as production-equivalent authentication.
- Require focused tests or other targeted verification for affected behavior.
  For authorization or repository changes, check policy-phase/security impact
  and backend parity respectively.

## Copilot-specific behavior

- Type `/graphify` in Copilot Chat to build or update the graph. When a graph
  already exists, follow the shared Graphify workflow in `AGENTS.md`.
