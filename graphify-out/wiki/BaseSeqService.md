# BaseSeqService

> God node · 135 connections · `gen_epix/seqdb/domain/service/seq.py`

**Community:** [Seq Service Interface](Seq_Service_Interface.md)

## Connections by Relation

### contains
- service/seq.py `EXTRACTED`

### imports
- test_casedb_case_upload.py `EXTRACTED`
- calculate_phylogenetic_tree.py `EXTRACTED`
- services/seq/upload.py `EXTRACTED`
- seqdb/domain/service/__init__.py `EXTRACTED`
- crud_protocol.py `EXTRACTED`
- crud_seq_profile.py `EXTRACTED`
- crud_allele.py `EXTRACTED`
- crud_ast_measurement.py `EXTRACTED`
- crud_ast_prediction.py `EXTRACTED`
- crud_locus.py `EXTRACTED`
- crud_locus_code_map.py `EXTRACTED`
- crud_locus_set.py `EXTRACTED`
- crud_pcr_measurement.py `EXTRACTED`
- crud_protocol_set.py `EXTRACTED`
- crud_protocol_set_member.py `EXTRACTED`
- crud_read_set.py `EXTRACTED`
- crud_read_set_identifier.py `EXTRACTED`
- crud_ref_allele.py `EXTRACTED`
- crud_ref_seq.py `EXTRACTED`
- crud_sample.py `EXTRACTED`
- *…and 16 more `imports` connection(s) not listed (lowest-degree first to go)*

### inherits
- BaseService `EXTRACTED`
- SeqService `EXTRACTED`

### method
- .crud_seq_distance() `EXTRACTED`
- .crud_seq_identifier() `EXTRACTED`
- .crud_seq_taxonomy() `EXTRACTED`
- .crud_taxon() `EXTRACTED`
- .crud_taxon_set() `EXTRACTED`
- .crud_taxon_set_member() `EXTRACTED`
- .crud_tree_algorithm() `EXTRACTED`
- .crud_tree_algorithm_class() `EXTRACTED`
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
- *…and 26 more `method` connection(s) not listed (lowest-degree first to go)*

### rationale_for
- Encapsulates seqdb handlers implemented by concrete sequence services. `EXTRACTED`

### references
- _get_best_id_per_sample() `EXTRACTED`
- seq_service_calculate_seq_distances_for_new_profiles() `EXTRACTED`
- _calculate_and_store_distances() `EXTRACTED`
- seq_service_convert_seq_format() `EXTRACTED`
- seq_service_update_seq_distances() `EXTRACTED`
- seq_service_retrieve_best_seq_classification_per_sample() `EXTRACTED`
- seq_service_retrieve_best_seq_per_sample() `EXTRACTED`
- seq_service_retrieve_best_seq_profile_per_sample() `EXTRACTED`
- seq_service_retrieve_seq_distance_last_modified() `EXTRACTED`
- seq_service_crud_protocol() `EXTRACTED`
- seq_service_crud_seq_profile() `EXTRACTED`
- seq_service_crud_allele() `EXTRACTED`
- seq_service_crud_ast_measurement() `EXTRACTED`
- seq_service_crud_ast_prediction() `EXTRACTED`
- seq_service_crud_locus_code_map() `EXTRACTED`
- seq_service_crud_locus() `EXTRACTED`
- seq_service_crud_locus_set() `EXTRACTED`
- seq_service_crud_pcr_measurement() `EXTRACTED`
- seq_service_crud_protocol_set_member() `EXTRACTED`
- seq_service_crud_protocol_set() `EXTRACTED`
- *…and 24 more `references` connection(s) not listed (lowest-degree first to go)*

### uses
- seq_service_calculate_phylogenetic_tree() `INFERRED`
- ServiceType `INFERRED`
- SampleBatchUploader `INFERRED`
- CaseUploadSetup `INFERRED`
- seq_service_upload_samples() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*