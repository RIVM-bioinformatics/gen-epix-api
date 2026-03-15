Creation Date: March 1, 2026

# Mutation Testing

This project supports local mutation testing with `pytest-gremlins`. Official docs: https://pytest-gremlins.readthedocs.io/en/latest/

For general testing workflows, see [06-Development-Guide](./06-Development-Guide.md).

---

## 1. Overview

`pytest-gremlins` mutates source code and reruns `pytest` per mutation. Interpretation of outcomes:

| Outcome | Meaning |
|---------|---------|
| `zapped` | A test failed on the mutation. This is good — the test caught the change. |
| `survived` | Tests still passed. Add or strengthen assertions. |
| `timeout` | The mutation caused hangs/very slow execution. |
| `error` | Pytest could not run the mutation properly (e.g. collection/import/setup crash). |

### Interpreting many `error` mutations

A high `error` count usually indicates run instability, not weak assertions. In this repository that is often caused by collection/setup paths outside pure unit scope (integration/performance-style dependencies, app startup/import side effects, env-sensitive setup).

Practical rule:

- First reduce `error` and `timeout` by using stable scoped runs.
- Then evaluate `survived` to improve test quality.

---

## 2. Prerequisites

- Python 3.11+ (project uses Python 3.14)
- Dev dependencies installed:

```console
python -m pip install -r dev-requirements.txt
```

---

## 3. Running Mutation Tests

**WINDOWS USERS → see section 5 (WSL) below.**

### Full run

```console
python -m pytest -c pytest.gremlins.ini --gremlins
```

### Full run with HTML report

```console
python -m pytest -c pytest.gremlins.ini --gremlins --gremlin-report=html
```

If full-suite collection fails, `pytest-gremlins` can still write an HTML report (when requested) to `gremlin-report.html`. For reliable local usage, prefer the scoped commands below.

---

## 4. Scoping Runs

Mutation testing can be slow. Start with a focused path:

```console
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins \
  --gremlin-targets=gen_epix/filter
```

Or a single test module:

```console
python -m pytest -c pytest.gremlins.ini test/filter/unit/test_base_filter.py --gremlins \
  --gremlin-targets=gen_epix/filter/base.py
```

### Reliable scoped run with cache (bash)

```bash
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins \
  --gremlin-targets=gen_epix/filter \
  --gremlin-cache \
  --gremlin-report=html
```

### Reliable scoped run with cache (PowerShell)

```powershell
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins `
  --gremlin-targets=gen_epix/filter `
  --gremlin-cache `
  --gremlin-report html
```

### Validate cache behavior (recommended sequence)

1. Warm cache (expected: mostly/all misses):

```bash
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins \
  --gremlin-targets=gen_epix/filter \
  --gremlin-cache --gremlin-clear-cache \
  --gremlin-report=html
```

2. Re-run using cache (expected: many/all `cache hit (skipping)`):

```bash
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins \
  --gremlin-targets=gen_epix/filter \
  --gremlin-cache
```

---

## 5. WSL Setup for Windows

`pytest-gremlins` full-suite runs can hit Windows command-length limits (`WinError 206`). Running in WSL avoids that and is usually faster.

### First-time WSL users (no prior installs)

1. Open **PowerShell as Administrator** and install WSL:

```powershell
wsl --install
```

2. Reboot if prompted.
3. Open **Ubuntu** (or your installed Linux distro) from the Start menu.
4. Complete first-run Linux setup (create UNIX username/password).
5. Install Python tooling in WSL:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe -y
sudo apt update
sudo apt install -y python3-venv python3-pip
```

### WSL already installed

