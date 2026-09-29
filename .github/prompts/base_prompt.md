# Evidence-Based Response Template

This optional prompt is attached manually in Copilot Chat when a structured,
evidence-based response is useful. It is not referenced automatically. Shared
repository rules remain in `AGENTS.md`; applicable path-specific instructions
and task skills still apply.

## Evidence

- Use documentation for navigation, then verify material claims in source,
  tests, executable configuration, and CI.
- Cite relevant repository paths and symbols.
- State documentation/code conflicts explicitly and recommend which should
  change.
- Search for missing references before reporting suspected stale documentation;
  do not invent replacements.

## Response

Include only sections relevant to the request:

1. Evidence consulted.
2. Answer or plan.
3. Patch, only when requested.
4. Validation performed or explicitly not run.
5. Concrete risks, assumptions, or suspected stale documentation.

Do not force architecture, backend, policy-phase, or identity-provider analysis
into unrelated tasks. Include those implications when the change affects them.
