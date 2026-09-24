# Links, Subtasks, and Dependencies

JIRA expresses hierarchy and dependencies through two distinct mechanisms:

- **Parent/child**: subtasks and epic membership, set with the `parent` field.
- **Issue links**: typed relationships such as Blocks, Relates, Duplicate, and
  Clones, created with `createIssueLink`.

GitHub's sub-issues, task lists, and dependencies all map onto these two.

## Issue links

Discover the available types first, because link type names are configured per
site:

```json
{ "cloudId": "<resolved cloud id>" }
```

Call `getIssueLinkTypes`, then create the link:

```json
{
  "cloudId": "<resolved cloud id>",
  "type": "Blocks",
  "inwardIssue": "LSP-1200",
  "outwardIssue": "LSP-1234",
  "comment": "Blocked pending the schema migration."
}
```

### Direction

Direction is the most common source of error. For directional types such as
`Blocks`:

- `inwardIssue` is the issue that **blocks**.
- `outwardIssue` is the issue that **is blocked**.

So "LSP-1234 is blocked by LSP-1200" becomes `inwardIssue: "LSP-1200"` and
`outwardIssue: "LSP-1234"`.

State the resulting sentence back to the user after linking, so the direction is
verifiable.

### Common link types

| Type | Meaning |
|------|---------|
| `Blocks` | One issue blocks another |
| `Relates` | Non-blocking association |
| `Duplicate` | One issue duplicates another |
| `Clones` | One issue is a clone of another |

## Reading links

`getJiraIssue` returns links when requested. Ask for the `issuelinks` field, or
use `fields: ["*all"]`:

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "fields": ["summary", "status", "issuelinks", "subtasks", "parent"]
}
```

Query link relationships in bulk with JQL, for example
`project = LSP AND issueLinkType = "is blocked by"`.

## Subtasks

Create a subtask by supplying the subtask issue type and the parent key:

```json
{
  "cloudId": "<resolved cloud id>",
  "projectKey": "LSP",
  "issueTypeName": "Subtask",
  "summary": "Add unit tests for the token parser",
  "parent": "LSP-1234"
}
```

The exact subtask type name varies per project. Confirm it with
`getJiraProjectIssueTypesMetadata` before creating.

A subtask inherits its parent's project and cannot be moved to another parent's
project. List existing subtasks through the `subtasks` field or with
`parent = LSP-1234` in JQL.

## Epics and parents

In current JIRA, epic membership uses the same `parent` field as subtasks. Set
it on an existing issue with `editJiraIssue`:

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "fields": { "parent": { "key": "LSP-1000" } }
}
```

Some sites still expose a legacy `Epic Link` custom field. If `parent` is
rejected, inspect the issue type's fields with `getJiraIssueTypeMetaWithFields`
and use the `customfield_*` ID reported there.

## Remote links

`getJiraIssueRemoteIssueLinks` lists links to resources outside JIRA, such as
pull requests and Confluence pages. Use it when reporting where the
implementation of an issue lives.
