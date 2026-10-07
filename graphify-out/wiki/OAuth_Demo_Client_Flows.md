# OAuth Demo Client Flows

> 70 nodes · cohesion 0.04

## Key Concepts

- **server.py** (36 connections) — `test/test_client/oauth/server.py`
- **OAuth2Client** (14 connections) — `test/test_client/oauth/demo_client.py`
- **token_endpoint()** (10 connections) — `test/test_client/oauth/server.py`
- **Any** (9 connections)
- **get** (8 connections)
- **create_client()** (7 connections) — `test/test_client/oauth/server.py`
- **token_introspection()** (7 connections) — `test/test_client/oauth/server.py`
- **authenticate_client()** (6 connections) — `test/test_client/oauth/server.py`
- **ClientResponse** (6 connections) — `test/test_client/oauth/server.py`
- **Request** (6 connections)
- **userinfo_endpoint()** (6 connections) — `test/test_client/oauth/server.py`
- **demo_client.py** (5 connections) — `test/test_client/oauth/demo_client.py`
- **authorize_endpoint()** (5 connections) — `test/test_client/oauth/server.py`
- **get_client()** (5 connections) — `test/test_client/oauth/server.py`
- **get_client_credentials()** (5 connections) — `test/test_client/oauth/server.py`
- **openid_configuration()** (5 connections) — `test/test_client/oauth/server.py`
- **ClientCreateRequest** (4 connections) — `test/test_client/oauth/server.py`
- **delete_client()** (4 connections) — `test/test_client/oauth/server.py`
- **jwks_endpoint()** (4 connections) — `test/test_client/oauth/server.py`
- **lifespan()** (4 connections) — `test/test_client/oauth/server.py`
- **list_clients()** (4 connections) — `test/test_client/oauth/server.py`
- **JSONResponse** (3 connections)
- **post** (3 connections)
- **demo_client_credentials_flow()** (3 connections) — `test/test_client/oauth/demo_client.py`
- **.create_client()** (3 connections) — `test/test_client/oauth/demo_client.py`
- *... and 45 more nodes in this community*

## Relationships

- [HTTP Exception Classes](HTTP_Exception_Classes.md) (9 shared connections)
- [OAuth Provider Test Harness](OAuth_Provider_Test_Harness.md) (8 shared connections)
- [OAuth Client Model](OAuth_Client_Model.md) (5 shared connections)
- [Authorization Code Store](Authorization_Code_Store.md) (4 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (3 shared connections)
- [OAuth Token Model Tests](OAuth_Token_Model_Tests.md) (2 shared connections)
- [OAuth Client Store](OAuth_Client_Store.md) (1 shared connections)
- [JWKS Key Management](JWKS_Key_Management.md) (1 shared connections)
- [OIDC Provider](OIDC_Provider.md) (1 shared connections)
- [Token Store Tests](Token_Store_Tests.md) (1 shared connections)
- [OAuth2 Request Validator](OAuth2_Request_Validator.md) (1 shared connections)

## Source Files

- `test/test_client/oauth/authorization_code_store.py`
- `test/test_client/oauth/demo_client.py`
- `test/test_client/oauth/server.py`

## Audit Trail

- EXTRACTED: 125 (89%)
- INFERRED: 16 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*