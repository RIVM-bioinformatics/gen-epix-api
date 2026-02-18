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

Generate an HTML mutation report:

```console
python -m pytest --gremlins --gremlin-report=html
```

Generate a JSON mutation report:

```console
python -m pytest --gremlins --gremlin-report=json
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

Run a faster scoped mutation pass (cache + parallel):

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache \
  --gremlin-clear-cache \
  --gremlin-parallel --gremlin-workers=8 \
  --gremlin-report=html
```

```powershell
python -m pytest test/filter/unit --gremlins `
  --gremlin-cache `
  --gremlin-clear-cache `
  --gremlin-parallel --gremlin-workers 8 `
  --gremlin-report html
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

Faster scoped run, with html report:

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache \
  --gremlin-clear-cache \
  --gremlin-parallel --gremlin-workers=8 \
  --gremlin-report=html
```

Faster scoped run, with json report:

```bash
python -m pytest test/filter/unit --gremlins \
  --gremlin-cache \
  --gremlin-clear-cache \
  --gremlin-parallel --gremlin-workers=8 \
  --gremlin-report=json
```

## Notes

- `pytest --gremlins` is expected to run much slower than a normal `pytest` run.
- Terminal output includes the mutation summary.
- With `--gremlin-report=html`, the plugin writes an HTML report to its default output location.
- Avoid `--gremlin-batch` for now if you rely on per-gremlin mutation or cache metrics; batch mode can produce misleading counts.
