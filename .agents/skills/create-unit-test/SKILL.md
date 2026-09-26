---
name: create-unit-test
description: "Create or update pytest unit tests for exactly one Python module. Use when asked to create, add, extend, refresh, or update unit tests, including after implementation changes. Assess module logic first and ask the user about likely defects before editing tests; cover input edge cases, mirror source paths, enforce test filenames, and register new test folders in VS Code launch configurations."
argument-hint: "<Python source module or existing unit test path>"
---

# Create or Update a Unit Test

## Scope and Prerequisites

- Test exactly one Python source module per invocation. If the request names
  several modules, ask which one to handle first. If only a test is supplied,
  identify its source module before proceeding; ask when the target is ambiguous.
- Inspect existing tests by both filename and imports of the target module.
  An existing test usually means the user wants it updated to match the current
  module, not a second competing test file. Preserve unrelated user edits.
- Use nearby fixtures and test utilities. Dependencies may be exercised or
  replaced at their boundaries, but do not add tests of other modules' behavior.

## 1. Mandatory Logic Review Before Test Edits

This gate applies equally to new tests and updates to existing tests. Do not
create, update, move, or rename test files until this assessment is complete.

1. Read the actual module, its signatures, validation, defaults, state changes,
   branches, return values, and exception paths. Read the nearest relevant call
   site, contract, dependency, or fixture only where needed to establish intent.
2. Compare the implementation with its intended contract and existing tests.
   Assess likely logic errors, including incorrect boundaries, inverted
   conditions, inconsistent defaults, mutation, missing validation, and incorrect
   error handling. Existing passing tests are not proof of correct behavior.
3. State the intended behavior and one cheap, focused check that could disprove
   the assessment. Derive expected results from the contract or an independent
   calculation, never by copying the implementation's output into assertions.
4. If any likely logic issue is found, **STOP and ask the user how to deal with
   it before implementing or updating tests**. Explain the source location,
   triggering input, expected versus actual behavior, and remaining uncertainty.
   Use the question tool when available; otherwise ask in the response and wait.
   Offer concrete choices such as fixing the module first, clarifying intended
   behavior, or explicitly authorizing a regression test of the intended behavior.
5. Do not silently fix production code, encode a suspected bug as expected
   behavior, or hide it with a skip/xfail. Resume only after the user responds;
   implement only the authorized resolution. If source code changes, reassess
   the changed logic before writing or updating tests.
6. If no likely issue is found, briefly report that assessment and proceed.
   Do not imply that the review proves the module correct.

If another likely implementation defect emerges during test writing or a test
run, apply the same stop-and-ask gate before further test edits.

## 2. Determine the Test Path and Filename

For a source module `gen_epix/<package>/<subfolders>/<module_name>.py`:

- Place its test in `test/<package>/unit/<subfolders>/`. Preserve every source
  subfolder in the same order; do not introduce feature-specific grouping folders.
- Define `path_with_underscores` as all source parent path components below
  `gen_epix`, joined with `_`, including `<package>` but excluding `gen_epix`.
- The filename MUST be
  `f"test_{path_with_underscores}_{module_name}.py"`, using the source filename
  stem as `module_name` without shortening, duplicating, or adding scenario names.

Example:

```text
Source: gen_epix/casedb/services/case/crud_case_set.py
Test:   test/casedb/unit/services/case/test_casedb_unit_services_case_crud_case_set.py

Source: gen_epix/fastapp/services/auth_service.py
Test:   test/fastapp/unit/services/test_fastapp_unit_services_auth_service.py
```

For a module directly under `gen_epix`, use `test/unit/test_unit_<module_name>.py`
without an empty-path double underscore. For source outside `gen_epix`, ask for
the source root and test mapping rather than inventing a layout.

Existing tests may use legacy paths or names. Update the existing coverage and
move/rename the target test to the required path after the logic-review gate;
update references affected by that move. Do not leave duplicate coverage behind
or rename unrelated tests. If existing coverage spans multiple modules or moving
it would require unrelated restructuring, ask how to isolate the target first.
Update launch configurations to reflect any changes in the test paths and filenames.

Record which destination directories did not exist before creating them; this
determines the launch configurations required in step 4.

## 3. Design and Implement Input Coverage

Build a compact coverage matrix for every function and method defined by the
module, including relevant constructors and private helpers, and for configurable
or module-level variables that affect behavior. Record applicable input
partitions, expected results/errors, and the test cases covering them.

Cover all applicable input edge cases, not merely the happy path:

- Omitted arguments versus explicit defaults and `None`; positional and keyword
  forms where their distinction matters; valid and invalid types, including
  booleans passed as integers when relevant.
- Empty, singleton, and multiple-item collections; duplicates, ordering, missing
  and extra keys, malformed items, iterators, and exhausted iterators as applicable.
- Values below, at, and above each boundary; zero, negative and large values;
  floating-point precision, NaN, and infinities when accepted by the interface.
- Empty and whitespace-only strings, Unicode, malformed formats, invalid enum
  values, identifiers, paths, and dates where relevant.
- Interacting arguments, mutually exclusive or dependent options, inconsistent
  lengths, repeated calls, mutable defaults, input mutation, and state-dependent
  behavior. Include combinations that exercise distinct outcomes, not just each
  argument in isolation.
- Dependency failures, expected exceptions, return shape/content, and observable
  side effects attributable to the target module.

Use finite equivalence classes and boundary representatives for unbounded input
spaces; do not claim to enumerate every possible value. Mark inapplicable cases
with a reason and explicitly disclose any remaining coverage gaps.

### Pytest and Reuse Requirements

- Use the `pytest` package to write all unit tests, not `unittest.TestCase`.
  Make full use of applicable pytest features instead of hand-written test
  infrastructure: plain assertions, `pytest.raises`, `pytest.warns`,
  `pytest.approx`, parametrization, fixtures, and registered markers.
