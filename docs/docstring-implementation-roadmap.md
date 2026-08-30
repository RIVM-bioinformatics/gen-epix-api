# Docstring Implementation Roadmap

This roadmap tracks the incremental repository docstring rollout. The selected
standard is PEP 257 as the baseline with Google-style structured sections when a
docstring needs sections such as `Args:`, `Returns:`, `Yields:`, `Raises:`,
`Attributes:`, or `Examples:`.

Docstrings should describe semantic behavior, contracts, constraints, side effects,
exceptions, invariants, domain meaning, and non-obvious assumptions. They should not
repeat Python type annotations unless the prose adds meaning that the type cannot
express.

## Implementation Order

Each package is documented bottom-up:

1. Functions and methods.
2. Classes.
3. Modules.
4. Nested packages and `__init__.py` files, deepest first.
5. The package root `__init__.py`.

Package documentation should summarize responsibilities already established by child
modules and packages.

## Package Phases

1. `util`
2. `transform`
3. `filter`
4. `fastapp`
5. `commondb`
6. `seqdb`
7. `casedb`

## Phase 1: `util`

Status: implemented and lint-workflow integrated in branch
`LSP-3786-util-module-docstrings`.

Scope:

- Document the public functions and non-trivial private helpers in
  `gen_epix/util.py`.
- Document the module and profiling decorator behavior, including synchronous
  and asynchronous wrappers.
- Confirm the module has no intra-package dependencies using the AST import
  graph tooling.
- Introduce Ruff docstring linting for `gen_epix/util.py` in local linting and
  CI.

Validation:

- `ruff check --select D --ignore D212,D417 gen_epix/util.py`
- `black -l 88 --check --diff gen_epix/util.py`
- `isort --check-only --diff --profile black --float-to-top --line-length=88 gen_epix/util.py`
- `python run.py test_all_unit`

## Phase 1: `transform`

Status: implemented and lint-workflow integrated in branch
`LSP-3743-enhance-docstrings-p1`.

Scope:

- Document missing public function and method docstrings in `gen_epix/transform`.
- Document non-trivial private helpers where they encode validation, lookup, or
  mapping contracts.
- Document classes and enum responsibilities.
- Document modules and package `__init__.py` files from
  `gen_epix/transform/transformers/__init__.py` to
  `gen_epix/transform/__init__.py`.
- Repair malformed docstring placement where prose was not attached to a symbol.
- Introduce Ruff docstring linting for `gen_epix/transform` only, wired into
  local linting and CI.

Validation:

- `ruff check --select D --ignore D212,D417 gen_epix/transform`
- `black --check --diff gen_epix/transform`
- `isort --check-only --diff --profile black --float-to-top --line-length=88 gen_epix/transform`
- `python run.py test_transform_unit`

Lint ownership:

- Ruff is the Google-style docstring enforcement mechanism. Pylint remains
  advisory and may intentionally overlap on missing-docstring diagnostics during
  the staged rollout.

## Phase 2: `filter`

Status: implemented in branch `LSP-3788-filter-folder-docstrings`.

Scope:

- Document filter modules, public filter classes, and matching methods.
- Document non-trivial validation and dynamically generated matching helpers.
- Preserve filter behavior while completing package-level docstring coverage.

Validation:

- `ruff check --select D --ignore D212,D417 gen_epix/filter`
- `black -l 88 --check --diff gen_epix/filter`
- `isort --check-only --diff --profile black --float-to-top --line-length=88 gen_epix/filter`
- `python run.py test_filter_unit`

## Later Phases

For each later package, repeat the same bottom-up sequence and expand the
configured Ruff docstring scope in local linting and CI only after the package
has been documented.

## Phase 3: `fastapp`

Status: implemented in branch `LSP-3760-fastapp-folder`.

Scope:

- Document the shared application framework modules, nested packages, public
  classes, and public methods under `gen_epix/fastapp`.
- Preserve command, policy, service, repository, and API-layer boundaries while
  documenting their contracts and lifecycle responsibilities.
- Record the missing `scripts/ast_import_graph.py` reference for follow-up
  tooling work; no runtime behavior was changed.

Validation:

- `ruff check --select D --ignore D212,D417 gen_epix/fastapp`
- `black -l 88 --check --diff gen_epix/fastapp`
- `isort --check-only --diff --profile black --float-to-top --line-length=88 gen_epix/fastapp`
- `python run.py test_fastapp_unit`

Phase 4 adds `gen_epix/commondb`.

Phase 5 adds `gen_epix/seqdb`.

Phase 6 adds `gen_epix/casedb`.

Phase 8 adds `gen_epix/omopdb`.

## Phase 8: `omopdb`

Status: in progress in branch `LSP-3787-phase-8-omopdb-folder`.

Scope:

- Document OmopDB modules, public APIs, commands, policies, services,
  repositories, models, and test-support helpers.
- Document the package facades deepest first after their child modules.
- Preserve the existing command, policy, service, repository, and API-layer
  responsibilities while documenting their caller-facing contracts.
- Document modules in dependency order where possible. The ticket's referenced
  `scripts/ast_import_graph.py` tool is absent from this repository, so the
  dependency order is established from local imports and existing architecture.

Validation:

- `python .agents/skills/write-docstring/scripts/check_docstrings.py gen_epix/omopdb`
- `ruff check --select D --ignore D212,D417 gen_epix/omopdb`
- `black -l 88 --check --diff gen_epix/omopdb`
- `isort --check-only --diff --profile black --float-to-top --line-length=88 gen_epix/omopdb`
- `python run.py test_omopdb_unit`

Stop after each phase to review noise from linting, stale-docstring review effort,
and test coverage for important documented behavior before adding more automation.
