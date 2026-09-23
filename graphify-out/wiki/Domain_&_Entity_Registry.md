# Domain & Entity Registry

> 215 nodes · cohesion 0.02

## Key Concepts

- **Entity** (192 connections) — `gen_epix/fastapp/domain/entity.py`
- **Domain** (110 connections) — `gen_epix/fastapp/domain/domain.py`
- **OnException** (38 connections) — `gen_epix/fastapp/enum.py`
- **Hashable** (25 connections)
- **Model** (19 connections)
- **Permission** (17 connections)
- **.has_model()** (15 connections) — `gen_epix/fastapp/domain/entity.py`
- **.register_entity()** (12 connections) — `gen_epix/fastapp/domain/domain.py`
- **.register_command()** (11 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_dag_sorted_entities()** (10 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_command_exists()** (10 connections) — `gen_epix/fastapp/domain/domain.py`
- **BaseModel** (10 connections)
- **._verify_service_type_exists()** (9 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_model_name()** (8 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_permissions_for_model()** (8 connections) — `gen_epix/fastapp/domain/domain.py`
- **._link_new_command()** (8 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_model_exists()** (8 connections) — `gen_epix/fastapp/domain/domain.py`
- **.set_model_class()** (8 connections) — `gen_epix/fastapp/domain/entity.py`
- **._verify_and_parse_model_links()** (8 connections) — `gen_epix/fastapp/domain/entity.py`
- **TestDAGAndCycleBehavior** (8 connections) — `test/fastapp/unit/domain/test_fastapp_domain.py`
- **.get_entity_for_model()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_model_links()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_permissions_for_command()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **.get_service_type_for_entity()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- **._verify_entity_exists()** (7 connections) — `gen_epix/fastapp/domain/domain.py`
- *... and 190 more nodes in this community*

## Relationships

- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (63 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (20 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (11 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (10 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (10 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (10 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (8 shared connections)
- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (7 shared connections)
- [Seq Repository Queries](Seq_Repository_Queries.md) (7 shared connections)
- [Transform Enums & Intervals](Transform_Enums_&_Intervals.md) (6 shared connections)
- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (5 shared connections)
- [Field Type Metadata](Field_Type_Metadata.md) (5 shared connections)

## Source Files

- `gen_epix/fastapp/app.py`
- `gen_epix/fastapp/domain/domain.py`
- `gen_epix/fastapp/domain/entity.py`
- `gen_epix/fastapp/enum.py`
- `gen_epix/fastapp/model.py`
- `gen_epix/fastapp/service.py`
- `test/fastapp/integration/repository/test_fastapp_repository.py`
- `test/fastapp/unit/domain/test_fastapp_domain.py`

## Audit Trail

- EXTRACTED: 536 (83%)
- INFERRED: 109 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*