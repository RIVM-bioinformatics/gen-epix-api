---
name: review
description: >-
  Review a GitHub PR for logical soundness and repo convention adherence, optionally
  checking the changes against a stated task description. Runs repository quality gates
  (Black, isort, tests, conventions), analyzes the diff, generates review comments,
  gets user approval, and posts approved comments to the PR with code context. Accepts an
  optional task description and an optional PR number; with neither, it falls back to the
  open PR for the current branch. Use when the user asks to review a PR, validate changes
  against a task before merge, or check a branch for issues.
argument-hint: '[task description] [#PR-number] — both optional; PR needs a leading #; defaults to the current branch''s open PR'
---

# PR Review

Comprehensive review of GitHub pull request changes. This skill validates code quality,
checks logical soundness (optionally against a stated task description), and surfaces
review comments for user approval before posting to GitHub.

## Arguments

Both arguments are optional and are passed as a single raw string that the skill parses
(there is no shell word-splitting — the task description may contain spaces freely):

- **Task description** (optional) — Free text describing what the PR is *supposed* to
  accomplish. When provided, Step 3 checks whether the diff actually fulfills it. May
  contain any number of spaces (including bare numbers); no quoting is needed.
- **PR number** (optional) — The GitHub PR number for the current repo. Written as a
  trailing `#`-prefixed integer, e.g. `#42`. The `#` is **required** — a bare trailing
  integer is never treated as a PR number.

### Parsing rule

Parse the raw argument string as follows:

1. **PR number** — If the argument string ends with `#<int>`, that integer is the PR
   number. Strip the `#<int>` token from the string. A bare trailing integer (no `#`) is
   **not** a PR number — it stays part of the task description. This avoids misreading a
   task that ends in a number.
2. **Task description** — Whatever remains (trimmed) is the task description. If empty,
   there is no task description.

Resolved behavior:

| Invocation | Task description | PR number |
|---|---|---|
| `/review` | none | infer from current branch |
| `/review #42` | none | 42 |
| `/review 42` | "42" | infer from current branch |
| `/review implement batch retry backoff` | "implement batch retry backoff" | infer from branch |
| `/review implement batch retry backoff #42` | "implement batch retry backoff" | 42 |
| `/review fix retry for issue 3` | "fix retry for issue 3" | infer from branch |
| `/review fix retry for issue 3 #42` | "fix retry for issue 3" | 42 |

## What it does

1. **Quality gates** — Runs the repository's Black and isort formatting checks, the
  documented test command, and conventions checks. Blocks on failure with clear feedback.
2. **Logical analysis** — Examines the diff for architectural soundness, adherence to repo
   conventions (complexity, nesting, naming, type hints), and correctness of the changes
   without being overly strict on style.
3. **Generate comments** — Proposes inline review comments keyed to specific file locations
   and code snippets, with actionable feedback.
4. **User approval** — Shows each proposed comment and asks the user to approve all, some,
   or none before posting.
5. **Post to GitHub** — Posts approved comments as PR reviews using `gh pr review`, with
   relevant code context.

## Prerequisites

- A GitHub PR to review — either passed by number, or open for the current branch.
- `.env` must have `GITHUB_TOKEN` configured (or `gh` CLI has valid auth).
- When reviewing the current branch's PR, the branch should be checked out with its
  changes staged or committed.

## Process

### Step 1: Resolve the PR

Determine which PR to review from the parsed arguments:

- **PR number provided** — Use it directly: `gh pr view <number> --json number,title,headRefName`.
  Verify the PR exists in the current repo; if not, stop with an error.
- **No PR number** — Infer from the current branch:
  `gh pr view --json number,title,headRefName`. If no open PR exists for the branch, stop
  with an error asking the user to open a PR or pass a PR number explicitly.

If a task description was provided, note it — it drives the intent check in Step 3.

### Step 2: Run quality gates

Run the repository quality checks directly:

- **isort --check-only --diff --profile black --float-to-top --line-length=88 .** —
  Validates import ordering.
- **black -l 88 --check --diff .** — Validates Python formatting.
- **python run.py test_all --include_e2e=False** — Runs the repository's curated test
  suite without E2E tests. For a narrowly scoped review, use the matching documented
  `python run.py test_<app>_<scope>` command instead.

Record each command as pass or fail with its relevant output. If any check fails, the
skill reports the failure clearly and stops. The user must fix the reported issue, rerun
the appropriate repository command, and re-invoke the skill.

Conventions not enforced by the formatting tools, including **no nested functions** and
**no mid-file imports**, are checked in Step 3 by reading the diff directly.

### Step 3: Analyze the diff

Fetch the PR's diff — `gh pr diff <number>` — so the review targets exactly the PR's
changes (not just local `main...HEAD`, which may diverge when reviewing another branch's
PR by number). Analyze it for:

