# Local Mutation Testing (mutmut)

This repo supports local-only mutation testing through `mutmut` using a single entrypoint:

```console
python tools/mutation.py full
```

`mutmut` requires process forking, so on native Windows you should run mutation commands from a WSL/Linux terminal.

## First-time WSL users (no prior installs)

1. Open **PowerShell as Administrator** and install WSL:

```powershell
wsl --install
```

2. Reboot if prompted.
3. Open **Ubuntu** (or your installed Linux distro) from the Start menu.
4. Complete first-run Linux setup (create UNIX username/password).
5. Install Python venv tooling in WSL.  
   Short explanation: these packages enable virtual environment creation (`venv`) and pip usage inside Linux.

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe -y
sudo apt update
sudo apt install -y python3-venv python3-pip
```

## WSL already installed

If WSL is already installed, run this once in your WSL terminal to ensure required Python tooling is available:

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository universe -y
sudo apt update
sudo apt install -y python3-venv python3-pip
```

## Store the repo on WSL Linux disk (recommended)

Running from `~/projects/...` is faster than `/mnt/c/...` for Python test and mutation workloads.

If this repo currently exists only on Windows disk, copy it once:

```bash
mkdir -p ~/projects
cp -a "/mnt/c/Py Projects/RIVM-LSP/gen-epix-api" ~/projects/
```

Or clone directly into Linux disk:

```bash
mkdir -p ~/projects
cd ~/projects
git clone <repo-url> gen-epix-api
```

## Open a WSL terminal window in this repo (Linux disk path)

Use either approach:

1. From Windows PowerShell:

```powershell
wsl
cd ~/projects/gen-epix-api
```

2. From VS Code:
- Open a new terminal.
- Select a WSL profile (for example, `Ubuntu`) as the terminal shell.
- In that WSL terminal, run:

```bash
cd ~/projects/gen-epix-api
```

You are in a WSL terminal when paths are Linux-style (for example `~/projects/...`) and the prompt looks like `user@machine:~$`.

## Create and activate virtual environment (inside WSL terminal)

Do not use `sudo` for this step, so files stay owned by your Linux user.

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
python -m pip install -U pip
```

Then continue with dependency installation:

```bash
python -m pip install -r requirements.txt
python -m pip install -r dev-requirements.txt
python -m pip install -r requirements-mutation.txt
```

## Run (inside WSL terminal)

Full run (includes baseline regression check with the canonical command `python run.py test_all`):

```bash
python tools/mutation.py full
```

Quick smoke run (scope mutations and tests to one module):

```bash
python tools/mutation.py smoke --path gen_epix/filter --tests test/filter/unit --skip-baseline
```

`smoke` automatically narrows test selection for common module roots (for example, `gen_epix/filter` runs `test/filter/unit`) to avoid unrelated integration-test failures during quick checks.

If needed, override smoke test selection explicitly:

```bash
python tools/mutation.py smoke --path gen_epix/filter --tests test/filter/unit --skip-baseline
```

If `python tools/mutation.py smoke --help` does not show `--tests`, sync your local `tools/mutation.py` first.

## View Results (inside WSL terminal)

Summary:

```bash
python tools/mutation.py results
```

Interactive browser:

```bash
python tools/mutation.py browse
```

## Notes

- `setup.cfg` contains the mutmut configuration.
- Test selection and warning flags are aligned with `run.py test_all`.
