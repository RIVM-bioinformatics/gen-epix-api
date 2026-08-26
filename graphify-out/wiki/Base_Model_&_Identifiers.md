# Base Model & Identifiers

> 125 nodes · cohesion 0.05

## Key Concepts

- **omopdb/domain/model/__init__.py** (135 connections) — `gen_epix/omopdb/domain/model/__init__.py`
- **model/omop/__init__.py** (79 connections) — `gen_epix/omopdb/domain/model/omop/__init__.py`
- **clinical_data.py** (52 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **FullPerson** (41 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **BaseIdentifier** (40 connections) — `gen_epix/commondb/domain/model/organization.py`
- **omop/non_persistable.py** (40 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **ModelNoId** (26 connections) — `gen_epix/commondb/domain/model/base.py`
- **omop/ontology.py** (26 connections) — `gen_epix/omopdb/domain/model/omop/ontology.py`
- **Person** (25 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **derived.py** (20 connections) — `gen_epix/omopdb/domain/model/omop/derived.py`
- **Provider** (17 connections) — `gen_epix/omopdb/domain/model/omop/health_system.py`
- **Model** (16 connections)
- **Specimen** (16 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **health_economics.py** (16 connections) — `gen_epix/omopdb/domain/model/omop/health_economics.py`
- **Measurement** (14 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **DataLineageMixin** (14 connections)
- **health_system.py** (14 connections) — `gen_epix/omopdb/domain/model/omop/health_system.py`
- **Observation** (13 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **metadata.py** (13 connections) — `gen_epix/omopdb/domain/model/omop/metadata.py`
- **Concept** (12 connections) — `gen_epix/omopdb/domain/model/omop/ontology.py`
- **VisitDetail** (11 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **VisitOccurrence** (11 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Location** (11 connections) — `gen_epix/omopdb/domain/model/omop/health_system.py`
- **ConditionOccurrence** (10 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **DeviceExposure** (10 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- *... and 100 more nodes in this community*

## Relationships

- [UUID Field Validation](UUID_Field_Validation.md) (62 shared connections)
- [Commondb Organization Domain Models](Commondb_Organization_Domain_Models.md) (26 shared connections)
- [Omopdb Upload Test Suite](Omopdb_Upload_Test_Suite.md) (18 shared connections)
- [Entity Key Generation](Entity_Key_Generation.md) (17 shared connections)
- [OMOP Model Validators](OMOP_Model_Validators.md) (13 shared connections)
- [Commondb Enums & Demo Data](Commondb_Enums_&_Demo_Data.md) (9 shared connections)
- [OMOP Model Tests](OMOP_Model_Tests.md) (9 shared connections)
- [OMOP Repository](OMOP_Repository.md) (8 shared connections)
- [FastApp Domain Registration & UserManager](FastApp_Domain_Registration_&_UserManager.md) (7 shared connections)
- [Seqdb Domain Models (Sample/Classification)](Seqdb_Domain_Models_Sample-Classification.md) (7 shared connections)
- [UUID Validation Helper](UUID_Validation_Helper.md) (7 shared connections)
- [Seqdb Upload Batch Processing](Seqdb_Upload_Batch_Processing.md) (5 shared connections)

## Source Files

- `gen_epix/commondb/domain/model/base.py`
- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/omopdb/domain/model/__init__.py`
- `gen_epix/omopdb/domain/model/base.py`
- `gen_epix/omopdb/domain/model/omop/__init__.py`
- `gen_epix/omopdb/domain/model/omop/base.py`
- `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- `gen_epix/omopdb/domain/model/omop/derived.py`
- `gen_epix/omopdb/domain/model/omop/health_economics.py`
- `gen_epix/omopdb/domain/model/omop/health_system.py`
- `gen_epix/omopdb/domain/model/omop/metadata.py`
- `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- `gen_epix/omopdb/domain/model/omop/ontology.py`
- `gen_epix/omopdb/domain/model/omop/upload.py`
- `test/omopdb/unit/domain/test_omopdb_matches_spec.py`
- `test/omopdb/unit/domain/test_omopdb_model.py`

## Audit Trail

- EXTRACTED: 623 (92%)
- INFERRED: 51 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*