- **Task fulfillment** (only when a task description was provided) — Does the diff actually
  accomplish what the task description states? Flag scope gaps (task asks for X but X is
  missing or only partially done) and scope creep (changes unrelated to the task). This is
  the primary lens when a task description is present.
- **Logical correctness** — Do the changes work without breaking invariants? Are there
  obvious bugs, off-by-one errors, missing error handling at system boundaries?
- **Convention adherence** — Do variable names follow `full_class_name_snake_case`? Are
  functions well-scoped with minimal nesting? Are type hints present on public functions?
- **Architecture fit** — Do the changes respect module boundaries, data flow patterns, and
  existing abstractions? Is there unnecessary refactoring or new dependencies?
- **Test coverage** — Do the changes add or modify tests? Are new public functions tested?

The analysis is **not strict on minor style issues** (e.g., line length near limits, comment
phrasing) — it focuses on issues that would likely cause bugs, confusion, or downstream
failures, and (when given a task) on whether the PR truly delivers the task.

### Step 4: Generate comments

For each finding, the skill composes a review comment with:

- **Location** — File, line range, and the relevant code snippet.
- **Issue** — Clear, specific description of what is wrong or unclear.
- **Suggestion** — Actionable recommendation (e.g., "add type hint", "extract to a function",
  "use early return").

Comments are grouped by severity (critical vs. advisory) and presented to the user for
approval.

### Step 5: Get user approval

The skill displays each proposed comment and asks:

- **Approve all** — Post every comment as-is.
- **Approve selected** — The user picks which comments to post; others are discarded.
- **Approve none** — Discard all comments, end the review without posting.

### Step 6: Post to GitHub

The skill invokes `.agents/scripts/post-pr-comments.sh` to post each approved comment
to the PR. The script uses the GitHub REST API to post inline comments at the specified
file and line range. Each comment includes the code snippet for context.

The script returns a JSON result with the list of successfully posted comments, failed
comments, and any error messages. If posting fails (network error, rate limit, etc.), the
skill reports the error and offers to retry or save the comments to a local file for
manual posting.

## Example workflow

```bash
# Current branch: feature/add-batch-retry, PR #42 open on GitHub.

# Review the current branch's PR, checking it against a task description:
/review implement exponential backoff for batch upload retries

# Or target a specific PR by number (with a task to check against):
/review implement exponential backoff for batch upload retries #42

# Or just review the current branch's PR with no task lens:
/review

# Output:
# [PR] Reviewing #42 "feat(etl): add batch retry backoff"
# [Task] Checking against: "implement exponential backoff for batch upload retries"
# [Quality gates] isort: pass, black: pass, tests: pass, conventions: pass ✓
# [Analyzing diff] Found 3 findings (1 task-gap, 2 advisory)
#
# Comment 1 (task-gap):
# - File: lsp_data/etl/orchestrate/processor.py
# - Lines: 45–52
# - Code snippet: [shown]
# - Issue: Backoff is linear (delay += step), not exponential as the task requires.
# - Suggestion: Use delay *= factor for exponential growth.
#
# Approve this comment? (y/n/all/none/skip)
# > all
#
# [Posting] Comment 1 → lsp_data/etl/orchestrate/processor.py:45
# [Posting] Comment 2 → lsp_data/etl/model/batch.py:18
# [Done] 2 comments posted to PR #42.
```

## Conventions checked

The skill validates adherence to the repo conventions:

- **Formatting** — Import order follows isort and Python formatting follows Black with
  the repository's configured 88-character line length.
- **No nested functions** — All functions defined at module level.
- **All imports at the top** — No mid-file imports.
- **Variable naming** — Full class name in lower_snake_case (e.g., `batch_fetcher`,
  `upload_command_builder`), exception for loop vars (`x`, `y`).
- **Early returns, minimal nesting** — Functions should return early and avoid deeply
  nested blocks.
- **Type hints + docstrings** — All public functions must have type hints and docstrings.

## When to use

- User asks: "review this PR", "review PR 42", "check the PR against this task", "validate
  this branch"
- Verify a PR actually delivers the task it was opened for (pass the task description)
- After making changes on a branch with an open PR: confirm code quality before merge
- Catch issues before final review or deployment
- Ensure new code follows repo conventions before it's reviewed by others

## Troubleshooting

- **No PR found** — Pass a PR number explicitly (with a leading `#`, e.g. `#42`), or check
  out the branch whose PR you want and ensure the PR is open on GitHub.
- **PR number ignored** — The PR number needs a leading `#` (e.g. `#42`); a bare `42` is
  treated as task text, not a PR number.
- **Quality gate fails** — Fix the reported issue, rerun the applicable isort, Black, or
  repository test command, and re-invoke the skill.
- **Can't post to GitHub** — Check that `gh` CLI is authenticated (`gh auth status`) and
  the token has `pull_request` scope.
