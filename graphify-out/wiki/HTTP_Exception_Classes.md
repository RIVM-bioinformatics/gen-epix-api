# HTTP Exception Classes

> 73 nodes · cohesion 0.05

## Key Concepts

- **server.py** (36 connections) — `test/test_client/oauth/server.py`
- **HTTPException** (20 connections)
- **fastapp/api/exc.py** (17 connections) — `gen_epix/fastapp/api/exc.py`
- **.__init__()** (11 connections) — `gen_epix/fastapp/api/exc.py`
- **token_endpoint()** (10 connections) — `test/test_client/oauth/server.py`
- **get** (8 connections)
- **create_client()** (7 connections) — `test/test_client/oauth/server.py`
- **token_introspection()** (7 connections) — `test/test_client/oauth/server.py`
- **authenticate_client()** (6 connections) — `test/test_client/oauth/server.py`
- **ClientResponse** (6 connections) — `test/test_client/oauth/server.py`
- **Request** (6 connections)
- **userinfo_endpoint()** (6 connections) — `test/test_client/oauth/server.py`
- **JSONResponse** (5 connections)
- **authorize_endpoint()** (5 connections) — `test/test_client/oauth/server.py`
- **get_client()** (5 connections) — `test/test_client/oauth/server.py`
- **get_client_credentials()** (5 connections) — `test/test_client/oauth/server.py`
- **openid_configuration()** (5 connections) — `test/test_client/oauth/server.py`
- **.dispatch()** (4 connections) — `gen_epix/fastapp/middleware/handle_no_response.py`
- **ClientCreateRequest** (4 connections) — `test/test_client/oauth/server.py`
- **delete_client()** (4 connections) — `test/test_client/oauth/server.py`
- **jwks_endpoint()** (4 connections) — `test/test_client/oauth/server.py`
- **lifespan()** (4 connections) — `test/test_client/oauth/server.py`
- **list_clients()** (4 connections) — `test/test_client/oauth/server.py`
- **BadRequest400HTTPException** (3 connections) — `gen_epix/fastapp/api/exc.py`
- **Forbidden403HTTPException** (3 connections) — `gen_epix/fastapp/api/exc.py`
- *... and 48 more nodes in this community*

## Relationships

- [OAuth Client Store](OAuth_Client_Store.md) (5 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (5 shared connections)
- [Authorization Code Store](Authorization_Code_Store.md) (4 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (3 shared connections)
- [OIDC Provider & JWKS](OIDC_Provider_&_JWKS.md) (3 shared connections)
- [Token Store Unit Tests](Token_Store_Unit_Tests.md) (2 shared connections)
- [App Composition & Startup](App_Composition_&_Startup.md) (2 shared connections)
- [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md) (1 shared connections)
- [API Exception Handling](API_Exception_Handling.md) (1 shared connections)
- [Casedb ABAC & Filter Logic](Casedb_ABAC_&_Filter_Logic.md) (1 shared connections)
- [Core App Base Class](Core_App_Base_Class.md) (1 shared connections)
- [Auth Exception Middleware](Auth_Exception_Middleware.md) (1 shared connections)

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