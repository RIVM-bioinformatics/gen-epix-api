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
python tools/patch_mutmut_template.py
```

`python tools/patch_mutmut_template.py` is safe to run multiple times.
Run it again whenever you recreate the virtual environment or reinstall `mutmut`.

## Run (inside WSL terminal)

Full run (includes baseline regression check with the canonical command `python run.py test_all`):

```bash
python tools/mutation.py full --max-children 1
```

Optional safety switch for all mutmut commands (`full`, `smoke`, `retry`, `results`, `browse`):

```bash
python tools/mutation.py full --max-children 1 --auto-patch-mutmut
```

This runs a pre-check and auto-applies `tools/patch_mutmut_template.py` when needed.

Quick smoke run (scope mutations and tests to one module):

```bash
python tools/mutation.py smoke --path gen_epix/filter --tests test/filter/unit --skip-baseline
```

`smoke` automatically narrows test selection for common module roots (for example, `gen_epix/filter` runs `test/filter/unit`) to avoid unrelated integration-test failures during quick checks.
Do not use bare `pytest -q` as a baseline in this repo; it can collect unsupported/custom/performance suites. Use `python run.py test_all` or an explicit scoped path (for example `pytest -q test/filter/unit`).

If needed, override smoke test selection explicitly:

```bash
python tools/mutation.py smoke --path gen_epix/filter --tests test/filter/unit --skip-baseline
```

If `python tools/mutation.py smoke --help` does not show `--tests`, sync your local `tools/mutation.py` first.
When smoke scoping is active, the command prints `Smoke test selection: ...` before running mutmut.

## Reload Latest Mutation Config In WSL

Use this checklist after pulling changes or after editing mutation tooling from Windows.

1. Sanity check: confirm you are in the expected WSL clone:

```bash
pwd
git rev-parse --show-toplevel
ls tools | grep patch_mutmut_template.py || echo "missing in this clone"
```

If the script is missing here but present in your Windows repo, you are using different clones (`/home/...` vs `/mnt/c/...`).
Sync this WSL clone first (via `git pull` after push, or copy updated files).

2. Move to the WSL repo and sync:

```bash
cd ~/projects/gen-epix-api
git pull --ff-only
```

If your WSL clone still misses local edits that exist in a Windows clone (for example uncommitted changes), copy the changed files explicitly:

```bash
WINDOWS_REPO="/mnt/c/<path-to-repo>"
WSL_REPO="$HOME/projects/gen-epix-api"

cp "$WINDOWS_REPO/tools/mutation.py" "$WSL_REPO/tools/mutation.py"
cp "$WINDOWS_REPO/tools/patch_mutmut_template.py" "$WSL_REPO/tools/patch_mutmut_template.py"
cp "$WINDOWS_REPO/setup.cfg" "$WSL_REPO/setup.cfg"
cp "$WINDOWS_REPO/docs/mutation_testing.md" "$WSL_REPO/docs/mutation_testing.md"
```

3. Activate the WSL virtual environment:

```bash
source .venv-wsl/bin/activate
```

4. Ensure mutation dependencies and local mutmut patch are current:

```bash
python -m pip install -r requirements-mutation.txt
python tools/patch_mutmut_template.py
```

5. Verify the expected script/config changes are actually present in WSL:

```bash
grep -n "auto-patch-mutmut" tools/mutation.py
grep -n "gen_epix/fastapp/services/rbac/service.py" setup.cfg
grep -n "gen_epix/commondb/domain/service/rbac.py" setup.cfg
grep -n "gen_epix/commondb/services/rbac.py" setup.cfg
grep -n "gen_epix/omopdb/services/rbac.py" setup.cfg
grep -n "gen_epix/commondb/services/abac.py" setup.cfg
grep -n "gen_epix/casedb/services/abac.py" setup.cfg
grep -n "gen_epix/commondb/env.py" setup.cfg
grep -n "gen_epix/seqdb/env.py" setup.cfg
grep -n "gen_epix/commondb/policies/\\*.py" setup.cfg
grep -n "gen_epix/seqdb/policies/\\*.py" setup.cfg
```

6. Verify mutmut is loading exclusions from `setup.cfg`:

```bash
python - <<'PY'
from pathlib import Path
from mutmut.__main__ import load_config
c = load_config()
print(c.should_ignore_for_mutation(Path("gen_epix/fastapp/services/rbac/service.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/commondb/domain/service/rbac.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/commondb/services/rbac.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/omopdb/services/rbac.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/commondb/services/abac.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/casedb/services/abac.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/commondb/env.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/seqdb/env.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/commondb/policies/read_organization_results_only_policy.py")))
print(c.should_ignore_for_mutation(Path("gen_epix/seqdb/policies/read_organization_results_only_policy.py")))
PY
```

All lines should print `True`.

7. Remove old mutation artifacts and rerun:

```bash
rm -rf mutants
python tools/mutation.py full --max-children 1 --auto-patch-mutmut
```

You do not need to restart WSL just to pick up repo file edits. Running the commands above from the same WSL shell is enough.

## Timeout Triage

If mutmut reports nearly all mutants as timeout, this usually means the selected tests exceed mutmut's runtime budget for each mutant. It does **not** automatically mean your tests contain infinite loops.

Start with:

```bash
python tools/mutation.py smoke --path gen_epix/filter --tests test/filter/unit --skip-baseline --max-children 1
```

If smoke works but `full` times out, run `full` with an explicit unit-focused test selection:

```bash
python tools/mutation.py full --skip-baseline --max-children 1 \
  --tests test/filter/unit \
  --tests test/transform/unit \
  --tests test/fastapp/unit \
  --tests test/commondb/unit \
  --tests test/casedb/unit \
  --tests test/seqdb/unit \
  --tests test/omopdb/unit \
  --tests test/general/docs
