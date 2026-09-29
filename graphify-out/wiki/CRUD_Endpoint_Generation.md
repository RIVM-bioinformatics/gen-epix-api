# CRUD Endpoint Generation

> 156 nodes · cohesion 0.03

## Key Concepts

- **CrudEndpointSet** (77 connections) — `gen_epix/fastapp/api/crud_endpoint_set.py`
- **CrudEndpointGenerator** (57 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **test_crud_endpoint_generator.py** (35 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **crud_endpoint_generator.py** (31 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **CrudEndpointType** (28 connections) — `gen_epix/fastapp/enum.py`
- **.create_crud_endpoint_set_for_domain()** (24 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **mock_exception_handler()** (23 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **mock_user_dependency()** (23 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **FastAPI** (23 connections)
- **._add_route()** (17 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.generate_endpoints()** (17 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **TestCrudEndpointGeneratorRegistration** (15 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.get_crud_endpoint_set_for_entity()** (14 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **FastAPI** (14 connections)
- **.generate_get_all()** (13 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **APIRouter** (13 connections)
- **crud_endpoint_set.py** (13 connections) — `gen_epix/fastapp/api/crud_endpoint_set.py`
- **create_ontology_endpoints()** (12 connections) — `gen_epix/casedb/api/ontology.py`
- **endpoint_function()** (11 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.generate_post_query()** (11 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.generate_delete_some()** (10 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.generate_post_one()** (10 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.test_generates_multiple_endpoint_types()** (10 connections) — `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- **.generate_get_one()** (9 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.generate_get_some()** (9 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- *... and 131 more nodes in this community*

## Relationships

- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (59 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (19 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (15 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (14 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (12 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (11 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (9 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (7 shared connections)
- [Row Filter Matching](Row_Filter_Matching.md) (7 shared connections)
- [ID String Parsing](ID_String_Parsing.md) (5 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (4 shared connections)
- [OMOP DB HTTP Client](OMOP_DB_HTTP_Client.md) (3 shared connections)

## Source Files

- `gen_epix/casedb/api/ontology.py`
- `gen_epix/fastapp/api/__init__.py`
- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `gen_epix/fastapp/api/crud_endpoint_set.py`
- `gen_epix/fastapp/enum.py`
- `test/fastapp/unit/api/test_crud_endpoint_generator.py`
- `test/fastapp/unit/api/test_crud_endpoint_set.py`

## Audit Trail

- EXTRACTED: 438 (79%)
- INFERRED: 116 (21%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*