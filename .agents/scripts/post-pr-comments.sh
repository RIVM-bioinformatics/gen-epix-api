#!/usr/bin/env bash
# Post inline review comments to a GitHub PR via the REST API.
# Shared by Claude Code, Codex, and GitHub Copilot.
#
# Input (stdin): JSON {pr_number, comments: [{file, line, side?, body}, ...]}
#   - pr_number: the target PR number (required)
#   - comments[].file: path relative to repo root (required)
#   - comments[].line: line number in the PR diff to attach the comment to (required)
#   - comments[].side: "RIGHT" (default, new code) or "LEFT" (old code) — optional
#   - comments[].body: markdown comment body (required)
# Output (stdout): JSON {success, posted: [idx...], failed: [{index, file, line, error}], error}
# Exit 0 always; the caller inspects the JSON.
set -euo pipefail

input=$(cat)
pr_number=$(echo "$input" | jq -r '.pr_number // empty')
comments=$(echo "$input" | jq -c '.comments // empty')

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

comment_count=$(echo "$comments" | jq 'length')
for i in $(seq 0 $((comment_count - 1))); do
  comment=$(echo "$comments" | jq -c ".[$i]")
  file=$(echo "$comment" | jq -r '.file')
  line=$(echo "$comment" | jq -r '.line')
  side=$(echo "$comment" | jq -r '.side // "RIGHT"')
  body=$(echo "$comment" | jq -r '.body')

  # -F sends typed fields (line as an integer); -f would stringify it.
  if err=$(gh api --method POST \
    "repos/{owner}/{repo}/pulls/$pr_number/comments" \
    -f body="$body" \
    -f commit_id="$head_sha" \
    -f path="$file" \
    -F line="$line" \
    -f side="$side" 2>&1 >/dev/null); then
    posted_json=$(echo "$posted_json" | jq --argjson idx "$i" '. + [$idx]')
  else
    failed_json=$(echo "$failed_json" | jq \
      --argjson idx "$i" --arg file "$file" --arg line "$line" --arg err "$err" \
      '. + [{index: $idx, file: $file, line: ($line | tonumber), error: $err}]')
  fi
done

failed_count=$(echo "$failed_json" | jq 'length')
success=$([ "$failed_count" -eq 0 ] && echo true || echo false)

jq -n \
  --argjson posted "$posted_json" \
  --argjson failed "$failed_json" \
  --argjson success "$success" \
  '{success: $success, posted: $posted, failed: $failed, error: ""}'
