---
name: implement-jira-issue
description: >-
  Investigate, implement, test, commit, and open a draft pull request for a
  JIRA issue. Use when asked to implement, fix, or deliver a JIRA ticket by
  its issue ID.
argument-hint: '<JIRA issue ID>'
---

# Implement JIRA Issue

Orchestrate the repository Jira, test, commit, and pull-request skills. Keep
their detailed mechanics in the owning skills.

## 1. Retrieve and assess

1. Use the `jira-issues` skill to retrieve the exact issue, including its
   description, acceptance criteria, status, links, comments, and attachments
   when relevant. State the issue ID, summary, status, and requested outcome.
2. Read the smallest relevant source, tests, configuration, documentation, and
   history needed to test the ticket assumptions.
3. Identify contradictions, missing acceptance criteria, unspecified edge
   cases, and repository, API, persistence, authorization, configuration, or
   migration implications.
4. Stop before mutation if a product or design decision remains unresolved.
   Present the evidence and ask for the decision; do not invent requirements.

## 2. Create the work branch

Only after assessment:

1. Require a clean worktree. Preserve unrelated changes; never reset, discard,
   stash, or commit them.
2. Fetch `origin/dev` and create a new branch directly from it without tracking
   `dev`: `git switch --create <branch-name> --no-track origin/dev`.
3. Name it `<ISSUE-ID>-<summary-slug>`, preserving the uppercase issue ID and
   using a lowercase, Git-safe ASCII slug. Stop on a collision.
4. Before the first push, verify the branch has no `dev` upstream. Publish with
   `git push -u origin HEAD:refs/heads/<branch-name>` and verify that it tracks
   the matching remote branch.

## 3. Baseline and implement

1. Unless the user declines a baseline, use the `pytest-run` skill to capture
   `python run.py test_all --include_e2e=False`. Record its exit status, summary,
   and existing failures. Run E2E or specialized external-service tests only
   when the issue requires them.
2. Stop for related baseline failures. Continue past unrelated failures only
   when they can be preserved and reported explicitly.
3. Implement the smallest coherent work items. Add focused tests for changed
   behavior and important error paths, following `AGENTS.md`.
4. After each work item, run the narrowest relevant named suite or precise
   pytest selection using the `pytest-run` skill. Repair failures in that slice
   before continuing.

## 4. Validate and deliver

1. Run focused tests and applicable quality checks from `AGENTS.md`, then
   repeat the baseline suite unless the user declined it. Preserve every
   baseline pass and report any unchanged unrelated failures.
2. Review the final diff and worktree. Use the `commit` skill for cohesive
   commits; stage only ticket work.
3. Use the `pr` skill to create or update one draft PR targeting `dev`. Include
   the Jira ID, behavior summary, actual validation, and baseline failures.
4. Only after PR creation succeeds, use the `jira-issues` skill to retrieve
   available transitions and move the issue to `In Test` when that transition
   exists. If it does not, report the available transitions instead of choosing
   a different status.
5. Report the branch, commits, validation, draft PR URL, and final Jira status.

## Safety

- Never mutate Jira, create a branch, write code, commit, or open a PR while a
  requirement decision remains unresolved.
- Never push directly to `dev`, force-push, merge, close the issue, or change
  unrelated Jira fields unless the user explicitly asks.
- PR creation is the gate for the final status transition.
