# Organization & User Endpoints

> 25 nodes · cohesion 0.09

## Key Concepts

- **create_organization_endpoints()** (34 connections) — `gen_epix/commondb/api/organization.py`
- **.app()** (9 connections) — `gen_epix/commondb/base_env.py`
- **data_collection_sets__put__data_collections()** (3 connections) — `gen_epix/commondb/api/organization.py`
- **invite_user__constraints()** (3 connections) — `gen_epix/commondb/api/organization.py`
- **organization_sets__put__organizations()** (3 connections) — `gen_epix/commondb/api/organization.py`
- **organizations__put__identifier_issuers()** (3 connections) — `gen_epix/commondb/api/organization.py`
- **retrieve__organization_contacts()** (3 connections) — `gen_epix/commondb/api/organization.py`
- **operational_data__delete()** (3 connections) — `gen_epix/commondb/api/system.py`
- **anonymize_user()** (2 connections) — `gen_epix/commondb/api/organization.py`
- **invite_user()** (2 connections) — `gen_epix/commondb/api/organization.py`
- **update_user()** (2 connections) — `gen_epix/commondb/api/organization.py`
- **update_user_own_organization()** (2 connections) — `gen_epix/commondb/api/organization.py`
- **user_me__retrieve_permissions()** (2 connections) — `gen_epix/commondb/api/organization.py`
- **user_registrations__post_one()** (2 connections) — `gen_epix/commondb/api/organization.py`
- **FastAPI** (2 connections)
- **user_me__get_one()** (1 connections) — `gen_epix/commondb/api/organization.py`
- **Any** (1 connections)
- **APIRouter** (1 connections)
- **App** (1 connections)
- **Exception** (1 connections)
- **NoReturn** (1 connections)
- **ServiceType** (1 connections)
- **Register all non-CRUD organization endpoints on the given router.** (1 connections) — `gen_epix/commondb/api/organization.py`
- **App** (1 connections)
- **Return the composed FastApp application.** (1 connections) — `gen_epix/commondb/base_env.py`

## Relationships

- [Case API Endpoints](Case_API_Endpoints.md) (12 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (9 shared connections)
- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (2 shared connections)
- [App Composer Base](App_Composer_Base.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/api/organization.py`
- `gen_epix/commondb/api/system.py`
- `gen_epix/commondb/base_env.py`

## Audit Trail

- EXTRACTED: 33 (58%)
- INFERRED: 24 (42%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*