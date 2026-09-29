# PR Comment Helper Tests

> 20 nodes · cohesion 0.17

## Key Concepts

- **run_helper()** (11 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **test_post_pr_comments.py** (9 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Path** (7 connections)
- **bash_path()** (5 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **is_wsl_bash()** (4 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **test_failed_stubbed_post_returns_failure_detail()** (4 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **test_invalid_json_returns_contract_json()** (4 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **test_missing_jq_returns_contract_json()** (4 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **test_successful_stubbed_post_returns_posted_index()** (4 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **write_executable()** (4 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Test the PR-comment helper without contacting GitHub.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Write a temporary executable using Unix line endings.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Return whether the executable is the Windows WSL launcher.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Return a path understood by Git Bash or WSL Bash.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Run the helper with isolated command stubs.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Return valid JSON and zero when jq is unavailable.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Return the documented invalid-input result.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Report a successful stubbed GitHub API call.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **Report a failed stubbed GitHub API call without a remote retry.** (1 connections) — `.agents/scripts/tests/test_post_pr_comments.py`
- **CompletedProcess** (1 connections)

## Relationships

- No strong cross-community connections detected

## Source Files

- `.agents/scripts/tests/test_post_pr_comments.py`

## Audit Trail

- EXTRACTED: 33 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*