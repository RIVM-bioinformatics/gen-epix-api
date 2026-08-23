---
name: handle-jira-issue
description: >-
  Investigate, implement, test, commit, and open a draft pull request for a
  JIRA issue. Use when asked to handle, implement, fix, or deliver a JIRA
  ticket by its issue ID.
argument-hint: '<JIRA issue ID>'
---

# Handle JIRA Issue

Use this skill only with an issue ID. The invocation prompt is simply:

```text
Handle issue <ISSUE-ID>
```

For example: `Handle issue LSP-3427`.

## 1. Retrieve and Assess the Issue

1. Retrieve the issue through the JIRA MCP using its exact ID. Obtain the
	summary, description, issue type, status, priority, assignee, reporter,
	labels, components, linked issues, acceptance criteria, comments, and
	attachments when available.
2. State the retrieved issue ID, summary, status, and the requested outcome.
	Do not infer requirements that are absent from the ticket.
3. Read the repository instructions and the smallest relevant code, tests,
	documentation, and recent history needed to assess the request against the
	existing implementation.
4. Assess whether the issue is sufficiently complete and logically sound:
	- Identify ambiguous requirements, contradictions, missing acceptance
	  criteria, unspecified edge cases, and invalid assumptions about the code.
	- Check stated implementation alternatives against the codebase. When a
	  stated approach is inconsistent or overlooks a materially better existing
	  pattern, explain the evidence and the viable alternatives.
	- Identify repository, API, persistence, authorization, configuration, and
	  migration implications when applicable.
5. If the issue is incomplete, inconsistent, or requires a product or design
	decision, stop before creating a branch or changing code. Present the
	evidence, the decision needed, and concise options; ask the user how to
	proceed. Do not silently choose a product requirement.

## 2. Create the Work Branch

Only after the assessment is clear:

1. Confirm the worktree state and current branch. Preserve unrelated user
	changes; do not reset, discard, stash, or commit them. If any uncommitted
	files are present, stop and ask the user to commit. A new issue branch must
	start with no uncommitted files.
2. Fetch the remote `dev` branch, then create the new branch directly from
	`origin/dev`, in line with repository policy.
3. Name the branch from `f"{issue_id}-{issue_description}"`, where
	`issue_description` is the issue summary normalized to a Git-safe ASCII
	slug: lowercase, with non-alphanumeric runs replaced by a single hyphen,
	leading/trailing hyphens removed, and truncated only when required by Git or
	remote limits. Preserve the uppercase issue ID prefix. For example,
	`LSP-3427-Age category derivation in different units is incorrect` becomes
	`LSP-3427-age-category-derivation-in-different-units-is-incorrect`.
4. If the normalized name collides with an existing branch for different work,
	stop and ask the user how to disambiguate it.

## 3. Establish the Test Baseline

Before implementation, run the full project test suite:

```text
python run.py test_all
```

Record the command, exit code, passed tests, skipped tests, and failures. This
is the baseline. If tests already fail, identify whether they are related to
the ticket. Continue only when the failures are unrelated and can be preserved
as known baseline failures; otherwise stop and ask the user how to proceed.

## 4. Implement Incrementally

1. Translate the validated requirements into the smallest coherent work items.
	Follow the repository architecture: API routes stay transport-only, domain
	behavior belongs in domain/services/policies, and repository behavior remains
	equivalent across supported repository implementations.
2. For a small cohesive change, implement it with focused automated tests. For
	multiple sizeable work items, complete them one at a time. Each work item
	must include relevant unit tests that cover new behavior and important error
	paths.
3. After each work item, run the narrowest relevant tests. Fix regressions in
	that same slice before continuing.
4. Commit each completed sizeable work item separately using the repository
	commit skill and conventional commit messages. Stage only files belonging to
	that work item; never include unrelated pre-existing changes.
5. Report concise progress after each work item, including tests run and the
	resulting commit hash.

## 5. Final Validation and Delivery

1. Run all relevant focused tests, then rerun:

```text
python run.py test_all
```

2. The final run must retain every passing baseline test and pass all newly
	added tests. Baseline failures may remain only when they are unchanged,
	unrelated, and clearly reported. Do not claim a green suite when the command
	fails.
3. Run any applicable required quality checks for the changed code. Review the
	final diff and worktree to ensure all ticket work is committed and unrelated
	changes remain untouched.
4. Create a final commit for any remaining ticket changes, if needed. Ensure the
	branch is ready for review with no uncommitted ticket work.
5. Create a draft pull request targeting `dev`. Its title and body must cite the
	JIRA ID, summarize implemented behavior, list the validation results, and
	explicitly disclose unchanged baseline failures. Reuse the repository pull
	request skill and do not create a duplicate PR.
6. Only after the draft PR has been created successfully, use the JIRA MCP to
	transition the issue to `In Test`. First retrieve the project transitions;
	select `In Test` when present, otherwise select the closest available testing
	or review status and report the exact status used. Do not transition the
	issue if PR creation failed.
7. Report the branch name, commits, validation results, draft PR URL, and final
	JIRA status.

## Safety Rules

- Never modify an issue, create a branch, write code, commit, or open a PR when
  the assessment identifies an unresolved requirement or decision.
- Never change JIRA fields or status except the final workflow transition.
- Never push directly to `dev`, force-push, merge a PR, or close the JIRA issue
  unless the user explicitly asks.
- Do not weaken authorization, bypass policy lifecycle behavior, or introduce
  repository-specific behavior without explicit justification and parity tests.
- Keep comments, tests, commits, and documentation focused on the issue.
