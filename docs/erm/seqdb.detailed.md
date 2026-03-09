# seqdb — Detailed Entity-Relationship Diagram

Auto-generated from domain model definitions.  Contains **62** persistable entities with their field definitions.

```mermaid
erDiagram
    %% seqdb — all persistable entities (detailed)

    %% Relationships
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
    ExternalIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    Site }o--|| Organization : "organization_id"
    Contact }o--|| Site : "site_id"
    User }o--|| Organization : "organization_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    OrganizationAdminPolicy }o--|| Organization : "organization_id"
    OrganizationAdminPolicy }o--|| User : "user_id"
    TaxonSetMember }o--|| TaxonSet : "taxon_set_id"
    TaxonSetMember }o--|| Taxon : "taxon_id"
    RefSeq }o--|| Taxon : "taxon_id"
    RefAllele }o--|| Locus : "locus_id"
    RefSnp }o--|| RefSeq : "ref_seq_id"
    RefSnpSetMember }o--|| RefSnpSet : "ref_snp_set_id"
    RefSnpSetMember }o--|| RefSnp : "ref_snp_id"
    SeqDistanceProtocol }o--|| LocusSet : "locus_set_id"
    SeqDistanceProtocol }o--|| RefSeq : "ref_seq_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    SeqCategory }o--|| SeqCategorySet : "seq_category_set_id"
    Sample }o--|| DataCollection : "created_in_data_collection_id"
    SampleDataCollectionLink }o--|| Sample : "sample_id"
    SampleDataCollectionLink }o--|| DataCollection : "data_collection_id"
    SampleIdentifier }o--|| Sample : "sample_id"
    SampleIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    ReadSet }o--|| Sample : "sample_id"
    ReadSet }o--|| SequencingProtocol : "sequencing_protocol_id"
    ReadSet }o--|| File : "fwd_file_id"
    ReadSet }o--|| File : "rev_file_id"
    Seq }o--|| Sample : "sample_id"
    Seq }o--|| File : "file_id"
    Seq }o--|| ReadSet : "read_set_id"
    Seq }o--|| ReadSet : "read_set2_id"
    Seq }o--|| AssemblyProtocol : "assembly_protocol_id"
    Allele }o--|| Locus : "locus_id"
    LocusProfile }o--|| Sample : "sample_id"
    LocusProfile }o--|| Seq : "seq_id"
    LocusProfile }o--|| LocusSet : "locus_set_id"
    LocusProfile }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    AlleleProfile }o--|| Sample : "sample_id"
    AlleleProfile }o--|| Seq : "seq_id"
    AlleleProfile }o--|| LocusSet : "locus_set_id"
    AlleleProfile }o--|| LocusDetectionProtocol : "locus_detection_protocol_id"
    KmerProfile }o--|| Sample : "sample_id"
    KmerProfile }o--|| Seq : "seq_id"
    KmerProfile }o--|| KmerDetectionProtocol : "kmer_detection_protocol_id"
    MlvaProfile }o--|| Sample : "sample_id"
    MlvaProfile }o--|| Seq : "seq_id"
    MlvaProfile }o--|| LocusSet : "locus_set_id"
    MlvaProfile }o--|| MlvaDetectionProtocol : "mlva_detection_protocol_id"
    SnpProfile }o--|| Sample : "sample_id"
    SnpProfile }o--|| Seq : "seq_id"
    SnpProfile }o--|| RefSeq : "ref_seq_id"
    SnpProfile }o--|| SnpDetectionProtocol : "snp_detection_protocol_id"
    AstMeasurement }o--|| Sample : "sample_id"
    AstMeasurement }o--|| AstProtocol : "ast_protocol_id"
    AstPrediction }o--|| Sample : "sample_id"
    AstPrediction }o--|| Seq : "seq_id"
    AstPrediction }o--|| AstProtocol : "ast_protocol_id"
    PcrMeasurement }o--|| Sample : "sample_id"
    PcrMeasurement }o--|| PcrProtocol : "pcr_protocol_id"
    SeqAlignment }o--|| Seq : "seq_id"
    SeqAlignment }o--|| AlignmentProtocol : "alignment_protocol_id"
    AlleleAlignment }o--|| Allele : "ref_allele_id"
    AlleleAlignment }o--|| Allele : "allele_id"
    AlleleAlignment }o--|| AlignmentProtocol : "alignment_protocol_id"
    SeqClassification }o--|| Sample : "sample_id"
    SeqClassification }o--|| Seq : "seq_id"
    SeqClassification }o--|| SeqClassificationProtocol : "seq_classification_protocol_id"
    SeqClassification }o--|| SeqCategory : "primary_category_id"
    SeqDistance }o--|| Sample : "sample_id"
    SeqDistance }o--|| SeqDistanceProtocol : "seq_distance_protocol_id"
    SeqTaxonomy }o--|| Sample : "sample_id"
    SeqTaxonomy }o--|| Seq : "seq_id"
    SeqTaxonomy }o--|| TaxonomyProtocol : "taxonomy_protocol_id"
    SeqTaxonomy }o--|| Taxon : "primary_taxon_id"

    %% Entity definitions
    Outage {
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
        UUID id PK
        string name
        string legal_entity_code
    }

    OrganizationSet {
        UUID id PK
        string name
        string description
    }

    OrganizationSetMember {
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

    DataCollection {
        UUID id PK
        string name
        string description
    }

    DataCollectionSet {
        UUID id PK
        string name
        string description
    }

    DataCollectionSetMember {
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

    IdentifierIssuer {
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationIdentifierIssuerLink {
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    ExternalIdentifier {
        UUID id PK
        enum identifier_type
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id
    }

    Site {
        UUID id PK
        UUID organization_id FK
        string name
    }

    Contact {
        UUID id PK
        UUID site_id FK
        string name
        string email
        string phone
    }

    User {
        UUID id PK
        string key
        string email
        string name
        bool is_active
        set[string] roles
        UUID organization_id FK
    }

    UserInvitation {
        UUID id PK
        string key
        string email
        string name
        string token
        timestamp expires_at
        set[string] roles
        UUID invited_by_user_id FK
        UUID organization_id FK
    }

    OrganizationAdminPolicy {
        UUID id PK
        UUID organization_id FK
        UUID user_id FK
        bool is_active
    }

    File {
        UUID id PK
        bytes content
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

    TaxonSet {
        UUID id PK
        string code
        string name
    }

    TaxonSetMember {
        UUID id PK
        UUID taxon_set_id FK
        UUID taxon_id FK
    }

    Locus {
        UUID id PK
        string code
        string name
        string description
        enum locus_type
        string gene_product_code
    }

    LocusSet {
        UUID id PK
        string code
        string name
        list[UUID] locus_ids
        any n_loci
    }

    LocusCodeMap {
        UUID id PK
        string code
        dict[string, UUID] code_map
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

    RefAllele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
        int index
    }

    RefSnp {
        UUID id PK
        string code
        UUID ref_seq_id FK
        int position
        string nucleotide
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

    AlignmentProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        bool is_multiple
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

    KmerDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    SequencingProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    LocusDetectionProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
    }

    MlvaDetectionProtocol {
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

    SeqClassificationProtocol {
        string code
        string name
        string version
        string description
        dict[string, string] props
        UUID id PK
        bool is_taxonomic
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

    SnpDetectionProtocol {
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

    TreeAlgorithmClass {
        UUID id PK
        string code
        string name
        bool is_seq_based
        bool is_dist_based
        int rank
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

    SeqCategorySet {
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

    Sample {
        string code
        UUID id PK
        UUID created_in_data_collection_id FK
        dict[string, string | int | float] props
    }

    SampleDataCollectionLink {
        UUID id PK
        UUID sample_id FK
        UUID data_collection_id FK
    }

    SampleIdentifier {
        UUID id PK
        UUID sample_id FK
        UUID identifier_issuer_id FK
        string identifier
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

    Allele {
        UUID id PK
        string seq
        enum seq_format
        int length
        UUID locus_id FK
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

    AstMeasurement {
        UUID id PK
        UUID sample_id FK
        UUID ast_protocol_id FK
        string ast_result
        enum ast_result_format
        int index
    }

    AstPrediction {
        UUID sample_id FK
        UUID id PK
        UUID seq_id FK
        UUID ast_protocol_id FK
        string ast_result
        enum ast_result_format
    }

    PcrMeasurement {
        UUID id PK
        UUID sample_id FK
        UUID pcr_protocol_id FK
        string pcr_result
        enum pcr_result_format
        int index
    }

    SeqAlignment {
        UUID id PK
        UUID seq_id FK
        UUID alignment_protocol_id FK
        list[ContigAlignment] contig_alignments
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

    SeqDistance {
        UUID sample_id FK
        UUID id PK
        UUID seq_distance_protocol_id FK
        UUID profile_id
        enum distance_format
        string distances
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
    }

```
