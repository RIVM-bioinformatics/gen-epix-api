# .create_person_for_upload

> 53 nodes · cohesion 0.09

## Key Concepts

- **.create_person_for_upload()** (47 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.upload_batch()** (43 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.expectStatusCount()** (38 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.expectBatchProcessed()** (30 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test2ChildObjectProvision** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test7OnExistsAndOnNewActions** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_4_1_child_null_person_id_set_during_upload()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_4_2_2_child_person_id_matches_succeeds()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_6_3_new_identifier_created_on_upload()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_2_2_person_with_measurements_only()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_2_3_person_with_observations_only()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_2_4_person_with_specimens_only()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_2_5_person_with_all_child_types()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_4_2_1_child_person_id_mismatch_fails()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_5_1_1_always_mutable_single_value_field()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_7_3_on_exists_update_with_existing_person_updates()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_batch_of_n_new_persons()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_1_no_identifiers_provided()** (7 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_1_1_person_id_not_provided_creates_new_person()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_1_2_person_id_provided_as_new_id_succeeds()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_2_1_person_without_children()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_6_1_no_identifiers_provided()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_7_1_on_exists_error_with_existing_person_fails()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_7_2_on_exists_skip_with_existing_person_skips()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_7_4_on_new_create_with_new_id_creates()** (6 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- *... and 28 more nodes in this community*

## Relationships

- [IdentifierForUpload](IdentifierForUpload.md) (43 shared connections)
- [.create_measurement_for_upload](create_measurement_for_upload.md) (31 shared connections)
- [BasePersonUploadTestCase](BasePersonUploadTestCase.md) (23 shared connections)
- [model/omop/upload.py](model-omop-upload.py.md) (4 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (4 shared connections)
- [PersonBatchForUpload](PersonBatchForUpload.md) (2 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (1 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (1 shared connections)

## Source Files

- `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`

## Audit Trail

- EXTRACTED: 227 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*