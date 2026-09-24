# Case Upload RBAC Tests

> 8 nodes · cohesion 0.36

## Key Concepts

- **TestVerifyUserRights** (11 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._make_cmd()** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_succeeds_for_allowed_roles()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_raises_for_user_with_only_guest_role()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_succeeds_for_none_user()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **Role** (1 connections)
- **Tests for RBAC verification in CaseBatchUploader.verify_user_rights.** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_raises_for_invalid_command_type()** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [Case Upload Tests](Case_Upload_Tests.md) (3 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (2 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (1 shared connections)
- [Case Upload ABAC Tests](Case_Upload_ABAC_Tests.md) (1 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (1 shared connections)
- [Case Data Collection Updates](Case_Data_Collection_Updates.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 17 (89%)
- INFERRED: 2 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*