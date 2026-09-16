# App Composition & ETL Setup

> 328 nodes · cohesion 0.02

## Key Concepts

- **commondb/domain/enum.py** (139 connections) — `gen_epix/commondb/domain/enum.py`
- **gen_epix/fastapp/enum.py** (119 connections) — `gen_epix/fastapp/enum.py`
- **commondb/domain/model/__init__.py** (104 connections) — `gen_epix/commondb/domain/model/__init__.py`
- **commondb/domain/command/__init__.py** (84 connections) — `gen_epix/commondb/domain/command/__init__.py`
- **AppImplDetails** (69 connections) — `gen_epix/commondb/app_impl_details.py`
- **gen_epix/fastapp/__init__.py** (66 connections) — `gen_epix/fastapp/__init__.py`
- **omopdb/domain/model/__init__.py** (64 connections) — `gen_epix/omopdb/domain/model/__init__.py`
- **commondb/domain/util.py** (62 connections) — `gen_epix/commondb/domain/util.py`
- **fastapp/app.py** (56 connections) — `gen_epix/fastapp/app.py`
- **gen_epix/util.py** (53 connections) — `gen_epix/util.py`
- **AppType** (51 connections) — `gen_epix/commondb/domain/enum.py`
- **commondb/env.py** (47 connections) — `gen_epix/commondb/env.py`
- **gen_epix/__init__.py** (46 connections) — `gen_epix/__init__.py`
- **test_seqdb_distance_optimization_benchmark.py** (42 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`
- **RoleSet** (40 connections) — `gen_epix/commondb/domain/enum.py`
- **test_client/enum.py** (40 connections) — `test/test_client/enum.py`
- **test_client.py** (39 connections) — `gen_epix/commondb/test/test_client.py`
- **get_app_cfgs()** (36 connections) — `gen_epix/commondb/domain/util.py`
- **app_impl_details.py** (35 connections) — `gen_epix/commondb/app_impl_details.py`
- **EnumTestType** (32 connections) — `test/test_client/enum.py`
- **DevRepositoryConfig** (31 connections) — `gen_epix/commondb/domain/enum.py`
- **gen_epix/fastapp/service.py** (31 connections) — `gen_epix/fastapp/service.py`
- **omopdb/domain/enum.py** (31 connections) — `gen_epix/omopdb/domain/enum.py`
- **test_casedb_case_upload.py** (31 connections) — `test/casedb/integration/case_upload/test_casedb_case_upload.py`
- **OrganizationService** (27 connections) — `gen_epix/commondb/services/organization.py`
- *... and 303 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (151 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (77 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (75 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (55 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (51 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (42 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (34 shared connections)
- [Role Mapping Generator](Role_Mapping_Generator.md) (30 shared connections)
- [Organization Contacts Retrieval](Organization_Contacts_Retrieval.md) (29 shared connections)
- [Casedb Service Wiring](Casedb_Service_Wiring.md) (27 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (26 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (26 shared connections)

## Source Files

- `.github/workflows/main.yml`
- `etl.py`
- `gen_epix/__init__.py`
- `gen_epix/commondb/api/abac.py`
- `gen_epix/commondb/api/auth.py`
- `gen_epix/commondb/api/rbac.py`
- `gen_epix/commondb/app_impl_details.py`
- `gen_epix/commondb/domain/__init__.py`
- `gen_epix/commondb/domain/command/__init__.py`
- `gen_epix/commondb/domain/enum.py`
- `gen_epix/commondb/domain/exc.py`
- `gen_epix/commondb/domain/model/__init__.py`
- `gen_epix/commondb/domain/policy/permission.py`
- `gen_epix/commondb/domain/policy/system.py`
- `gen_epix/commondb/domain/service/__init__.py`
- `gen_epix/commondb/domain/service/abac.py`
- `gen_epix/commondb/domain/service/organization.py`
- `gen_epix/commondb/domain/service/rbac.py`
- `gen_epix/commondb/domain/service/system.py`
- `gen_epix/commondb/domain/service/user_manager.py`

## Audit Trail

- EXTRACTED: 2130 (95%)
- INFERRED: 119 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*