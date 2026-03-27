# seqdb / SEQ — Detailed ERD

Auto-generated.  Service type **SEQ** — 43 entities.

```mermaid
erDiagram
    %% seqdb / SEQ (detailed)

    %% Relationships
<<<<<<< HEAD
    MlvaProfileForUpload }o--|| Sample : "sample_id"
    MlvaProfileForUpload }o--|| Seq : "seq_id"
    MlvaProfileForUpload }o--|| LocusSet : "locus_set_id"
    MlvaProfileForUpload }o--|| MlvaDetectionProtocol : "mlva_detection_protocol_id"
    ReadSetIdentifier }o--|| ReadSet : "internal_id"
    KmerProfileIdentifier }o--|| KmerProfile : "internal_id"
    LocusProfileIdentifier }o--|| LocusProfile : "internal_id"
    SampleDataCollectionLink }o--|| Sample : "sample_id"
    RefSnp }o--|| RefSeq : "ref_seq_id"
    ReadSetForUpload }o--|| Sample : "sample_id"
    ReadSetForUpload }o--|| SequencingProtocol : "sequencing_protocol_id"
    AlleleProfile }o--|| Sample : "sample_id"
    AlleleProfile }o--|| Seq : "seq_id"
    AlleleProfile }o--|| LocusSet : "locus_set_id"
    AlleleProfile }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    SeqIdentifier }o--|| Seq : "internal_id"
    RefSeq }o--|| Taxon : "taxon_id"
    SnpProfile }o--|| Sample : "sample_id"
    SnpProfile }o--|| Seq : "seq_id"
    SnpProfile }o--|| RefSeq : "ref_seq_id"
    SnpProfile }o--|| SnpDetectionProtocol : "snp_detection_protocol_id"
    SeqDistance }o--|| Sample : "sample_id"
    SeqDistance }o--|| SeqDistanceProtocol : "seq_distance_protocol_id"
    AstMeasurement }o--|| Sample : "sample_id"
    AstMeasurement }o--|| AstProtocol : "ast_protocol_id"
    KmerProfileForUpload }o--|| Sample : "sample_id"
    KmerProfileForUpload }o--|| Seq : "seq_id"
    KmerProfileForUpload }o--|| KmerDetectionProtocol : "kmer_detection_protocol_id"
    MlvaProfileIdentifier }o--|| MlvaProfile : "internal_id"
    Allele }o--|| Locus : "locus_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    AlleleAlignment }o--|| Allele : "ref_allele_id"
    AlleleAlignment }o--|| Allele : "allele_id"
    AlleleAlignment }o--|| AlignmentProtocol : "alignment_protocol_id"
    AlleleProfileIdentifier }o--|| AlleleProfile : "internal_id"
    PcrMeasurement }o--|| Sample : "sample_id"
    PcrMeasurement }o--|| PcrProtocol : "pcr_protocol_id"
    SeqForUpload }o--|| Sample : "sample_id"
    SeqForUpload }o--|| ReadSet : "read_set_id"
    SeqForUpload }o--|| ReadSet : "read_set2_id"
    SeqForUpload }o--|| AssemblyProtocol : "assembly_protocol_id"
    LocusProfile }o--|| Sample : "sample_id"
    LocusProfile }o--|| Seq : "seq_id"
    LocusProfile }o--|| LocusSet : "locus_set_id"
    LocusProfile }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    SnpProfileIdentifier }o--|| SnpProfile : "internal_id"
    SeqClassification }o--|| Sample : "sample_id"
    SeqClassification }o--|| Seq : "seq_id"
    SeqClassification }o--|| SeqClassificationProtocol : "seq_classification_protocol_id"
    SeqClassification }o--|| SeqCategory : "primary_category_id"
    SampleIdentifier }o--|| Sample : "internal_id"
    RefSnpSetMember }o--|| RefSnpSet : "ref_snp_set_id"
    RefSnpSetMember }o--|| RefSnp : "ref_snp_id"
    SeqDistanceProtocol }o--|| LocusSet : "locus_set_id"
    SeqDistanceProtocol }o--|| RefSeq : "ref_seq_id"
    AlleleProfileForUpload }o--|| Sample : "sample_id"
    AlleleProfileForUpload }o--|| Seq : "seq_id"
    AlleleProfileForUpload }o--|| LocusSet : "locus_set_id"
    AlleleProfileForUpload }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    SnpProfileForUpload }o--|| Sample : "sample_id"
    SnpProfileForUpload }o--|| Seq : "seq_id"
    SnpProfileForUpload }o--|| RefSeq : "ref_seq_id"
    SnpProfileForUpload }o--|| SnpDetectionProtocol : "snp_detection_protocol_id"
    ReadSet }o--|| Sample : "sample_id"
    ReadSet }o--|| SequencingProtocol : "sequencing_protocol_id"
    SeqTaxonomy }o--|| Sample : "sample_id"
    SeqTaxonomy }o--|| Seq : "seq_id"
    SeqTaxonomy }o--|| TaxonomyProtocol : "taxonomy_protocol_id"
    SeqTaxonomy }o--|| Taxon : "primary_taxon_id"
    KmerProfile }o--|| Sample : "sample_id"
    KmerProfile }o--|| Seq : "seq_id"
    KmerProfile }o--|| KmerDetectionProtocol : "kmer_detection_protocol_id"
    RefAllele }o--|| Locus : "locus_id"
    TaxonSetMember }o--|| TaxonSet : "taxon_set_id"
    TaxonSetMember }o--|| Taxon : "taxon_id"
    SeqCategory }o--|| SeqCategorySet : "seq_category_set_id"
    MlvaProfile }o--|| Sample : "sample_id"
    MlvaProfile }o--|| Seq : "seq_id"
    MlvaProfile }o--|| LocusSet : "locus_set_id"
    MlvaProfile }o--|| MlvaDetectionProtocol : "mlva_detection_protocol_id"
    Seq }o--|| Sample : "sample_id"
    Seq }o--|| ReadSet : "read_set_id"
    Seq }o--|| ReadSet : "read_set2_id"
    Seq }o--|| AssemblyProtocol : "assembly_protocol_id"
    SeqAlignment }o--|| Seq : "seq_id"
    SeqAlignment }o--|| AlignmentProtocol : "alignment_protocol_id"
    AlleleForUpload }o--|| Locus : "locus_id"
    AstPrediction }o--|| Sample : "sample_id"
    AstPrediction }o--|| Seq : "seq_id"
    AstPrediction }o--|| AstProtocol : "ast_protocol_id"

    %% Entity definitions
    MlvaProfileForUpload {
        list[IdentifierForUpload] identifiers
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID mlva_detection_protocol_id FK
        UUID locus_set_id FK
        string mlva_profile
        enum mlva_profile_format
        UUID mlva_profile_hash
        string mlva_detection_protocol_code
        string locus_set_code
        UUID locus_code_map_id
        string locus_code_map_code
        list[int] repeat_numbers
        dict[string, int] locus_repeat_number_map
    }

    LocusSet {
        UUID id PK
        string code
        string name
        list[UUID] locus_ids
        any n_loci
    }

    ReadSetIdentifier {
=======
    ReadSetForUpload }o--|| Sample : "sample_id"
    ReadSetForUpload }o--|| Protocol : "protocol_id"
    Allele }o--|| Locus : "locus_id"
    TaxonSetMember }o--|| TaxonSet : "taxon_set_id"
    TaxonSetMember }o--|| Taxon : "taxon_id"
    PcrMeasurement }o--|| Sample : "sample_id"
    PcrMeasurement }o--|| Protocol : "protocol_id"
    ReadSetIdentifier }o--|| ReadSet : "internal_id"
    AstMeasurement }o--|| Sample : "sample_id"
    AstMeasurement }o--|| Protocol : "protocol_id"
    SeqIdentifier }o--|| Seq : "internal_id"
    AstPrediction }o--|| Sample : "sample_id"
    AstPrediction }o--|| Seq : "seq_id"
    AstPrediction }o--|| Protocol : "protocol_id"
    SeqClassification }o--|| Sample : "sample_id"
    SeqClassification }o--|| Seq : "seq_id"
    SeqClassification }o--|| Protocol : "protocol_id"
    SeqClassification }o--|| SeqCategory : "primary_category_id"
    SeqProfileForUpload }o--|| Sample : "sample_id"
    SeqProfileForUpload }o--|| Seq : "seq_id"
    SeqProfileForUpload }o--|| Protocol : "protocol_id"
    SeqDistance }o--|| Sample : "sample_id"
    SeqDistance }o--|| Protocol : "protocol_id"
    SeqDistance }o--|| SeqProfile : "seq_profile_id"
    ProtocolSetMember }o--|| ProtocolSet : "protocol_set_id"
    ProtocolSetMember }o--|| Protocol : "protocol_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    SeqClassificationForUpload }o--|| Sample : "sample_id"
    SeqClassificationForUpload }o--|| Seq : "seq_id"
    SeqClassificationForUpload }o--|| Protocol : "protocol_id"
    SeqClassificationForUpload }o--|| SeqCategory : "primary_category_id"
    Protocol }o--|| RefSeq : "ref_seq_id"
    Protocol }o--|| SeqCategorySet : "seq_category_set_id"
    Protocol }o--|| LocusSet : "locus_set_id"
    RefAllele }o--|| Locus : "locus_id"
    AlleleForUpload }o--|| Locus : "locus_id"
    SeqForUpload }o--|| Sample : "sample_id"
    SeqForUpload }o--|| ReadSet : "read_set_id"
    SeqForUpload }o--|| ReadSet : "read_set2_id"
    SeqForUpload }o--|| Protocol : "protocol_id"
    SeqCategory }o--|| SeqCategorySet : "seq_category_set_id"
    SeqTaxonomy }o--|| Sample : "sample_id"
    SeqTaxonomy }o--|| Seq : "seq_id"
    SeqTaxonomy }o--|| Protocol : "protocol_id"
    SeqTaxonomy }o--|| Taxon : "primary_taxon_id"
    SampleIdentifier }o--|| Sample : "internal_id"
    SampleDataCollectionLink }o--|| Sample : "sample_id"
    Seq }o--|| Sample : "sample_id"
    Seq }o--|| ReadSet : "read_set_id"
    Seq }o--|| ReadSet : "read_set2_id"
    Seq }o--|| Protocol : "protocol_id"
    SeqProfile }o--|| Sample : "sample_id"
    SeqProfile }o--|| Seq : "seq_id"
    SeqProfile }o--|| Protocol : "protocol_id"
    SeqProfileIdentifier }o--|| SeqProfile : "internal_id"
    ReadSet }o--|| Sample : "sample_id"
    ReadSet }o--|| Protocol : "protocol_id"
    RefSeq }o--|| Taxon : "taxon_id"

    %% Entity definitions
    ReadSetForUpload {
        list[IdentifierForUpload] identifiers
        enum qc_result
        float qc_score
        Json qc_report
        string code
        UUID sample_id FK
        UUID id PK
        UUID protocol_id FK
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

    Locus {
        UUID id PK
        string code
        string name
        string description
        enum locus_type
        string gene_product_code
    }

    Allele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    BaseSeq {
        UUID id
        string seq
        enum seq_format
        int length
    }

    LocusSet {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        UUID id PK
        string code
        string name
        list[UUID] locus_ids
        any n_loci
    }

<<<<<<< HEAD
    KmerProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    LocusProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SampleDataCollectionLink {
        UUID id PK
        UUID sample_id FK
        UUID data_collection_id FK
    }

    RefSnp {
        UUID id PK
        string code
        UUID ref_seq_id FK
        int position
        string nucleotide
    }

    ReadSetForUpload {
        list[IdentifierForUpload] identifiers
        float qc_score
        enum qc_result
        string code
        UUID sample_id FK
        UUID id PK
        UUID sequencing_protocol_id FK
        string fwd_uri
        string rev_uri
        UUID fwd_file_id FK
        UUID rev_file_id FK
        enum file_format
        enum file_compression
        UUID fwd_reads_hash
        UUID rev_reads_hash
        string sequencing_run_code
        string sequencing_protocol_code
        any is_available
    }

    AlleleProfile {
=======
    SeqCategorySet {
        UUID id PK
        string code
        string name
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

    TaxonSetMember {
        UUID id PK
        UUID taxon_set_id FK
        UUID taxon_id FK
    }

    PcrMeasurement {
        enum qc_result
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID sample_id FK
        UUID id PK
<<<<<<< HEAD
        UUID locus_set_id FK
        UUID locus_detection_protocol_id FK
        int n_loci
        string allele_profile
        enum allele_profile_format
        UUID allele_profile_hash
    }

    SeqIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    LocusCodeMap {
        UUID id PK
        string code
        dict[string, UUID] code_map
    }

    AlignmentProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        bool is_multiple
    }

    MultipleAlignment {
        UUID id
        UUID alignment_protocol_id
        list[UUID] seq_ids
        int n_seqs
        list[int] n_contigs
        list[list[string]] contig_seqs
        int n_alignments
        list[int] n_columns
        list[list[int]] start_columns
        list[list[int]] contig_ordinals
        list[list[int]] contig_start_positions
        list[list[bool]] contig_directions
        list[list[int]] lengths
=======
    }

    Sample {
        string code
        UUID id PK
        UUID created_in_data_collection_id FK
        dict[string, string | int | float] props
    }

    TaxonSet {
        UUID id PK
        string code
        string name
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    RefSeq {
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

    AstMeasurement {
        enum qc_result
<<<<<<< HEAD
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID ref_seq_id FK
        UUID snp_detection_protocol_id FK
        string snp_profile
        enum snp_profile_format
        UUID snp_profile_hash
    }

    AstProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        bool is_predicted
        list[string] antimicrobial_names
    }

    SeqDistance {
        UUID sample_id FK
        UUID id PK
        UUID seq_distance_protocol_id FK
        UUID profile_id
        enum distance_format
        string distances
    }

    AstMeasurement {
        UUID id PK
        UUID sample_id FK
        UUID ast_protocol_id FK
        string ast_result
        enum ast_result_format
        int index
    }

    KmerProfileForUpload {
=======
        float qc_score
        Json qc_report
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID sample_id FK
        UUID id PK
    }

    SeqIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
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
        UUID id PK
        UUID primary_category_id FK
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

    SeqProfileForUpload {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
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
        UUID id PK
<<<<<<< HEAD
        UUID kmer_detection_protocol_id FK
        string kmer_profile
        enum kmer_profile_format
        UUID kmer_profile_hash
        string kmer_detection_protocol_code
        dict[string, float] kmer_frequency_map
    }

    PcrProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        list[string] target_names
=======
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

    SeqDistance {
        FormatType format
        UUID content_hash
        string content
        string content2
        UUID protocol_id FK
        UUID sample_id FK
        UUID id PK
        UUID seq_profile_id FK
    }

    ProtocolSetMember {
        UUID id PK
        UUID protocol_set_id FK
        UUID protocol_id FK
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    TreeAlgorithm {
        UUID id PK
        enum code
        string name
        string description
        UUID tree_algorithm_class_id FK
        bool is_ultrametric
        int rank
    }

<<<<<<< HEAD
    Locus {
        UUID id PK
        string code
        string name
        string description
        enum locus_type
        string gene_product_code
    }

    SeqClassificationProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        bool is_taxonomic
    }

    MlvaProfileIdentifier {
=======
    LocusCodeMap {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        UUID id PK
        string code
        dict[string, UUID] code_map
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
        UUID id PK
        UUID primary_category_id FK
        string protocol_code
        string primary_category_code
    }

<<<<<<< HEAD
    Allele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    TreeAlgorithm {
        UUID id PK
        enum code
        string name
        string description
        UUID tree_algorithm_class_id FK
        bool is_ultrametric
        int rank
    }

    AlleleAlignment {
        float qc_score
        enum qc_result
        string aln
        enum aln_format
        UUID aln_hash
=======
    Taxon {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        UUID id PK
        UUID ref_allele_id FK
        UUID allele_id FK
        UUID alignment_protocol_id FK
    }

    MlvaDetectionProtocol {
        string code
        string name
<<<<<<< HEAD
        string version
        string description
        dict[string, string] props
        UUID id PK
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
        list[UploadResult] locus_profiles
        list[UploadResult] allele_profiles
        list[UploadResult] snp_profiles
        list[UploadResult] mlva_profiles
        list[UploadResult] kmer_profiles
        list[UploadResult] pcr_measurements
        list[UploadResult] ast_measurements
=======
        enum rank
        int ncbi_taxid
        string ictv_ictv_id
        int snomed_sctid
        list[int] ncbi_ancestor_taxids
        list[UUID] ancestor_taxon_ids
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    CalculateSeqDistancesResult {
        list[EtlLogItem] logs
        UUID id
        enum status
        bool is_new
        UUID seq_distance_profile_id
    }

<<<<<<< HEAD
    Taxon {
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

    AlleleProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    PcrMeasurement {
        UUID id PK
        UUID sample_id FK
        UUID pcr_protocol_id FK
        string pcr_result
        enum pcr_result_format
        int index
=======
    PhylogeneticTree {
        UUID id
        enum tree_algorithm
        UUID protocol_id
        Protocol protocol
        list[string] leaf_names
        list[UUID] profile_ids
        string newick_repr
    }

    Protocol {
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

    RefAllele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
        int index
    }

    AlleleForUpload {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    SeqForUpload {
        list[IdentifierForUpload] identifiers
        enum qc_result
        float qc_score
        Json qc_report
        string code
        UUID sample_id FK
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

<<<<<<< HEAD
    LocusProfile {
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID locus_set_id FK
        UUID locus_detection_protocol_id FK
        int n_loci
        string locus_profile
        enum locus_profile_format
        UUID locus_profile_hash
    }

    SnpDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    SnpProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    TreeAlgorithmClass {
        UUID id PK
        string code
        string name
        bool is_seq_based
        bool is_dist_based
        int rank
    }

    PhylogeneticTree {
        UUID id
        enum tree_algorithm
        UUID seq_distance_protocol_id
        SeqDistanceProtocol seq_distance_protocol
        list[string] leaf_names
        list[UUID] profile_ids
        string newick_repr
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
        any has_locus_profiles
        any has_allele_profiles
        any has_snp_profiles
        any has_mlva_profiles
        any has_kmer_profiles
        any has_pcr_measurements
        any has_ast_measurements
    }

    SeqClassification {
        UUID sample_id FK
        UUID id PK
        UUID seq_id FK
        UUID seq_classification_protocol_id FK
        UUID primary_category_id FK
        string classification
        enum classification_format
        UUID classification_hash
    }

    SampleIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Sample {
        string code
        UUID id PK
        UUID created_in_data_collection_id FK
        dict[string, string | int | float] props
    }

    RefSnpSet {
        UUID id PK
        string code
        string name
    }

    RefSnpSetMember {
        UUID id PK
        UUID ref_snp_set_id FK
        UUID ref_snp_id FK
        int index
    }

    SeqDistanceProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        enum seq_distance_protocol_type
        UUID locus_set_id FK
        UUID ref_seq_id FK
        bool is_integer_distance
        float max_stored_distance
    }

    AlleleProfileForUpload {
        list[IdentifierForUpload] identifiers
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID locus_set_id FK
        UUID locus_detection_protocol_id FK
        int n_loci
        string allele_profile
        enum allele_profile_format
        UUID allele_profile_hash
        string locus_detection_protocol_code
        string locus_set_code
        UUID locus_code_map_id
        string locus_code_map_code
        list[UUID] allele_ids
        dict[string, UUID] locus_allele_id_map
    }

    TaxonSet {
        UUID id PK
        string code
        string name
=======
    SeqCategory {
        UUID id PK
        string code
        string name
        UUID seq_category_set_id FK
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
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
        UUID id PK
        UUID primary_taxon_id FK
    }

<<<<<<< HEAD
    BaseSeq {
        UUID id
        string seq
        enum seq_format
        int length
=======
    ProtocolSet {
        UUID id PK
        string code
        string name
    }

    SampleIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SampleDataCollectionLink {
        UUID id PK
        UUID sample_id FK
        UUID data_collection_id FK
    }

    Seq {
        enum qc_result
        float qc_score
        Json qc_report
        string code
        UUID sample_id FK
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
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
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
        UUID id PK
        enum seq_profile_type
    }

<<<<<<< HEAD
    ReadSet {
        float qc_score
        enum qc_result
        string code
        UUID sample_id FK
        UUID id PK
        UUID sequencing_protocol_id FK
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

    SeqTaxonomy {
        UUID sample_id FK
        UUID id PK
        UUID seq_id FK
        UUID taxonomy_protocol_id FK
        UUID primary_taxon_id FK
        string taxonomy
        enum taxonomy_format
        UUID taxonomy_hash
=======
    SeqProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
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

<<<<<<< HEAD
    KmerProfile {
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID kmer_detection_protocol_id FK
        string kmer_profile
        enum kmer_profile_format
        UUID kmer_profile_hash
    }

    RefAllele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
        int index
    }

    SampleForUpload {
        list[IdentifierForUpload] identifiers
        UUID id PK
        Sample sample
        list[ReadSetForUpload] read_sets
        list[SeqForUpload] seqs
        list[SeqTaxonomy] seq_taxonomies
        list[SeqClassification] seq_classifications
        list[LocusProfile] locus_profiles
        list[AlleleProfileForUpload] allele_profiles
        list[SnpProfileForUpload] snp_profiles
        list[MlvaProfileForUpload] mlva_profiles
        list[KmerProfileForUpload] kmer_profiles
        list[PcrMeasurement] pcr_measurements
        list[AstMeasurement] ast_measurements
    }

    TaxonSetMember {
        UUID id PK
        UUID taxon_set_id FK
        UUID taxon_id FK
    }

    SeqCategory {
        UUID id PK
        string code
        string name
        UUID seq_category_set_id FK
    }

    MlvaProfile {
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID mlva_detection_protocol_id FK
        UUID locus_set_id FK
        string mlva_profile
        enum mlva_profile_format
        UUID mlva_profile_hash
    }

    ContigAlignment {
        string aln
        enum aln_format
        UUID aln_hash
        UUID id
        UUID ref_seq_id
    }

    Seq {
        float qc_score
        enum qc_result
        string code
        UUID sample_id FK
        UUID id PK
        string uri
        UUID file_id FK
        enum file_format
        enum file_compression
        UUID file_hash
        UUID read_set_id FK
        UUID read_set2_id FK
        UUID assembly_protocol_id FK
        list[Contig] contigs
        any is_available
        any seq_hash
        any n_contigs
        any length
        any max_contig_length
        any min_contig_length
        any median_contig_length
        any n50
=======
    ReadSet {
        enum qc_result
        float qc_score
        Json qc_report
        string code
        UUID sample_id FK
        UUID id PK
        UUID protocol_id FK
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
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    SeqAlignment {
        UUID id PK
        UUID seq_id FK
        UUID alignment_protocol_id FK
        list[ContigAlignment] contig_alignments
    }

<<<<<<< HEAD
    AlleleForUpload {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    KmerDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    TaxonomyProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    AstPrediction {
        UUID sample_id FK
        UUID id PK
        UUID seq_id FK
        UUID ast_protocol_id FK
        string ast_result
        enum ast_result_format
    }

    SequencingProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    AssemblyProtocol {
=======
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
        UUID id PK
        string seq
        enum seq_format
        int length
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
        string code
        string name
        string description
<<<<<<< HEAD
        dict[string, string] props
        UUID id PK
        bool has_manual_curation
=======
        UUID taxon_id FK
        string genbank_accession_code
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

```
