# App & Abac Service Setup

> 30 nodes · cohesion 0.08

## Key Concepts

- **.__init__()** (14 connections) — `gen_epix/commondb/env.py`
- **._init_service()** (11 connections) — `gen_epix/commondb/env.py`
- **.compose_application()** (10 connections) — `gen_epix/commondb/env.py`
- **._get_services()** (9 connections) — `gen_epix/commondb/env.py`
- **create_ssl_context()** (8 connections) — `gen_epix/fastapp/util.py`
- **App** (6 connections) — `gen_epix/commondb/env.py`
- **Any** (5 connections)
- **._setup_application_logging()** (4 connections) — `gen_epix/commondb/env.py`
- **Enum** (4 connections)
- **.cfg()** (3 connections) — `gen_epix/commondb/env.py`
- **Dynaconf** (3 connections)
- **Logger** (2 connections)
- **RbacService** (2 connections)
- **AbacService** (1 connections)
- **Command** (1 connections)
- **Domain** (1 connections)
- **Model** (1 connections)
- **UserManager** (1 connections)
- **Create the App instance, initialise all services and repositories, and register…** (1 connections) — `gen_epix/commondb/env.py`
- **Retrieve the core services from the application implementation details.** (1 connections) — `gen_epix/commondb/env.py`
- **Initialise a single service and its repository from configuration.** (1 connections) — `gen_epix/commondb/env.py`
- **Application class for the GenEpix FastAPI application. Overrides some…** (1 connections) — `gen_epix/commondb/env.py`
- **Log the start of the application composition process.** (1 connections) — `gen_epix/commondb/env.py`
- **Loaded Dynaconf settings object.** (1 connections) — `gen_epix/commondb/env.py`
- **Initialise the composer, parse configuration, and compose the application.** (1 connections) — `gen_epix/commondb/env.py`
- *... and 5 more nodes in this community*

## Relationships

- [App Composition & Startup](App_Composition_&_Startup.md) (10 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (8 shared connections)
- [RBAC/ABAC Policy Implementations](RBAC-ABAC_Policy_Implementations.md) (3 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)
- [App Composition & Service Wiring](App_Composition_&_Service_Wiring.md) (1 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (1 shared connections)
- [ABAC Base Policies](ABAC_Base_Policies.md) (1 shared connections)
- [App Command/Domain Base](App_Command-Domain_Base.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/env.py`
- `gen_epix/fastapp/util.py`

## Audit Trail

- EXTRACTED: 62 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*