---
description: "Use when writing or changing Python implementation code alongside its tests, or when diagnosing/fixing a pytest test failure. Covers mock imports, test selection, and diagnose-before-editing workflow."
applyTo: "gen_epix/**/*.py,test/**/*.py"
---
# Python & Pytest Conventions

- Use the `pytest-run` skill when available: capture a run once to a log file and
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
- Use a `test_*` method defined in [run.py](../../run.py) for an existing named
  or curated suite (for example,
  `python run.py test_casedb_unit_services_case_upload`). Use direct `pytest`
  for an exact file, node ID, or `-k` selection.
