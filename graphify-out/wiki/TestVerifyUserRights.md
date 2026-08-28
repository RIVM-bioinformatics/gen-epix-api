# TestVerifyUserRights

> 9 nodes · cohesion 0.36

## Key Concepts

- **TestVerifyUserRights** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._make_cmd()** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **User** (5 connections)
- **.test_succeeds_for_allowed_roles()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_raises_for_user_with_only_guest_role()** (3 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_succeeds_for_none_user()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Role** (1 connections)
- **Tests for RBAC verification in CaseBatchUploader.verify_user_rights.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_raises_for_invalid_command_type()** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [test_casedb_upload.py](test_casedb_upload.py.md) (4 shared connections)
- [.create_uploader](create_uploader.md) (1 shared connections)
- [.create_case_for_upload](create_case_for_upload.md) (1 shared connections)
- [UploadCasesCommand](UploadCasesCommand.md) (1 shared connections)
- [.create_case](create_case.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 21 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*