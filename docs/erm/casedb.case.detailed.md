# casedb / CASE — Detailed ERD

Auto-generated.  Service type **CASE** — 33 entities.

```mermaid
erDiagram
    %% casedb / CASE (detailed)

    %% Relationships
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    CaseDataCollectionLink }o--|| Case : "case_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"
    CaseTypeCol }o--|| CaseType : "case_type_id"
    CaseTypeCol }o--|| CaseTypeDim : "case_type_dim_id"
    CaseTypeCol }o--|| Col : "col_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    Col }o--|| Dim : "dim_id"
    Col }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseTypeColSetMember }o--|| CaseTypeColSet : "case_type_col_set_id"
    CaseTypeColSetMember }o--|| CaseTypeCol : "case_type_col_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    Case }o--|| CaseType : "case_type_id"
    CaseTypeDim }o--|| CaseType : "case_type_id"
    CaseTypeDim }o--|| Dim : "dim_id"

    %% Entity definitions
    CaseSetDataCollectionLink {
        UUID id PK
        UUID case_set_id FK
        UUID data_collection_id FK
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

    CaseDataCollectionLink {
        UUID id PK
        UUID case_id FK
        UUID data_collection_id FK
    }

    CaseSetQuery {
        UUID id
        string label
        TypedCompositeFilter filter
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
        dict[UUID, Dim] dims
        dict[UUID, Col] cols
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

    CaseTypeSetMember {
        UUID id PK
        UUID case_type_set_id FK
        UUID case_type_id FK
    }

    CaseTypeCol {
        UUID id PK
        UUID case_type_id FK
        UUID case_type_dim_id FK
        UUID col_id FK
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

    CaseQuery {
        UUID id
        string label
        UUID case_type_id
        set[UUID] case_set_ids
        TypedDatetimeRangeFilter datetime_range_filter
        TypedCompositeFilter filter
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

    CaseBatchForUpload {
        UUID id PK
        timestamp created_at
        list[CaseForUpload] cases
        any has_read_sets
        any has_seqs
    }

    CaseSetCategory {
        UUID id PK
        string name
        string description
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

    Col {
        UUID id PK
        UUID dim_id FK
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

    ReadSetForUpload {
        bool is_new_id
        UUID id PK
        UUID case_id
        UUID case_type_col_id
        UUID sample_id
        ExternalIdentifierForUpload external_sample_id
        UUID sequencing_protocol_id
        string sequencing_protocol_code
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

    CaseSetMember {
        UUID id PK
        UUID case_set_id FK
        UUID case_id FK
        enum classification
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

    CaseBatchUploadResult {
        UUID id PK
        enum status
        list[UploadLogItem] logs
        UUID batch_id
        list[CaseUploadResult] cases
    }

    CaseStats {
        UUID case_type_id
        UUID case_set_id
        int n_cases
        int n_own_cases
        timestamp first_case_date
        timestamp last_case_date
    }

    CaseSetStatus {
        UUID id PK
        string name
        string description
    }

    Dim {
        UUID id PK
        enum dim_type
        string code
        string label
        int rank
        string col_code_prefix
        string description
        dict[string, Any] props
    }

    CaseTypeColSetMember {
        UUID id PK
        UUID case_type_col_set_id FK
        UUID case_type_col_id FK
    }

    CaseTypeSetCategory {
        UUID id PK
        string name
        string description
        int rank
        enum purpose
    }

    TreeAlgorithmClass {
        UUID id PK
        string code
        string name
        bool is_seq_based
        bool is_dist_based
        int rank
    }

    CaseTypeSet {
        UUID id PK
        string name
        string description
        UUID case_type_set_category_id FK
        float rank
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

    CaseTypeDim {
        UUID id PK
        UUID case_type_id FK
        UUID dim_id FK
        int occurrence
        string code
        string label
        string description
        int rank
        bool is_case_date_dim
    }

    CaseQueryResult {
        UUID id
        CaseQuery case_query
        list[UUID] case_ids
        bool is_max_results_exceeded
    }

    CaseTypeColSet {
        UUID id PK
        string name
        string description
    }

    SeqForUpload {
        bool is_new_id
        UUID id PK
        UUID case_id
        UUID case_type_col_id
        UUID sample_id
        ExternalIdentifierForUpload external_sample_id
        UUID assembly_protocol_id
        string assembly_protocol_code
    }

    CaseForUpload {
        list[ExternalIdentifierForUpload] external_identifiers
        bool is_new_id
        UUID id PK
        Case case
        list[ReadSetForUpload] read_sets
        list[SeqForUpload] seqs
    }

    CaseUploadResult {
        UUID id
        enum status
        list[UploadLogItem] logs
        list[UploadResult] external_identifiers
        list[CaseDataIssue] data_issues
        dict[UUID, string] validated_content
        list[UploadResult] read_sets
        list[UploadResult] seqs
    }

```
