# API Exception Handling

> 24 nodes · cohesion 0.20

## Key Concepts

- **commondb/api/exc.py** (26 connections) — `gen_epix/commondb/api/exc.py`
- **handle_command()** (14 connections) — `gen_epix/commondb/api/exc.py`
- **handle_exception()** (13 connections) — `gen_epix/commondb/api/exc.py`
- **LogLevel** (12 connections) — `gen_epix/fastapp/enum.py`
- **IdsError** (12 connections) — `gen_epix/fastapp/exc.py`
- **generate_handle_exception_function()** (10 connections) — `gen_epix/commondb/api/exc.py`
- **_handle_invalid_ids_exception()** (8 connections) — `gen_epix/commondb/api/exc.py`
- **Logger** (7 connections)
- **NoReturn** (7 connections)
- **log_and_raise_invalid_ids_exception()** (6 connections) — `gen_epix/commondb/api/exc.py`
- **_handle_auth_exception()** (5 connections) — `gen_epix/commondb/api/exc.py`
- **_handle_service_exception()** (5 connections) — `gen_epix/commondb/api/exc.py`
- **Hashable** (5 connections)
- **__extract_invalid_ids()** (4 connections) — `gen_epix/commondb/api/exc.py`
- **DuplicateIdsError** (4 connections) — `gen_epix/fastapp/exc.py`
- **get_logger_fmap()** (3 connections) — `gen_epix/commondb/api/exc.py`
- **App** (3 connections)
- **Exception** (3 connections)
- **User** (3 connections)
- **.__init__()** (2 connections) — `gen_epix/fastapp/exc.py`
- **.__init__()** (2 connections) — `gen_epix/fastapp/exc.py`
- **Any** (1 connections)
- **Command** (1 connections)
- **# TODO: Consider refactoring this into a callable ExceptionHandler class** (1 connections) — `gen_epix/commondb/api/exc.py`

## Relationships

- [Domain Exception Classes](Domain_Exception_Classes.md) (10 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (7 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (5 shared connections)
- [Organization API Models](Organization_API_Models.md) (4 shared connections)
- [Case API Endpoints](Case_API_Endpoints.md) (3 shared connections)
- [OMOP API Endpoints](OMOP_API_Endpoints.md) (3 shared connections)
- [ETL Result Logging](ETL_Result_Logging.md) (3 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (2 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (2 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (1 shared connections)
- [Casedb Domain CRUD Commands](Casedb_Domain_CRUD_Commands.md) (1 shared connections)
- [Case Data Serialization](Case_Data_Serialization.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/api/exc.py`
- `gen_epix/fastapp/enum.py`
- `gen_epix/fastapp/exc.py`

## Audit Trail

- EXTRACTED: 99 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*