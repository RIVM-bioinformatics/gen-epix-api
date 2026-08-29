---
name: pr
description: >-
  Create or update GitHub pull requests from the current git branch using the
  GitHub CLI. Use when the user asks to open a PR, create a pull request, update
  an existing PR, push the current branch for review, prepare a PR body, or watch
  PR checks after local work is committed. Also use when the user asks to generate
  a ready-to-run gh pr create command without executing it.
---

# Pull Request

Create or update a GitHub pull request for the current branch with explicit
preflight checks, a concise PR body, and a clear validation summary.

## Workflow

1. Gather read-only context first:
   - `git status --short --branch`
   - `git remote -v`
   - `git branch --show-current`
   - `git branch --show-current | grep -oiE 'lsp-[0-9]+' || true`
   - `git log dev..HEAD --pretty=format:"---%ncommit: %h%nsubject: %s%n%n%b%n"` for `lsp-data`
   - `git diff --stat <base>...HEAD`
   - `gh auth status`
   - `gh repo view --json nameWithOwner,defaultBranchRef,url,viewerPermission`
2. Stop before changing remote state when:
   - `gh` is missing or unauthenticated.
   - The checkout is detached.
   - The current branch is the default/base branch.
   - There are uncommitted changes and the user did not explicitly ask to PR
     with a dirty worktree.
   - The branch has no commits ahead of the chosen base.
3. Choose the base branch:
   - For `lsp-data`, default to `dev`.
   - Otherwise use `gh repo view --json defaultBranchRef`.
   - Respect any user-provided base branch.
4. Build the PR title:
   - Prefer the user-provided title.
   - Otherwise use the latest commit subject when the branch has one cohesive
     commit.
   - Otherwise summarize the branch name in sentence case.
5. Look for plan notes:
   - Extract the ticket ID from the branch case-insensitively, normalizing it to
     uppercase `LSP-XXXX`.
   - If a ticket ID exists, search `notes/plans/<LSP-ID>-*.md` relative to the
     repo root.
   - If a matching plan file exists, read it and prefer it over commit messages
     when generating the PR description.
6. Build the PR body:
   - Keep it concise; default to 20 lines maximum unless the user asks for more.
   - Use this structure for command-only output:
     `## Summary`, `## Changes`, `## Notes`.
   - For actual PR creation/update, include `## Validation` when validation
     commands were run or need to be reported as not run.
   - Ground claims in the plan file, full commit messages, and changed files.
   - Do not invent validation results.
7. Push and create/update the PR only after the preflight is clean:
   - Push with `git push -u origin HEAD`.
   - Use `gh pr create --base <base> --head <branch> --title <title> --body-file <file>`.
   - If a PR already exists for the branch, use `gh pr edit` instead of opening
     a duplicate.
8. Report the PR URL and useful next command:
   - `gh pr checks --watch` for CI status.
   - `gh pr view --web` when the user wants to review in the browser.

## Command-Only Mode

When the user asks only to prepare a command, do not push, create, or update a
PR. Produce one ready-to-run shell command:

```bash
gh pr create \
  --base dev \
  --head <current-branch> \
  --title "<one-line goal summary>" \
  --body "<generated markdown description>"
```

Escape quotes and newlines so the command can be pasted directly into a shell.
Use `--print-command` on `.agents/scripts/pr.sh` for this mode.

## Helper Script

Use `.agents/scripts/pr.sh` for the standard workflow. Read or patch
it first if the requested behavior differs from its options.

```bash
.agents/scripts/pr.sh --base dev
.agents/scripts/pr.sh --base dev --draft
.agents/scripts/pr.sh --base dev --dry-run
.agents/scripts/pr.sh --base dev --print-command
.agents/scripts/pr.sh --base dev --body-only
.agents/scripts/pr.sh --base test --title "fix(etl): handle empty batches"
```

The script prints the generated PR body path during dry runs and removes its
temporary body file after successful create/update.

## lsp-data Defaults

For this repository:

- Use `dev` as the default PR base.
- Extract ticket IDs with case-insensitive `LSP-XXXX` matching; this repo often
  uses lower-case ticket IDs in branch names.
- Search for planning notes at `notes/plans/<LSP-ID>-*.md`; if present, use the
  plan content first, then supplement with commits and changed files.
- Mention cross-repo impact when changes touch shared `gen_epix` models, remote
  app clients, API contracts, or ETL behavior that depends on `../gen-epix-api`.
- Prefer validation commands from `AGENTS.md`: `pytest`, `python run.py test_all`,
  `ruff check --fix`, `ruff format`, and `ty check .`.
- Do not invent validation results. If a command was not run, say so directly.

## Safety Rules

- Never merge a PR unless the user explicitly asks.
- Never force-push unless the user explicitly asks and the target branch is
  confirmed.
- Never commit unstaged or unrelated work as part of this skill.
- Do not overwrite a user-authored PR title/body unless the user asked to update
  the existing PR.
