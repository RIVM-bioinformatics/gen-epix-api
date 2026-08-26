# FastApp Entity & Model Core

> 123 nodes · cohesion 0.03

## Key Concepts

- **Entity** (174 connections) — `gen_epix/fastapp/domain/entity.py`
- **TestRegistrationAndLookups** (25 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **DomainException** (18 connections) — `gen_epix/fastapp/exc.py`
- **.has_model()** (15 connections) — `gen_epix/fastapp/domain/entity.py`
- **BaseModel** (10 connections)
- **.set_model_class()** (8 connections) — `gen_epix/fastapp/domain/entity.py`
- **._verify_and_parse_model_links()** (8 connections) — `gen_epix/fastapp/domain/entity.py`
- **TestCrudPermissionTypeMapCompleteness** (8 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **TestDAGAndCycleBehavior** (8 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **TestServiceTypeDagSorting** (8 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **.get_field_names()** (7 connections) — `gen_epix/fastapp/domain/entity.py`
- **Any** (7 connections)
- **Self** (7 connections)
- **TestStaticUtilities** (7 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **.get_obj_id()** (6 connections) — `gen_epix/fastapp/domain/entity.py`
- **.set_crud_command_class()** (6 connections) — `gen_epix/fastapp/domain/entity.py`
- **.topological_sort()** (6 connections) — `gen_epix/fastapp/domain/entity.py`
- **BaseDomainTestCase** (6 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **.model_class()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- **.set_create_api_model_class()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- **.set_db_model_class()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- **.set_read_api_model_class()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- **._validate_keys()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- **._validate_links()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- **._verify_link_field_name()** (5 connections) — `gen_epix/fastapp/domain/entity.py`
- *... and 98 more nodes in this community*

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (37 shared connections)
- [FastApp Domain Registry Core](FastApp_Domain_Registry_Core.md) (30 shared connections)
- [SA Repository Mapper & ERM Diagram Gen](SA_Repository_Mapper_&_ERM_Diagram_Gen.md) (8 shared connections)
- [Entity Key Generation](Entity_Key_Generation.md) (6 shared connections)
- [FastApp SA Repository Core](FastApp_SA_Repository_Core.md) (6 shared connections)
- [Domain Entity Registration](Domain_Entity_Registration.md) (6 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (6 shared connections)
- [Seq Dict Repository](Seq_Dict_Repository.md) (6 shared connections)
- [Dict Repository Loading Tests](Dict_Repository_Loading_Tests.md) (5 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (5 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (5 shared connections)
- [RBAC Service Test Setup](RBAC_Service_Test_Setup.md) (4 shared connections)

## Source Files

- `gen_epix/fastapp/domain/domain.py`
- `gen_epix/fastapp/domain/entity.py`
- `gen_epix/fastapp/exc.py`
- `gen_epix/fastapp/model.py`
- `gen_epix/seqdb/repositories/organization_dict.py`
- `test/fastapp/unit/domain/test_fastapp_domain.py`

## Audit Trail

- EXTRACTED: 277 (78%)
- INFERRED: 78 (22%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*