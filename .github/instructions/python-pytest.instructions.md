---
description: "Use when writing or changing Python implementation code alongside its tests, or when diagnosing/fixing a pytest test failure. Covers mock imports, test selection, and diagnose-before-editing workflow."
applyTo: "gen_epix/**/*.py,test/**/*.py"
---
# Python & Pytest Conventions

- Use the `run-pytest` skill when available: capture a run once to a log file and
  re-inspect that file for follow-up questions instead of re-running pytest.
- Import `MagicMock`, `Mock`, `patch` from `test.util.mock_compat`, never from
  `unittest.mock` directly.
- On a test failure, read the nearest implementation, fixture, and test before
  editing. State the intended behavior and one focused check that could disprove
  your diagnosis before changing code.
- After an edit, immediately run the narrowest relevant pytest selection. Widen the
  selection only after the focused check passes, or after repairing a failure found
  in that same narrow slice.
- Test behavior, not implementation details: cover expected errors, malformed
  input, empty input, and other important boundaries — not internal call sequences.
- To run tests in a specific folder or suite, use one of these approaches:
  - **Named suites** (preferred): Call the `test_all` methods or use run.py methods
    for curated suites, e.g., `python run.py test_all` or `python run.py test_all_unit`.
  - **Specific folders**: Use `run_test` with the folder path, e.g.,
    `python run.py run_test "test/casedb/unit"` or VS Code's launch configs.
  - **Exact test selection**: Use direct `pytest` for precise targeting:
    `pytest test/casedb/unit -k oauth` or `pytest test/file.py::test_name`.

## Adding a New Test Folder

When creating a new test folder, add a corresponding launch configuration in
[`.vscode/launch.json`](.vscode/launch.json):

1. **Name** the config using the pattern `test.<dotted.path>` matching the folder
   path with dots: `test/casedb/unit/domain` → `test.casedb.unit.domain`.
2. **Set args** to call `run_test` with the folder path:
   ```json
   "args": ["run_test", "test/casedb/unit/domain"]
   ```
3. **Place the config** in lexicographic order among the test configs in the
   `configurations` array (after all API/env/ETL configs but within the test group).
4. Use a simple template:
   ```json
   {
       "name": "test.casedb.unit.domain",
       "type": "debugpy",
       "request": "launch",
       "program": "run.py",
       "args": ["run_test", "test/casedb/unit/domain"],
       "console": "integratedTerminal",
       "justMyCode": true
   }
   ```

Then you can launch the new test folder directly from VS Code's debug view.
