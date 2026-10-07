# POST_ONE Endpoint Tests

> 8 nodes · cohesion 0.25

## Key Concepts

- **TestPostOneEndpoint** (5 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **.test_post_one_model1_invalid_request()** (3 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **.test_post_one_model1_success()** (3 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **.test_post_one_model2_success()** (3 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Tests for POST_ONE CRUD endpoint.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Verify POST /model1 creates a new record.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Verify POST /model2 creates a new record.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`
- **Verify POST /model1 with invalid data returns error.** (1 connections) — `test/fastapp/integration/api/test_fastapp_api.py`

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