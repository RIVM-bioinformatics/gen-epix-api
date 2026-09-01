#!/usr/bin/env bash
set -euo pipefail

base=""
title=""
body_file=""
draft=false
dry_run=false
skip_push=false
allow_dirty=false
print_command=false
body_only=false

usage() {
  cat <<'USAGE'
Usage: pr.sh [options]

Options:
  --base BRANCH       Base branch. Defaults to dev for lsp-data, otherwise repo default.
  --title TITLE       PR title. Defaults to plan notes, one commit, or branch goal.
  --body-file FILE    Use an existing PR body file instead of generating one.
  --draft             Create the PR as a draft.
  --dry-run           Print planned actions without pushing or creating/updating a PR.
  --print-command     Print a ready-to-run gh pr create command without executing it.
  --body-only         Print only the generated PR body without executing anything.
  --skip-push         Do not push before creating/updating the PR.
  --allow-dirty       Continue even when the worktree has uncommitted changes.
  -h, --help          Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      base="${2:?missing value for --base}"
      shift 2
      ;;
    --title)
      title="${2:?missing value for --title}"
      shift 2
      ;;
    --body-file)
      body_file="${2:?missing value for --body-file}"
      shift 2
      ;;
    --draft)
      draft=true
      shift
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    --print-command)
      print_command=true
      shift
      ;;
    --body-only)
      body_only=true
      shift
      ;;
    --skip-push)
      skip_push=true
      shift
      ;;
    --allow-dirty)
      allow_dirty=true
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

branch_title() {
  local branch_name="$1"
  echo "$branch_name" | sed -E 's/^[A-Za-z]+-[0-9]+-//; s/[-_]+/ /g'
}

title_from_branch() {
  local branch_name="$1"
  local ticket_id="$2"
  local summary

  summary="$(branch_title "$branch_name")"
  if [[ -n "$ticket_id" ]]; then
    echo "${ticket_id}: ${summary}"
  else
    echo "$summary"
  fi
}

ticket_id_from_branch() {
  local branch_name="$1"
  echo "$branch_name" | grep -oiE 'lsp-[0-9]+' | head -1 | tr '[:lower:]' '[:upper:]' || true
}

plan_file_for_ticket() {
  local ticket_id="$1"
  if [[ -z "$ticket_id" || ! -d notes/plans ]]; then
    return 0
  fi

  find notes/plans -maxdepth 1 -type f -iname "${ticket_id}-*.md" | sort | head -1
}

first_plan_line() {
  local plan_file="$1"
  sed -E '/^[[:space:]]*$/d; /^[[:space:]]*#/d' "$plan_file" | head -1
}

generated_body() {
  local base_branch="$1"
  local temp_file="$2"
  local ticket_id="$3"
  local plan_file="$4"
  local summary

  summary="$(branch_title "$branch")"
  if [[ -n "$plan_file" ]]; then
    summary="$(first_plan_line "$plan_file")"
  fi

  if [[ -n "$ticket_id" && "$summary" != "$ticket_id"* ]]; then
    summary="${ticket_id}: ${summary}"
  fi

  {
    echo "## Summary"
    echo "$summary"
    echo
    echo "## Changes"
    git log --reverse --format='- %s' "${base_branch}..HEAD" 2>/dev/null | head -3
    echo
    echo "## Notes"
    if [[ -n "$plan_file" ]]; then
      echo "- Plan: \`${plan_file}\`."
    fi
    echo "- Generated from branch \`${branch}\` against \`${base_branch}\`."
  } | head -20 >"$temp_file"
}

print_ready_command() {
  local base_branch="$1"
  local head_branch="$2"
  local pr_title="$3"
  local pr_body_file="$4"

  printf "gh pr create \\\\\n"
  printf "  --base %q \\\\\n" "$base_branch"
  printf "  --head %q \\\\\n" "$head_branch"
  printf "  --title %q \\\\\n" "$pr_title"
  printf "  --body %q\n" "$(cat "$pr_body_file")"
}

