# Root User Bootstrap

> 7 nodes · cohesion 0.33

## Key Concepts

- **create_root_user_from_claims()** (6 connections) — `gen_epix/commondb/test/util.py`
- **get_existing_root_user()** (4 connections) — `gen_epix/commondb/test/util.py`
- **App** (2 connections)
- **Dynaconf** (2 connections)
- **User** (2 connections)
- **Retrieve the configured root user from an initialized application. Args: cfg:…** (1 connections) — `gen_epix/commondb/test/util.py`
- **Create the configured root user through the application's claim workflow. Args:…** (1 connections) — `gen_epix/commondb/test/util.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (3 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/test/util.py`

## Audit Trail

- EXTRACTED: 11 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*