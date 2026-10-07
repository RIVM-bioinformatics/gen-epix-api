# User & Organization Printing

> 12 nodes · cohesion 0.17

## Key Concepts

- **.get_root_user()** (8 connections) — `gen_epix/commondb/test/test_client.py`
- **.read_all_users()** (5 connections) — `gen_epix/commondb/test/test_client.py`
- **.print_data_collections()** (4 connections) — `gen_epix/commondb/test/test_client.py`
- **.print_organizations()** (4 connections) — `gen_epix/commondb/test/test_client.py`
- **.print_users()** (4 connections) — `gen_epix/commondb/test/test_client.py`
- **.read_users_by_role()** (4 connections) — `gen_epix/commondb/test/test_client.py`
- **Print all organisations to stdout.** (1 connections) — `gen_epix/commondb/test/test_client.py`
- **Print all data collections to stdout.** (1 connections) — `gen_epix/commondb/test/test_client.py`
- **Print all users with their organisations and roles to stdout.** (1 connections) — `gen_epix/commondb/test/test_client.py`
- **Retrieve all users via the app as the root user.** (1 connections) — `gen_epix/commondb/test/test_client.py`
- **Retrieve all users that have the given role.** (1 connections) — `gen_epix/commondb/test/test_client.py`
- **Retrieve the root user from the app's user manager.** (1 connections) — `gen_epix/commondb/test/test_client.py`

## Relationships

- [Organization Test Helpers](Organization_Test_Helpers.md) (7 shared connections)
- [Integration Test Client](Integration_Test_Client.md) (6 shared connections)

## Source Files

- `gen_epix/commondb/test/test_client.py`

## Audit Trail

- EXTRACTED: 24 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*