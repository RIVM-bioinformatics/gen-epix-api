# Omopdb Remote App Client

> 16 nodes · cohesion 0.16

## Key Concepts

- **OmopdbRemoteApp** (12 connections) — `gen_epix/omopdb/services/remote_app.py`
- **test_omopdb_remote_app.py** (11 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **_make_app()** (5 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **.retrieve_persons_by_id()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **.retrieve_persons_by_query()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **.retrieve_specimen_ids_by_cohort_ids()** (4 connections) — `gen_epix/omopdb/services/remote_app.py`
- **_fake_app_init()** (4 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **.__init__()** (3 connections) — `gen_epix/omopdb/services/remote_app.py`
- **test_registers_person_retrieval_routes_and_handlers()** (2 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **test_retrieve_persons_by_query_posts_query_body()** (2 connections) — `test/omopdb/unit/services/test_omopdb_remote_app.py`
- **Any** (1 connections)
- **Retrieve specimen IDs for the given cohort IDs.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Remote app client for the omopdb service.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Register all omopdb routes and command handlers.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Retrieve persons matching the given query.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`
- **Retrieve full person records by their IDs.** (1 connections) — `gen_epix/omopdb/services/remote_app.py`

## Relationships

- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (5 shared connections)
- [Base Model & Identifiers](Base_Model_&_Identifiers.md) (4 shared connections)
- [OMOP Domain CRUD Commands](OMOP_Domain_CRUD_Commands.md) (4 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (1 shared connections)
- [Commondb Remote App Client](Commondb_Remote_App_Client.md) (1 shared connections)
- [Person Upload Command](Person_Upload_Command.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)
- [Remote App Auth Header Tests](Remote_App_Auth_Header_Tests.md) (1 shared connections)
- [Remote App Test Base](Remote_App_Test_Base.md) (1 shared connections)

## Source Files

- `gen_epix/omopdb/services/remote_app.py`
- `test/omopdb/unit/services/test_omopdb_remote_app.py`

## Audit Trail

- EXTRACTED: 34 (89%)
- INFERRED: 4 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*