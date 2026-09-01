# server.py

> 73 nodes

## Key Concepts

- **server.py** (36 connections) — `test/test_client/oauth/server.py`
- **HTTPException** (20 connections)
- **fastapp/api/exc.py** (17 connections) — `gen_epix/fastapp/api/exc.py`
- **.__init__()** (11 connections) — `gen_epix/fastapp/api/exc.py`
- **token_endpoint()** (10 connections) — `test/test_client/oauth/server.py`
- **get** (8 connections)
- **create_client()** (7 connections) — `test/test_client/oauth/server.py`
- **token_introspection()** (7 connections) — `test/test_client/oauth/server.py`
- **ClientResponse** (6 connections) — `test/test_client/oauth/server.py`
- **authenticate_client()** (6 connections) — `test/test_client/oauth/server.py`
- **userinfo_endpoint()** (6 connections) — `test/test_client/oauth/server.py`
- **Request** (6 connections)
- **authorize_endpoint()** (5 connections) — `test/test_client/oauth/server.py`
- **get_client()** (5 connections) — `test/test_client/oauth/server.py`
- **get_client_credentials()** (5 connections) — `test/test_client/oauth/server.py`
- **openid_configuration()** (5 connections) — `test/test_client/oauth/server.py`
- **JSONResponse** (5 connections)
- **ClientCreateRequest** (4 connections) — `test/test_client/oauth/server.py`
- **.dispatch()** (4 connections) — `gen_epix/fastapp/middleware/handle_no_response.py`
- **delete_client()** (4 connections) — `test/test_client/oauth/server.py`
- **jwks_endpoint()** (4 connections) — `test/test_client/oauth/server.py`
- **lifespan()** (4 connections) — `test/test_client/oauth/server.py`
- **list_clients()** (4 connections) — `test/test_client/oauth/server.py`
- **BadRequest400HTTPException** (3 connections) — `gen_epix/fastapp/api/exc.py`
- **Forbidden403HTTPException** (3 connections) — `gen_epix/fastapp/api/exc.py`
- *... and 48 more nodes in this community*

## Relationships

- [Client](Client.md) (12 shared connections)
- [AuthorizationCodeStore](AuthorizationCodeStore.md) (4 shared connections)
- [AppCfg](AppCfg.md) (4 shared connections)
- [JWKSManager](JWKSManager.md) (3 shared connections)
- [Token](Token.md) (2 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (2 shared connections)
- [HandleNoResponseMiddleware](HandleNoResponseMiddleware.md) (1 shared connections)
- [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md) (1 shared connections)
- [CrudOperation](CrudOperation.md) (1 shared connections)
- [commondb/api/exc.py](commondb-api-exc.py.md) (1 shared connections)
- [composite.py](composite.py.md) (1 shared connections)
- [OIDCProvider](OIDCProvider.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/api/exc.py`
- `gen_epix/fastapp/middleware/handle_no_response.py`
- `test/test_client/oauth/authorization_code_store.py`
- `test/test_client/oauth/server.py`

## Audit Trail

- EXTRACTED: 140 (89%)
- INFERRED: 17 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*