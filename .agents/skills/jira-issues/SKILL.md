---
name: jira-issues
description: 'Create, update, and manage JIRA issues using the Atlassian MCP tools. Use this skill when users want to create bug reports, feature requests, or task issues, update existing issues, set fields (priority, labels, components, fix versions, due dates, custom fields), assign issues, set issue types, transition issue status, add comments or worklogs, link issues, or track blocked-by/blocking relationships. Triggers on requests like "create a JIRA issue", "file a bug in JIRA", "raise a ticket", "update LSP-1234", "set the priority", "move it to In Test", "assign the ticket", "link issues", "blocked by", "blocking", or any JIRA issue management task.'
---

# JIRA Issues

Manage JIRA issues using the Atlassian MCP server (`atlassian-mcp`).

For implementing a ticket end to end (branch, code, tests, PR, final status
transition), use the `implement-jira-issue` skill instead. This skill covers
issue management itself.

## Prerequisite: Resolve `cloudId`

Nearly every JIRA tool requires a `cloudId`. Resolve it once per session and
reuse it.

1. If the user supplied a site link such as `https://site.atlassian.net/...`,
   pass the hostname (`site.atlassian.net`) directly as `cloudId` and skip the
   lookup.
2. Otherwise call `getAccessibleAtlassianResources`, which takes no parameters,
   to list accessible sites.
3. If exactly one site is returned, use its cloud ID. If several are returned,
   ask the user which site to use. Do not guess.

`cloudId` accepts either the site UUID or the site hostname.

The exceptions are `search`, `fetch`, `atlassianUserInfo`, and
`getAccessibleAtlassianResources`. These derive the site from the access token
or the ARI and need no `cloudId`.

## Available Tools

Tool names below omit the client-specific MCP prefix. Use whatever prefixed form
your client exposes for the `atlassian-mcp` server.

### Read operations

| Tool | Purpose | Key parameters |
|------|---------|----------------|
| `getAccessibleAtlassianResources` | List accessible sites and resolve `cloudId` | none |
| `atlassianUserInfo` | Identify the current Atlassian user | none |
| `getJiraIssue` | Read one issue by ID or key, including comments and custom fields | `issueIdOrKey`, `fields`, `expand`, `properties` |
| `searchJiraIssuesUsingJql` | Search issues with JQL | `jql`, `fields`, `maxResults`, `nextPageToken`, `searchResultMode` |
| `search` | Rovo search across JIRA and Confluence | `query` |
| `fetch` | Fetch an issue or page by ARI returned from search | `id` |
| `getVisibleJiraProjects` | List projects by permitted action | `action`, `searchString`, `expandIssueTypes` |
| `getJiraProjectIssueTypesMetadata` | List issue types available in a project | `projectIdOrKey` |
| `getJiraIssueTypeMetaWithFields` | List required and optional fields for an issue type | `projectIdOrKey`, `issueTypeId`, `requiredFieldsOnly` |
| `getTransitionsForJiraIssue` | List valid workflow transitions for an issue | `issueIdOrKey`, `includeUnavailableTransitions` |
| `getIssueLinkTypes` | List link types (Blocks, Duplicate, Clones, Relates) | `cloudId` only |
| `getJiraIssueRemoteIssueLinks` | List remote links on an issue | `issueIdOrKey`, `globalId` |
| `lookupJiraAccountId` | Resolve a user to an account ID for assignment | `searchString` |

### Write operations

| Tool | Purpose | Required parameters |
|------|---------|---------------------|
| `createJiraIssue` | Create an issue or subtask | `projectKey`, `issueTypeName`, `summary` |
| `editJiraIssue` | Update fields on an existing issue | `issueIdOrKey`, `fields` |
| `transitionJiraIssue` | Move an issue through its workflow | `issueIdOrKey`, `transition.id` |
| `addCommentToJiraIssue` | Add or update a comment | `issueIdOrKey`, `commentBody` |
| `createIssueLink` | Link two issues, including blocked-by relationships | `inwardIssue`, `outwardIssue`, `type` |
| `addWorklogToJiraIssue` | Log work against an issue | `issueIdOrKey`, `timeSpent` |

All write tools also require `cloudId`.

Unlike GitHub, JIRA writes are fully supported by MCP tools. No CLI fallback is
required.

## Workflow

1. **Determine action**: Create, update, transition, or query?
2. **Resolve context**: `cloudId`, then project key, issue type, and any fields.
3. **Check for duplicates**: Search with JQL before creating a new issue.
4. **Structure content**: Use the templates in [references/templates.md](references/templates.md).
5. **Execute**: Call the MCP tool.
6. **Confirm**: Report the issue key and browse URL to the user.

