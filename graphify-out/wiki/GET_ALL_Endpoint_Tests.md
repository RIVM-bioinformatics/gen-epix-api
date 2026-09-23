# GET_ALL Endpoint Tests

> 8 nodes · cohesion 0.25

## Key Concepts

- **TestGetAllEndpoint** (5 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **.test_get_all_model1_empty()** (3 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **.test_get_all_model1_with_records()** (3 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **.test_get_all_model2_empty()** (3 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Tests for GET_ALL CRUD endpoint.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Verify GET /model1 returns empty list when no records exist.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Verify GET /model2 returns empty list when no records exist.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Verify GET /model1 returns all records.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`

## Relationships

- [Integration Test Client](Integration_Test_Client.md) (3 shared connections)
- [FastApp API Tests](FastApp_API_Tests.md) (1 shared connections)

## Source Files

- `test/fastapp/integration/api/test_fastapp_api.py`

## Audit Trail

- EXTRACTED: 11 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*