- Inspect existing fixtures, `conftest.py` files, test utilities, and pytest
  configuration before adding new setup. Reuse them whenever suitable.
- Do not repeatedly declare variables with the same hard-coded content in
  individual tests. Define shared immutable example data once; use fixtures or
  factory fixtures to supply fresh mutable objects and per-case overrides.
  Do not let shared dictionaries, lists, or model instances leak mutations
  between tests or parametrized cases.
- Extract setup, builders, actions, or assertion helpers reused by two or more
  tests when they express the same operation, and always review repetition
  across three or more tests for extraction. Keep helpers focused and readable;
  do not hide the behavior under test or combine unrelated scenarios merely
  because their code looks similar.
- Use `pytest.mark.parametrize` and descriptive case IDs for tests differing
  only in input and expected output. Use parametrized fixtures for reusable
  setup variants and fixture dependencies for composed setup.
- Keep fixtures local when only this module needs them. Share fixtures across
  test modules through the nearest appropriate `conftest.py`, and use existing
  test utilities for reusable non-fixture helpers. Choose fixture scope
  deliberately; default to function scope for mutable state. Use `yield` for
  teardown and `autouse` only for genuinely universal setup at that scope.
- Prefer `monkeypatch` for environment and attribute changes, `tmp_path` for
  temporary files, and `capsys`/`caplog` for output/log assertions. Put shared
  pytest options and marker registrations in the existing pytest configuration
  when required; avoid per-test setup duplication and unrelated global changes.
- Import mocks from `test.util.mock_compat`, never directly from `unittest.mock`.
  Patch dependencies where looked up; do not mock away the module logic under
  test. Keep tests deterministic, avoid real external services, and assert
  behavior rather than internal call sequences.

## 4. Register Every New Test Folder

The repository's launch file is
[`.vscode/launch.json`](../../../.vscode/launch.json), not a root `.launch.json`.
When new test directories are created, add a folder-level launch configuration
for each newly created directory (including newly created intermediate parents).
Do not add duplicates or create a second launch file. If no directory was added,
no new folder launch configuration is required.

Use the following template, replacing both paths consistently:

```json
{
    "name": "test.casedb.unit.services.case",
    "type": "debugpy",
    "request": "launch",
    "program": "run.py",
    "args": ["run_test", "test/casedb/unit/services/case"],
    "console": "integratedTerminal",
    "justMyCode": true
}
```

Insert entries in lexicographic folder-path order among existing test launch
configurations, after API/environment/ETL entries. Keep parents before children
and preserve unrelated entries, comments, and formatting. Validate as JSON with
comments (JSONC) where applicable and check that each args path exists.

## 5. Validate and Report

Use the bundled [file runner](./scripts/run_unit_test.py) from the repository
root with the selected project Python:

```powershell
python .agents/skills/create-unit-test/scripts/run_unit_test.py test/fastapp/unit/services/test_fastapp_services_auth_service.py
```

Replace the example test path with the actual existing test file. The script
accepts exactly one unit-test file, imports `Run.DEFAULT_PYTEST_ARGS` directly
from `run.py`, runs from the repository root so normal pytest configuration and
fixtures apply, and propagates pytest's exit code. It does not copy the defaults
or use the curated full-suite coverage/report flags. Optional `-k EXPRESSION`
narrows cases within the file; `--collect-only` checks discovery without running
tests. Neither option changes the default parameters unless explicitly supplied.
Relative input paths resolve from the caller's current directory; absolute paths
also work. Additional positional files and directories are rejected.

### Other Test Selections

For verification beyond this skill's single-file workflow, choose the existing
repository runner appropriate to the requested scope:

- **Named suites (preferred for suite-level runs):** Use the `test_all` methods
  in `run.py`, for example `python run.py test_all` or
  `python run.py test_all_unit`.
- **Specific folders:** Use `python run.py run_test "test/casedb/unit"` with the
  actual folder path, or its corresponding VS Code launch configuration.
- **Exact selections outside the bundled runner's supported scope:** Direct
  pytest supports folder filtering such as `pytest test/casedb/unit -k oauth`
  and node IDs such as `pytest path/to/test_file.py::test_name`. Substitute an
  existing path. For this skill's single-file checks, keep using the bundled
  runner and its optional `-k` selector to preserve `Run.DEFAULT_PYTEST_ARGS`.

These options do not authorize broader test runs by default. Widen selection
only when the task requires it and after the focused check passes; if it fails,
diagnose and repair that same narrow slice, then rerun it before widening.

### Verification Checklist

- Immediately after a test edit, run the narrowest relevant test selection for
  the single target module with this script using project Python 3.14 or newer.
  Use the [run-pytest skill](../run-pytest/SKILL.md) to capture output once and
  inspect the log rather than rerunning unchanged tests to reread results. Keep
  the script's shared defaults when capturing; do not substitute a raw pytest
  command with a different flag set.
- Diagnose failures from the implementation, fixture, and test before editing.
  Fix local test mistakes and rerun the focused selection; suspected production
  defects must go back through the user-approval gate in step 1.
- Run the complete target test module after focused cases pass. Check relevant
  formatting and diagnostics and reconcile the result with the coverage matrix.
  Coverage metrics can expose gaps but do not prove behavioral correctness.
- Verify the final mirrored path, required filename, single-module scope, and
  launch entries for all newly created folders. Review repeated literals and
  setup/assertion blocks for fixture, parametrization, or helper extraction.
  Do not run unrelated suites or change generated reports unnecessarily.
- Report the source module, test path, covered edge-case categories, validation
  result, launch changes, and any unresolved or unverified requirements. Do not
  claim tests passed when execution was blocked or not performed.