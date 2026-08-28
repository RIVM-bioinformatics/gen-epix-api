# TestCreateUserFromToken

> 21 nodes · cohesion 0.20

## Key Concepts

- **TestCreateUserFromToken** (13 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **._make_env_with_creator()** (12 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **._make_pending_user()** (12 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **._add_invitation()** (10 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **make_cdb_organization()** (7 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **UUID** (6 connections)
- **make_cdb_invitation()** (5 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_create_new_user_accepts_various_token_formats()** (5 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_create_new_user_from_token_does_not_affect_other_users()** (5 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_create_new_user_from_token_duplicate_raises()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_create_new_user_from_token_stores_user()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_create_new_user_from_token_user_is_retrievable()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **.test_create_new_user_nonexistent_creator_raises()** (4 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **UserInvitation** (3 connections)
- **.test_create_new_user_missing_invitation_raises()** (3 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **parametrize** (1 connections)
- **Return a valid future-expiring UserInvitation.** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **Verify that the commondb UserManager correctly creates a user from an…** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **Build an AuthEnv with a pre-stored creator (inviting) user.** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **Return a User that is not yet stored in the repository.** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`
- **Return a fresh commondb Organization.** (1 connections) — `test/commondb/unit/auth/test_commondb_auth.py`

## Relationships

- [InMemoryOrganizationRepository](InMemoryOrganizationRepository.md) (6 shared connections)
- [CrudOperation](CrudOperation.md) (4 shared connections)
- [make_cdb_user](make_cdb_user.md) (4 shared connections)
- [AuthEnv](AuthEnv.md) (3 shared connections)

## Source Files

- `test/commondb/unit/auth/test_commondb_auth.py`

## Audit Trail

- EXTRACTED: 60 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*