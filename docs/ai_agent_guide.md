# Copilot Chat and Repository Context

Use the smallest relevant set of repository context in Copilot Chat.

## Customization layers

- `AGENTS.md` is the shared source of repository rules and architecture.
- `.github/copilot-instructions.md` contains only Copilot-specific behavior and
  points to `AGENTS.md`.
- `.github/instructions/*.instructions.md` adds path-specific guidance.
- `.agents/skills/*/SKILL.md` contains task-specific workflows.
- `docs/00-Index.md` is the documentation map. Documentation guides; source,
  tests, executable configuration, and CI decide.

## Supplying context

1. Confirm that `AGENTS.md` appears in the chat references. Attach it with
   `#AGENTS.md` if the client did not include it automatically.
2. Use `@workspace` for broad discovery questions.
3. Attach `#docs/00-Index.md` only when documentation navigation is needed.
4. Attach the smallest relevant set of code, tests, and focused documentation.
   Avoid changelogs, generated reports, and unrelated configuration.

Ask for repository paths and symbols when an answer needs evidence. If an
instruction references something that cannot be found, ask Copilot to report
the search evidence instead of inventing a replacement.

## Optional response template

`.github/prompts/base_prompt.md` is a manually attached response template for
tasks that benefit from a fixed evidence and reporting structure. It is not
referenced automatically by Copilot instructions and is not a second source of
repository rules.

To use it:

1. Attach `#.github/prompts/base_prompt.md`.
2. Attach the relevant files or use `@workspace` for discovery.
3. State the task and whether a patch is requested.

Update the prompt in place instead of copying it into other documentation.
