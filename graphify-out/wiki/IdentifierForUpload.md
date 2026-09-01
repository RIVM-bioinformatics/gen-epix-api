# IdentifierForUpload

> 39 nodes

## Key Concepts

- **IdentifierForUpload** (32 connections) — `gen_epix/commondb/domain/model/organization.py`
- **.create_specimen_for_upload()** (22 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.create_identifier_for_upload()** (18 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test8SpecimenIdentifiers** (17 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.expectBatchFailed()** (11 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.get_specimen_identifier_from_for_upload()** (11 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_1_1_existing_identifier_null_specimen_sets_id()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_1_2_1_existing_identifier_same_specimen_succeeds()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_3_1_multiple_identifiers_some_existing_same_specimen()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_1_2_2_existing_identifier_different_specimen_fails()** (9 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_2_new_identifier_new_specimen()** (9 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_3_1_multiple_identifiers_some_existing_different_specimen()** (9 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_3_2_multiple_identifiers_all_new_different_issuer()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_3_1_identifier_issuer_id_not_found()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_3_2_identifier_issuer_code_not_found()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_3_3_identifier_issuer_id_and_code_mismatch()** (8 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_8_2_3_2_multiple_identifiers_all_new_same_issuer()** (4 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_specimen_chain_retry_reusing_identifier_produces_readable_error()** (3 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.__eq__()** (2 connections) — `gen_epix/commondb/domain/model/organization.py`
- **.__hash__()** (1 connections) — `gen_epix/commondb/domain/model/organization.py`
- **SpecimenIdentifier** (1 connections)
- **An external identifier, defined as the combination of (identifier issuer,…** (1 connections) — `gen_epix/commondb/domain/model/organization.py`
- **Check equality based on identifier_issuer_id, identifier_issuer_code, and…** (1 connections) — `gen_epix/commondb/domain/model/organization.py`
- **Test scenarios related to Identifiers for Specimen objects.** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test 8.2.1.1: Existing Identifier with NULL specimen ID - should set specimen…** (1 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- *... and 14 more nodes in this community*

## Relationships

- [.create_person_for_upload](create_person_for_upload.md) (43 shared connections)
- [.create_measurement_for_upload](create_measurement_for_upload.md) (10 shared connections)
- [BasePersonUploadTestCase](BasePersonUploadTestCase.md) (6 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (4 shared connections)
- [.create_child2_for_upload](create_child2_for_upload.md) (3 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (3 shared connections)
- [omopdb/domain/model/__init__.py](omopdb-domain-model-__init__.py.md) (3 shared connections)
- [.create_read_set_for_upload](create_read_set_for_upload.md) (2 shared connections)
- [BaseBatchForUpload](BaseBatchForUpload.md) (2 shared connections)
- [test_omopdb_upload.py](test_omopdb_upload.py.md) (2 shared connections)
- [._get_allele_profile_for_ids](_get_allele_profile_for_ids.md) (1 shared connections)
- [.create_parent_for_upload](create_parent_for_upload.md) (1 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/organization.py`
- `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`

## Audit Trail

- EXTRACTED: 159 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*