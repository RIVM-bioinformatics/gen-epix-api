# Review Invocation and Posting

Read this reference only when parsing review arguments, posting approved inline
comments, or troubleshooting those operations.

## Argument parsing

Treat the invocation as one raw string:

1. If it ends with `#<integer>`, use that integer as the PR number and remove
   the token.
2. Treat the trimmed remainder as the optional task description.
3. A bare trailing integer remains task text, not a PR number.

Examples:

| Invocation | Task | PR |
| --- | --- | --- |
| `/review` | none | current branch PR |
| `/review #42` | none | 42 |
| `/review fix retry for issue 3` | full text | current branch PR |
| `/review implement retry #42` | implement retry | 42 |

## Posting approved comments

Send one JSON document on standard input to
`.agents/scripts/post-pr-comments.sh`:

```json
{
  "pr_number": 42,
  "comments": [
    {"file": "gen_epix/example.py", "line": 18, "side": "RIGHT", "body": "Comment"}
  ]
}
```

`start_line` and `start_side` are optional for multi-line comments. Lines must
refer to the PR diff. The helper resolves the PR head SHA, posts through the
GitHub REST API using `gh api`, and returns JSON containing `success`, `posted`,
`failed`, and `error`.

The helper appends the required AI-generated attribution once. Do not post any
comment before the user approves it. If only some posts fail, report the
successful indexes and each failure; ask before retrying.

Posting requires `bash`, `jq`, `git`, and an authenticated `gh` CLI. The helper
returns a JSON failure with exit code 0 when `jq` is unavailable so callers can
continue to inspect the documented result shape.

## Troubleshooting

- No PR: pass `#<number>` or check out a branch with an open PR.
- PR number treated as task text: add the required leading `#`.
- Missing `jq`: install it before retrying the approved posting operation.
- Authentication failure: run `gh auth status` and report the result.
- Invalid position: refresh the diff and use a line on the correct side.
