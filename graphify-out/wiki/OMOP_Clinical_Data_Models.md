# OMOP Clinical Data Models

> 98 nodes · cohesion 0.06

## Key Concepts

- **model/omop/__init__.py** (80 connections) — `gen_epix/omopdb/domain/model/omop/__init__.py`
- **clinical_data.py** (46 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **BaseIdentifier** (42 connections) — `gen_epix/commondb/domain/model/organization.py`
- **omop/non_persistable.py** (40 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **FullPerson** (40 connections) — `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- **DataLineageMixin** (31 connections) — `gen_epix/omopdb/domain/model/omop/base.py`
- **Concept** (24 connections) — `gen_epix/casedb/domain/model/ontology.py`
- **derived.py** (20 connections) — `gen_epix/omopdb/domain/model/omop/derived.py`
- **Person** (19 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Concept** (19 connections) — `gen_epix/omopdb/domain/model/omop/ontology.py`
- **Model** (16 connections)
- **health_economics.py** (16 connections) — `gen_epix/omopdb/domain/model/omop/health_economics.py`
- **Measurement** (13 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Represents an external identifier with a person record.** (13 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Observation** (12 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Specimen** (12 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **ConditionOccurrence** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Death** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **DeviceExposure** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **DrugExposure** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **Note** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **ObservationPeriod** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **ProcedureOccurrence** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **VisitDetail** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- **VisitOccurrence** (9 connections) — `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- *... and 73 more nodes in this community*

## Relationships

- [OMOP Concept Key Validation](OMOP_Concept_Key_Validation.md) (21 shared connections)
- [Provider & Location Models](Provider_&_Location_Models.md) (17 shared connections)
- [OMOP Model Base & Validation](OMOP_Model_Base_&_Validation.md) (16 shared connections)
- [OMOP Concept Validators](OMOP_Concept_Validators.md) (14 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (12 shared connections)
- [OmopDB Enums & Base Model](OmopDB_Enums_&_Base_Model.md) (9 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (7 shared connections)
- [OMOP Concept ID Normalization](OMOP_Concept_ID_Normalization.md) (7 shared connections)
- [Upload Identifier Models](Upload_Identifier_Models.md) (6 shared connections)
- [User & Person Commands](User_&_Person_Commands.md) (5 shared connections)
- [Case Operational Data Models](Case_Operational_Data_Models.md) (4 shared connections)
- [Audit Timestamp Model Tests](Audit_Timestamp_Model_Tests.md) (4 shared connections)

## Source Files

- `gen_epix/casedb/domain/model/ontology.py`
- `gen_epix/commondb/domain/model/organization.py`
- `gen_epix/omopdb/domain/model/omop/__init__.py`
- `gen_epix/omopdb/domain/model/omop/base.py`
- `gen_epix/omopdb/domain/model/omop/clinical_data.py`
- `gen_epix/omopdb/domain/model/omop/derived.py`
- `gen_epix/omopdb/domain/model/omop/health_economics.py`
- `gen_epix/omopdb/domain/model/omop/non_persistable.py`
- `gen_epix/omopdb/domain/model/omop/ontology.py`
- `gen_epix/seqdb/domain/model/seq/profile.py`
- `gen_epix/seqdb/domain/model/seq/reads.py`
- `gen_epix/seqdb/domain/model/seq/sample.py`
- `gen_epix/seqdb/domain/model/seq/seq.py`

## Audit Trail

- EXTRACTED: 391 (86%)
- INFERRED: 66 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*