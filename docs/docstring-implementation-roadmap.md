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

1. `transform`
2. `fastapp`
3. `commondb`
4. `seqdb`
5. `casedb`

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

## Later Phases

For each later package, repeat the same bottom-up sequence and expand the
configured Ruff docstring scope in local linting and CI only after the package
has been documented.

Phase 2 adds `gen_epix/fastapp`.

Phase 3 adds `gen_epix/commondb`.

Phase 4 adds `gen_epix/seqdb`.

Phase 5 adds `gen_epix/casedb`.

Stop after each phase to review noise from linting, stale-docstring review effort,
and test coverage for important documented behavior before adding more automation.
