# App Composer Base

> 23 nodes · cohesion 0.11

## Key Concepts

- **BaseAppComposer** (20 connections) — `gen_epix/commondb/base_env.py`
- **base_env.py** (16 connections) — `gen_epix/commondb/base_env.py`
- **.create_repository()** (7 connections) — `gen_epix/commondb/base_env.py`
- **.services()** (5 connections) — `gen_epix/commondb/base_env.py`
- **.repositories()** (4 connections) — `gen_epix/commondb/base_env.py`
- **Enum** (4 connections)
- **.cfg()** (3 connections) — `gen_epix/commondb/base_env.py`
- **.idp_user_dependency()** (2 connections) — `gen_epix/commondb/base_env.py`
- **.__init__()** (2 connections) — `gen_epix/commondb/base_env.py`
- **.new_user_dependency()** (2 connections) — `gen_epix/commondb/base_env.py`
- **.registered_user_dependency()** (2 connections) — `gen_epix/commondb/base_env.py`
- **Any** (2 connections)
- **Dynaconf** (2 connections)
- **Define the abstract composition contract shared by commondb applications.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Encapsulates dependencies and repository construction for concrete app…** (1 connections) — `gen_epix/commondb/base_env.py`
- **Initialize abstract composition state placeholders. Raises:…** (1 connections) — `gen_epix/commondb/base_env.py`
- **Return the application's resolved Dynaconf settings.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Return services keyed by their service type.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Return repositories keyed by their service type.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Return the API dependency that resolves registered users.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Return the API dependency that resolves new users.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Return the API dependency that resolves identity-provider users.** (1 connections) — `gen_epix/commondb/base_env.py`
- **Create a repository using the configured persistence backend. Args: cls:…** (1 connections) — `gen_epix/commondb/base_env.py`

## Relationships

- [Generic Repository Base](Generic_Repository_Base.md) (4 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (4 shared connections)
- [Domain & Entity Registry](Domain_&_Entity_Registry.md) (3 shared connections)
- [In-Memory Dict Repository](In-Memory_Dict_Repository.md) (3 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (2 shared connections)
- [SQLAlchemy Repository Queries](SQLAlchemy_Repository_Queries.md) (2 shared connections)
- [Audit Metadata Modifiers](Audit_Metadata_Modifiers.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [Domain Registry & ABAC Policies](Domain_Registry_&_ABAC_Policies.md) (1 shared connections)
- [Commondb SQLAlchemy Mapper](Commondb_SQLAlchemy_Mapper.md) (1 shared connections)
- [Test Client Initialization](Test_Client_Initialization.md) (1 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/base_env.py`

## Audit Trail

- EXTRACTED: 49 (91%)
- INFERRED: 5 (9%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*