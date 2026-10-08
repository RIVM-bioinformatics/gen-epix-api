---
name: wrap-up-module
description: "Wrap up implementation work for one specified Python module using the intermediate-commit workflow. Reconcile its tests, fix scoped lint issues, update docstrings, format and sort imports, then write a Conventional Commit message snippet. Does not stage, commit, push, or edit VS Code launch configuration."
argument-hint: "Required: one gen_epix/<package>/<path>/<module>.py source module or none, in which case the currently active module is used)"
---

# Wrap Up a Module

Prepare implementation work for one explicitly supplied Python module as a
clean intermediate-commit unit. Do not discover the target from changed files,
expand to other modules, stage or commit changes, push, create a PR, or perform a
final PR-readiness audit. Complete the steps below in order. The final filesystem
operation is writing the proposed commit message snippet to the module-specific
path described in Step 6.

## 1. Validate the Target and Inventory Its Changes

1. Require exactly one existing `.py` source path beneath `gen_epix/`. If none is 
   provided, use the currently active module. Resolve relative paths from the 
   repository root. Reject directories, test files, paths outside `gen_epix/`, and
   multiple module paths.
2. Derive the module's canonical unit-test path using
   [create-unit-test](../create-unit-test/SKILL.md). Keep the source module and
   that test as the primary scope; include other files only when they are
   necessary consequences of work on this module.
3. Do not edit `.vscode/launch.json`. Record every newly created test directory
   whose launch entry must be added in a later, centralized update. This is an
   explicit workflow exception for parallel module work; it defers only launch
   configuration and does not waive the other test-path requirements.

## 2. Reconcile and Update This Module's Unit Test

1. Load [create-unit-test](../create-unit-test/SKILL.md) and apply it only to the
   specified module. Do not search for tests outside its canonical unit-test path
   and do not check if other related canonical tests may cover functionality that
   should be covered by this test. Do not edit `launch.json`.
2. If the logic review finds a likely implementation defect, stop before test
   edits and explain the exact source location (as a clickable link), triggering 
   input, expected versus actual behavior, and uncertainty. Ask whether to fix 
   production code first, clarify the contract, or explicitly authorize a regression
   test. Do not silently fix production code, encode suspected buggy behavior, or hide
   it with skip/xfail. If a likely defect emerges later, stop and apply the same 
   approval gate.
3. Factor only this target's relevant tests into its canonical module and reuse 
   appropriate fixtures


## 3. Fix Scoped Lint Issues and Retest

Fix lint issues in the target actual-code module and every test file created,
moved, split, or updated for it. Use the current formatter and linter
configuration, selecting only in-scope files. The repository guide specifies
Black at line length 88, isort with the Black profile, and pylint with
`C0301` disabled; inspect current configuration before running them. Check
editor diagnostics as well. Do not suppress findings wholesale or format the
whole repository.

After changing actual code, immediately run the corresponding focused unit test
to check behavior preservation; after focused cases pass, run the complete
canonical test module. Test edits also require focused validation. Diagnose
failures before editing and honor create-unit-test's approval gate for suspected
production defects.

If a necessary repair affects another previously unchanged module, identify it
as a necessary adjacent change and repeat the relevant test, lint, and
documentation steps for that module only if the user authorizes expanding this
single-module scope. Otherwise stop and report the blocker. Do not call this
module clean while scoped gates remain unmet.

## 4. Update Docstrings

Use [write-docstring](../write-docstring/SKILL.md) for the target actual-code
module and any necessary in-scope code changes. Follow its bottom-up review,
Google-style requirements, and preservation of accurate existing
documentation. Review in-scope definitions, not only changed lines; do not
introduce behavior changes merely to document code.

Run its scoped audit, then recheck formatting, lint, and diagnostics for edited
files. Run affected unit tests after any executable change. Disclose audit
limitations or unresolved findings, and re-inspect the final target diff against
`HEAD`, including new files, to ensure all changes belong to this module.

## 5. Format Code and Sort Imports

Ensure all changed code and test files for this module follow the project's
formatting standards and have properly sorted imports. Use the repository's
current settings and exact file selections; avoid unrelated formatting changes.

## 6. Draft and Write the Commit Message Snippet

Use the message conventions in [commit](../commit/SKILL.md), but do not execute
its staging or commit steps. Inspect the final intended module diff, branch
name, and previous two commit subjects. Use the intended module changes rather
than only staged changes. Do not include unrelated work or deferred launch-file
changes in this module's message.

Draft a compact Conventional Commit subject in the form
`type(scope): <imperative description>` using an appropriate type from
`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`, or
`style`. Infer the scope from the dominant module/component and recent commit
conventions; omit it only when no meaningful scope exists. Keep the lower-case
subject under about 72 characters with no trailing period. Add a short body only
when it genuinely adds value. For fixes, follow the existing wrap-up convention
of one `fix(scope): <description> in <path>` line per fixed issue, with the scope
the code folder directly under the top-level code directory and the remaining
path components separated by dots.

Derive `module_path_with_underscores` from the source path relative to
`gen_epix/`: remove the `.py` suffix and join all remaining path components with
underscores. For example, `gen_epix/casedb/api/abac.py` maps to
`casedb_api_abac`. Write the proposed message text, and only that text, as the
last filesystem operation to:

```text
tmp/wrap-up-module.{module_path_with_underscores}.commit.txt
```

Do not overwrite a snippet belonging to another module. If the destination
already exists and ownership is unclear, stop and ask. Confirm the output path
is ignored/generated scratch content and do not stage or commit it. If any
required workflow gate is blocked, do not write a misleading commit snippet;
report the blocker instead.

Report the target source module and test path, code/test files prepared, any
moves, launch folders deferred for centralized registration, checks actually
run and their outcomes, and remaining blockers. Distinguish this intermediate
verification from final PR readiness. Creating a commit requires a separate
explicit request.
