# casedb / CASE — Detailed ERD

Auto-generated.  Service type **CASE** — 34 entities.

```mermaid
erDiagram
    %% casedb / CASE (detailed)

    %% Relationships
    CaseTypeCol }o--|| CaseType : "case_type_id"
    CaseTypeCol }o--|| CaseTypeDim : "case_type_dim_id"
    CaseTypeCol }o--|| RefCol : "ref_col_id"
    CaseTypeDim }o--|| CaseType : "case_type_id"
    CaseTypeDim }o--|| RefDim : "ref_dim_id"
    RefCol }o--|| RefDim : "ref_dim_id"
    RefCol }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
    Case }o--|| CaseType : "case_type_id"
    CaseDataCollectionLink }o--|| Case : "case_id"
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    CaseTypeColSetMember }o--|| CaseTypeColSet : "case_type_col_set_id"
    CaseTypeColSetMember }o--|| CaseTypeCol : "case_type_col_id"

    %% Entity definitions
    CaseTypeCol {
        UUID id PK
        UUID case_type_id FK
        UUID case_type_dim_id FK
        UUID ref_col_id FK
        string code
        int rank
        string label
        string description
        float min_value
        float max_value
        timestamp min_datetime
        timestamp max_datetime
        int min_length
        int max_length
        string pattern
        string ncbi_taxid
        UUID genetic_sequence_case_type_col_id
        set[enum] tree_algorithm_codes
        dict[string, Any] props
    }

    CaseBatchForUpload {
        UUID id PK
        timestamp created_at
        list[CaseForUpload] cases
        any has_read_sets
        any has_seqs
    }

    CaseTypeDim {
        UUID id PK
        UUID case_type_id FK
        UUID ref_dim_id FK
        int occurrence
        string code
        string label
        string description
        int rank
        bool is_case_date_dim
    }

    CaseType {
        UUID id PK
        string name
        string description
        UUID disease_id FK
        UUID etiological_agent_id FK
        int create_max_n_cases
        int read_max_n_cases
        int read_max_tree_size
        int update_max_n_cases
        int delete_max_n_cases
    }

    SeqForUpload {
        UUID id PK
        UUID case_id
        UUID case_type_col_id
        UUID sample_id
        ExternalIdentifierForUpload external_sample_id
        UUID assembly_protocol_id
        string assembly_protocol_code
    }

    RefCol {
        UUID id PK
        UUID ref_dim_id FK
        string code_suffix
        string code
        int rank
        string label
        enum col_type
        UUID concept_set_id FK
        UUID region_set_id FK
        UUID genetic_distance_protocol_id FK
        string description
        dict[string, Any] props
    }

    CaseSetRights {
        UUID id
        UUID created_in_data_collection_id
        UUID case_type_id
        set[UUID] data_collection_ids
        bool is_full_access
        set[UUID] add_data_collection_ids
        set[UUID] remove_data_collection_ids
        bool can_delete
        set[UUID] shared_in_data_collection_ids
        UUID case_set_id
        bool read_case_set
        bool write_case_set
    }

    TreeAlgorithm {
        UUID id PK
        UUID tree_algorithm_class_id FK
        UUID seqdb_tree_algorithm_id
        enum code
        string name
        string description
        bool is_ultrametric
        int rank
    }

    CaseSetQuery {
        UUID id
        string label
        TypedCompositeFilter filter
    }

    GeneticDistanceProtocol {
        UUID id PK
        UUID seqdb_seq_distance_protocol_id
        enum seqdb_seq_distance_protocol_type
        string name
        string description
        float seqdb_max_stored_distance
        bool seqdb_is_integer_distance
        float min_scale_unit
    }

    RefDataAccess {
        UUID id
        UUID user_id
        bool is_full_access
        set[UUID] case_type_set_ids
        set[UUID] case_type_ids
        set[UUID] case_type_col_set_ids
        set[UUID] case_type_col_ids
        set[UUID] case_type_dim_ids
        set[UUID] ref_dim_ids
        set[UUID] ref_col_ids
    }

    CaseStats {
        UUID case_type_id
        UUID case_set_id
        int n_cases
        int n_own_cases
        timestamp first_case_date
        timestamp last_case_date
    }

    CaseTypeSetMember {
        UUID id PK
        UUID case_type_set_id FK
        UUID case_type_id FK
    }

    CaseSetCategory {
        UUID id PK
        string name
        string description
    }

    CaseSetDataCollectionLink {
        UUID id PK
        UUID case_set_id FK
        UUID data_collection_id FK
    }

    CaseSet {
        UUID id PK
        UUID case_type_id FK
        UUID created_in_data_collection_id FK
        string name
        string description
        timestamp created_at
        UUID case_set_category_id FK
        UUID case_set_status_id FK
    }

    Case {
        UUID id PK
        string code
        UUID case_type_id FK
        UUID subject_id FK
        UUID created_in_data_collection_id FK
        int count
        timestamp case_date
        dict[UUID, string] content
    }

    TreeAlgorithmClass {
        UUID id PK
        string code
        string name
        bool is_seq_based
        bool is_dist_based
        int rank
    }

    CaseDataCollectionLink {
        UUID id PK
        UUID case_id FK
        UUID data_collection_id FK
    }

    CaseUploadResult {
        UUID id
        enum status
        bool is_new
        list[UploadLogItem] logs
        list[UploadResult] external_identifiers
        list[CaseDataIssue] data_issues
        dict[UUID, string] validated_content
        list[UploadResult] read_sets
        list[UploadResult] seqs
    }

    CaseSetMember {
        UUID id PK
        UUID case_set_id FK
        UUID case_id FK
        enum classification
    }

    CaseBatchUploadResult {
        UUID id PK
        enum status
        bool is_new
        list[UploadLogItem] logs
        UUID batch_id
        list[CaseUploadResult] cases
    }

    CaseTypeSetCategory {
        UUID id PK
        string name
        string description
        int rank
        enum purpose
    }

    CompleteCaseType {
        UUID id
        string name
        string description
        UUID disease_id
        Disease disease
        UUID etiological_agent_id
        EtiologicalAgent etiological_agent
        int create_max_n_cases
        int read_max_n_cases
        int read_max_tree_size
        int update_max_n_cases
        int delete_max_n_cases
        UUID user_id
        dict[UUID, Etiology] etiologies
        dict[UUID, EtiologicalAgent] etiological_agents
        dict[UUID, RefDim] ref_dims
        dict[UUID, RefCol] ref_cols
        dict[UUID, CaseTypeDim] case_type_dims
        dict[UUID, CaseTypeCol] case_type_cols
        list[UUID] ordered_case_type_dim_ids
        list[UUID] ordered_case_type_col_ids
        dict[UUID, list[UUID]] ordered_case_type_col_ids_by_dim
        dict[UUID, GeneticDistanceProtocol] genetic_distance_protocols
        dict[enum, TreeAlgorithm] tree_algorithms
        dict[UUID, CaseTypeAccessAbac] case_type_access_abacs
        dict[UUID, CaseTypeShareAbac] case_type_share_abacs
        UUID case_date_case_type_dim_id
        dict[enum, UUID] case_date_col_type_map
    }

    ReadSetForUpload {
        UUID id PK
        UUID case_id
        UUID case_type_col_id
        UUID sample_id
        ExternalIdentifierForUpload external_sample_id
        UUID sequencing_protocol_id
        string sequencing_protocol_code
    }

    CaseRights {
        UUID id
        UUID created_in_data_collection_id
        UUID case_type_id
        set[UUID] data_collection_ids
        bool is_full_access
        set[UUID] add_data_collection_ids
        set[UUID] remove_data_collection_ids
        bool can_delete
        set[UUID] shared_in_data_collection_ids
        UUID case_id
        set[UUID] read_case_type_col_ids
        set[UUID] write_case_type_col_ids
    }

    CaseTypeColSet {
        UUID id PK
        string name
        string description
    }

    CaseTypeSet {
        UUID id PK
        string name
        string description
        UUID case_type_set_category_id FK
        float rank
    }

    CaseQueryResult {
        UUID id
        CaseQuery case_query
        list[UUID] case_ids
        bool is_max_results_exceeded
    }

    CaseForUpload {
        list[ExternalIdentifierForUpload] external_identifiers
        UUID id PK
        Case case
        list[ReadSetForUpload] read_sets
        list[SeqForUpload] seqs
    }

    RefDim {
        UUID id PK
        enum dim_type
        string code
        string label
        int rank
        string col_code_prefix
        string description
        dict[string, Any] props
    }

    CaseSetStatus {
        UUID id PK
        string name
        string description
    }

    CaseTypeColSetMember {
        UUID id PK
        UUID case_type_col_set_id FK
        UUID case_type_col_id FK
    }

    CaseQuery {
        UUID id
        string label
        UUID case_type_id
        set[UUID] case_set_ids
        TypedDatetimeRangeFilter datetime_range_filter
        TypedCompositeFilter filter
    }

```
