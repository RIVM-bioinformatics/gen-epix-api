---
name: commit
description: >-
  Create one or more compact Conventional Commits from staged changes. Check
  for unstaged or untracked changes first and ask before staging them. Infer the
  type and scope from the diff, branch, and recent history; split only clearly
  unrelated changes. Use when asked to commit changes.
argument-hint: 'Optional: a scope hint or the gist of the change'
---

# Commit

Compose and create git commit(s) for the **currently staged** changes, using
Conventional Commits messages that are descriptive but compact.

## 1. Check for unstaged changes first

Run `git status --short`. If it reports any unstaged or untracked changes, 
present a yes/no prompt that asks the user: “There are unstaged changes. Should I stage them?”. 
Do not stage anything until the user answers **yes**. If the answer is yes, stage all
reported changes with `git add -A`; if the answer is no, leave them untouched
and continue with the currently staged changes.

## 2. Gather context in one pass (read-only)

In one tool invocation, collect and use all of this output — do not rerun these
commands or inspect unrelated files unless the output is missing or a commit
attempt fails:

- `git diff --staged --stat` and `git diff --staged` — what is actually staged. Commit
  only this; never `git add` beyond regrouping already-staged changes unless the user
  asked.
- `git log -2 --pretty=format:'%s'` — the previous two commit subjects, for type/scope
  continuity and to detect whether this change follows on from them.
- `git rev-parse --abbrev-ref HEAD` — the branch name, which often encodes a
  ticket/feature/component.

If nothing is staged, stop and tell the user.

## 3. Choose commits and messages

Default to one commit when the staged diff is cohesive. Split only when it contains
clearly unrelated purposes and the groups are obvious from the current diff; stage
each group precisely with `git add <paths>` or `git add -p`, then commit in a sensible
order. Do not search the repository for additional context just to decide grouping.

For each commit, use:

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

- Keep the subject under about 72 characters and add a short body only when it
  genuinely adds value. If the change clearly continues either recent commit,
  reuse its scope and use wording such as "extend" or "finish"; never fabricate
  that relationship.

## 4. Commit immediately

Create each commit with its composed message, appending any required attribution
trailer after a blank line. Do not run tests, formatters, or extra validation unless
the user asks or a commit hook fails. Report each final message and short hash.
