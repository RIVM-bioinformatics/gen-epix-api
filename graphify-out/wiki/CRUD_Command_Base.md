# CRUD Command Base

> 35 nodes · cohesion 0.09

## Key Concepts

- **UpdateAssociationCommand** (20 connections) — `gen_epix/commondb/domain/command/base.py`
- **.crud()** (11 connections) — `gen_epix/fastapp/service.py`
- **.update_association()** (11 connections) — `gen_epix/fastapp/service.py`
- **.__init__()** (10 connections) — `gen_epix/fastapp/service.py`
- **._verify_same_service_links()** (9 connections) — `gen_epix/fastapp/service.py`
- **._verify_other_service_links()** (8 connections) — `gen_epix/fastapp/service.py`
- **Any** (8 connections)
- **.crud_repository()** (7 connections) — `gen_epix/fastapp/service.py`
- **.create_log_message()** (6 connections) — `gen_epix/fastapp/service.py`
- **._get_model_links()** (6 connections) — `gen_epix/fastapp/service.py`
- **.set_object_id()** (6 connections) — `gen_epix/fastapp/service.py`
- **.register_crud_listener()** (5 connections) — `gen_epix/fastapp/service.py`
- **.unregister_crud_listener()** (5 connections) — `gen_epix/fastapp/service.py`
- **.logger()** (4 connections) — `gen_epix/fastapp/service.py`
- **.repository()** (4 connections) — `gen_epix/fastapp/service.py`
- **Hashable** (4 connections)
- **Model** (4 connections)
- **.generate_id()** (3 connections) — `gen_epix/fastapp/service.py`
- **.props()** (3 connections) — `gen_epix/fastapp/service.py`
- **.register_handlers()** (3 connections) — `gen_epix/fastapp/service.py`
- **.service_type()** (2 connections) — `gen_epix/fastapp/service.py`
- **Logger** (2 connections)
- **setter** (2 connections)
- **Repository** (2 connections)
- **Extends parent UpdateAssociationCommand with more narrowly typed properties.** (1 connections) — `gen_epix/commondb/domain/command/base.py`
- *... and 10 more nodes in this community*

## Relationships

- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (20 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (13 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (4 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (4 shared connections)
- [Generic Repository Base](Generic_Repository_Base.md) (2 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (2 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (2 shared connections)
- [Ontology Commands](Ontology_Commands.md) (1 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (1 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (1 shared connections)
- [Case Type Set Association](Case_Type_Set_Association.md) (1 shared connections)
- [Column Set Association](Column_Set_Association.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/command/base.py`
- `gen_epix/fastapp/service.py`

## Audit Trail

- EXTRACTED: 103 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*