```

Then add integration/end-to-end suites back gradually only if runtime remains stable.

Run a small troubleshooting batch (max 6 mutants) from current results:

```bash
python tools/mutation.py retry --status timeout --contains "RangeFilter" --limit 6 \
  --path gen_epix/filter/range.py --tests test/filter/unit --skip-baseline
```

`retry` runs the selected mutants in one mutmut invocation so prior statuses are not reset to `not checked`.

## View Results (inside WSL terminal)

Summary:

```bash
python tools/mutation.py results
```

Interactive browser:

```bash
python tools/mutation.py browse
```

## Workflow

This section describes how to work with mutmut to enhance your test suite.

1. Run mutmut. A full run is preferred but if you're just
   getting started you can exit in the middle and start working with what you
   have found so far.
```bash
python tools/mutation.py full --max-children 1
```
2. Show the mutants with:
```bash
python tools/mutation.py browse
```
3. Find a mutant you want to work on and write a test to try to kill it.
4. Press `r` to rerun the mutant and see if you successfully managed to kill it.

Mutmut keeps the data of what it has done and the mutants in the `mutants/`
directory.If  you want to make sure you run a full mutmut run you can delete
this directory to start from scratch.

## Notes

- `setup.cfg` contains the mutmut configuration.
- Test selection and warning flags are aligned with `run.py test_all`.
- `tools/patch_mutmut_template.py` patches the installed `mutmut` trampoline template in the active environment to avoid known `dict` alias collisions during stats collection.
- `tools/mutation.py` disables the custom Excel pytest report during mutmut runs (`GEN_EPIX_DISABLE_PYTEST_XLSX_REPORT=1`) to reduce per-mutant overhead and avoid false timeout-heavy runs.
- `test/conftest.py` resets report state at `pytest_sessionstart`, preventing cross-session growth when mutmut executes many pytest sessions.
- Local timeout triage exclusions are configured in `setup.cfg` under `do_not_mutate`:
  - `gen_epix/filter/base.py`
  - `gen_epix/filter/composite.py`
  - `gen_epix/fastapp/repositories/__init__.py`
  - `gen_epix/fastapp/services/auth/*.py`
  - `gen_epix/fastapp/services/rbac/service.py`
  - `gen_epix/commondb/domain/service/rbac.py` (reason: mutmut generates helper names from class+method, so superclass/subclass collide and recurse)
  - `gen_epix/commondb/services/rbac.py`
  - `gen_epix/casedb/services/rbac.py`
  - `gen_epix/seqdb/services/rbac.py`
  - `gen_epix/omopdb/services/rbac.py` (same helper-name collision pattern for inherited service classes, e.g. `RbacService.__init__`)
  - `gen_epix/commondb/services/abac.py`
  - `gen_epix/casedb/services/abac.py` (same superclass/subclass helper-name collision pattern as RBAC)
  - `gen_epix/commondb/env.py`
  - `gen_epix/casedb/env.py`
  - `gen_epix/seqdb/env.py`
  - `gen_epix/omopdb/env.py` (same helper-name collision pattern for `AppComposer.__init__` across inherited env composers)
  - `gen_epix/commondb/policies/*.py`
  - `gen_epix/casedb/policies/*.py`
  - `gen_epix/seqdb/policies/*.py`
  - `gen_epix/omopdb/policies/*.py` (same helper-name collision pattern for inherited policy classes, e.g. `ReadOrganizationResultsOnlyPolicy.__init__`)
- If you want to investigate those files specifically, temporarily remove the relevant exclusion lines, run a scoped smoke command, then add them back.
