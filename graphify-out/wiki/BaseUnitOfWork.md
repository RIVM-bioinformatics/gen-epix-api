# BaseUnitOfWork

> God node · 246 connections · `gen_epix/fastapp/unit_of_work.py`

**Community:** [Casedb Case CRUD Commands](Casedb_Case_CRUD_Commands.md)

## Connections by Relation

### contains
- fastapp/unit_of_work.py `EXTRACTED`

### imports
- case/service.py `EXTRACTED`
- gen_epix/fastapp/__init__.py `EXTRACTED`
- test_fastapp_dict_repository.py `EXTRACTED`
- sa/repository.py `EXTRACTED`
- test_commondb_upload.py `EXTRACTED`
- test_casedb_upload.py `EXTRACTED`
- calculate_seq_distance.py `EXTRACTED`
- test_seqdb_calculate_seq_distance.py `EXTRACTED`
- casedb/services/case/base.py `EXTRACTED`
- test_omopdb_upload.py `EXTRACTED`
- case/crud_common.py `EXTRACTED`
- test_seqdb_upload.py `EXTRACTED`
- retrieve_case.py `EXTRACTED`
- gen_epix/fastapp/service.py `EXTRACTED`
- test_seqdb_retrieve_best.py `EXTRACTED`
- services/upload.py `EXTRACTED`
- dict/repository.py `EXTRACTED`
- services/case/upload.py `EXTRACTED`
- crud_dim.py `EXTRACTED`
- test_seqdb_upload_verify_batch_refdata.py `EXTRACTED`

### inherits
- SAUnitOfWork `EXTRACTED`
- DictUnitOfWork `EXTRACTED`

### method
- .__exit__() `EXTRACTED`
- .commit() `EXTRACTED`
- .rollback() `EXTRACTED`
- .__enter__() `EXTRACTED`
- .is_managing_context() `EXTRACTED`
- .flush() `EXTRACTED`
- .__init__() `EXTRACTED`

### references
- _crud_cascade_delete() `EXTRACTED`
- _verify_children_seq_profiles() `EXTRACTED`
- crud_with_access_filter() `EXTRACTED`
- _calculate_and_store_distances() `EXTRACTED`
- .crud() `EXTRACTED`
- _verify_sample_refdata() `EXTRACTED`
- _verify_children_seq_classifications() `EXTRACTED`
- .crud() `EXTRACTED`
- _verify_children_seqs() `EXTRACTED`
- _get_cases_for_create_file_for_read_sets_or_seqs() `EXTRACTED`
- _verify_protocol() `EXTRACTED`
- _crud_create_dim() `EXTRACTED`
- ._retrieve_cases_with_content_right() `EXTRACTED`
- .upsert_batch() `EXTRACTED`
- .verify_link_id() `EXTRACTED`
- .update_association() `EXTRACTED`
- case_service_get_case_date_col_mappers() `EXTRACTED`
- _crud_dim_with_abac() `EXTRACTED`
- case_service_read_association_with_valid_ids() `EXTRACTED`
- _verify_case_filter() `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*