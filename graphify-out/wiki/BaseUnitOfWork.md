# BaseUnitOfWork

> God node · 286 connections · `gen_epix/fastapp/unit_of_work.py`

**Community:** [SQLAlchemy Case Repository](SQLAlchemy_Case_Repository.md)

## Connections by Relation

### contains
- fastapp/unit_of_work.py `EXTRACTED`

### imports
- case/service.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- gen_epix/fastapp/__init__.py `EXTRACTED`
- test_commondb_upload.py `EXTRACTED`
- sa/repository.py `EXTRACTED`
- casedb/services/case/base.py `EXTRACTED`
- test_casedb_upload.py `EXTRACTED`
- test_seqdb_calculate_seq_distance.py `EXTRACTED`
- calculate_seq_distance.py `EXTRACTED`
- case/crud_common.py `EXTRACTED`
- test_omopdb_upload.py `EXTRACTED`
- test_seqdb_upload.py `EXTRACTED`
- retrieve_case.py `EXTRACTED`
- test_seqdb_retrieve_best.py `EXTRACTED`
- services/case/upload.py `EXTRACTED`
- services/upload.py `EXTRACTED`
- dict/repository.py `EXTRACTED`
- crud_dim.py `EXTRACTED`
- gen_epix/fastapp/service.py `EXTRACTED`
- case_date.py `EXTRACTED`
- *…and 45 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- SAUnitOfWork `EXTRACTED`
- DictUnitOfWork `EXTRACTED`
- TrackingUnitOfWork `EXTRACTED`

### method
- .__exit__() `EXTRACTED`
- .commit() `EXTRACTED`
- .rollback() `EXTRACTED`
- .__enter__() `EXTRACTED`
- .__init__() `EXTRACTED`
- .is_managing_context() `EXTRACTED`
- .flush() `EXTRACTED`

### rationale_for
- Encapsulates the base context manager for repository transaction boundaries. `EXTRACTED`

### references
- _crud_cascade_delete() `EXTRACTED`
- _verify_children_seq_profiles() `EXTRACTED`
- crud_with_access_filter() `EXTRACTED`
- _calculate_and_store_distances() `EXTRACTED`
- .crud() `EXTRACTED`
- _verify_sample_refdata() `EXTRACTED`
- _verify_children_seq_classifications() `EXTRACTED`
- _verify_children_seqs() `EXTRACTED`
- .crud() `EXTRACTED`
- _verify_protocol() `EXTRACTED`
- ._retrieve_cases_with_content_right() `EXTRACTED`
- .update_association() `EXTRACTED`
- .upsert_batch() `EXTRACTED`
- case_service_get_case_date_col_mappers() `EXTRACTED`
- ._retrieve_case_sets_with_content_right() `EXTRACTED`
- .create_identifiers() `EXTRACTED`
- .verify_children() `EXTRACTED`
- .verify_link_id() `EXTRACTED`
- ._filter_cases_by_access_and_content() `EXTRACTED`
- .create_child_identifiers() `EXTRACTED`
- *…and 110 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- DictRepository `INFERRED`
- SARepository `INFERRED`
- BaseService `INFERRED`
- BaseRepository `INFERRED`
- BaseUploadTestCase `INFERRED`
- BasePersonUploadTestCase `INFERRED`
- BaseUploadTestCase `INFERRED`
- CaseBatchUploader `INFERRED`
- BaseUserManager `INFERRED`
- BaseCrudTestCase `INFERRED`
- SeqDictRepository `INFERRED`
- _make_crud_side_effect() `INFERRED`
- BaseSeqRepository `INFERRED`
- BaseSnpUploadTestCase `INFERRED`
- PersonBatchUploader `INFERRED`
- TestCalculateSeqDistancesForNewProfiles `INFERRED`
- _get_cases_for_create_file_for_read_sets_or_seqs() `INFERRED`
- SequenceRepository `INFERRED`
- _crud_create_dim() `INFERRED`
- DummyRepository `INFERRED`
- *…and 59 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*