## Creating Issues

`createJiraIssue` requires `cloudId`, `projectKey`, `issueTypeName`, and
`summary`.

```json
{
  "cloudId": "<resolved cloud id>",
  "projectKey": "LSP",
  "issueTypeName": "Bug",
  "summary": "Login fails with SSO enabled",
  "description": "## Description\nThe login page crashes when using SSO.",
  "additional_fields": {
    "priority": { "name": "High" },
    "labels": ["authentication"],
    "components": [{ "name": "Backend" }]
  }
}
```

### Optional parameters

| Parameter | Use for |
|-----------|---------|
| `description` | Issue body. Markdown by default; see content format below |
| `assignee_account_id` | Assignee, resolved via `lookupJiraAccountId` |
| `parent` | Parent issue key when creating a subtask |
| `transition` | Apply a workflow transition during creation |
| `additional_fields` | Everything else: priority, labels, components, fix versions, due date, custom fields |

`additional_fields` is the **only** way to set priority, labels, components,
fix versions, and custom fields. There are no dedicated parameters for them.

Verify field names before use. Call `getJiraProjectIssueTypesMetadata` for
available issue types, then `getJiraIssueTypeMetaWithFields` for the fields that
issue type actually accepts. Field availability is per project and per issue
type, so never assume a field exists.

### Content format

`description` and comment bodies accept two formats:

- `contentFormat: "markdown"` (default) for plain text or Markdown.
- `contentFormat: "adf"` for Atlassian Document Format JSON when you need full
  fidelity such as panels, tables, or structured content.

Use `responseContentFormat` to control the format of returned body content.

### Issue types

Prefer the project's configured issue types over labels for categorization.
Typical types are `Bug`, `Task`, `Story`, `Epic`, and `Subtask`, but the exact
set is project-specific. Discover them with
`getJiraProjectIssueTypesMetadata`, and do not invent a type name.

### Summary guidelines

- Be specific and actionable.
- Keep under 72 characters.
- Do not add redundant prefixes like `[Bug]`; the issue type already carries it.
- Examples:
  - `Login fails with SSO enabled` (type Bug)
  - `Add dark mode support` (type Story)
  - `Add unit tests for auth module` (type Task)

### Description structure

Always use the templates in [references/templates.md](references/templates.md).
Choose based on the request:

| User request | Template |
|--------------|----------|
| Bug, error, broken, not working | Bug Report |
| Feature, enhancement, add, new | Feature Request / Story |
| Task, chore, refactor, update | Task |

## Updating Issues

`editJiraIssue` sets fields by name or `customfield_*` ID:

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "fields": {
    "summary": "Updated summary",
    "priority": { "name": "Medium" },
    "labels": ["authentication", "regression"]
  }
}
```

Only include fields you intend to change. To clear a field, pass an explicit
`null`.

Labels and other collection fields are replaced, not merged. Read the current
values with `getJiraIssue` first when you intend to add to an existing list.

## Transitioning Issues

JIRA has no direct `state` field. Status changes go through the project
workflow, and available transitions depend on the current status.

1. Call `getTransitionsForJiraIssue` for the issue.
2. Select the transition whose name matches the target status.
3. Call `transitionJiraIssue` with that transition `id`.

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "transition": { "id": "31" }
}
```

Never hardcode transition IDs; they differ per workflow. If the target status is
unavailable from the current status, report the available transitions rather
than forcing an unrelated one.

If a reopened issue refuses to transition, clear the stale resolution with
`editJiraIssue` using `{ "resolution": null }`.

`transitionJiraIssue` also accepts `update` for advanced field operations and
`historyMetadata` for attribution. Neither is needed for ordinary status
changes.

## Assigning Issues

JIRA assigns by account ID, not username. Resolve it first with
`lookupJiraAccountId`, passing a display name or email as `searchString`:

```json
{ "cloudId": "<resolved cloud id>", "searchString": "jane.doe@example.com" }
```

Apply the returned account ID with `assignee_account_id` on `createJiraIssue`,
or with `editJiraIssue`:

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "fields": { "assignee": { "accountId": "<account id>" } }
}
```

If the lookup returns several candidates, ask the user which one to use rather
than assigning to the first match. Use `atlassianUserInfo`, which takes no
parameters, to identify the current user when the request says "assign it to
me".

## Comments and Worklogs

`addCommentToJiraIssue` adds a comment, or updates an existing one when
`commentId` is supplied. Restrict visibility with `commentVisibility`:

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "commentBody": "Reproduced on the SQLite repository backend.",
  "commentVisibility": { "type": "role", "value": "Developers" }
}
```

