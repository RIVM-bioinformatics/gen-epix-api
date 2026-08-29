# Commondb App Composition (env.py)

> 24 nodes

## Key Concepts

- **.__init__()** (14 connections) — `gen_epix/commondb/env.py`
- **._init_service()** (11 connections) — `gen_epix/commondb/env.py`
- **.compose_application()** (10 connections) — `gen_epix/commondb/env.py`
- **._get_services()** (9 connections) — `gen_epix/commondb/env.py`
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
- **OrganizationService** (1 connections)
- **RoleGenerator** (1 connections)
- **Create the App instance, initialise all services and repositories, and register…** (1 connections) — `gen_epix/commondb/env.py`
- **Retrieve the core services from the application implementation details.** (1 connections) — `gen_epix/commondb/env.py`
- **Initialise a single service and its repository from configuration.** (1 connections) — `gen_epix/commondb/env.py`
- **Log the start of the application composition process.** (1 connections) — `gen_epix/commondb/env.py`
- **Loaded Dynaconf settings object.** (1 connections) — `gen_epix/commondb/env.py`
- **Initialise the composer, parse configuration, and compose the application.** (1 connections) — `gen_epix/commondb/env.py`

## Relationships

- [AppCfg](AppCfg.md) (10 shared connections)
- [CrudOperation](CrudOperation.md) (7 shared connections)
- [commondb/domain/model/__init__.py](commondb-domain-model-__init__.py.md) (3 shared connections)
- [OrganizationService](OrganizationService.md) (1 shared connections)
- [AuthService](AuthService.md) (1 shared connections)
- [Policy](Policy.md) (1 shared connections)
- [CommondbDictModelModifier](CommondbDictModelModifier.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/env.py`

## Audit Trail

- EXTRACTED: 52 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*