# ServiceTestClient

> 20 nodes · cohesion 0.13

## Key Concepts

- **ServiceTestClient** (18 connections) — `test/fastapp/service_test_client.py`
- **.__init__()** (14 connections) — `test/fastapp/service_test_client.py`
- **.create_repository()** (7 connections) — `test/fastapp/service_test_client.py`
- **env()** (6 connections) — `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- **TestRepository** (5 connections) — `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- **Service1** (5 connections) — `test/fastapp/service.py`
- **Service2** (5 connections) — `test/fastapp/service.py`
- **.test_create_some()** (4 connections) — `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- **Any** (3 connections)
- **.get_model_instances_for_class()** (3 connections) — `test/fastapp/service_test_client.py`
- **.get_test_client()** (3 connections) — `test/fastapp/service_test_client.py`
- **.finalize_outputs()** (2 connections) — `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- **.test_tear_down()** (2 connections) — `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- **Model** (2 connections)
- **.get_model_instance_for_class()** (2 connections) — `test/fastapp/service_test_client.py`
- **fixture** (1 connections)
- **FixtureRequest** (1 connections)
- **.register_handlers()** (1 connections) — `test/fastapp/service.py`
- **.register_handlers()** (1 connections) — `test/fastapp/service.py`
- **ServiceType** (1 connections)

## Relationships

- [test_fastapp_rbac_service.py](test_fastapp_rbac_service.py.md) (18 shared connections)
- [test/test_client/util.py](test-test_client-util.py.md) (3 shared connections)
- [BaseService](BaseService.md) (3 shared connections)
- [BaseRepository](BaseRepository.md) (3 shared connections)
- [DictRepository](DictRepository.md) (2 shared connections)
- [env](env.md) (2 shared connections)
- [.get_test_client](get_test_client.md) (1 shared connections)
- [RBACTestClient](RBACTestClient.md) (1 shared connections)
- [casedb/domain/enum.py](casedb-domain-enum.py.md) (1 shared connections)
- [UserManager](UserManager.md) (1 shared connections)
- [App](App.md) (1 shared connections)

## Source Files

- `test/fastapp/performance/repository/test_fastapp_repository_performance.py`
- `test/fastapp/service.py`
- `test/fastapp/service_test_client.py`

## Audit Trail

- EXTRACTED: 54 (89%)
- INFERRED: 7 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*