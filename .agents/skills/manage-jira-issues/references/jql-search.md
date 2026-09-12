# JQL Search

Use `searchJiraIssuesUsingJql` for structured queries: explicit field filters,
ranges, sorting, and duplicate checks. JQL replaces GitHub's search qualifiers
and is considerably more expressive.

For open-ended content discovery, prefer the Rovo `search` tool described at the
end of this file.

## Calling the tool

```json
{
  "cloudId": "<resolved cloud id>",
  "jql": "project = LSP AND status != Done ORDER BY created DESC",
  "maxResults": 50,
  "fields": ["summary", "status", "assignee", "priority"]
}
```

| Parameter | Notes |
|-----------|-------|
| `jql` | The query. Sorting belongs here via `ORDER BY`, not a separate parameter |
| `maxResults` | 50 to 100 |
| `fields` | Defaults to a standard set; pass `"*all"` for every field including custom fields; include `"comment"` to fetch comments |
| `nextPageToken` | Pagination token from a previous response |
| `searchResultMode` | `issues` (default), `count`, or `all` |

Use `searchResultMode: "count"` only when a total is genuinely needed and no
trusted count exists. Never request a count while paginating with
`nextPageToken`, and reuse a known total for the same query.

## Common queries

| Goal | JQL |
|------|-----|
| Open issues in a project | `project = LSP AND statusCategory != Done` |
| Duplicate check before filing | `project = LSP AND summary ~ "dark mode"` |
| Assigned to me | `assignee = currentUser() AND statusCategory != Done` |
| Recently updated | `project = LSP AND updated >= -7d ORDER BY updated DESC` |
| By issue type and priority | `project = LSP AND issuetype = Bug AND priority = High` |
| By label or component | `labels = authentication AND component = Backend` |
| In a release | `fixVersion = "v1.2"` |
| Blocked issues | `project = LSP AND issueLinkType = "is blocked by"` |
| Subtasks of a parent | `parent = LSP-1234` |
| Unresolved and unassigned | `resolution = Unresolved AND assignee IS EMPTY` |
| Text across fields | `text ~ "sso login"` |

## Operators

- `=`, `!=`, `>`, `>=`, `<`, `<=` for exact and range comparisons.
- `~` for text contains; `!~` for does not contain.
- `IN`, `NOT IN` for sets: `status IN (Open, "In Progress")`.
- `IS EMPTY`, `IS NOT EMPTY` for absence.
- `AND`, `OR`, `NOT` with parentheses for grouping.

## Values and quoting

- Quote values containing spaces: `status = "In Test"`.
- Relative dates use `-7d`, `-4w`, `startOfDay()`, `endOfMonth()`.
- Functions such as `currentUser()`, `membersOf()`, and `openSprints()` are
  evaluated by JIRA.
- Prefer `statusCategory != Done` over listing every done status, because status
  names are workflow-specific.

## Universal search

`search` performs a Rovo natural-language search across JIRA and Confluence. It
takes a single `query` parameter and needs no `cloudId`, because the site is
derived from the access token.

It returns ARIs such as `ari:cloud:jira:<cloudId>:issue/10107`. Pass one to
`fetch` as `id` to read the full content.

Choose between the two:

- Use `search` for open-ended discovery, cross-product lookups, and when the
  user describes what they want in prose.
- Use `searchJiraIssuesUsingJql` when the request maps to structured filters,
  needs sorting or pagination, or explicitly mentions JQL.
