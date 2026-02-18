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

```console
python -m pytest --gremlins
```

Generate an HTML mutation report:

```console
python -m pytest --gremlins --gremlin-report=html
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

## Notes

- `pytest --gremlins` is expected to run much slower than a normal `pytest` run.
- Terminal output includes the mutation summary.
- With `--gremlin-report=html`, the plugin writes an HTML report to its default output location.
