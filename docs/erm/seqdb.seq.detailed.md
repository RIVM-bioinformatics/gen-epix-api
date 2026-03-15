# seqdb / SEQ — Detailed ERD

Auto-generated.  Service type **SEQ** — 69 entities.

```mermaid
erDiagram
    %% seqdb / SEQ (detailed)

    %% Relationships
    SeqTaxonomy }o--|| Sample : "sample_id"
    SeqTaxonomy }o--|| Seq : "seq_id"
    SeqTaxonomy }o--|| TaxonomyProtocol : "taxonomy_protocol_id"
    SeqTaxonomy }o--|| Taxon : "primary_taxon_id"
    AlleleForUpload }o--|| Locus : "locus_id"
    AlleleProfile }o--|| Sample : "sample_id"
    AlleleProfile }o--|| Seq : "seq_id"
    AlleleProfile }o--|| LocusSet : "locus_set_id"
    AlleleProfile }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    MlvaProfile }o--|| Sample : "sample_id"
    MlvaProfile }o--|| Seq : "seq_id"
    MlvaProfile }o--|| LocusSet : "locus_set_id"
    MlvaProfile }o--|| MlvaDetectionProtocol : "mlva_detection_protocol_id"
    AstMeasurement }o--|| Sample : "sample_id"
    AstMeasurement }o--|| AstProtocol : "ast_protocol_id"
    SnpProfileIdentifier }o--|| SnpProfile : "internal_id"
    SeqAlignment }o--|| Seq : "seq_id"
    SeqAlignment }o--|| AlignmentProtocol : "alignment_protocol_id"
    MlvaProfileIdentifier }o--|| MlvaProfile : "internal_id"
    Seq }o--|| Sample : "sample_id"
    Seq }o--|| ReadSet : "read_set_id"
    Seq }o--|| ReadSet : "read_set2_id"
    Seq }o--|| AssemblyProtocol : "assembly_protocol_id"
    KmerProfileForUpload }o--|| Sample : "sample_id"
    KmerProfileForUpload }o--|| Seq : "seq_id"
    KmerProfileForUpload }o--|| KmerDetectionProtocol : "kmer_detection_protocol_id"
    AlleleProfileIdentifier }o--|| AlleleProfile : "internal_id"
    SeqDistanceProtocol }o--|| LocusSet : "locus_set_id"
    SeqDistanceProtocol }o--|| RefSeq : "ref_seq_id"
    AlleleAlignment }o--|| Allele : "ref_allele_id"
    AlleleAlignment }o--|| Allele : "allele_id"
    AlleleAlignment }o--|| AlignmentProtocol : "alignment_protocol_id"
    SeqDistance }o--|| Sample : "sample_id"
    SeqDistance }o--|| SeqDistanceProtocol : "seq_distance_protocol_id"
    ReadSetIdentifier }o--|| ReadSet : "internal_id"
    SnpProfile }o--|| Sample : "sample_id"
    SnpProfile }o--|| Seq : "seq_id"
    SnpProfile }o--|| RefSeq : "ref_seq_id"
    SnpProfile }o--|| SnpDetectionProtocol : "snp_detection_protocol_id"
    ReadSetForUpload }o--|| Sample : "sample_id"
    ReadSetForUpload }o--|| SequencingProtocol : "sequencing_protocol_id"
    KmerProfileIdentifier }o--|| KmerProfile : "internal_id"
    RefSnpSetMember }o--|| RefSnpSet : "ref_snp_set_id"
    RefSnpSetMember }o--|| RefSnp : "ref_snp_id"
    AlleleProfileForUpload }o--|| Sample : "sample_id"
    AlleleProfileForUpload }o--|| Seq : "seq_id"
    AlleleProfileForUpload }o--|| LocusSet : "locus_set_id"
    AlleleProfileForUpload }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    RefSnp }o--|| RefSeq : "ref_seq_id"
    MlvaProfileForUpload }o--|| Sample : "sample_id"
    MlvaProfileForUpload }o--|| Seq : "seq_id"
    MlvaProfileForUpload }o--|| LocusSet : "locus_set_id"
    MlvaProfileForUpload }o--|| MlvaDetectionProtocol : "mlva_detection_protocol_id"
    SeqClassification }o--|| Sample : "sample_id"
    SeqClassification }o--|| Seq : "seq_id"
    SeqClassification }o--|| SeqClassificationProtocol : "seq_classification_protocol_id"
    SeqClassification }o--|| SeqCategory : "primary_category_id"
    ReadSet }o--|| Sample : "sample_id"
    ReadSet }o--|| SequencingProtocol : "sequencing_protocol_id"
    LocusProfileIdentifier }o--|| LocusProfile : "internal_id"
    SampleDataCollectionLink }o--|| Sample : "sample_id"
    SeqForUpload }o--|| Sample : "sample_id"
    SeqForUpload }o--|| ReadSet : "read_set_id"
    SeqForUpload }o--|| ReadSet : "read_set2_id"
    SeqForUpload }o--|| AssemblyProtocol : "assembly_protocol_id"
    SnpProfileForUpload }o--|| Sample : "sample_id"
    SnpProfileForUpload }o--|| Seq : "seq_id"
    SnpProfileForUpload }o--|| RefSeq : "ref_seq_id"
    SnpProfileForUpload }o--|| SnpDetectionProtocol : "snp_detection_protocol_id"
    SeqCategory }o--|| SeqCategorySet : "seq_category_set_id"
    Allele }o--|| Locus : "locus_id"
    RefSeq }o--|| Taxon : "taxon_id"
    AstPrediction }o--|| Sample : "sample_id"
    AstPrediction }o--|| Seq : "seq_id"
    AstPrediction }o--|| AstProtocol : "ast_protocol_id"
    RefAllele }o--|| Locus : "locus_id"
    KmerProfile }o--|| Sample : "sample_id"
    KmerProfile }o--|| Seq : "seq_id"
    KmerProfile }o--|| KmerDetectionProtocol : "kmer_detection_protocol_id"
    PcrMeasurement }o--|| Sample : "sample_id"
    PcrMeasurement }o--|| PcrProtocol : "pcr_protocol_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    SeqIdentifier }o--|| Seq : "internal_id"
    TaxonSetMember }o--|| TaxonSet : "taxon_set_id"
    TaxonSetMember }o--|| Taxon : "taxon_id"
    LocusProfile }o--|| Sample : "sample_id"
    LocusProfile }o--|| Seq : "seq_id"
    LocusProfile }o--|| LocusSet : "locus_set_id"
    LocusProfile }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    SampleIdentifier }o--|| Sample : "internal_id"

    %% Entity definitions
    SeqTaxonomy {
        UUID sample_id FK
        UUID id PK
        UUID seq_id FK
        UUID taxonomy_protocol_id FK
        UUID primary_taxon_id FK
        string taxonomy
        enum taxonomy_format
        UUID taxonomy_hash
    }

    AlleleForUpload {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    AlleleProfile {
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
    }

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

    AstMeasurement {
        UUID id PK
        UUID sample_id FK
        UUID ast_protocol_id FK
        string ast_result
        enum ast_result_format
        int index
    }

    SnpProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SeqAlignment {
        UUID id PK
        UUID seq_id FK
        UUID alignment_protocol_id FK
        list[ContigAlignment] contig_alignments
    }

    MlvaProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
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
    }

    LocusCodeMap {
        UUID id PK
        string code
        dict[string, UUID] code_map
    }

    KmerProfileForUpload {
        list[IdentifierForUpload] identifiers
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID kmer_detection_protocol_id FK
        string kmer_profile
        enum kmer_profile_format
        UUID kmer_profile_hash
        string kmer_detection_protocol_code
        dict[string, float] kmer_frequency_map
    }

    AlleleProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SequencingProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
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

    AlleleAlignment {
        float qc_score
        enum qc_result
        string aln
        enum aln_format
        UUID aln_hash
        UUID id PK
        UUID ref_allele_id FK
        UUID allele_id FK
        UUID alignment_protocol_id FK
    }

    SeqDistance {
        UUID sample_id FK
        UUID id PK
        UUID seq_distance_protocol_id FK
        UUID profile_id
        enum distance_format
        string distances
    }

    ReadSetIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SnpProfile {
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID ref_seq_id FK
        UUID snp_detection_protocol_id FK
        string snp_profile
        enum snp_profile_format
        UUID snp_profile_hash
    }

    AssemblyProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        bool has_manual_curation
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

    MlvaDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
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

    KmerProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    RefSnpSetMember {
        UUID id PK
        UUID ref_snp_set_id FK
        UUID ref_snp_id FK
        int index
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

    RefSnp {
        UUID id PK
        string code
        UUID ref_seq_id FK
        int position
        string nucleotide
    }

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

    LocusDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
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
    }

    LocusProfileIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    TaxonSet {
        UUID id PK
        string code
        string name
    }

    CalculateSeqDistancesResult {
        UUID id
        enum status
        bool is_new
        list[UploadLogItem] logs
        UUID seq_distance_profile_id
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

    SampleDataCollectionLink {
        UUID id PK
        UUID sample_id FK
        UUID data_collection_id FK
    }

    SeqForUpload {
        list[IdentifierForUpload] identifiers
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
        string assembly_protocol_code
        any is_available
        any seq_hash
        any n_contigs
        any length
        any max_contig_length
        any min_contig_length
        any median_contig_length
        any n50
    }

    KmerDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    PcrProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        list[string] target_names
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

    BaseSeq {
        UUID id
        string seq
        enum seq_format
        int length
    }

    SnpProfileForUpload {
        list[IdentifierForUpload] identifiers
        float qc_score
        enum qc_result
        UUID seq_id FK
        UUID sample_id FK
        UUID id PK
        UUID ref_seq_id FK
        UUID snp_detection_protocol_id FK
        string snp_profile
        enum snp_profile_format
        UUID snp_profile_hash
        string ref_seq_code
        string snp_detection_protocol_code
        string aligned_nucleotide_seq
    }

    RefSnpSet {
        UUID id PK
        string code
        string name
    }

    SeqCategory {
        UUID id PK
        string code
        string name
        UUID seq_category_set_id FK
    }

    Allele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
    }

    SampleUploadResult {
        UUID id
        enum status
        bool is_new
        list[UploadLogItem] logs
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
    }

    Sample {
        string code
        UUID id PK
        UUID created_in_data_collection_id FK
        dict[string, string | int | float] props
    }

    SeqCategorySet {
        UUID id PK
        string code
        string name
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

    SampleBatchUploadResult {
        UUID id PK
        enum status
        bool is_new
        list[UploadLogItem] logs
        UUID batch_id
        list[SampleUploadResult] samples
        list[CalculateSeqDistancesResult] seq_distances
    }

    AstPrediction {
        UUID sample_id FK
        UUID id PK
        UUID seq_id FK
        UUID ast_protocol_id FK
        string ast_result
        enum ast_result_format
    }

    RefAllele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
        int index
    }

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

    LocusSet {
        UUID id PK
        string code
        string name
        list[UUID] locus_ids
        any n_loci
    }

    PcrMeasurement {
        UUID id PK
        UUID sample_id FK
        UUID pcr_protocol_id FK
        string pcr_result
        enum pcr_result_format
        int index
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

    ContigAlignment {
        string aln
        enum aln_format
        UUID aln_hash
        UUID id
        UUID ref_seq_id
    }

    Locus {
        UUID id PK
        string code
        string name
        string description
        enum locus_type
        string gene_product_code
    }

    TreeAlgorithmClass {
        UUID id PK
        string code
        string name
        bool is_seq_based
        bool is_dist_based
        int rank
    }

    SeqIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    SnpDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    TaxonSetMember {
        UUID id PK
        UUID taxon_set_id FK
        UUID taxon_id FK
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

    SampleIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    TaxonomyProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
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

```
