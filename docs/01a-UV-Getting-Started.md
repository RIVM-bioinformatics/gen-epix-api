Creation Date: April 30, 2026

# UV Getting Started

This is a minimal guide for contributors who are new to `uv` and want to run this
repository quickly. uv is a package manager as well as a environment manager. It is fully compatible with the pyproject.toml standard and uses that as its source of truth.
Additionally, uv maintains a uv.lock file in the background to strictly pin versions of packages and their (sub)dependencies. This ensures consistency in functionality of python packages across environments

Last but not least, it's blazing fast locally and in pipelines.

---

## 1. Install uv

Install `uv` using the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or on macOS with Homebrew:

```bash
brew install uv
```

---

## 2. Sync Dependencies

From the repository root:

```bash
uv sync
```

That's all. This will:

- Create or update a virtual environment in `.venv/`
- Install and use the python version defined in .python-version or pyproject.toml
- Install runtime as well as development dependencies
- Generate or update `uv.lock` with pinned package versions for reproducible installs

---

## 3. Run Commands With uv

The settings.json in this repo automatically activates the uv virtual environment and uses it in the terminal as well. 
If you are outside of vscode, or if the venv is not activated, you have to prepend any call to a python script or tool with `uv run ...`.
See examples below.

Starting the API:

```bash
uv run python run.py api casedb mock dict_demo
```

Running the full test suite:

```bash
uv run python run.py test_all
```

Run linters:

```bash
uv run python run.py other_general_run_linters
```

---

## 5. Updating Dependencies (Maintainers)

uv is fully based on the pyproject.toml standard
When dependencies change in `pyproject.toml`, refresh the virtual environment and lockfile with `sync`:

```bash
uv sync
```

To add a new package use `uv add`. This will add the package in your virtual environment and automatically update pyproject.toml and uv.lock

To ensure backwards compatibility with production (which currently still uses requirements.txt files), run the following commands after adding/changing package dependencies:

```bash
uv export --no-dev --format requirements-txt > requirements.txt
uv export --only-dev --format requirements-txt > dev-requirements.txt
```

---


