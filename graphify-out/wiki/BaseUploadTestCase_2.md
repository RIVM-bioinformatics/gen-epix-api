# BaseUploadTestCase

> 13 nodes · cohesion 0.15

## Key Concepts

- **BaseUploadTestCase** (32 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **UUID** (10 connections)
- **.create_read_set_for_upload()** (6 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.setup_method()** (4 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.assertBatchFailed()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.assertBatchProcessed()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.assertHasLogCode()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **.assertStatusCount()** (2 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **ReadSetForUpload** (2 connections)
- **ParentUploadResult** (1 connections)
- **Helper to create a ReadSetForUpload with default or specified properties.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Base test case with common fixtures and utilities.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`
- **Set up test fixtures.** (1 connections) — `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Relationships

- [.create_command_and_result_for_samples](create_command_and_result_for_samples.md) (9 shared connections)
- [_verify_children_seq_classifications](_verify_children_seq_classifications.md) (8 shared connections)
- [.create_seq_for_upload](create_seq_for_upload.md) (7 shared connections)
- [test_seqdb_upload.py](test_seqdb_upload.py.md) (4 shared connections)
- [.create_sample_for_upload](create_sample_for_upload.md) (4 shared connections)
- [BaseUnitOfWork](BaseUnitOfWork.md) (4 shared connections)
- [App](App.md) (1 shared connections)
- [Permission](Permission.md) (1 shared connections)
- [Role](Role.md) (1 shared connections)
- [FileCompression](FileCompression.md) (1 shared connections)
- [seqdb/domain/enum.py](seqdb-domain-enum.py.md) (1 shared connections)
- [commondb/domain/enum.py](commondb-domain-enum.py.md) (1 shared connections)

## Source Files

- `test/seqdb/unit/services/seq/upload/test_seqdb_upload.py`

## Audit Trail

- EXTRACTED: 51 (94%)
- INFERRED: 3 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*