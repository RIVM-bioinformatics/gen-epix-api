# seqdb / SEQ — Detailed ERD

Auto-generated.  Service type **SEQ** — 31 entities.

```mermaid
erDiagram
    %% seqdb / SEQ (detailed)

    %% Relationships
    RefSeq }o--|| Taxon : "taxon_id"
    TaxonSetMember }o--|| TaxonSet : "taxon_set_id"
    TaxonSetMember }o--|| Taxon : "taxon_id"
    RefAllele }o--|| Locus : "locus_id"
    Allele }o--|| Locus : "locus_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    SeqCategory }o--|| SeqCategorySet : "seq_category_set_id"
    SampleDataCollectionLink }o--|| Sample : "sample_id"
    SampleIdentifier }o--|| Sample : "internal_id"
    Protocol }o--|| RefSeq : "ref_seq_id"
    Protocol }o--|| SeqCategorySet : "seq_category_set_id"
    Protocol }o--|| LocusSet : "locus_set_id"
    ProtocolSetMember }o--|| ProtocolSet : "protocol_set_id"
    ProtocolSetMember }o--|| Protocol : "protocol_id"
    ReadSet }o--|| Sample : "sample_id"
    ReadSet }o--|| Protocol : "protocol_id"
    AstMeasurement }o--|| Sample : "sample_id"
    AstMeasurement }o--|| Protocol : "protocol_id"
    PcrMeasurement }o--|| Sample : "sample_id"
    PcrMeasurement }o--|| Protocol : "protocol_id"
    ReadSetIdentifier }o--|| ReadSet : "internal_id"
    Seq }o--|| Sample : "sample_id"
    Seq }o--|| ReadSet : "read_set_id"
    Seq }o--|| ReadSet : "read_set2_id"
    Seq }o--|| Protocol : "protocol_id"
    SeqIdentifier }o--|| Seq : "internal_id"
    SeqProfile }o--|| Sample : "sample_id"
    SeqProfile }o--|| Seq : "seq_id"
    SeqProfile }o--|| Protocol : "protocol_id"
    AstPrediction }o--|| Sample : "sample_id"
    AstPrediction }o--|| Seq : "seq_id"
    AstPrediction }o--|| Protocol : "protocol_id"
    SeqClassification }o--|| Sample : "sample_id"
    SeqClassification }o--|| Seq : "seq_id"
    SeqClassification }o--|| Protocol : "protocol_id"
    SeqClassification }o--|| SeqCategory : "primary_category_id"
    SeqTaxonomy }o--|| Sample : "sample_id"
    SeqTaxonomy }o--|| Seq : "seq_id"
    SeqTaxonomy }o--|| Protocol : "protocol_id"
    SeqTaxonomy }o--|| Taxon : "primary_taxon_id"
    SeqProfileIdentifier }o--|| SeqProfile : "internal_id"
    SeqDistance }o--|| Sample : "sample_id"
    SeqDistance }o--|| Protocol : "protocol_id"
    SeqDistance }o--|| SeqProfile : "seq_profile_id"

    %% Entity definitions
    Taxon {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        enum rank
        int ncbi_taxid
        string ictv_ictv_id
        int snomed_sctid
        list[int] ncbi_ancestor_taxids
        list[UUID] ancestor_taxon_ids
    }

    TaxonSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
    }

    Locus {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        string description
        enum locus_type
        string gene_product_code
    }

    LocusSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        list[UUID] locus_ids
        any n_loci
    }

    LocusCodeMap {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        dict[string, UUID] code_map
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

    SeqCategorySet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
    }

    ProtocolSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
    }

    Sample {
        string code
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID created_in_data_collection_id FK
        dict[string, string | int | float] props
    }

    RefSeq {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string seq
        enum seq_format
        int length
        string code
        string name
        string description
        UUID taxon_id FK
        string genbank_accession_code
    }

    TaxonSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID taxon_set_id FK
        UUID taxon_id FK
    }

    RefAllele {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
        int index
    }

    Allele {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    TreeAlgorithm {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        enum code
        string name
        string description
        UUID tree_algorithm_class_id FK
        bool is_ultrametric
        int rank
    }

    SeqCategory {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        UUID seq_category_set_id FK
    }

    SampleDataCollectionLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID sample_id FK
        UUID data_collection_id FK
    }

    SampleIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Protocol {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        string description
        enum protocol_type
        string git_repository_uri
        string git_commit_hash
        string git_commit_tag
        timestamp valid_start_datetime
        timestamp valid_end_datetime
        UUID ref_seq_id FK
        UUID seq_category_set_id FK
        UUID locus_set_id FK
        enum seq_profile_type
        enum seq_distance_type
        bool is_integer_distance
        float max_stored_distance
        dict[string, Any] props
    }

    ProtocolSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID protocol_set_id FK
        UUID protocol_id FK
    }

    ReadSet {
        enum qc_result
        float qc_score
        Json qc_report
        UUID protocol_id FK
        string code
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string fwd_uri
        string rev_uri
        UUID fwd_file_id FK
        UUID rev_file_id FK
        enum file_format
        enum file_compression
        UUID fwd_reads_hash
        UUID rev_reads_hash
        string sequencing_run_code
        any is_available
    }

    AstMeasurement {
        enum qc_result
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
    }

    PcrMeasurement {
        enum qc_result
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
    }

    ReadSetIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Seq {
        enum qc_result
        float qc_score
        Json qc_report
        string code
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string uri
        UUID file_id FK
        enum file_format
        enum file_compression
        UUID file_hash
        UUID read_set_id FK
        UUID read_set2_id FK
        UUID protocol_id FK
        list[Contig] contigs
        UUID seq_hash
        any is_available
        any n_contigs
        any length
        any max_contig_length
        any min_contig_length
        any median_contig_length
        any n50
    }

    SeqIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SeqProfile {
        enum qc_result
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID seq_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        enum seq_profile_type
    }

    AstPrediction {
        enum qc_result
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID seq_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
    }

    SeqClassification {
        enum qc_result
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID seq_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID primary_category_id FK
    }

    SeqTaxonomy {
        enum qc_result
        float qc_score
        Json qc_report
        enum format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID seq_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID primary_taxon_id FK
    }

    SeqProfileIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SeqDistance {
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID sample_id FK
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID seq_profile_id FK
    }

```
