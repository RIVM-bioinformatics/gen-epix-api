# User Anonymization Tests

> 11 nodes · cohesion 0.18

## Key Concepts

- **TestAnonymizeUser** (9 connections) — `test/commondb/unit/services/test_organization.py`
- **.setup_method()** (2 connections) — `test/commondb/unit/services/test_organization.py`
- **.test_anonymize_keeps_keys_unique_for_users_in_same_organization()** (2 connections) — `test/commondb/unit/services/test_organization.py`
- **.test_anonymize_normalizes_organization_name_in_user_key()** (2 connections) — `test/commondb/unit/services/test_organization.py`
- **.test_anonymize_user_information()** (2 connections) — `test/commondb/unit/services/test_organization.py`
- **scenario_ids** (1 connections)
- **Include each user ID so forgotten users in one organization remain unique.** (1 connections) — `test/commondb/unit/services/test_organization.py`
- **Verify anonymization of the target user.** (1 connections) — `test/commondb/unit/services/test_organization.py`
- **Set up test fixtures.** (1 connections) — `test/commondb/unit/services/test_organization.py`
- **Anonymize personal fields and deactivate the anonymized user.** (1 connections) — `test/commondb/unit/services/test_organization.py`
- **Anonymize personal fields and deactivate the anonymized user.** (1 connections) — `test/commondb/unit/services/test_organization.py`

## Relationships

- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (2 shared connections)
- [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md) (1 shared connections)

## Source Files

- `test/commondb/unit/services/test_organization.py`

## Audit Trail

- EXTRACTED: 11 (85%)
- INFERRED: 2 (15%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*