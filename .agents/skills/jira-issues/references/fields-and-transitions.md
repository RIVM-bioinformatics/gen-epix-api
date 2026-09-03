# Fields, Issue Types, and Transitions

JIRA field and workflow configuration is per project and per issue type. Always
discover before writing, and never assume a field, type, status, or transition
exists.

## Discovering projects and issue types

```json
{ "cloudId": "<resolved cloud id>", "action": "create" }
```

`getVisibleJiraProjects` accepts an `action` of `view`, `browse`, `edit`, or
`create`. Use `create` to list only projects where the user may file issues, and
`searchString` to narrow by name or key.

`getJiraProjectIssueTypesMetadata` returns the issue types configured for a
project, with their IDs. You need the issue type ID for field metadata.

## Discovering fields

```json
{
  "cloudId": "<resolved cloud id>",
  "projectIdOrKey": "LSP",
  "issueTypeId": "10002",
  "requiredFieldsOnly": true
}
```

`getJiraIssueTypeMetaWithFields` defaults to required fields only, which keeps
the response small and answers the practical question "what must I supply to
create this issue?". Set `requiredFieldsOnly: false` to see optional fields and
their allowed values.

Use this whenever a create or edit call fails with an unknown or unavailable
field error.

## Setting fields

| Operation | Parameter |
|-----------|-----------|
| Create | `additional_fields` on `createJiraIssue` |
| Update | `fields` on `editJiraIssue` |

Both accept field names and `customfield_*` IDs as keys.

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "fields": {
    "priority": { "name": "High" },
    "labels": ["authentication", "regression"],
    "components": [{ "name": "Backend" }],
    "fixVersions": [{ "name": "v9.1.0" }],
    "duedate": "2026-09-30",
    "customfield_10001": "value"
  }
}
```

### Field shapes

- Simple values: strings, numbers, and dates such as `duedate` in `YYYY-MM-DD`.
- Named objects: `priority`, `resolution`, and similar single-select fields take
  `{ "name": "..." }`.
- Arrays of objects: `components` and `fixVersions`.
- Arrays of strings: `labels`.
- Users: `{ "accountId": "..." }`, resolved via `lookupJiraAccountId`.

### Clearing and replacing

Pass an explicit `null` to clear a field. Collection fields are replaced
wholesale, so read current values with `getJiraIssue` before adding to a list.

## Releases instead of milestones

JIRA has no milestones. `fixVersions` is the closest equivalent for release
targeting, and sprints serve iteration planning. Both are project configuration:
a version must already exist on the project before it can be set on an issue.

## Transitions

Status is workflow-driven. There is no writable `status` field.

1. `getTransitionsForJiraIssue` lists transitions valid **from the current
   status**. Set `includeUnavailableTransitions: true` to see why a transition
   is not offered.
2. Match the target status by transition name.
3. `transitionJiraIssue` with the transition `id`.

```json
{
  "cloudId": "<resolved cloud id>",
  "issueIdOrKey": "LSP-1234",
  "transition": { "id": "31" },
  "fields": { "resolution": { "name": "Done" } }
}
```

Some transitions require or permit fields, most commonly `resolution` on a
closing transition. Supply them in `fields` on the transition call when the
workflow demands it.

### Transition rules

- Transition IDs are workflow-specific. Always look them up; never reuse an ID
  across projects or assume a numbering scheme.
- If the target status is unreachable from the current status, report the
  available transitions instead of choosing an unrelated one.
- A reopened issue that still carries a resolution may refuse to transition.
  Clear it with `editJiraIssue` and `{ "resolution": null }`.
- `createJiraIssue` accepts a `transition` to apply during creation, which is
  useful when an issue should not start in the default status.
