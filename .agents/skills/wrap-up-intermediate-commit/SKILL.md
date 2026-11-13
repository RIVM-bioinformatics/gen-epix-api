---
name: wrap-up-intermediate-commit
description: "Wrap up a chunk of implementation work for a clean intermediate commit in a series leading to a review-ready PR. Use when asked to prepare or wrap up an intermediate commit: inventory saved changes, reconcile unit tests, fix scoped lint issues, update docstrings, and draft a Conventional Commits message. Does not stage, commit, push, or prepare the final PR unless separately requested."
argument-hint: "Optional: implementation chunk, file scope, or initializer modules to include"
---

# Wrap Up an Intermediate Commit

Prepare the current implementation chunk for an intermediate commit, not the
final review-ready PR. Complete the steps below in order. Do not run unrelated
full suites, update release metadata or generated reports, push, create a PR, or
perform a final PR-readiness audit. Do not stage or commit without a separate
explicit request. The final output of this workflow is a proposed commit message
and an honest account of verification and blockers.

## 1. Save and Inventory Changes

1. Save all open files using VS Code's `workbench.action.files.saveAll` command
   through an available editor tool. Check whether any files remain unsaved;
   untitled buffers or save failures need user action. If saving or confirming
   saved state is unavailable, ask the user to save all files and confirm before
   relying on the filesystem inventory. Do not claim that Git sees unsaved edits.
2. Inspect `git status --short`, `git diff HEAD --name-status`, and
   `git diff HEAD`. This comparison includes both staged and unstaged tracked
   changes relative to the last commit. Also list untracked, non-ignored files
   with `git ls-files --others --exclude-standard` and read relevant files;
   untracked content is absent from the diff. Inspect renames and deletions too.
3. Identify the intended chunk, preserving unrelated user changes and index
   state. If unrelated work makes ownership ambiguous, ask which changes belong
   in this commit. Do not undo changes or automatically stage everything.
4. Maintain two explicit lists: all changed files in the chunk, and actual code
   modules requiring tests, lint, and documentation. Exclude tests, documentation,
   data, configuration, and generated artifacts from the actual-code list.
   Exclude `__init__.py` unless the user specifically includes it. Deleted modules
   require test reconciliation, not new tests for nonexistent source. For code
   outside `gen_epix`, ask for the test mapping as required by create-unit-test;
   do not silently skip executable scripts or invent a mapping.

## 2. Reconcile and Update Unit Tests

Load [create-unit-test](../create-unit-test/SKILL.md). Apply it separately to
every actual code module in the worklist, including modules with existing tests.
Its mandatory logic-review and suspected-defect approval gates still apply before
creating, moving, splitting, or updating tests. Do not encode a suspected bug as
expected behavior or silently repair it while writing tests.

1. Run its inventory script:

   ```text
   python .agents/skills/create-unit-test/scripts/list_missing_or_unmatched_tests.py
   ```

   Use `--include-init` only for explicitly included initializers and filter those
   findings to the authorized scope. Inventory is repository-wide; remediation
   stays within the implementation chunk and necessary adjacent changes.
2. For each `UNMATCHED_TEST`, consider whether its filename suggests coverage of
   a worklist module; also check imports so misleading names do not hide existing
   coverage. Inspect plausible candidates to confirm their behavior under test.
3. After logic review, move or rename an entirely relevant single-module test
   using `git mv <old> <canonical>` (create its destination directory first).
   Never overwrite an existing canonical test. For untracked tests, use an
   available filesystem move and disclose why `git mv` cannot apply; do not
   stage them just to enable the move. Git moves change the index, so record that
   exception and preserve unrelated staging.
4. If a test covers multiple modules, factor only the relevant tests into the
   canonical module, reuse appropriate fixtures, and preserve unrelated coverage.
   Update imports and references affected by moves/splits. Ask before unrelated
   restructuring, as create-unit-test requires. Reconcile stale tests for deleted
   or renamed source without deleting still-relevant coverage blindly.
5. For every missing canonical test, create it through create-unit-test, or
   update it if the move/split just created it. Update every existing canonical
   test for changed source, even when it was not reported missing. Follow that
   skill's edge-case matrix, mock conventions, launch-folder registration, and
   focused file-runner validation. If a referenced runner is absent, report the
   blocker and obtain agreement on an alternative; do not claim it ran.
6. Rerun the inventory after reconciliation and resolve findings for worklist
   modules. Report unrelated unmatched tests without restructuring them.

## 3. Fix Scoped Lint Issues and Retest

Fix all lint issues in actual code modules and every created, moved, split, or
updated test file. Use the repository's current formatter/linter configuration,
with exact file selections. The guide specifies Black at line length 88, isort
with the Black profile, and pylint with `C0301` disabled; inspect current
configuration before invoking them. Check editor diagnostics as well. Do not
suppress issues wholesale or format the whole repository for a focused chunk.

Immediately after changing actual code, run its corresponding focused unit tests
to check behavior preservation; after focused cases pass, run the complete target
test module. Test edits also require their focused validation. Diagnose failures
before editing and honor create-unit-test's approval gate for suspected defects.

If fixing an issue requires changes in a previously unchanged module, add it to
the changed-file and actual-code lists, repeat step 2 for that module, then lint
and test it. Necessary adjacent fixes are in scope; unrelated cleanup is not.
Repeat until all scoped lint issues are fixed and corresponding tests pass, or
report a concrete blocker. Do not call the chunk clean while gates remain unmet.

## 4. Update Docstrings

Use [write-docstring](../write-docstring/SKILL.md) for every changed actual code
module and its contents, including modules added during lint repairs. Follow its
bottom-up review, Google-style requirements, and preservation of accurate existing
documentation. Review all in-scope definitions, not just changed lines. Do not
introduce behavior changes merely to document code.

Run its scoped audit, then recheck formatting, lint, and diagnostics for edited
files. Run affected unit tests after any executable change; disclose documentation
audit limitations or unresolved findings. Reinspect the final diff against HEAD,
including new files, to confirm all changes still belong to the chunk.

## 5. Format code and sort imports

Ensure that all changed files adheres to the project's formatting standards and 
that imports are properly sorted. This helps maintain consistency and readability
across the codebase.

## 6. Draft the Commit Message

Use the message conventions in [commit](../commit/SKILL.md), but do not execute
its staging or commit steps. Inspect the final intended diff, branch name, and
previous two commit subjects. Use the intended chunk rather than only staged
changes because this workflow does not stage files.

Draft `type(<scope>): <description>` with a compact imperative subject and an optional
short body only when useful. If the chunk contains unrelated purposes, propose
separate messages and file groups; do not silently stage or split commits. For fixes
create one `fix(scope): <description> in <path>` line per fixed issue, whereby scope is
the name of the folder directly under the top level code folder and path is the remainder
of the path after this folder separated by dots.

Report the proposed message, code/test files prepared, any moves or launch changes,
checks actually run and their outcomes, and remaining blockers. Distinguish this
intermediate verification from final PR readiness. Creating the intermediate
commit itself requires a separate explicit request or existing explicit authority.