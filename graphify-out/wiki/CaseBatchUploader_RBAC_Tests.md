# CaseBatchUploader RBAC Tests

> 13 nodes · cohesion 0.22

## Key Concepts

- **TestVerifyUserRights** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._make_cmd()** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.setup_method()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **User** (5 connections)
- **.test_succeeds_for_allowed_roles()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_to_casedb_role_set()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_raises_for_user_with_only_guest_role()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **_mock_uow()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_succeeds_for_none_user()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Role** (1 connections)
- **Map commondb role enums to casedb role strings with CASEDB_ prefix.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Tests for RBAC verification in CaseBatchUploader.verify_user_rights.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_raises_for_invalid_command_type()** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload Tests](Case_Upload_Tests.md) (7 shared connections)
- [Case Batch Upload](Case_Batch_Upload.md) (2 shared connections)
- [Case Upload Bridge Tests](Case_Upload_Bridge_Tests.md) (2 shared connections)
- [Case Upload Feature Tests](Case_Upload_Feature_Tests.md) (1 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 30 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*