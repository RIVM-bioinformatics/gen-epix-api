# OMOP Endpoints

> 12 nodes · cohesion 0.17

## Key Concepts

- **create_omop_endpoints()** (18 connections) — `gen_epix/omopdb/api/omop.py`
- **retrieve__person_ids_by_query()** (2 connections) — `gen_epix/omopdb/api/omop.py`
- **retrieve__persons_by_ids()** (2 connections) — `gen_epix/omopdb/api/omop.py`
- **retrieve__specimen_ids_by_cohort_ids()** (2 connections) — `gen_epix/omopdb/api/omop.py`
- **upload__persons()** (2 connections) — `gen_epix/omopdb/api/omop.py`
- **FastAPI** (2 connections)
- **Any** (1 connections)
- **APIRouter** (1 connections)
- **App** (1 connections)
- **Exception** (1 connections)
- **NoReturn** (1 connections)
- **Register OMOP upload, retrieval, and generated CRUD transport endpoints.** (1 connections) — `gen_epix/omopdb/api/omop.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (4 shared connections)
- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (3 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/api/omop.py`

## Audit Trail

- EXTRACTED: 16 (70%)
- INFERRED: 7 (30%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*