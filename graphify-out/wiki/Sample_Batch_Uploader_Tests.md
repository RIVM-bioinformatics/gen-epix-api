# Sample Batch Uploader Tests

> 19 nodes · cohesion 0.19

## Key Concepts

- **set_service_repository()** (14 connections) — `test/seqdb/performance/common.py`
- **_build_upload_command()** (11 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **Env** (10 connections)
- **_build_snp_upload_command()** (8 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **TestSampleBatchUploader** (8 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **.setup()** (7 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **.test_upload_new_profiles_against_existing()** (6 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **.test_upload_new_profiles_against_existing()** (6 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **.test_sample_batch_for_upload_happy_flow()** (5 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **.test_snp_batch_for_upload_happy_flow()** (5 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **parametrize** (4 connections)
- **UUID** (3 connections)
- **Any** (2 connections)
- **RepositoryType** (1 connections)
- **Given a created dict dataset, build a UploadSamplesCommand. db_index selects…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **Build an UploadSamplesCommand for SNP profiles using the SNP protocol from the…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **Configure root user for the test environment, if CREATE_DEMO_DATA is True,…** (1 connections) — `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- **Env** (1 connections)
- **Point the live SEQ service at the given repository.** (1 connections) — `test/seqdb/performance/common.py`

## Relationships

- [Seq Dict Repository](Seq_Dict_Repository.md) (15 shared connections)
- [Seq SA Repository](Seq_SA_Repository.md) (5 shared connections)
- [Seqdb Test Client](Seqdb_Test_Client.md) (4 shared connections)
- [Upload/ETL Result Model](Upload-ETL_Result_Model.md) (2 shared connections)
- [Seq Distance Update Tests](Seq_Distance_Update_Tests.md) (2 shared connections)
- [Sequence Generation Settings](Sequence_Generation_Settings.md) (1 shared connections)
- [SeqDB Demo Data Generator](SeqDB_Demo_Data_Generator.md) (1 shared connections)
- [Distance Optimization Benchmarks](Distance_Optimization_Benchmarks.md) (1 shared connections)

## Source Files

- `test/seqdb/performance/calculate_seq_distances/test_seqdb_calculate_seq_distances_performance.py`
- `test/seqdb/performance/common.py`

## Audit Trail

- EXTRACTED: 55 (87%)
- INFERRED: 8 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*