`addWorklogToJiraIssue` logs work. `timeSpent` is required for a new worklog and
accepts JIRA duration syntax such as `2h`, `30m`, or `4d`. Supply `started` as
an ISO 8601 date-time to backdate the entry; it defaults to now. Pass
`worklogId` to update an existing worklog.

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "timeSpent": "2h",
  "started": "2026-08-29T09:00:00.000+0000",
  "commentBody": "Investigated the SSO callback failure."
}
```

## Examples

### Example 1: Bug report

**User**: "Create a bug in LSP - the login page crashes when using SSO"

**Action**: call `createJiraIssue` with:

```json
{
  "cloudId": "<resolved cloud id>",
  "projectKey": "LSP",
  "issueTypeName": "Bug",
  "summary": "Login page crashes when using SSO",
  "description": "## Description\nThe login page crashes when users authenticate using SSO.\n\n## Steps to Reproduce\n1. Navigate to the login page\n2. Select 'Sign in with SSO'\n3. The page crashes\n\n## Expected Behavior\nSSO authentication completes and redirects to the dashboard.\n\n## Actual Behavior\nThe page becomes unresponsive and displays an error."
}
```

### Example 2: Feature request with priority

**User**: "Create a high priority feature request for dark mode"

**Action**: call `createJiraIssue` with:

```json
{
  "cloudId": "<resolved cloud id>",
  "projectKey": "LSP",
  "issueTypeName": "Story",
  "summary": "Add dark mode support",
  "description": "## Summary\nAdd a dark mode theme option.\n\n## Motivation\n- Reduces eye strain in low-light environments\n- Increasingly expected by users\n\n## Acceptance Criteria\n- [ ] Toggle switch in settings\n- [ ] Persists user preference\n- [ ] Respects system preference by default",
  "additional_fields": {
    "priority": { "name": "High" }
  }
}
```

### Example 3: Mark an issue as blocked

**User**: "LSP-1234 is blocked by LSP-1200"

**Action**: call `createIssueLink` with `type: "Blocks"`,
`inwardIssue: "LSP-1200"` (the blocker), and `outwardIssue: "LSP-1234"` (the
blocked issue). See [references/links-and-subtasks.md](references/links-and-subtasks.md).

## Common Fields

| Field | Shape | Use for |
|-------|-------|---------|
| `priority` | `{ "name": "High" }` | Urgency |
| `labels` | `["bug"]` | Lightweight categorization |
| `components` | `[{ "name": "Backend" }]` | Owning area of the product |
| `fixVersions` | `[{ "name": "v1.2" }]` | Release targeting, the JIRA equivalent of milestones |
| `duedate` | `"2026-09-30"` | Target date |
| `assignee` | `{ "accountId": "..." }` | Ownership |
| `parent` | `{ "key": "LSP-1000" }` | Epic or parent link |

Priority names, component names, and versions are configured per project.
Validate them before use rather than assuming the defaults exist.

## Repository Context

This repository tracks work in the `LSP` JIRA project; branches such as
`LSP-3743-enhance-docstrings-p1` follow the issue key. Confirm the project key
with the user when it is not evident from the branch or the request.

## Tips

- Always confirm the site and project before creating issues.
- Search for existing issues with JQL before filing a duplicate.
- Ask for missing critical information rather than guessing field values.
- Reference related issues by key in the description, and create a formal link
  when the relationship matters.
- For updates, read the issue first so unchanged values are preserved.
- Report the issue key and its browse URL after any write.

## Safety Rules

- Do not transition an issue, change its assignee, or edit its fields beyond
  what the user asked for.
- Do not close or resolve issues unless the user explicitly asks.
- Do not add worklogs unless the user explicitly asks.
- Comments and edits are visible to the whole team; confirm before posting to an
  issue you did not create in this session.

## Extended Capabilities

| Capability | When to use | Reference |
|------------|-------------|-----------|
| Issue templates | Structuring bug, story, and task descriptions | [references/templates.md](references/templates.md) |
| JQL search | Filtering, cross-project queries, date ranges, duplicate checks | [references/jql-search.md](references/jql-search.md) |
| Links, subtasks, dependencies | Blocked-by/blocking, epics, parents, subtasks | [references/links-and-subtasks.md](references/links-and-subtasks.md) |
| Fields, issue types, transitions | Custom fields, field discovery, workflow status changes | [references/fields-and-transitions.md](references/fields-and-transitions.md) |
