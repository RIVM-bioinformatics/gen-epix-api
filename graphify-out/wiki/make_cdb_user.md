# make_cdb_user

> 31 nodes

## Key Concepts

- **make_cdb_user()** (23 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **TestAuth** (14 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **TestRootTokenTTL** (12 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **get_name_from_claims()** (11 connections) — `gen_epix/fastapp/services/auth/util.py`
- **._make_root_env()** (9 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **._make_env_with_user()** (8 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_update_user_name_persisted_in_repo()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_update_user_name_changed()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_update_user_name_no_change()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_update_user_name_real_user()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_update_user_name_real_user_last_name()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_non_root_user_not_affected_by_ttl()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_ttl_none_uses_default_ttl()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_ttl_zero_disables_expiry()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_verify_root_ttl_directly_accepts_fresh_token()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_verify_root_ttl_directly_rejects_old_token()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_extracts_name_fallback_email()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_extracts_name_given_family()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_extracts_name_prefers_name()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_extracts_name_returns_none_when_no_claims_present()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_extracts_preferred_username()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_fresh_root_token_within_ttl_is_accepted()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_old_root_token_exceeding_ttl_is_rejected()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_ttl_disabled_allows_old_root_token()** (2 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **Any** (2 connections)
- *... and 6 more nodes in this community*

## Relationships

- [AuthEnv](AuthEnv.md) (12 shared connections)
- [CrudOperation](CrudOperation.md) (4 shared connections)
- [TestCreateUserFromToken](TestCreateUserFromToken.md) (4 shared connections)
- [Commondb UserManager Service](Commondb_UserManager_Service.md) (2 shared connections)
- [InMemoryOrganizationRepository](InMemoryOrganizationRepository.md) (2 shared connections)
- [services/user_manager.py](services-user_manager.py.md) (1 shared connections)
- [auth/__init__.py](auth-__init__.py.md) (1 shared connections)

## Source Files

- `gen_epix/fastapp/services/auth/util.py`
- `test/commondb/unit/auth/test_commondb_auth.py`

## Audit Trail

- EXTRACTED: 79 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*