Run this once in your WSL terminal:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe -y
sudo apt update
sudo apt install -y python3-venv python3-pip
```

### Store the repo on WSL Linux disk (recommended)

Running from `~/projects/...` is faster than `/mnt/c/...` for Python testing and mutation workloads.

If your repo is only on Windows disk, copy it once:

```bash
mkdir -p ~/projects
cp -a "/mnt/c/Py Projects/LSP-RIVM/gen-epix-api" ~/projects/
```

Or clone directly into Linux disk:

```bash
mkdir -p ~/projects
cd ~/projects
git clone <repo-url> gen-epix-api
```

### Open a WSL terminal in this repo

From Windows PowerShell:

```powershell
wsl
cd ~/projects/gen-epix-api
```

Or from VS Code:
1. Open a new terminal.
2. Select a WSL profile (e.g. `Ubuntu`) as the terminal shell.
3. In that WSL terminal, run: `cd ~/projects/gen-epix-api`

### Create and activate virtual environment (inside WSL)

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m pip install -r dev-requirements.txt
```

### Run mutation testing in WSL

Full run:

```bash
python -m pytest -c pytest.gremlins.ini --gremlins --gremlin-report=html
```

Scoped run with cache and HTML report:

```bash
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins \
  --gremlin-targets=gen_epix/filter \
  --gremlin-cache \
  --gremlin-report=html
```

Re-run same scope using cache (console summary):

```bash
python -m pytest -c pytest.gremlins.ini test/filter/unit --gremlins \
  --gremlin-targets=gen_epix/filter \
  --gremlin-cache
```

### Refresh WSL after config changes

When you change config files (e.g. `pytest.ini`, `pyproject.toml`, or `pytest.gremlins.ini`), make sure your WSL working copy has those changes before rerunning.

1. Open WSL and navigate to the repo:

```bash
cd ~/projects/gen-epix-api
```

2. Sync changes (e.g. via `git pull`/`merge`).
3. Re-activate your virtual environment:

```bash
source .venv-wsl/bin/activate
```

4. Verify key config changes are present:

```bash
grep -n "norecursedirs" pytest.ini || echo "MISSING: norecursedirs in pytest.ini"
grep -n "mutants" pytest.ini || echo "MISSING: mutants ignore in pytest.ini"
```

5. Optional quick validation before a long run:

```bash
python -m pytest -c pytest.gremlins.ini --collect-only -q
```

---

## 6. Notes & Best Practices

- `pytest --gremlins` runs much slower than a normal `pytest` run.
- Terminal output includes the mutation summary.
- Supported report modes: `console` (default) and `html`.
- With `--gremlin-report=html`, the plugin writes an HTML report to its default output location.
- Excel export from `test/conftest.py` is skipped automatically for `--gremlins` runs; regular pytest runs still generate the Excel report by default.
- If you see import mismatch errors under `mutants/...`, that directory is from another mutation workflow and should not be collected by pytest.
- `[tool.pytest-gremlins]` in `pyproject.toml` controls mutation source targeting (e.g. `paths`, `operators`), not pytest test collection baseline.
- Use `pytest.gremlins.ini` to define the practical baseline test scope for mutation runs.
- For consistency, include `-c pytest.gremlins.ini` in full and scoped mutation commands. Omit it only when you intentionally want to include paths ignored by that config.
- `Cache: 4803 hits, 0 misses` on the second run is expected when no files changed and `--gremlin-clear-cache` is omitted.
- Cached `ERROR`/`TIMEOUT` results are reused too; if you change runtime flags, run once with `--gremlin-clear-cache` to refresh.
- Use `--gremlin-clear-cache` when you need a fresh baseline:
  - First run for a new scope/path.
  - After changing gremlins runtime options.
  - After large source/test edits when you want to recompute all mutation outcomes from scratch.
- Warning `DeprecationWarning: pl.count() is deprecated` comes from test code (`test/conftest.py`) and does not indicate a gremlins failure.
- Avoid `--gremlin-parallel` for now in this project; it can produce unstable runs with many `Error` results.
- Avoid `--gremlin-batch` for now if you rely on per-gremlin mutation or cache metrics; batch mode can produce misleading counts.

---

## Evidence Sources

- `Extending-the-System-mutation_testing.md` (primary source, adapted nearly intact)
- `dev-requirements.txt#L1-L25`
- `pytest.gremlins.ini`
- `pyproject.toml` (`[tool.pytest-gremlins]` section)
