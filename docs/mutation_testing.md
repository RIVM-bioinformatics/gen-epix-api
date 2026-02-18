# Mutation Testing

This project supports local mutation testing with `pytest-gremlins`.
Official docs on: https://pytest-gremlins.readthedocs.io/en/latest/

## Prerequisites

- Python 3.11+ (project uses Python 3.14)
- Dev dependencies installed:

```console
python -m pip install -r dev-requirements.txt
```

## Run Mutation Testing

Run the full mutation test pass:

**WINDOWS USERS -> please see chapter: "Use WSL on Windows.." below**

```console
python -m pytest --gremlins
```

If full-suite collection fails in this repository, `pytest-gremlins` can still write
an HTML report (when requested) to `gremlin-report.html`. For reliable local usage,
prefer the scoped commands in the next section.

Generate an HTML mutation report:

```console
python -m pytest --gremlins --gremlin-report=html
```

Use console summary output (default):

```console
python -m pytest --gremlins
```

## Scope the Run

Mutation testing can be slow. Start with a focused path:

```console
python -m pytest test/filter/unit --gremlins
```

Or a single test module:

```console
python -m pytest test/filter/unit/test_base_filter.py --gremlins
```

Run a reliable scoped mutation pass (cache, no parallel):

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache \
  --gremlin-report=html
```

```powershell
python -m pytest test/filter/unit --gremlins `
  --gremlin-cache `
  --gremlin-report html
```

Validate cache behavior (recommended sequence):

1. Warm cache (expected: mostly/all misses):

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache --gremlin-clear-cache \
  --gremlin-report=html
```

2. Re-run using cache (expected: many/all `cache hit (skipping)`):

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache
```

## Use WSL on Windows (recommended for full runs)

`pytest-gremlins` full-suite runs can hit Windows command-length limits (`WinError 206`).
Running in WSL avoids that and is usually faster.

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
2. Select a WSL profile (for example, `Ubuntu`) as the terminal shell.
3. In that WSL terminal, run:

```bash
cd ~/projects/gen-epix-api
```

### Create and activate virtual environment (inside WSL)

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
python -m pip install -U pip
```

Install project dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip install -r dev-requirements.txt
```

### Run mutation testing in WSL

Full run:

```bash
python -m pytest --gremlins --gremlin-report=html
```

Scoped run, with html report:

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache \
  --gremlin-report=html
```

Re-run same scope using cache (console summary):

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache
```

## Notes

- `pytest --gremlins` is expected to run much slower than a normal `pytest` run.
- Terminal output includes the mutation summary.
- Supported report modes in this project are `console` (default) and `html`.
- With `--gremlin-report=html`, the plugin writes an HTML report to its default output location.
- If you see import mismatch errors under `mutants/...`, that directory is from another mutation workflow and should not be collected by pytest.
- `Cache: 4803 hits, 0 misses` on the second run is expected when no files changed and `--gremlin-clear-cache` is omitted.
- Cached `ERROR`/`TIMEOUT` results are reused too; if you change runtime flags, run once with `--gremlin-clear-cache` to refresh results.
- Use `--gremlin-clear-cache` when you need a fresh baseline:
  - First run for a new scope/path.
  - After changing gremlins runtime options (for example parallel/cache settings).
  - After large source/test edits when you want to recompute all mutation outcomes from scratch.
- Warning `DeprecationWarning: pl.count() is deprecated` comes from test code (`test/conftest.py`) and does not indicate a gremlins failure.
- Avoid `--gremlin-parallel` for now in this project; it can produce unstable runs with many `Error` results.
- Avoid `--gremlin-batch` for now if you rely on per-gremlin mutation or cache metrics; batch mode can produce misleading counts.
