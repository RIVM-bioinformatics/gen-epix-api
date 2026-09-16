# Sample Batch Upload Model

> 38 nodes · cohesion 0.09

## Key Concepts

- **SeqGenerationSettings** (19 connections) — `test/seqdb/seqdb_test_client.py`
- **SampleBatchForUpload** (17 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.generate_random_sequences()** (11 connections) — `test/seqdb/seqdb_test_client.py`
- **computed_field** (7 connections)
- **TestGenerateRandomSequences** (7 connections) — `test/seqdb/unit/test_seqdb_generate_random_sequences.py`
- **get_random_sequences()** (6 connections) — `test/seqdb/performance/generate_seq_distances.py`
- **computed_field** (5 connections)
- **Random** (5 connections)
- **test_seqdb_generate_random_sequences.py** (5 connections) — `test/seqdb/unit/test_seqdb_generate_random_sequences.py`
- **._apply_locus_deletions()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **._apply_nucleotide_deletions()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **._apply_nucleotide_substitutions()** (4 connections) — `test/seqdb/seqdb_test_client.py`
- **.has_ast_measurements()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_pcr_measurements()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_read_sets()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_seq_classifications()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_seq_profiles()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_seq_taxonomies()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.has_seqs()** (3 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **.test_generate_sequences_happy_flow()** (3 connections) — `test/seqdb/unit/test_seqdb_generate_random_sequences.py`
- **.test_generate_sequences_reproducibility()** (3 connections) — `test/seqdb/unit/test_seqdb_generate_random_sequences.py`
- **.test_generate_sequences_uniqueness()** (3 connections) — `test/seqdb/unit/test_seqdb_generate_random_sequences.py`
- **Indicates whether there are any sequences in the sample set.** (2 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **BaseModel** (2 connections)
- **.p_locus_deletion_vec()** (2 connections) — `test/seqdb/seqdb_test_client.py`
- *... and 13 more nodes in this community*

## Relationships

- [Protocol Creation Tests](Protocol_Creation_Tests.md) (9 shared connections)
- [Seq Distance Data Generation](Seq_Distance_Data_Generation.md) (6 shared connections)
- [FastAPI App Composition](FastAPI_App_Composition.md) (3 shared connections)
- [Organization & ABAC Models](Organization_&_ABAC_Models.md) (2 shared connections)
- [Case Upload Batch Models](Case_Upload_Batch_Models.md) (2 shared connections)
- [Commondb Base Models](Commondb_Base_Models.md) (1 shared connections)
- [Seqdb Protocol Factories](Seqdb_Protocol_Factories.md) (1 shared connections)

## Source Files

- `gen_epix/seqdb/domain/model/seq/upload.py`
- `test/seqdb/performance/generate_seq_distances.py`
- `test/seqdb/seqdb_test_client.py`
- `test/seqdb/unit/test_seqdb_generate_random_sequences.py`

## Audit Trail

- EXTRACTED: 83 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*