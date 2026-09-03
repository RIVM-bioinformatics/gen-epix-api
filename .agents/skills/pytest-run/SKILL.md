---
name: pytest-run
description: >-
  Run pytest ONCE to a captured log file, then inspect that file repeatedly with
  grep/sed/awk instead of re-running pytest for every question (which failed, why,
  the summary line, warnings). Use when: running more than one pytest invocation to
  look at different aspects of the same test run; iterating on a failure and about
  to re-run pytest just to re-read output already seen; asked to check test status,
  failures, tracebacks, or warnings after a run. Do NOT use to decide whether a
  fresh run is needed — rerun pytest for real whenever source or test code changed
  since the last capture.
argument-hint: 'Optional: pytest target/args, e.g. "test/etl/test_batch_uploader.py -k upload"'
---

# Pytest Run (capture once, inspect many times)

Running `pytest` repeatedly with different `-k`/`--grep`-via-pipe/verbosity flags to
answer different questions about the *same* test run is slow and wasteful. Run it
once, capture full output to a file, then answer every follow-up question by reading
that file.

## When to use

- You're about to run pytest a second (or third) time only to look at a different
  slice of the *same* underlying run (e.g. first `| grep FAILED`, then
  `| grep -A20 "test_foo"`, then `| tail -30` for the summary).
- You need to check several things after one run: which tests failed, a specific
  traceback, the pass/fail counts, deprecation warnings.

## When NOT to use (rerun for real)

- Source or test code changed since the last capture — the log is stale, run pytest
  again.
- You need a different test selection (`-k`, a different path, different markers)
  than what's in the existing log — that's a new run, not a new grep.

## Method

1. **Capture once** to a fixed, gitignored path under `tmp/` (already gitignored in
   this repo). Reuse the same filename so stale logs don't accumulate silently.

   For the **full suite**, run the repo's curated runner, not raw pytest on the
   whole `test/` folder:

   ```bash
   python run.py test_all --include_e2e=False > tmp/pytest-run.log 2>&1; echo "exit: $?"
   ```

   For a **single unit test or a narrow slice**, pytest may be invoked directly on
   that target (a file, `-k EXPR`, a marker) — this is still a single capture:

   ```bash
   pytest test/etl/test_batch_uploader.py -v --tb=long -ra > tmp/pytest-run.log 2>&1; echo "exit: $?"
   ```

   - `-v` prints one PASSED/FAILED/ERROR line per test (needed to grep by test
     name). `--tb=long` keeps full tracebacks in the file so a second run isn't
     needed just to see more context. `-ra` (already a project default) adds the
     short summary block at the end with reasons for skips/xfails.
   - The `> ... 2>&1` redirect is not in the pre-approved command allowlist, so
     expect one permission prompt on first use per session — this is expected, not
     an error.
   - Echoing `$?` captures the exit code even though the file redirect swallows
     pytest's own screen output.

2. **Inspect the file** with plain text tools, as many times as needed, without
   touching pytest again:

   ```bash
   # overall result + summary block (bottom of output)
   tail -40 tmp/pytest-run.log

   # just the failed/errored test node IDs
   grep -E "^(FAILED|ERROR) " tmp/pytest-run.log

   # full traceback for one test
   grep -n "test_upload_batch_success" tmp/pytest-run.log
   sed -n '120,180p' tmp/pytest-run.log   # use the line number from the grep above

   # warnings
   grep -A3 "warnings summary" tmp/pytest-run.log

   # pass/fail/error counts only
   grep -E "^[0-9]+ (passed|failed|error|skipped)" tmp/pytest-run.log
   tail -1 tmp/pytest-run.log
   ```

3. **Only re-run pytest** when you've made a code change, need a different test
   selection, or the log file doesn't exist yet.

## Notes

- One fixed filename (`tmp/pytest-run.log`) is intentional: it's per-session scratch,
  not a history — each new capture overwrites the last, and there's nothing to clean
  up. Use `pytest-run-<topic>.log` only if two runs genuinely need to be compared
  side by side.
- Still respect existing markers: `live` and `integration` are deselected by default
  (`pyproject.toml` `addopts`). Add `-m "integration"` etc. explicitly if the task
  requires them, same as any normal invocation.
- Still finish with the repo's real verification step before calling work done —
  this skill is for *iterating*, not a replacement for a clean final
  `python run.py test_all --include_e2e=False` run per the session conventions.
  Individual unit tests may still be verified directly with pytest.
