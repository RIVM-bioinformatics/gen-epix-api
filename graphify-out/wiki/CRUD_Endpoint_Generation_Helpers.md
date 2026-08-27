# CRUD Endpoint Generation Helpers

> 12 nodes · cohesion 0.21

## Key Concepts

- **.create_crud_endpoint_set_for_domain()** (23 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.get_crud_endpoint_set_for_entity()** (13 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **StringCasing** (12 connections) — `gen_epix/fastapp/enum.py`
- **.get_crud_endpoint_types_for_operations()** (4 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.get_crud_operations_for_permissions()** (4 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **.get_endpoint_basename()** (4 connections) — `gen_epix/fastapp/api/crud_endpoint_generator.py`
- **App** (2 connections)
- **.get_name_by_casing()** (2 connections) — `gen_epix/fastapp/domain/entity.py`
- **DummyEntity** (2 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **.get_name_by_casing()** (2 connections) — `test/fastapp/unit/test_fastapp_remote_app.py`
- **Hashable** (1 connections)
- **Model** (1 connections)

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (9 shared connections)
- [CRUD Endpoint Generator](CRUD_Endpoint_Generator.md) (7 shared connections)
- [ABAC API Routers](ABAC_API_Routers.md) (4 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (4 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (3 shared connections)
- [FastApp Entity & Model Core](FastApp_Entity_&_Model_Core.md) (3 shared connections)
- [Query Filter Engine](Query_Filter_Engine.md) (2 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (1 shared connections)
- [Geo API Endpoints](Geo_API_Endpoints.md) (1 shared connections)
- [Ontology API Endpoints](Ontology_API_Endpoints.md) (1 shared connections)
- [Organization API Endpoints](Organization_API_Endpoints.md) (1 shared connections)
- [OMOP API Endpoints](OMOP_API_Endpoints.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/api/crud_endpoint_generator.py`
- `gen_epix/fastapp/domain/entity.py`
- `gen_epix/fastapp/enum.py`
- `test/fastapp/unit/test_fastapp_remote_app.py`

## Audit Trail

- EXTRACTED: 56 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*