# casedb — Detailed Entity-Relationship Diagram

Auto-generated from domain model definitions.  Contains **49** persistable entities with their field definitions.

```mermaid
erDiagram
    %% casedb — all persistable entities (detailed)

    %% Relationships
    Site }o--|| Organization : "organization_id"
    User }o--|| Organization : "organization_id"
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
    Concept }o--|| ConceptSet : "concept_set_id"
    Etiology }o--|| Disease : "disease_id"
    Etiology }o--|| EtiologicalAgent : "etiological_agent_id"
    CaseType }o--|| Disease : "disease_id"
    CaseType }o--|| EtiologicalAgent : "etiological_agent_id"
    Region }o--|| RegionSet : "region_set_id"
    RegionSetShape }o--|| RegionSet : "region_set_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    RefCol }o--|| RefDim : "ref_dim_id"
    RefCol }o--|| ConceptSet : "concept_set_id"
    RefCol }o--|| RegionSet : "region_set_id"
    RefCol }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    Contact }o--|| Site : "site_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    OrganizationAdminPolicy }o--|| Organization : "organization_id"
    OrganizationAdminPolicy }o--|| User : "user_id"
    ConceptRelation }o--|| Concept : "from_concept_id"
    ConceptRelation }o--|| Concept : "to_concept_id"
    Dim }o--|| CaseType : "case_type_id"
    Dim }o--|| RefDim : "ref_dim_id"
    Case }o--|| CaseType : "case_type_id"
    Case }o--|| DataCollection : "created_in_data_collection_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| DataCollection : "created_in_data_collection_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
    RegionRelation }o--|| Region : "from_region_id"
    RegionRelation }o--|| Region : "to_region_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"
    OrganizationAccessCasePolicy }o--|| Organization : "organization_id"
    OrganizationAccessCasePolicy }o--|| DataCollection : "data_collection_id"
    OrganizationAccessCasePolicy }o--|| CaseTypeSet : "case_type_set_id"
    OrganizationAccessCasePolicy }o--|| ColSet : "read_col_set_id"
    OrganizationAccessCasePolicy }o--|| ColSet : "write_col_set_id"
    OrganizationShareCasePolicy }o--|| Organization : "organization_id"
    OrganizationShareCasePolicy }o--|| DataCollection : "data_collection_id"
    OrganizationShareCasePolicy }o--|| CaseTypeSet : "case_type_set_id"
    OrganizationShareCasePolicy }o--|| DataCollection : "from_data_collection_id"
    UserAccessCasePolicy }o--|| User : "user_id"
    UserAccessCasePolicy }o--|| DataCollection : "data_collection_id"
    UserAccessCasePolicy }o--|| CaseTypeSet : "case_type_set_id"
    UserAccessCasePolicy }o--|| ColSet : "read_col_set_id"
    UserAccessCasePolicy }o--|| ColSet : "write_col_set_id"
    UserShareCasePolicy }o--|| User : "user_id"
    UserShareCasePolicy }o--|| DataCollection : "data_collection_id"
    UserShareCasePolicy }o--|| CaseTypeSet : "case_type_set_id"
    UserShareCasePolicy }o--|| DataCollection : "from_data_collection_id"
    Col }o--|| CaseType : "case_type_id"
    Col }o--|| Dim : "dim_id"
    Col }o--|| RefCol : "ref_col_id"
    CaseIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    CaseIdentifier }o--|| Case : "internal_id"
    CaseDataCollectionLink }o--|| Case : "case_id"
    CaseDataCollectionLink }o--|| DataCollection : "data_collection_id"
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    CaseSetDataCollectionLink }o--|| DataCollection : "data_collection_id"
    ColSetMember }o--|| ColSet : "col_set_id"
    ColSetMember }o--|| Col : "col_id"

    %% Entity definitions
    Outage {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string description
        timestamp active_from
        timestamp active_to
        timestamp visible_from
        timestamp visible_to
        bool is_active
        bool is_visible
    }

    Organization {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    DataCollection {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    DataCollectionSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string description
    }

    IdentifierIssuer {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        string description
    }

    ConceptSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        enum type
        string description
    }

    Disease {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string icd_code
    }

    EtiologicalAgent {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string name
        string type
    }

    RegionSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        bool region_code_as_label
        float resolution
    }

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

    Site {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_id FK
        string name
    }

    User {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string key
        string email
        string name
        string description
        bool is_active
        set[string] roles
        UUID organization_id FK
    }

    OrganizationSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

    DataCollectionSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

    OrganizationIdentifierIssuerLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    Concept {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID concept_set_id FK
        string code
        string name
        string description
        int rank
        dict[string, Any] props
    }

    Etiology {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID disease_id FK
        UUID etiological_agent_id FK
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

    Region {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID region_set_id FK
        string code
        string name
        float centroid_lat
        float centroid_lon
        float center_lat
        float center_lon
    }

    RegionSetShape {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID region_set_id FK
        float scale
        string geo_json
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

    Contact {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID site_id FK
        string name
        string email
        string phone
    }

    UserInvitation {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string key
        string email
        string name
        string description
        string token
        timestamp expires_at
        set[string] roles
        UUID invited_by_user_id FK
        UUID organization_id FK
    }

    OrganizationAdminPolicy {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID organization_id FK
        UUID user_id FK
        bool is_active
    }

    ConceptRelation {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID from_concept_id FK
        UUID to_concept_id FK
        enum relation
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

    RegionRelation {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID from_region_id FK
        UUID to_region_id FK
        enum relation
    }

    CaseTypeSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_type_set_id FK
        UUID case_type_id FK
    }

    OrganizationAccessCasePolicy {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID data_collection_id FK
        UUID case_type_set_id FK
        bool is_active
        bool add_case
        bool remove_case
        bool add_case_set
        bool remove_case_set
        UUID organization_id FK
        bool is_private
        UUID read_col_set_id FK
        UUID write_col_set_id FK
        bool read_case_set
        bool write_case_set
    }

    OrganizationShareCasePolicy {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID data_collection_id FK
        UUID case_type_set_id FK
        bool is_active
        bool add_case
        bool remove_case
        bool add_case_set
        bool remove_case_set
        UUID organization_id FK
        UUID from_data_collection_id FK
    }

    UserAccessCasePolicy {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID data_collection_id FK
        UUID case_type_set_id FK
        bool is_active
        bool add_case
        bool remove_case
        bool add_case_set
        bool remove_case_set
        UUID user_id FK
        UUID read_col_set_id FK
        UUID write_col_set_id FK
        bool read_case_set
        bool write_case_set
    }

    UserShareCasePolicy {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID data_collection_id FK
        UUID case_type_set_id FK
        bool is_active
        bool add_case
        bool remove_case
        bool add_case_set
        bool remove_case_set
        UUID user_id FK
        UUID from_data_collection_id FK
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

    CaseIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    CaseDataCollectionLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID case_id FK
        UUID data_collection_id FK
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

```
