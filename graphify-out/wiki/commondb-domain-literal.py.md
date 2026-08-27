# commondb/domain/literal.py

> 67 nodes · cohesion 0.06

## Key Concepts

- **commondb/domain/literal.py** (37 connections) — `gen_epix/commondb/domain/literal.py`
- **SampleBatchUploadResult** (32 connections) — `gen_epix/seqdb/domain/model/seq/upload.py`
- **upload_verify_batch.py** (26 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- **upload_verify_batch_refdata.py** (22 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_batch_refdata_snp_profiles()** (20 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **BaseSnpUploadTestCase** (18 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.create_command_and_result()** (16 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.create_snp_profile()** (14 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.create_protocol()** (11 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.mock_crud_for_snp()** (10 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_empty_content_fails()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_protocol_no_ref_seq_id_fails()** (9 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **_verify_batch_refdata_allele_profiles()** (8 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_batch_refdata_kmer_profiles()** (8 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **_verify_batch_refdata_mlva_profiles()** (8 connections) — `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- **.get_profile_result()** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **TestSnpInvalidCases** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_any_valid_json_passes_structural_only()** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_missing_ref_seq_fails()** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_valid_snp_content_passes()** (8 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **TestSnpBehavior** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_batch_validation_idempotent()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **TestSnpValidCases** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_matching_ref_seq_accepted()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- **.test_two_profiles_same_ref_seq_same_length()** (7 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`
- *... and 42 more nodes in this community*

## Relationships

- [BaseUnitOfWork](BaseUnitOfWork.md) (37 shared connections)
- [seqdb/domain/enum.py](seqdb-domain-enum.py.md) (11 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (7 shared connections)
- [CrudOperation](CrudOperation.md) (6 shared connections)
- [entity.py](entity.py.md) (6 shared connections)
- [.create_sample_for_upload](create_sample_for_upload.md) (6 shared connections)
- [seqdb/domain/model/__init__.py](seqdb-domain-model-__init__.py.md) (4 shared connections)
- [test_seqdb_upload.py](test_seqdb_upload.py.md) (4 shared connections)
- [.create_command_and_result_for_samples](create_command_and_result_for_samples.md) (4 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (4 shared connections)
- [casedb/domain/command/__init__.py](casedb-domain-command-__init__.py.md) (3 shared connections)
- [.create_seq_for_upload](create_seq_for_upload.md) (3 shared connections)

## Source Files

- `gen_epix/commondb/domain/literal.py`
- `gen_epix/seqdb/domain/model/seq/upload.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch.py`
- `gen_epix/seqdb/services/seq/upload_verify_batch_refdata.py`
- `test/seqdb/unit/services/seq/upload/test_seqdb_upload_verify_batch_refdata.py`

## Audit Trail

- EXTRACTED: 257 (99%)
- INFERRED: 3 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*