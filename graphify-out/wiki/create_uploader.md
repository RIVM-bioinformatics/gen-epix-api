# .create_uploader

> 12 nodes · cohesion 0.23

## Key Concepts

- **.create_uploader()** (9 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **TestExistingContentKeyNormalization** (7 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **._run_upsert_with_existing_key()** (6 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.create_org_user()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upsert_batch_update_does_not_persist_none_content_values()** (5 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_upsert_batch_create_does_not_persist_none_content_values()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_calculated_case_date_preserved_for_existing_case()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_content_deletion_delta_is_restored_before_generic_upsert()** (4 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_string_keys_from_sql_repo_are_converted_to_uuid()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **.test_uuid_keys_from_dict_repo_are_accepted()** (2 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **After re-validation, case_date set by calculate_case_date must not be reset to…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`
- **read_fields row[1] keys may be UUID objects (DICT) or strings (SQL); both must…** (1 connections) — `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Relationships

- [test_casedb_upload.py](test_casedb_upload.py.md) (10 shared connections)
- [.create_case](create_case.md) (4 shared connections)
- [.create_case_for_upload](create_case_for_upload.md) (4 shared connections)
- [TestVerifyUserRights](TestVerifyUserRights.md) (1 shared connections)
- [UploadCasesCommand](UploadCasesCommand.md) (1 shared connections)

## Source Files

- `test/casedb/unit/services/case/upload/test_casedb_upload.py`

## Audit Trail

- EXTRACTED: 35 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*