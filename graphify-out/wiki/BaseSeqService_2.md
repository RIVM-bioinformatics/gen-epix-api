# BaseSeqService

> God node · 135 connections · `gen_epix/seqdb/domain/service/seq.py`

**Community:** [BaseSeqService](BaseSeqService.md)

## Connections by Relation

### contains
- service/seq.py `EXTRACTED`

### imports
- seq/service.py `EXTRACTED`
- [calculate_seq_distance.py](calculate_seq_distance.py.md) `EXTRACTED`
- [test_seqdb_upload.py](test_seqdb_upload.py.md) `EXTRACTED`
- test_casedb_case_upload.py `EXTRACTED`
- test_seqdb_upload_verify_batch_refdata.py `EXTRACTED`
- calculate_phylogenetic_tree.py `EXTRACTED`
- services/seq/upload.py `EXTRACTED`
- retrieve_best.py `EXTRACTED`
- seqdb/domain/service/__init__.py `EXTRACTED`
- crud_protocol.py `EXTRACTED`
- [crud_seq_profile.py](crud_seq_profile.py.md) `EXTRACTED`
- [crud_allele.py](crud_allele.py.md) `EXTRACTED`
- crud_ast_measurement.py `EXTRACTED`
- [crud_ast_prediction.py](crud_ast_prediction.py.md) `EXTRACTED`
- crud_locus.py `EXTRACTED`
- [crud_locus_code_map.py](crud_locus_code_map.py.md) `EXTRACTED`
- crud_locus_set.py `EXTRACTED`
- [crud_pcr_measurement.py](crud_pcr_measurement.py.md) `EXTRACTED`
- crud_protocol_set.py `EXTRACTED`
- crud_protocol_set_member.py `EXTRACTED`

### inherits
- [BaseService](BaseService.md) `EXTRACTED`
- [SeqService](SeqService.md) `EXTRACTED`

### method
- .crud_protocol() `EXTRACTED`
- .crud_protocol_set() `EXTRACTED`
- .crud_protocol_set_member() `EXTRACTED`
- .crud_allele() `EXTRACTED`
- .crud_ast_measurement() `EXTRACTED`
- .crud_ast_prediction() `EXTRACTED`
- .crud_locus() `EXTRACTED`
- .crud_locus_code_map() `EXTRACTED`
- .crud_seq_profile() `EXTRACTED`
- .crud_seq_profile_identifier() `EXTRACTED`
- .crud_locus_set() `EXTRACTED`
- .crud_pcr_measurement() `EXTRACTED`
- .crud_read_set() `EXTRACTED`
- .crud_read_set_identifier() `EXTRACTED`
- .crud_ref_allele() `EXTRACTED`
- .crud_ref_seq() `EXTRACTED`
- .crud_sample() `EXTRACTED`
- .crud_sample_data_collection_link() `EXTRACTED`
- .crud_sample_identifier() `EXTRACTED`
- .crud_seq() `EXTRACTED`

### references
- _get_best_id_per_sample() `EXTRACTED`
- seq_service_calculate_seq_distances_for_new_profiles() `EXTRACTED`
- _calculate_and_store_distances() `EXTRACTED`
- seq_service_calculate_phylogenetic_tree() `EXTRACTED`
- seq_service_update_seq_distances() `EXTRACTED`
- seq_service_crud_seq_profile() `EXTRACTED`
- seq_service_retrieve_best_seq_classification_per_sample() `EXTRACTED`
- seq_service_retrieve_best_seq_per_sample() `EXTRACTED`
- seq_service_retrieve_best_seq_profile_per_sample() `EXTRACTED`
- seq_service_crud_protocol() `EXTRACTED`
- seq_service_crud_allele() `EXTRACTED`
- seq_service_crud_ast_measurement() `EXTRACTED`
- seq_service_crud_ast_prediction() `EXTRACTED`
- seq_service_crud_locus_code_map() `EXTRACTED`
- seq_service_crud_locus() `EXTRACTED`
- seq_service_crud_locus_set() `EXTRACTED`
- seq_service_crud_pcr_measurement() `EXTRACTED`
- seq_service_crud_protocol_set_member() `EXTRACTED`
- seq_service_crud_protocol_set() `EXTRACTED`
- seq_service_crud_read_set_identifier() `EXTRACTED`

### uses
- ServiceType `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*