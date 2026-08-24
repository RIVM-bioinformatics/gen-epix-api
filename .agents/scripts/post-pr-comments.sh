#!/usr/bin/env bash
# Post inline review comments to a GitHub PR via the REST API.
# Shared by Claude Code, Codex, and GitHub Copilot.
#
# Input (stdin): JSON {pr_number, comments: [{file, line, start_line?, start_side?, side?, body}, ...]}
#   - pr_number: the target PR number (required)
#   - comments[].file: path relative to repo root (required)
#   - comments[].line: ending line number in the PR diff to attach the comment to (required)
#   - comments[].start_line: starting line for a multi-line comment (optional)
#   - comments[].start_side: "RIGHT" or "LEFT" for the start line (optional)
#   - comments[].side: "RIGHT" (default, new code) or "LEFT" (old code) — optional
#   - comments[].body: markdown comment body (required)
# Output (stdout): JSON {success, posted: [idx...], failed: [{index, file, line, error}], error}
# Exit 0 always; the caller inspects the JSON.
set -euo pipefail

ai_attribution='*AI-generated comment; not written by the person posting this review.*'

input=$(cat)
if ! jq -e . >/dev/null 2>&1 <<<"$input"; then
  jq -n '{success: false, posted: [], failed: [], error: "invalid JSON input"}'
  exit 0
fi
if ! pr_number=$(jq -er '.pr_number // empty' <<<"$input"); then
  jq -n '{success: false, posted: [], failed: [], error: "pr_number is missing or null"}'
  exit 0
fi
if ! comments=$(jq -ce '.comments | select(type == "array")' <<<"$input"); then
  jq -n '{success: false, posted: [], failed: [], error: "comments is missing or not an array"}'
  exit 0
fi

if [[ -z "$pr_number" ]]; then
  jq -n '{success: false, posted: [], failed: [], error: "pr_number is missing or null"}'
  exit 0
fi
if [[ -z "$comments" || "$comments" == "null" ]]; then
  jq -n '{success: false, posted: [], failed: [], error: "comments is missing or null"}'
  exit 0
fi

root=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root"

# The head commit the comments anchor to must be the PR's head SHA, not local HEAD
# (they differ when reviewing another branch's PR by number). gh fills {owner}/{repo}.
head_sha=$(gh pr view "$pr_number" --json headRefOid --jq '.headRefOid' 2>/dev/null || true)
if [[ -z "$head_sha" ]]; then
  jq -n --arg pr "$pr_number" \
    '{success: false, posted: [], failed: [], error: ("could not resolve head SHA for PR #" + $pr)}'
  exit 0
fi

posted_json="[]"
failed_json="[]"

comment_count=$(jq 'length' <<<"$comments")
for i in $(seq 0 $((comment_count - 1))); do
  comment=$(jq -c ".[$i]" <<<"$comments")
  file=$(jq -r '.file // empty' <<<"$comment")
  line=$(jq -r '.line // empty' <<<"$comment")
  start_line=$(jq -r '.start_line // empty' <<<"$comment")
  side=$(jq -r '.side // "RIGHT"' <<<"$comment")
  start_side=$(jq -r '.start_side // empty' <<<"$comment")
  body=$(jq -r '.body // empty' <<<"$comment")

  if [[ -z "$file" || -z "$line" || -z "$body" ||
        ! "$line" =~ ^[1-9][0-9]*$ ||
        ( -n "$start_line" && ! "$start_line" =~ ^[1-9][0-9]*$ ) ||
        ( "$side" != "LEFT" && "$side" != "RIGHT" ) ||
        ( -n "$start_side" && "$start_side" != "LEFT" && "$start_side" != "RIGHT" ) ]]; then
    failed_json=$(jq \
      --argjson idx "$i" --arg file "$file" --arg line "$line" \
      '. + [{index: $idx, file: $file, line: $line, error: "file, body, and positive integer line are required; sides must be LEFT or RIGHT"}]' \
      <<<"$failed_json")
    continue
  fi
  if [[ "$body" != *"$ai_attribution"* ]]; then
    body="$body

$ai_attribution"
  fi

  # -F sends typed fields (line as an integer); -f would stringify it.
  api_args=(-f body="$body" -f commit_id="$head_sha" -f path="$file" -F line="$line" -f side="$side")
  if [[ -n "$start_line" ]]; then
    api_args+=(-F start_line="$start_line" -f start_side="${start_side:-$side}")
  fi
  if err=$(gh api --method POST \
    "repos/{owner}/{repo}/pulls/$pr_number/comments" \
    "${api_args[@]}" 2>&1 >/dev/null); then
    posted_json=$(echo "$posted_json" | jq --argjson idx "$i" '. + [$idx]')
  else
    failed_json=$(echo "$failed_json" | jq \
      --argjson idx "$i" --arg file "$file" --arg line "$line" --arg err "$err" \
      '. + [{index: $idx, file: $file, line: $line, error: $err}]')
  fi
done

failed_count=$(echo "$failed_json" | jq 'length')
success=$([ "$failed_count" -eq 0 ] && echo true || echo false)

jq -n \
  --argjson posted "$posted_json" \
  --argjson failed "$failed_json" \
  --argjson success "$success" \
  '{success: $success, posted: $posted, failed: $failed, error: ""}'
