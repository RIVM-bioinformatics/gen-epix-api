---
name: manage-jira-issues
description: >-
  Create, query, update, assign, transition, comment on, link, and log work on
  Jira issues through the configured Atlassian MCP server. Use for Jira issue
  management; use implement-jira-issue for end-to-end code delivery from a
  ticket.
---

# Jira Issues

Manage Jira issues through the Atlassian MCP server configured in
`.vscode/mcp.json`. Use the tool names exposed by the current client.

## Resolve the site

Most Jira tools require `cloudId`. Resolve it once and reuse it:

1. If the user supplied an Atlassian site URL, use its hostname as `cloudId`.
2. Otherwise call `getAccessibleAtlassianResources`.
3. Use the result directly when exactly one site is available; ask the user to
   choose when several are returned. Never guess.

`search`, `fetch`, `atlassianUserInfo`, and
`getAccessibleAtlassianResources` derive the site from the access token and do
not need `cloudId`.

## Load details only when needed

- For issue bodies, read [references/templates.md](references/templates.md).
- For fields, issue types, custom fields, or status changes, read
  [references/fields-and-transitions.md](references/fields-and-transitions.md).
- For structured search, duplicate checks, sorting, or pagination, read
  [references/jql-search.md](references/jql-search.md).
- For blockers, links, subtasks, parents, epics, or remote links, read
  [references/links-and-subtasks.md](references/links-and-subtasks.md).

Do not load every reference for an ordinary read or simple comment.

## Core workflow

1. Determine whether the request is a read, create, update, transition, comment,
   worklog, assignment, or link operation.
2. Resolve the site, project, issue type, and required field metadata. Read an
   existing issue before changing it. Search for duplicates before creation.
3. Execute only the requested operation.
4. Report the issue key, resulting state, and browse URL.

For creation, `createJiraIssue` requires a project key, issue type, and summary;
use `additional_fields` for priority, labels, components, versions, dates, and
custom fields. Discover issue types and accepted fields instead of assuming
them. For updates, include only intended fields; collection values replace the
existing collection, so read before adding to one.

For status changes, call `getTransitionsForJiraIssue` and use the returned
transition ID. Never hardcode transition IDs or force an unrelated transition.
Resolve assignees with `lookupJiraAccountId`; ask when lookup is ambiguous.

### Worklogs

Use worklog tooling only when the user asks to log time or update a worklog.
Read the issue first, then call `addWorklogToJiraIssue` when that tool name is
exposed by the current client. A new worklog requires `cloudId`,
`issueIdOrKey`, and `timeSpent` in Jira duration syntax such as `1h 30m`.
Pass `commentBody` only when requested. To update an existing entry, also pass
its `worklogId` and only the fields the user asked to change.

`started` is optional. Preserve an explicit date, time, and UTC offset supplied
by the user; when a local time is ambiguous, ask for its time zone. Otherwise
omit `started` and let Jira default it to the current time. Never infer logged
duration or start time from commits, issue activity, or elapsed wall-clock time.

A worklog is a team-visible accounting write. Confirm the exact issue, duration,
start time, and comment immediately before the call unless the user's current
request already supplied and explicitly authorized those values. Report the
created worklog and the duration recorded.

## Repository context and safety

This repository normally tracks work in the `LSP` project and uses issue keys
in branch names. Confirm the project when it is not evident from the request or
current branch.

- Do not edit fields, transition, assign, comment, link, or log work beyond the
  user request.
- Do not close or resolve issues unless explicitly asked.
- Comments and edits are team-visible. Confirm before writing to an issue the
  user did not ask to modify.
- State blocker-link direction back to the user after creating it.
