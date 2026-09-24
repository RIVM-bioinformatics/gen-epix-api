# JWT Claims Extraction

> 26 nodes · cohesion 0.10

## Key Concepts

- **DummyIdpClient** (11 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **TestIdpClientAbstractMethods** (8 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **TestIdpClientInitialization** (7 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.__call__()** (5 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.__call__()** (4 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **Any** (4 connections)
- **.get_claims_from_jwt()** (3 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **.get_claims_from_jwt()** (3 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.get_claims_from_userinfo()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.get_identity_provider()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **scenario_ids** (2 connections)
- **.setup_method()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_default_initialization_sets_expected_values()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_initialization_with_overrides()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_ssl_context_boolean_values()** (2 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **Request** (1 connections)
- **Extract claims from JWT token.** (1 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **Returns the claims of the user from the request or None if claims cannot be…** (1 connections) — `gen_epix/fastapp/services/auth/idp_client.py`
- **Request** (1 connections)
- **Test abstract method behavior exposed via base class.** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **Concrete minimal client that delegates to base for abstract methods. This…** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **Test initialization and public attributes of IdpClient.** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test___call___raises_not_implemented()** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_get_claims_from_jwt_raises_not_implemented()** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- **.test_get_claims_from_userinfo_raises_not_implemented()** (1 connections) — `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`
- *... and 1 more nodes in this community*

## Relationships

- [Auth Protocols & Structured Logging](Auth_Protocols_&_Structured_Logging.md) (7 shared connections)
- [Authentication Service Base](Authentication_Service_Base.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/idp_client.py`
- `test/fastapp/unit/services/auth/test_fastapp_idp_client.py`

## Audit Trail

- EXTRACTED: 38 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*