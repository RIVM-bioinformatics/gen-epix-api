# Identity Provider Client

> 37 nodes · cohesion 0.07

## Key Concepts

- **IdpClient** (20 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **DummyIdpClient** (11 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **TestIdpClientAbstractMethods** (8 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **test_fastapp_idp_client.py** (7 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **TestIdpClientInitialization** (7 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.__call__()** (5 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.__call__()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **Any** (4 connections)
- **.get_claims_from_jwt()** (3 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.get_identity_provider()** (3 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.__init__()** (3 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.get_claims_from_jwt()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.get_claims_from_userinfo()** (2 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **UUID** (2 connections)
- **.idp_clients()** (2 connections) — `gen_epix/fastapp/services/auth/service.py`
- **.get_claims_from_userinfo()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.get_identity_provider()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **scenario_ids** (2 connections)
- **.setup_method()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_default_initialization_sets_expected_values()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_initialization_with_overrides()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_ssl_context_boolean_values()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **Request** (1 connections)
- **SSLContext** (1 connections)
- **Get identity provider configuration.** (1 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- *... and 12 more nodes in this community*

## Relationships

- [Identity Providers Command](Identity_Providers_Command.md) (8 shared connections)
- [Auth Service User Claims](Auth_Service_User_Claims.md) (3 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (1 shared connections)
- [IDP Client Initialization](IDP_Client_Initialization.md) (1 shared connections)
- [Mock IDP Client](Mock_IDP_Client.md) (1 shared connections)
- [OAuth IDP Client](OAuth_IDP_Client.md) (1 shared connections)
- [Auth Service Tests](Auth_Service_Tests.md) (1 shared connections)
- [Casedb CaseSet CRUD & Tests](Casedb_CaseSet_CRUD_&_Tests.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/idp_client.py`
- `gen_epix/fastapp/services/auth/service.py`
- `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`

## Audit Trail

- EXTRACTED: 62 (95%)
- INFERRED: 3 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*