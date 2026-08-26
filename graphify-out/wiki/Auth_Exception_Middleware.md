# Auth Exception Middleware

> 26 nodes · cohesion 0.10

## Key Concepts

- **HandleAuthExceptionMiddleware** (11 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **handle_auth_exception.py** (9 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **middleware/__init__.py** (8 connections) — `gen_epix/fastapp/middleware/__init__.py`
- **UpdateResponseHeaderMiddleware** (7 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **update_response_header.py** (6 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **.dispatch()** (5 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **.__init__()** (4 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **limiter.py** (4 connections) — `gen_epix/fastapp/middleware/limiter.py`
- **limiter_key_func()** (4 connections) — `gen_epix/fastapp/middleware/limiter.py`
- **.dispatch()** (4 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **._log_exception()** (3 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **FastAPI** (2 connections)
- **FastAPI** (2 connections)
- **.__init__()** (2 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **App** (1 connections)
- **BaseHTTPMiddleware** (1 connections)
- **Exception** (1 connections)
- **Logger** (1 connections)
- **Request** (1 connections)
- **Response** (1 connections)
- **# TODO: check if other domain exceptions need to be caught here** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **Request** (1 connections)
- **Key function for the rate limiter.** (1 connections) — `gen_epix/fastapp/middleware/limiter.py`
- **BaseHTTPMiddleware** (1 connections)
- **Request** (1 connections)
- *... and 1 more nodes in this community*

## Relationships

- [App Composition & Startup](App_Composition_&_Startup.md) (9 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (4 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (3 shared connections)
- [Domain Exception Classes](Domain_Exception_Classes.md) (1 shared connections)
- [Commondb Auth Tests](Commondb_Auth_Tests.md) (1 shared connections)
- [HTTP Exception Classes](HTTP_Exception_Classes.md) (1 shared connections)
- [Organization API Models](Organization_API_Models.md) (1 shared connections)
- [Project Utility Functions](Project_Utility_Functions.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/middleware/__init__.py`
- `gen_epix/fastapp/middleware/handle_auth_exception.py`
- `gen_epix/fastapp/middleware/limiter.py`
- `gen_epix/fastapp/middleware/update_response_header.py`

## Audit Trail

- EXTRACTED: 48 (92%)
- INFERRED: 4 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*