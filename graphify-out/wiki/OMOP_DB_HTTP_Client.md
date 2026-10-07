# OMOP DB HTTP Client

> 11 nodes · cohesion 0.31

## Key Concepts

- **HttpMethod** (19 connections) — `gen_epix/fastapp/enum.py`
- **OmopdbClient** (12 connections) — `gen_epix/omopdb/services/client.py`
- **test_omopdb_client.py** (11 connections) — `test/omopdb/unit/services/test_omopdb_client.py`
- **omopdb/services/client.py** (10 connections) — `gen_epix/omopdb/services/client.py`
- **_make_app()** (6 connections) — `test/omopdb/unit/services/test_omopdb_client.py`
- **test_registers_person_retrieval_routes_and_handlers()** (3 connections) — `test/omopdb/unit/services/test_omopdb_client.py`
- **.__init__()** (2 connections) — `gen_epix/omopdb/services/client.py`
- **_fake_app_init()** (2 connections) — `test/omopdb/unit/services/test_omopdb_client.py`
- **test_retrieve_persons_by_query_posts_query_body()** (2 connections) — `test/omopdb/unit/services/test_omopdb_client.py`
- **Encapsulates identifying an HTTP request method.** (1 connections) — `gen_epix/fastapp/enum.py`
- **Any** (1 connections)

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (8 shared connections)
- [FastApp HTTP Client](FastApp_HTTP_Client.md) (5 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (3 shared connections)
- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (3 shared connections)
- [CRUD Endpoint Generation](CRUD_Endpoint_Generation.md) (3 shared connections)
- [Commondb Client](Commondb_Client.md) (3 shared connections)
- [Geographic Region Commands](Geographic_Region_Commands.md) (2 shared connections)
- [User & Person Commands](User_&_Person_Commands.md) (2 shared connections)
- [Casedb Client Handlers](Casedb_Client_Handlers.md) (1 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (1 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (1 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/enum.py`
- `gen_epix/omopdb/services/client.py`
- `test/omopdb/unit/services/test_omopdb_client.py`

## Audit Trail

- EXTRACTED: 43 (83%)
- INFERRED: 9 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*