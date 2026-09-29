# Sequence Distance Calculation

> 11 nodes · cohesion 0.22

## Key Concepts

- **CalculateSeqDistancesEtlResult** (16 connections) — `gen_epix/seqdb/domain/model/seq/distance.py`
- **UpdateSeqDistancesCommand** (8 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **.calculate_seq_distances_for_new_profiles()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.update_seq_distances()** (5 connections) — `gen_epix/seqdb/services/seq/service.py`
- **.update_seq_distances()** (4 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **.update_seq_distances()** (3 connections) — `gen_epix/seqdb/services/client.py`
- **Represents a request to create missing distances for profiles under a distance…** (1 connections) — `gen_epix/seqdb/domain/command/seq.py`
- **Represents the result of calculating distances between existing profiles and…** (1 connections) — `gen_epix/seqdb/domain/model/seq/distance.py`
- **Update stored sequence-distance calculations. Args: cmd: Distance-update…** (1 connections) — `gen_epix/seqdb/domain/service/seq.py`
- **Delegate missing-profile distance calculation to the distance operation.** (1 connections) — `gen_epix/seqdb/services/seq/service.py`
- **Delegate distance updates to the distance operation.** (1 connections) — `gen_epix/seqdb/services/seq/service.py`

## Relationships

- [Sequence Distance Calculation](Sequence_Distance_Calculation.md) (4 shared connections)
- [Seqdb Sequence Commands](Seqdb_Sequence_Commands.md) (3 shared connections)
- [New Profile Distance Tests](New_Profile_Distance_Tests.md) (3 shared connections)
- [Seq Service Interface](Seq_Service_Interface.md) (2 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (2 shared connections)
- [Sequence Reference Data Models](Sequence_Reference_Data_Models.md) (2 shared connections)
- [Seqdb Sequence Retrieval Commands](Seqdb_Sequence_Retrieval_Commands.md) (1 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (1 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (1 shared connections)
- [ETL Batch Result Models](ETL_Batch_Result_Models.md) (1 shared connections)
- [Sample Batch Upload](Sample_Batch_Upload.md) (1 shared connections)
- [Phylogenetics & Format Conversion](Phylogenetics_&_Format_Conversion.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/command/seq.py`
- `gen_epix/seqdb/domain/model/seq/distance.py`
- `gen_epix/seqdb/domain/service/seq.py`
- `gen_epix/seqdb/services/client.py`
- `gen_epix/seqdb/services/seq/service.py`

## Audit Trail

- EXTRACTED: 33 (97%)
- INFERRED: 1 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*