# BaseCaseService

> God node · 147 connections · `gen_epix/casedb/services/case/base.py`

**Community:** [Casedb Case Service Implementation](Casedb_Case_Service_Implementation.md)

## Connections by Relation

### contains
- casedb/services/case/base.py `EXTRACTED`

### imports
- case/service.py `EXTRACTED`
- [test_casedb_upload.py](test_casedb_upload.py.md) `EXTRACTED`
- case/crud_common.py `EXTRACTED`
- [case_validator.py](case_validator.py.md) `EXTRACTED`
- test_casedb_retrieve_case.py `EXTRACTED`
- [retrieve_case.py](retrieve_case.py.md) `EXTRACTED`
- services/case/upload.py `EXTRACTED`
- [crud_dim.py](crud_dim.py.md) `EXTRACTED`
- test_casedb_retrieve_similar_cases.py `EXTRACTED`
- crud_case_set.py `EXTRACTED`
- retrieve_complete_case_type.py `EXTRACTED`
- create_seq.py `EXTRACTED`
- test_casedb_retrieve_is_own_cases.py `EXTRACTED`
- crud_col.py `EXTRACTED`
- retrieve_seq.py `EXTRACTED`
- test_retrieve_complete_case_type.py `EXTRACTED`
- crud_case.py `EXTRACTED`
- crud_case_data_collection_link.py `EXTRACTED`
- crud_case_set_data_collection_link.py `EXTRACTED`
- crud_case_set_member.py `EXTRACTED`

### inherits
- DomainBaseCaseService `EXTRACTED`

### method
- ._retrieve_cases_with_content_right() `EXTRACTED`
- ._retrieve_case_sets_with_content_right() `EXTRACTED`
- ._retrieve_seq_column_data() `EXTRACTED`
- ._read_association_with_valid_ids() `EXTRACTED`
- ._retrieve_association_map() `EXTRACTED`
- ._retrieve_case_data_collections_map() `EXTRACTED`
- ._retrieve_case_set_data_collections_map() `EXTRACTED`
- ._retrieve_case_case_sets_map() `EXTRACTED`
- ._verify_case_set_member_case_type() `EXTRACTED`
- ._compose_id_filter() `EXTRACTED`
- .__init__() `EXTRACTED`

### rationale_for
- Abstract base class for case services defining the interface contract. This… `EXTRACTED`

### uses
- AppImplDetails `INFERRED`
- [CaseService](CaseService.md) `INFERRED`
- [CaseValidator](CaseValidator.md) `INFERRED`
- _crud_cascade_delete() `INFERRED`
- BaseUploadTestCase `INFERRED`
- crud_with_access_filter() `INFERRED`
- case_service_crud_dim() `INFERRED`
- [BaseRetrieveCaseTestCase](BaseRetrieveCaseTestCase.md) `INFERRED`
- case_service_crud_case_set() `INFERRED`
- case_service_create_file_for_read_set_or_seq() `INFERRED`
- case_service_retrieve_cases_by_query() `INFERRED`
- CaseBatchUploader `INFERRED`
- case_service_crud_ref_col() `INFERRED`
- case_service_retrieve_is_own_cases() `INFERRED`
- _get_cases_for_create_file_for_read_sets_or_seqs() `INFERRED`
- is_app_admin_or_above() `INFERRED`
- _crud_create_dim() `INFERRED`
- case_service_retrieve_cases_by_id() `INFERRED`
- [BaseIsOwnCasesTestCase](BaseIsOwnCasesTestCase.md) `INFERRED`
- [BaseSimilarCasesTestCase](BaseSimilarCasesTestCase.md) `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*