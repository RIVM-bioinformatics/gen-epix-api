# BaseCommondbRemoteAppTestCase

> 24 nodes · cohesion 0.09

## Key Concepts

- **BaseCommondbRemoteAppTestCase** (12 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **TestHttpTimeoutConfiguration** (9 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **scenario_ids** (7 connections)
- **DerivedRemoteApp** (6 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **TestCreateLocalOrRemoteApp** (6 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_app_setup_type_case_insensitive()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_invalid_app_setup_type_rejected()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_derived_remote_app_initialization()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_timeout_configuration_does_not_affect_none_auth()** (3 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_base_remote_app_has_empty_timeouts()** (2 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_create_remote_app_applies_timeouts()** (2 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.test_derived_remote_app_has_timeout_configuration()** (2 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **.teardown_method()** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Minimal subclass of CommondbRemoteApp for testing timeout configuration.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Test create_local_or_remote_app class method.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Raise error for invalid app_setup_type.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **app_setup_type is case-insensitive.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Test HTTP timeout configuration per command class.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **DerivedRemoteApp has DEFAULT_HTTP_TIMEOUTS configured.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **DerivedRemoteApp can be initialized.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **_create_remote_app applies DEFAULT_HTTP_TIMEOUTS to remote app.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Base CommondbRemoteApp has empty DEFAULT_HTTP_TIMEOUTS.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Timeout configuration works independently of auth protocol.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`
- **Base test case with common fixtures and setup for CommondbRemoteApp.** (1 connections) — `test/commondb/unit/remote_app/test_commondb_remote_app.py`

## Relationships

- [CrudOperation](CrudOperation.md) (5 shared connections)
- [DummyCommand](DummyCommand.md) (4 shared connections)
- [._create_remote_app](_create_remote_app.md) (2 shared connections)
- [TestInitialization](TestInitialization.md) (2 shared connections)
- [TestOAuth2Validation](TestOAuth2Validation.md) (2 shared connections)
- [.create_local_or_remote_app](create_local_or_remote_app.md) (2 shared connections)
- [OmopdbRemoteApp](OmopdbRemoteApp.md) (1 shared connections)
- [Domain](Domain.md) (1 shared connections)
- [CommondbRemoteApp](CommondbRemoteApp.md) (1 shared connections)

## Source Files

- `test/commondb/unit/remote_app/test_commondb_remote_app.py`

## Audit Trail

- EXTRACTED: 43 (96%)
- INFERRED: 2 (4%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*