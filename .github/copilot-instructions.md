# Gen-EpiX AI Agent Instructions

Gen-EpiX is a **multi-service genomic epidemiology platform** with strict access controls and a sophisticated architectural pattern. Understanding these core patterns will make you immediately productive.

## Architecture Overview

**Four Independent Services**: `casedb`, `seqdb`, `omopdb`, `commondb` - each runs as a separate FastAPI app on different ports with its own database, auth, and domain logic.

**Hexagonal Architecture**: Each service follows strict layering:
- `domain/` - Pure business logic (models, commands, policies)  
- `services/` - Application layer (orchestration, CRUD operations)
- `repositories/` - Data access (SQLAlchemy or in-memory dict implementations)
- `api/` - FastAPI endpoints and HTTP concerns

**Command-Query Pattern**: All operations flow through `Command` objects handled by the central `App` mediator. Never call services directly - always use `app.handle(SomeCommand(...))`.

## Key Patterns

### 1. Service/Repository/UnitOfWork Pattern
```python
# Always use Unit of Work for database transactions
with self.repository.uow() as uow:
    result = self.repository.crud(uow, user_id, Model, obj, None, CrudOperation.CREATE_ONE)
```

### 2. Command-Driven Architecture
```python
# Commands are the only way to trigger operations
from gen_epix.casedb.domain.command import CreateCaseCommand
cmd = CreateCaseCommand(user=user, case_data=data)
result = app.handle(cmd)  # Goes through policies, auth, logging
```

### 3. ABAC/RBAC Authorization
- **RBAC**: Role-based (`ROOT`, `APP_ADMIN`, `ORG_ADMIN`, `ORG_USER`, `GUEST`)
- **ABAC**: Attribute-based policies in `policies/` directories
- Policies are automatically applied during command execution via the `PolicyDecisionPoint`

### 4. Multi-Repository Support
Each service supports both SQLAlchemy and in-memory dict repositories:
```python
# Configuration determines repository type
enum.RepositoryType.SA_SQL  # SQLAlchemy + real database
enum.RepositoryType.DICT    # In-memory for testing
```

## Critical Development Commands

### Starting Services
```bash
# New standardized format: SERVICE_NAME IDP_CONFIG REPOSITORY_CONFIG
python run.py api CASEDB IDPS DICT_DEMO        # Production auth with demo data
python run.py api CASEDB MOCK DICT_DEMO        # Mock auth for dev
python run.py api SEQDB IDPS SA_SQLITE_DEMO    # SeqDB with SQLite and demo data
python run.py api OMOPDB MOCK DICT_EMPTY       # OMOP with mock auth and empty data

# Services run on different ports:
# - CASEDB: 8000
# - SEQDB: 8001  
# - OMOPDB: 8002
# - COMMONDB: 8000
```

### Testing
```bash
python run.py test_all                    # Full test suite
python run.py test_casedb_integration     # Service-specific tests
python run.py test_all_unit              # Unit tests only
python run.py test_integration_content    # Content integration tests
python run.py test_remote_app_unit        # Remote service connection tests
```

### Data Loading
```bash
python run.py etl_load_demo_data all     # Load demo data for all services
python run.py etl_load_demo_data casedb  # Service-specific data
```

## Project-Specific Conventions

### File Organization
- **Domain logic**: `gen_epix/{service}/domain/`
- **Service implementations**: `gen_epix/{service}/services/`  
- **Repository models**: `gen_epix/{service}/repositories/sa_model/`
- **API endpoints**: `gen_epix/{service}/api/`

### Configuration System
**NEW: Dynaconf-based Configuration Management**
- **Settings files**: `gen_epix/{service}/config/settings.toml` (TOML format)
- **Secrets**: `gen_epix/{service}/config/.secrets.{component}.toml` (separate files by component)
- **Auth configs**: `gen_epix/{service}/config/idp/` (IDP configurations)
- **Repository configs**: Service-specific TOML files with connection strings, file paths, etc.
- **Environment variables**: Auto-discovery via `set_env_variables()` function
- **Dev configs**: Standardized patterns like `DICT_DEMO`, `SA_SQLITE_DEMO`, `SA_SQL`, etc.

Configuration structure example:
```toml
[service.auth.props.root.organization]
id = "018d074d-ea0c-e942-07db-a3cc0ba1d653"
name = "DUMMY"
legal_entity_code = "DUMMY"

[service.auth.props.root.user]
key = "root@dummy.org"
email = "root@dummy.org"

[repository.defaults]
type = "DICT"
[repository.defaults.props]
dir = "./data/casedb/demo"
```

### Transform Framework
The `gen_epix.transform` module provides stream-processing pipelines for data transformation:
```python
from gen_epix.transform import FieldTransformer, TransformerPipeline
pipeline = TransformerPipeline([FieldTransformer("name", str.title)])
```

## Common Gotchas

1. **Environment Variables**: Services auto-discover configs via `ConfigDiscovery.get_config_path()` - don't hardcode paths
2. **Repository Registration**: Always call `repository.register_mappers()` before using SQLAlchemy repos
3. **Service Dependencies**: `casedb` depends on `seqdb` - start `seqdb` when working with `casedb`
4. **Command IDs**: All commands auto-generate UUIDs - don't manually set `id` fields
5. **User Context**: Commands require a `user` parameter for authorization - use test fixtures for this
5. **User Context**: Commands require a `user` parameter for authorization - use test fixtures for this

## Integration Points

- **Cross-service communication**: Services communicate via HTTP APIs, not direct imports
- **Remote service support**: Services can connect to remote instances via `RemoteApp` pattern
- **Shared models**: Common models in `gen_epix.commondb` (User, Organization, etc.)
- **Auth tokens**: JWT tokens shared across services via `gen_epix.fastapp.services.auth`

Understanding these patterns means you can navigate between any service and immediately understand the flow from API → Command → Service → Repository → Database.