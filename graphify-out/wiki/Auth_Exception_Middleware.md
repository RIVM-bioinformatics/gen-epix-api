# Auth Exception Middleware

> 36 nodes · cohesion 0.07

## Key Concepts

- **HandleAuthExceptionMiddleware** (12 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **handle_auth_exception.py** (9 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **middleware/__init__.py** (9 connections) — `gen_epix/fastapp/middleware/__init__.py`
- **UpdateResponseHeaderMiddleware** (8 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **update_response_header.py** (6 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **.dispatch()** (5 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **.__init__()** (5 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **limiter.py** (5 connections) — `gen_epix/fastapp/middleware/limiter.py`
- **._log_exception()** (4 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **limiter_key_func()** (4 connections) — `gen_epix/fastapp/middleware/limiter.py`
- **.dispatch()** (4 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/middleware/update_response_header.py`
- **FastAPI** (2 connections)
- **FastAPI** (2 connections)
- **BaseHTTPMiddleware** (1 connections)
- **Exception** (1 connections)
- **Logger** (1 connections)
- **Request** (1 connections)
- **Response** (1 connections)
- **Middleware that converts authentication errors to HTTP responses.** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **Encapsulates logging authentication errors and return an HTTP 401 response.** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **Initialize a HandleAuthExceptionMiddleware instance.** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **Log an authentication exception through the configured application logger.** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **Process a request and translate authentication exception groups to HTTP 401.** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- **# TODO: check if other domain exceptions need to be caught here** (1 connections) — `gen_epix/fastapp/middleware/handle_auth_exception.py`
- *... and 11 more nodes in this community*

## Relationships

- [FastAPI App Composition](FastAPI_App_Composition.md) (7 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (3 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [No-Response Middleware](No-Response_Middleware.md) (2 shared connections)
- [Command Exception Handling](Command_Exception_Handling.md) (1 shared connections)
- [Auth Claim Utilities](Auth_Claim_Utilities.md) (1 shared connections)
- [Auth Test Clients & Mocks](Auth_Test_Clients_&_Mocks.md) (1 shared connections)
- [Casedb ABAC & Geo Endpoints](Casedb_ABAC_&_Geo_Endpoints.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/middleware/__init__.py`
- `gen_epix/fastapp/middleware/handle_auth_exception.py`
- `gen_epix/fastapp/middleware/limiter.py`
- `gen_epix/fastapp/middleware/update_response_header.py`

## Audit Trail

- EXTRACTED: 56 (95%)
- INFERRED: 3 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*