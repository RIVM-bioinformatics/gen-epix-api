# Seq Upload & SQL Models

> 68 nodes · cohesion 0.09

## Key Concepts

- **seqdb/repositories/sa_model/__init__.py** (58 connections) — `gen_epix/seqdb/repositories/sa_model/__init__.py`
- **sa_model/seq/__init__.py** (35 connections) — `gen_epix/seqdb/repositories/sa_model/seq/__init__.py`
- **seq/ref_data.py** (26 connections) — `gen_epix/seqdb/repositories/sa_model/seq/ref_data.py`
- **seq/operational_data.py** (25 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **SeqProfile** (25 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **RowMetadataMixin** (16 connections)
- **Encapsulates the SQLAlchemy model for its persistable domain model.** (15 connections) — `gen_epix/seqdb/repositories/sa_model/seq/ref_data.py`
- **Seq** (12 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **QualityMixin** (11 connections) — `gen_epix/seqdb/repositories/sa_model/seq/base.py`
- **RowMetadataMixin** (11 connections)
- **SampleIdentifier** (11 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **SeqClassification** (11 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **SeqTaxonomy** (11 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **ContentMixin** (10 connections) — `gen_epix/seqdb/repositories/sa_model/seq/base.py`
- **AstMeasurement** (10 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **AstPrediction** (10 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **PcrMeasurement** (10 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **ReadSet** (10 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **Sample** (10 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **sa_model/seq/base.py** (9 connections) — `gen_epix/seqdb/repositories/sa_model/seq/base.py`
- **ReadSetIdentifier** (8 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **SampleDataCollectionLink** (8 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **SeqIdentifier** (8 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **SeqProfileIdentifier** (8 connections) — `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- **ReadSetForUpload** (7 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- *... and 43 more nodes in this community*

## Relationships

- [SQLAlchemy Model Mixins](SQLAlchemy_Model_Mixins.md) (36 shared connections)
- [Organization SQL Repository](Organization_SQL_Repository.md) (18 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (14 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (14 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (7 shared connections)
- [Casedb ABAC SQL Models](Casedb_ABAC_SQL_Models.md) (7 shared connections)
- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (6 shared connections)
- [Benchmark Chart Generation](Benchmark_Chart_Generation.md) (5 shared connections)
- [Seqdb File Commands & Enums](Seqdb_File_Commands_&_Enums.md) (4 shared connections)
- [Seq Profile Upload Validation](Seq_Profile_Upload_Validation.md) (3 shared connections)
- [Seq Repository Queries](Seq_Repository_Queries.md) (3 shared connections)
- [Sample Retrieval Commands](Sample_Retrieval_Commands.md) (3 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/upload.py`
- `gen_epix/seqdb/repositories/sa_model/__init__.py`
- `gen_epix/seqdb/repositories/sa_model/seq/__init__.py`
- `gen_epix/seqdb/repositories/sa_model/seq/base.py`
- `gen_epix/seqdb/repositories/sa_model/seq/operational_data.py`
- `gen_epix/seqdb/repositories/sa_model/seq/ref_data.py`
- `test/seqdb/performance/calculate_seq_distances/test_seqdb_distance_optimization_benchmark.py`

## Audit Trail

- EXTRACTED: 325 (98%)
- INFERRED: 7 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*