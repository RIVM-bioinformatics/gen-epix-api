---
name: commit
description: >-
  Create one or more git commits with Conventional Commits messages that are
  descriptive but compact — one subject sentence, followed by a short body
  paragraph only when it genuinely adds value.
  Infers the commit type and the bracketed scope from the staged diff, the branch
  name, and the previous two commits, ties the message to recent work when it
  genuinely continues it, and splits unrelated changes into separate commits. Use
  when asked to commit staged changes.
argument-hint: 'Optional: a scope hint or the gist of the change'
---

# Commit

Compose and create git commit(s) for the **currently staged** changes, using
Conventional Commits messages that are descriptive but compact.

## 1. Gather context first (read-only)

Run these and use their output — do not skip:

- `git diff --staged --stat` and `git diff --staged` — what is actually staged. Commit
  only this; never `git add` beyond regrouping already-staged changes unless the user
  asked.
- `git log -2 --pretty=format:'%s'` — the previous two commit subjects, for type/scope
  continuity and to detect whether this change follows on from them.
- `git rev-parse --abbrev-ref HEAD` — the branch name, which often encodes a
  ticket/feature/component.

If nothing is staged, stop and tell the user.

## 2. Decide how many commits

Group the staged changes by purpose. If they form one cohesive change, make a single
commit. If they span clearly distinct purposes or features (e.g. a feature *plus* an
unrelated docs fix *plus* a config change), split them into **multiple commits — one per
coherent purpose** — and commit them in a sensible order (e.g. refactors/deps before the
feature that uses them). Stage each group precisely with `git add <paths>` (or
`git add -p` for hunks within a file), then apply the rules below to each commit. Do not
force unrelated changes into one commit just to save steps.

## 3. Message format

```
type(scope): description
```

- **type** — one of `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`,
  `build`, `ci`, `style`. Choose from what that commit's diff actually does.
- **scope** — the bracketed component. Infer it in this priority order:
  1. The dominant directory/module in the diff (e.g. `hooks`, `skills`, `etl`,
     `batch-uploader`).
  2. A component/ticket implied by the branch name (e.g. branch
     `lsp-3559-optimize-agentic-ai-...` → a scope like `agents`).
  3. Consistency with the previous two commits — reuse their scope when this change
     continues the same line of work.
  Omit the scope only when no meaningful one exists.
- **description** — one lower-case, imperative sentence that summarizes the change.
  No trailing period on the subject line.

## 4. Keep it compact

- Use **one descriptive subject sentence**. Aim for a subject under ~72 characters
  while keeping it clear.
- Add **one short body paragraph** after a blank line only when it genuinely adds
  value, such as explaining the why or linking the change to recent work.

## 5. Relate to recent work when relevant

If a change continues, completes, or fixes up either of the previous two commits, reflect
that: reuse their scope and phrase the description as a continuation (e.g. "extend",
"finish", "follow up on"). Never fabricate a relationship that isn't supported by the
diff and history.

## 6. Commit

Create each commit with its composed message. Append any attribution trailer your
environment requires (e.g. a `Co-Authored-By:` line) after a blank line. Then report each
final message and its resulting short hash.

## Examples

- Branch `lsp-3559-optimize-agentic-ai-usage-in-lsp-data-repo`; last commit
  `feat: add hooks for conventions reminder...`; staged diff touches `.agents/scripts/`
  and `.claude/settings.json` →
  `feat(agents): share guardrail hooks across Claude Code, Codex, and Copilot`
- Last commit `feat(skills): add refdata-troubleshooting skill`; staged diff only fixes a
  broken path in that skill →
  `fix(skills): correct the loader path in refdata-troubleshooting`
- Staged diff mixes a new ETL feature with an unrelated README typo → two commits:
  `feat(etl): add batch retry backoff` and `docs: fix typo in setup instructions`.
