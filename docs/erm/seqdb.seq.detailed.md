# seqdb / SEQ — Detailed ERD

Auto-generated.  Service type **SEQ** — 43 entities.

```mermaid
erDiagram
    %% seqdb / SEQ (detailed)

    %% Relationships
    SampleIdentifier }o--|| Sample : "internal_id"
    TaxonSetMember }o--|| TaxonSet : "taxon_set_id"
    TaxonSetMember }o--|| Taxon : "taxon_id"
    SeqClassificationForUpload }o--|| Sample : "sample_id"
    SeqClassificationForUpload }o--|| Seq : "seq_id"
    SeqClassificationForUpload }o--|| Protocol : "protocol_id"
    SeqClassificationForUpload }o--|| SeqCategory : "primary_category_id"
    PcrMeasurement }o--|| Sample : "sample_id"
    PcrMeasurement }o--|| Protocol : "protocol_id"
    SeqTaxonomy }o--|| Sample : "sample_id"
    SeqTaxonomy }o--|| Seq : "seq_id"
    SeqTaxonomy }o--|| Protocol : "protocol_id"
    SeqTaxonomy }o--|| Taxon : "primary_taxon_id"
    SeqProfile }o--|| Sample : "sample_id"
    SeqProfile }o--|| Seq : "seq_id"
    SeqProfile }o--|| Protocol : "protocol_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    SeqIdentifier }o--|| Seq : "internal_id"
    ReadSetIdentifier }o--|| ReadSet : "internal_id"
    SampleDataCollectionLink }o--|| Sample : "sample_id"
    SeqProfileForUpload }o--|| Sample : "sample_id"
    SeqProfileForUpload }o--|| Seq : "seq_id"
    SeqProfileForUpload }o--|| Protocol : "protocol_id"
    Allele }o--|| Locus : "locus_id"
    Protocol }o--|| RefSeq : "ref_seq_id"
    Protocol }o--|| SeqCategorySet : "seq_category_set_id"
    Protocol }o--|| LocusSet : "locus_set_id"
    RefAllele }o--|| Locus : "locus_id"
    SeqCategory }o--|| SeqCategorySet : "seq_category_set_id"
    AlleleForUpload }o--|| Locus : "locus_id"
    AstPrediction }o--|| Sample : "sample_id"
    AstPrediction }o--|| Seq : "seq_id"
    AstPrediction }o--|| Protocol : "protocol_id"
    SeqDistance }o--|| Sample : "sample_id"
    SeqDistance }o--|| Protocol : "protocol_id"
    SeqDistance }o--|| SeqProfile : "seq_profile_id"
    SeqClassification }o--|| Sample : "sample_id"
    SeqClassification }o--|| Seq : "seq_id"
    SeqClassification }o--|| Protocol : "protocol_id"
    SeqClassification }o--|| SeqCategory : "primary_category_id"
    AstMeasurement }o--|| Sample : "sample_id"
    AstMeasurement }o--|| Protocol : "protocol_id"
    Seq }o--|| Sample : "sample_id"
    Seq }o--|| ReadSet : "read_set_id"
    Seq }o--|| ReadSet : "read_set2_id"
    Seq }o--|| Protocol : "protocol_id"
    ReadSetForUpload }o--|| Sample : "sample_id"
    ReadSetForUpload }o--|| Protocol : "protocol_id"
    ReadSet }o--|| Sample : "sample_id"
    ReadSet }o--|| Protocol : "protocol_id"
    SeqProfileIdentifier }o--|| SeqProfile : "internal_id"
    ProtocolSetMember }o--|| ProtocolSet : "protocol_set_id"
    ProtocolSetMember }o--|| Protocol : "protocol_id"
    RefSeq }o--|| Taxon : "taxon_id"
    SeqForUpload }o--|| Sample : "sample_id"
    SeqForUpload }o--|| ReadSet : "read_set_id"
    SeqForUpload }o--|| ReadSet : "read_set2_id"
    SeqForUpload }o--|| Protocol : "protocol_id"

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

    SampleIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    ProtocolSet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
    }

    TaxonSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID taxon_set_id FK
        UUID taxon_id FK
    }

    SeqClassificationForUpload {
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
        string protocol_code
        string primary_category_code
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

    SeqIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SampleUploadResult {
        list[EtlLogItem] logs
        UUID id
        enum status
        bool is_new
        list[UploadResult] identifiers
        list[SampleDataIssue] data_issues
        list[UploadResult] read_sets
        list[UploadResult] seqs
        list[UploadResult] seq_taxonomies
        list[UploadResult] seq_classifications
        list[UploadResult] seq_profiles
        list[UploadResult] pcr_measurements
        list[UploadResult] ast_measurements
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

    SampleDataCollectionLink {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID sample_id FK
        UUID data_collection_id FK
    }

    SeqProfileForUpload {
        list[IdentifierForUpload] identifiers
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
        string protocol_code
        string aligned_nucleotide_seq
        UUID locus_code_map_id
        string locus_code_map_code
        list[UUID] allele_ids
        dict[string, UUID] locus_allele_id_map
        list[int] repeat_numbers
        dict[string, int] locus_repeat_number_map
        dict[string, float] kmer_frequency_map
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

    SampleBatchUploadResult {
        list[EtlLogItem] logs
        UUID id PK
        enum status
        bool is_new
        UUID batch_id
        list[SampleUploadResult] samples
        list[CalculateSeqDistancesResult] seq_distances
    }

    BaseSeq {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id
        string seq
        enum seq_format
        int length
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

    CalculateSeqDistancesResult {
        list[EtlLogItem] logs
        UUID id
        enum status
        bool is_new
        UUID seq_distance_profile_id
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

    SeqCategory {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
        UUID seq_category_set_id FK
    }

    AlleleForUpload {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    PhylogeneticTree {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id
        enum tree_algorithm
        UUID protocol_id
        Protocol protocol
        list[string] leaf_names
        list[UUID] profile_ids
        string newick_repr
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
        any is_available
        any seq_hash
        any n_contigs
        any length
        any max_contig_length
        any min_contig_length
        any median_contig_length
        any n50
    }

    ReadSetForUpload {
        list[IdentifierForUpload] identifiers
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
        string protocol_code
        any is_available
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

    SeqProfileIdentifier {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    ProtocolSetMember {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        UUID protocol_set_id FK
        UUID protocol_id FK
    }

    SampleForUpload {
        list[IdentifierForUpload] identifiers
        UUID id PK
        Sample sample
        list[ReadSetForUpload] read_sets
        list[SeqForUpload] seqs
        list[SeqTaxonomy] seq_taxonomies
        list[SeqClassificationForUpload] seq_classifications
        list[SeqProfileForUpload] seq_profiles
        list[PcrMeasurement] pcr_measurements
        list[AstMeasurement] ast_measurements
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

    SeqForUpload {
        list[IdentifierForUpload] identifiers
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
        string protocol_code
        any is_available
        any seq_hash
        any n_contigs
        any length
        any max_contig_length
        any min_contig_length
        any median_contig_length
        any n50
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

    SeqCategorySet {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        string name
    }

    SampleBatchForUpload {
        UUID id PK
        timestamp created_at
        list[SampleForUpload] samples
        list[AlleleForUpload] alleles
        any has_read_sets
        any has_seqs
        any has_seq_taxonomies
        any has_seq_classifications
        any has_seq_profiles
        any has_pcr_measurements
        any has_ast_measurements
    }

    LocusCodeMap {
        timestamp created_at
        timestamp modified_at
        UUID modified_by
        UUID id PK
        string code
        dict[string, UUID] code_map
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

```
