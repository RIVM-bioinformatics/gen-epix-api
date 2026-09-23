# Upload Identifier Models

> 156 nodes · cohesion 0.04

## Key Concepts

- **.create_person_for_upload()** (49 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.upload_batch()** (45 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **IdentifierForUpload** (44 connections) — `gen_epix/commondb/domain/model/organization.py`
- **test_omopdb_upload.py** (39 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **BasePersonUploadTestCase** (39 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.expectStatusCount()** (38 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.expectBatchProcessed()** (30 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.create_specimen_for_upload()** (24 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **IdentifiersMixin** (21 connections) — `gen_epix/commondb/domain/model/upload.py`
- **.create_identifier_for_upload()** (19 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test8SpecimenIdentifiers** (18 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **PersonForUpload** (16 connections) — `gen_epix/omopdb/domain/model/omop/upload.py`
- **.create_measurement_for_upload()** (14 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.get_specimen_identifier_from_for_upload()** (12 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **Test2ChildObjectProvision** (12 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_person_with_all_children_and_identifiers()** (12 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.expectBatchFailed()** (11 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **UUID** (11 connections)
- **Test7OnExistsAndOnNewActions** (11 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.create_observation_for_upload()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_2_6_person_with_all_child_types()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_6_2_existing_identifier_resolves_person()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.test_multiple_persons_mixed_child_types()** (10 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **.create_measurement_relation_for_upload()** (9 connections) — `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`
- **scenario_ids** (9 connections)
- *... and 131 more nodes in this community*

## Relationships

- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (24 shared connections)
- [Person Upload Batch Stats](Person_Upload_Batch_Stats.md) (9 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (8 shared connections)
- [Batch Upload Validation](Batch_Upload_Validation.md) (6 shared connections)
- [Case Upload Batch Mixin](Case_Upload_Batch_Mixin.md) (6 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (6 shared connections)
- [Parent-Child Upload Models](Parent-Child_Upload_Models.md) (6 shared connections)
- [OMOP Clinical Data Models](OMOP_Clinical_Data_Models.md) (6 shared connections)
- [Case Domain CRUD Commands](Case_Domain_CRUD_Commands.md) (5 shared connections)
- [App Composition & ETL Setup](App_Composition_&_ETL_Setup.md) (5 shared connections)
- [Role Generation & Hierarchy](Role_Generation_&_Hierarchy.md) (5 shared connections)
- [Case Upload Validation](Case_Upload_Validation.md) (4 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/commondb/domain/model/upload.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `test/omopdb/unit/services/omop/upload/test_omopdb_upload.py`

## Audit Trail

- EXTRACTED: 511 (93%)
- INFERRED: 37 (7%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*