require_command git
require_command gh

gh auth status >/dev/null

repo_name="$(gh repo view --json nameWithOwner --jq .nameWithOwner)"
repo_default_branch="$(gh repo view --json defaultBranchRef --jq .defaultBranchRef.name)"
branch="$(git branch --show-current)"
ticket_id="$(ticket_id_from_branch "$branch")"
plan_file="$(plan_file_for_ticket "$ticket_id")"

if [[ -z "$branch" ]]; then
  echo "Cannot create a PR from a detached HEAD." >&2
  exit 1
fi

if [[ -z "$base" ]]; then
  if [[ "$repo_name" == "RIVM-bioinformatics/lsp-data" ]]; then
    base="dev"
  else
    base="$repo_default_branch"
  fi
fi

if [[ "$branch" == "$base" || "$branch" == "$repo_default_branch" ]]; then
  echo "Refusing to create a PR from base/default branch '$branch'." >&2
  exit 1
fi

if [[ "$allow_dirty" == false && -n "$(git status --porcelain)" ]]; then
  echo "Worktree has uncommitted changes. Commit/stash them or pass --allow-dirty." >&2
  git status --short
  exit 1
fi

git fetch origin "$base" >/dev/null 2>&1 || true
base_ref="origin/$base"
if ! git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
  base_ref="$base"
fi

ahead_count="$(git rev-list --count "${base_ref}..HEAD")"
if [[ "$ahead_count" == "0" ]]; then
  echo "Current branch has no commits ahead of $base_ref." >&2
  exit 1
fi

if [[ -z "$title" ]]; then
  if [[ -n "$plan_file" ]]; then
    title="$(first_plan_line "$plan_file")"
  elif [[ "$ahead_count" == "1" ]]; then
    title="$(git log -1 --format=%s)"
  else
    title="$(title_from_branch "$branch" "$ticket_id")"
  fi
fi

if [[ -z "$title" ]]; then
  title="$(title_from_branch "$branch" "$ticket_id")"
fi

created_temp_body=false
if [[ -z "$body_file" ]]; then
  body_file="$(mktemp "${TMPDIR:-/tmp}/pr.XXXXXX")"
  created_temp_body=true
  generated_body "$base_ref" "$body_file" "$ticket_id" "$plan_file"
fi

existing_pr_url="$(gh pr list --head "$branch" --json url --jq '.[0].url // ""')"

if [[ "$body_only" == true ]]; then
  cat "$body_file"
  if [[ "$created_temp_body" == true ]]; then
    rm -f "$body_file"
  fi
  exit 0
fi

if [[ "$print_command" == true ]]; then
  print_ready_command "$base" "$branch" "$title" "$body_file"
  if [[ "$created_temp_body" == true ]]; then
    rm -f "$body_file"
  fi
  exit 0
fi

echo "Repository: $repo_name"
echo "Branch: $branch"
if [[ -n "$ticket_id" ]]; then
  echo "Ticket: $ticket_id"
fi
echo "Base: $base"
echo "Title: $title"
echo "Body file: $body_file"
if [[ -n "$existing_pr_url" ]]; then
  echo "Existing PR: $existing_pr_url"
fi

if [[ "$dry_run" == true ]]; then
  echo "Dry run: no push or PR mutation performed."
  exit 0
fi

if [[ "$skip_push" == false ]]; then
  git push -u origin HEAD
fi

if [[ -n "$existing_pr_url" ]]; then
  gh pr edit "$existing_pr_url" --base "$base" --title "$title" --body-file "$body_file"
  pr_url="$existing_pr_url"
else
  create_args=(--base "$base" --head "$branch" --title "$title" --body-file "$body_file")
  if [[ "$draft" == true ]]; then
    create_args+=(--draft)
  fi
  pr_url="$(gh pr create "${create_args[@]}")"
fi

if [[ "$created_temp_body" == true ]]; then
  rm -f "$body_file"
fi

echo "$pr_url"
echo "Next: gh pr checks --watch"
