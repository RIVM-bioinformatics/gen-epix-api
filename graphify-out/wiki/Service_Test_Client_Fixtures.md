# Service Test Client Fixtures

> 15 nodes · cohesion 0.17

## Key Concepts

- **ServiceTestClient** (18 connections) — `test/fastapp/service_test_client.py`
- **env()** (8 connections) — `test/fastapp/unit/repository/test_fastapp_repository.py`
- **TestRepository** (8 connections) — `test/fastapp/unit/repository/test_fastapp_repository.py`
- **.create_repository()** (7 connections) — `test/fastapp/service_test_client.py`
- **Any** (3 connections)
- **.get_model_instances_for_class()** (3 connections) — `test/fastapp/service_test_client.py`
- **.get_test_client()** (3 connections) — `test/fastapp/service_test_client.py`
- **Model** (2 connections)
- **.get_model_instance_for_class()** (2 connections) — `test/fastapp/service_test_client.py`
- **.test_create_some()** (2 connections) — `test/fastapp/unit/repository/test_fastapp_repository.py`
- **.test_to_from_sql()** (2 connections) — `test/fastapp/unit/repository/test_fastapp_repository.py`
- **ServiceType** (1 connections)
- **fixture** (1 connections)
- **FixtureRequest** (1 connections)
- **scenario_ids** (1 connections)

## Relationships

- [Fastapp CRUD Command Tests](Fastapp_CRUD_Command_Tests.md) (15 shared connections)
- [Fastapp Repository Performance Tests](Fastapp_Repository_Performance_Tests.md) (3 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (3 shared connections)
- [Repository Association Handling](Repository_Association_Handling.md) (2 shared connections)
- [RBAC Service Test Setup](RBAC_Service_Test_Setup.md) (1 shared connections)
- [Abac Service Access Control](Abac_Service_Access_Control.md) (1 shared connections)
- [Base Service Class](Base_Service_Class.md) (1 shared connections)

## Source Files

- `test/fastapp/service_test_client.py`
- `test/fastapp/unit/repository/test_fastapp_repository.py`

## Audit Trail

- EXTRACTED: 37 (84%)
- INFERRED: 7 (16%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*