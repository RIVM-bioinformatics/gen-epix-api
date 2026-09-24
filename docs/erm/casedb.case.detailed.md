# casedb / CASE — Detailed ERD

Auto-generated.  Service type **CASE** — 21 entities.

```mermaid
erDiagram
    %% casedb / CASE (detailed)

    %% Relationships
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    RefCol }o--|| RefDim : "ref_dim_id"
    RefCol }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    Dim }o--|| CaseType : "case_type_id"
    Dim }o--|| RefDim : "ref_dim_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"
    Col }o--|| CaseType : "case_type_id"
    Col }o--|| Dim : "dim_id"
    Col }o--|| RefCol : "ref_col_id"
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    ColSetMember }o--|| ColSet : "col_set_id"
    ColSetMember }o--|| Col : "col_id"
    Case }o--|| CaseType : "case_type_id"
    CaseIdentifier }o--|| Case : "internal_id"
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseDataCollectionLink }o--|| Case : "case_id"

    %% Entity definitions
    TreeAlgorithmClass {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        bool is_seq_based
        bool is_dist_based
        int rank
    }

    GeneticDistanceProtocol {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID seqdb_seq_distance_protocol_id
        enum seqdb_seq_distance_type
        string name
        string description
        float seqdb_max_stored_distance
        bool seqdb_is_integer_distance
        float min_scale_unit
    }

    RefDim {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        enum dim_type
        string code
        string label
        int rank
        string col_code_prefix
        string description
        dict[string, Any] props
    }

    CaseTypeSetCategory {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
        int rank
        enum purpose
    }

    CaseType {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
        UUID disease_id FK
        UUID etiological_agent_id FK
        CaseTypeProps props
    }

    ColSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    CaseSetCategory {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
        int rank
    }

    CaseSetStatus {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
        int rank
    }

    TreeAlgorithm {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID tree_algorithm_class_id FK
        UUID seqdb_tree_algorithm_id
        enum code
        string name
        string description
        bool is_ultrametric
        int rank
    }

    RefCol {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID ref_dim_id FK
        string code_suffix
        string code
        int rank
        string label
        enum col_type
        enum unit
        UUID concept_set_id FK
        UUID region_set_id FK
        UUID genetic_distance_protocol_id FK
        string description
        string regex
        string schema_definition
        string schema_uri
        dict[string, Any] props
    }

    CaseTypeSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
        UUID case_type_set_category_id FK
        float rank
    }

    Dim {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
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

    CaseSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_type_id FK
        UUID created_in_data_collection_id FK
        string name
        string code
        string description
        timestamp case_set_date
        UUID case_set_category_id FK
        UUID case_set_status_id FK
    }

    CaseTypeSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_type_set_id FK
        UUID case_type_id FK
    }

    Col {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_type_id FK
        UUID dim_id FK
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
        UUID genetic_sequence_col_id
        set[enum] tree_algorithm_codes
        dict[string, Any] props
    }

    CaseSetDataCollectionLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_set_id FK
        UUID data_collection_id FK
    }

    ColSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID col_set_id FK
        UUID col_id FK
    }

    Case {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        UUID case_type_id FK
        UUID created_in_data_collection_id FK
        dict[UUID, UUID] cohort
        int count
        timestamp case_date
        dict[UUID, string] content
    }

    CaseIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    CaseSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_set_id FK
        UUID case_id FK
        enum classification
    }

    CaseDataCollectionLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_id FK
        UUID data_collection_id FK
    }

```
