# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules
from __future__ import annotations

import datetime
import uuid
from enum import Enum

import ulid

from gen_epix.commondb.domain.enum import RoleSet as RoleSet


class TimestampFactory(Enum):
    DATETIME_NOW = lambda: datetime.datetime.now(datetime.timezone.utc)


class IdFactory(Enum):
    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid


class ServiceType(Enum):
    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"
    SEQ = "SEQ"
    FILE = "FILE"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class Role(Enum):
    ROOT = "SEQDB_ROOT"
    APP_ADMIN = "SEQDB_APP_ADMIN"
    ORG_ADMIN = "SEQDB_ORG_ADMIN"
    REFDATA_ADMIN = "SEQDB_REFDATA_ADMIN"
    ORG_USER = "SEQDB_ORG_USER"
    GUEST = "SEQDB_GUEST"
    ROLE1 = "SEQDB_ROLE1"


class TreeAlgorithm(Enum):
    # See https://en.wikipedia.org/wiki/Hierarchical_clustering
    SLINK = "SLINK"  # Single linkage clustering
    CLINK = "CLINK"  # Complete linkage clustering
    UPGMA = "UPGMA"  # Unweighted average linkage clustering
    WPGMA = "WPGMA"  # Weighted average linkage clustering
    UPGMC = "UPGMC"  # Centroid linkage clustering
    WPGMC = "WPGMC"  # Median linkage clustering
    VERSATILE = "VERSATILE"  # Versatile linkage clustering
    MISSQ = "MISSQ"  # Ward linkage, Minimum Increase of Sum of Squares
    MNSSQ = "MNSSQ"  # Minimum Error Sum of Squares
    MIVAR = "MIVAR"  # Minimum Increase in Variance
    MNVAR = "MNVAR"  # Minimum Variance
    MINI_MAX = "MINI_MAX"  # Mini-Max linkage
    HAUSDORFF = "HAUSDORFF"  # Hausdorff linkage
    MIN_SUM_MEDOID = "MIN_SUM_MEDOID"  # Minimum Sum Medoid linkage
    MIN_SUM_INCREASE_MEDOID = (
        "MIN_SUM_INCREASE_MEDOID"  # Minimum Sum Increase Medoid linkage
    )
    MEDOID = "MEDOID"  # Medoid linkage
    MIN_ENERGY = "MIN_ENERGY"  # Minimum energy clustering
    FITCH_MARGOLIASH = "FITCH_MARGOLIASH"  # Fitch–Margoliash
    MAX_PARSIMONY = "MAX_PARSIMONY"  # Maximum parsimony
    ML = "ML"  # Maximum likelihood
    BAYESIAN_INFERENCE = "BAYESIAN_INFERENCE"  # Bayesian inference
    MIN_SPANNING = "MIN_SPANNING"  # Minimum spanning
    NJ = "NJ"  # Neighbor joining


class TreeAlgorithmSet(Enum):
    HIERARCHICAL_CLUSTERING = frozenset(
        {
            TreeAlgorithm.SLINK,
            TreeAlgorithm.CLINK,
            TreeAlgorithm.UPGMA,
            TreeAlgorithm.WPGMA,
            TreeAlgorithm.UPGMC,
            TreeAlgorithm.WPGMC,
            TreeAlgorithm.VERSATILE,
            TreeAlgorithm.MISSQ,
            TreeAlgorithm.MNSSQ,
            TreeAlgorithm.MIVAR,
            TreeAlgorithm.MNVAR,
            TreeAlgorithm.MINI_MAX,
            TreeAlgorithm.HAUSDORFF,
            TreeAlgorithm.MIN_SUM_MEDOID,
            TreeAlgorithm.MIN_SUM_INCREASE_MEDOID,
            TreeAlgorithm.MEDOID,
            TreeAlgorithm.MIN_ENERGY,
            TreeAlgorithm.FITCH_MARGOLIASH,
        }
    )
    NETWORK = frozenset({TreeAlgorithm.MIN_SPANNING})
    NJ = frozenset({TreeAlgorithm.NJ})
    PHYLOGENETIC_INFERENCE = frozenset(
        {
            TreeAlgorithm.MAX_PARSIMONY,
            TreeAlgorithm.ML,
            TreeAlgorithm.BAYESIAN_INFERENCE,
        }
    )
    DISTANCE_BASED = frozenset(
        {
            TreeAlgorithm.SLINK,
            TreeAlgorithm.CLINK,
            TreeAlgorithm.UPGMA,
            TreeAlgorithm.WPGMA,
            TreeAlgorithm.UPGMC,
            TreeAlgorithm.WPGMC,
            TreeAlgorithm.VERSATILE,
            TreeAlgorithm.MISSQ,
            TreeAlgorithm.MNSSQ,
            TreeAlgorithm.MIVAR,
            TreeAlgorithm.MNVAR,
            TreeAlgorithm.MINI_MAX,
            TreeAlgorithm.HAUSDORFF,
            TreeAlgorithm.MIN_SUM_MEDOID,
            TreeAlgorithm.MIN_SUM_INCREASE_MEDOID,
            TreeAlgorithm.MEDOID,
            TreeAlgorithm.MIN_ENERGY,
            TreeAlgorithm.FITCH_MARGOLIASH,
            TreeAlgorithm.MIN_SPANNING,
            TreeAlgorithm.NJ,
        }
    )


class Protocol(Enum):
    SEQUENCING = "SEQUENCING"
    LOCUS_DETECTION = "LOCUS_DETECTION"
    ALIGNMENT = "ALIGNMENT"
    TAXONOMY = "TAXONOMY"
    PCR = "PCR"
    AST = "AST"
    CLASSIFICATION = "CLASSIFICATION"
    SEQUENCE_DISTANCE = "SEQUENCE_DISTANCE"


class TaxonRank(Enum):
    NO_RANK = "NO_RANK"
    ACELLULAR_ROOT = "ACELLULAR_ROOT"
    REALM = "REALM"
    DOMAIN = "DOMAIN"
    SUPERKINGDOM = "SUPERKINGDOM"
    KINGDOM = "KINGDOM"
    SUBKINGDOM = "SUBKINGDOM"
    PHYLUM = "PHYLUM"
    SUBPHYLUM = "SUBPHYLUM"
    SUPERCLASS = "SUPERCLASS"
    CLASS = "CLASS"
    SUBCLASS = "SUBCLASS"
    INFRACLASS = "INFRACLASS"
    ORDER = "ORDER"
    SUBORDER = "SUBORDER"
    FAMILY = "FAMILY"
    SUBFAMILY = "SUBFAMILY"
    GENUS = "GENUS"
    SUBGENUS = "SUBGENUS"
    SPECIES_GROUP = "SPECIES_GROUP"
    SPECIES_SUBGROUP = "SPECIES_SUBGROUP"
    SPECIES = "SPECIES"
    SEROGROUP = "SEROGROUP"
    SEROTYPE = "SEROTYPE"
    BIOTYPE = "BIOTYPE"
    VARIETAS = "VARIETAS"
    FORMA_SPECIALIS = "FORMA_SPECIALIS"
    SUBSPECIES = "SUBSPECIES"
    GENOTYPE = "GENOTYPE"
    STRAIN = "STRAIN"
    CLADE = "CLADE"
    TRIBE = "TRIBE"
    ISOLATE = "ISOLATE"


class QualityControlResult(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

    def is_usable(self) -> bool:
        return self in {QualityControlResult.PASS, QualityControlResult.WARN}


class LocusType(Enum):
    GENE = "GENE"
    INTERGENIC_REGION = "INTERGENIC_REGION"
    TANDEM_REPEAT = "TANDEM_REPEAT"
    PCR = "PCR"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class SeqAlphabet(Enum):
    """
    Standard sequence alphabets and their variants.
    """

    DNA = frozenset("acgt")
    DNA_INCL_GAP = frozenset("acgt-")
    DNA_INCL_N = frozenset("acgtn")
    DNA_INCL_N_AND_GAP = frozenset("acgtn-")
    DNA_INCL_AMBIGUOUS = frozenset("acgturyswkmbdhvn")
    DNA_INCL_AMBIGUOUS_AND_GAP = frozenset("acgturyswkmbdhvn-")
    DNA_AMBIGUOUS = frozenset("uryswkmbdhvn")
    DNA_AMBIGUOUS_2 = frozenset("ryswkm")
    DNA_AMBIGUOUS_3 = frozenset("bdhv")
    DNA_AMBIGUOUS_4 = frozenset("n")
    DNA_AMBIGUOUS_2_3 = frozenset("uryswkmbdhv")
    DNA_AMBIGUOUS_2_4 = frozenset("ryswkmn")
    DNA_AMBIGUOUS_3_4 = frozenset("bdhvn")
    RNA = frozenset("acgu")
    RNA_INCL_GAP = frozenset("acgu-")
    RNA_INCL_N = frozenset("acgun")
    RNA_INCL_N_AND_GAP = frozenset("acgun-")


class DnaAmbiguityMap(Enum):
    """
    Maps an ambiguity code to the set of nucleotides it represents.
    """

    A = frozenset("a")
    C = frozenset("c")
    G = frozenset("g")
    T = frozenset("t")
    R = frozenset("ag")
    Y = frozenset("ct")
    S = frozenset("gc")
    W = frozenset("at")
    K = frozenset("gt")
    M = frozenset("ac")
    B = frozenset("cgt")
    D = frozenset("agt")
    H = frozenset("act")
    V = frozenset("acg")
    N = frozenset("acgt")


class DnaReverseAmbiguityMap(Enum):
    """
    Maps a nucleotide to itself and all ambiguity codes that include it.
    """

    A = frozenset("arwmdhvn")
    C = frozenset("cysmbhvn")
    G = frozenset("grskbdvn")
    T = frozenset("tywkbdhn")


class SeqFormat(Enum):
    HASH_ONLY = "HASH_ONLY"  # Only the hash code of the sequence is known or stored
    STR_DNA = "STR_DNA"  # String of IUPAC DNA characters without gaps
    STR_DNA_INCL_GAP = (
        "STR_DNA_INCL_GAP"  # String of IUPAC DNA characters including gaps
    )


class AlignmentFormat(Enum):
    CIGAR = "CIGAR"


class LocusProfileFormat(Enum):
    LOCUS_PROFILE_FORMAT1 = "LOCUS_PROFILE_FORMAT1"


class AlleleProfileFormat(Enum):
    SORTED_ALLELE_IDS = "SORTED_ALLELE_IDS"


class SnpProfileFormat(Enum):
    REF_ALN_SEQ = "REF_ALN_SEQ"


class MlvaProfileFormat(Enum):
    SORTED_REPEAT_NUMBERS = "SORTED_REPEAT_NUMBERS"


class KmerProfileFormat(Enum):
    KMER_FREQUENCY_MAP = "KMER_PROFILE_FORMAT1"


class SeqClassificationFormat(Enum):
    SEQ_CLASSIFICATION_FORMAT1 = "SEQ_CLASSIFICATION_FORMAT1"


class TaxonomyFormat(Enum):
    TAXONOMY_FORMAT1 = "TAXONOMY_FORMAT1"


class PcrResultFormat(Enum):
    PCR_RESULT_FORMAT1 = "PCR_RESULT_FORMAT1"


class AstResultFormat(Enum):
    AST_RESULT_FORMAT1 = "AST_RESULT_FORMAT1"


class ProtocolType(Enum):
    ALIGNMENT = "ALIGNMENT"
    ASSEMBLY = "ASSEMBLY"
    AST = "AST"
    KMER_PROFILE = "KMER_PROFILE"
    SEQUENCING = "SEQUENCING"
    ALLELE_PROFILE = "ALLELE_PROFILE"
    LOCUS_PROFILE = "LOCUS_PROFILE"
    MLVA_PROFILE = "MLVA_PROFILE"
    PCR = "PCR"
    SEQ_CLASSIFICATION = "SEQ_CLASSIFICATION"
    SEQ_DISTANCE = "SEQ_DISTANCE"
    SNP_PROFILE = "SNP_PROFILE"
    TAXONOMY = "TAXONOMY"


class ProtocolTypeSet(Enum):
    AST = frozenset({ProtocolType.AST})
    PCR = frozenset({ProtocolType.PCR})
    SEQUENCING = frozenset({ProtocolType.SEQUENCING})
    ASSEMBLY = frozenset({ProtocolType.ASSEMBLY})
    SEQ_CLASSIFICATION = frozenset({ProtocolType.SEQ_CLASSIFICATION})
    TAXONOMY = frozenset({ProtocolType.TAXONOMY})
    CLASSIFICATION = frozenset({ProtocolType.SEQ_CLASSIFICATION, ProtocolType.TAXONOMY})
    ALIGNMENT = frozenset({ProtocolType.ALIGNMENT})
    SEQ_PROFILE = frozenset(
        {
            ProtocolType.KMER_PROFILE,
            ProtocolType.ALLELE_PROFILE,
            ProtocolType.MLVA_PROFILE,
            ProtocolType.SNP_PROFILE,
            ProtocolType.LOCUS_PROFILE,
        }
    )
    SEQ_DISTANCE = frozenset({ProtocolType.SEQ_DISTANCE})
    HAS_REF_SEQ = frozenset(
        {
            ProtocolType.SNP_PROFILE,
        }
    )
    HAS_LOCUS_SET = frozenset(
        {
            ProtocolType.LOCUS_PROFILE,
            ProtocolType.ALLELE_PROFILE,
            ProtocolType.MLVA_PROFILE,
        }
    )
    IS_SEQ_DISTANCE = frozenset({ProtocolType.SEQ_DISTANCE})


class SeqProfileType(Enum):
    ALLELE = "ALLELE"
    MLVA = "MLVA"
    SNP = "SNP"
    LOCUS = "LOCUS"
    KMER = "KMER"


class SeqProfileTypeSet(Enum):
    ALLELE = frozenset({SeqProfileType.ALLELE})
    MLVA = frozenset({SeqProfileType.MLVA})
    SNP = frozenset({SeqProfileType.SNP})
    LOCUS = frozenset({SeqProfileType.LOCUS})
    KMER = frozenset({SeqProfileType.KMER})
    LOCUS_SET_BASED = frozenset(
        {
            SeqProfileType.ALLELE,
            SeqProfileType.MLVA,
            SeqProfileType.LOCUS,
        }
    )
    REF_SEQ_BASED = frozenset(
        {
            SeqProfileType.SNP,
        }
    )


class SeqDistanceType(Enum):
    ALLELE_HAMMING = "ALLELE_HAMMING"
    SNP_HAMMING = "SNP_HAMMING"
    MLVA_HAMMING = "MLVA_HAMMING"
    MLVA_EUCLIDEAN = "MLVA_EUCLIDEAN"
    KMER_EUCLIDEAN = "KMER_EUCLIDEAN"


class SeqDistanceProtocolTypeSet(Enum):
    ALLELE_PROFILE_BASED = frozenset({SeqDistanceType.ALLELE_HAMMING})
    SNP_PROFILE_BASED = frozenset({SeqDistanceType.SNP_HAMMING})
    KMER_PROFILE_BASED = frozenset({SeqDistanceType.KMER_EUCLIDEAN})
    MLVA_PROFILE_BASED = frozenset({SeqDistanceType.MLVA_HAMMING})
    HAMMING_DISTANCE_BASED = frozenset(
        {
            SeqDistanceType.ALLELE_HAMMING,
            SeqDistanceType.SNP_HAMMING,
            SeqDistanceType.MLVA_HAMMING,
        }
    )
    EUCLIDEAN_DISTANCE_BASED = frozenset(
        {SeqDistanceType.KMER_EUCLIDEAN, SeqDistanceType.MLVA_EUCLIDEAN}
    )
    LOCUS_SET_BASED = frozenset(
        {
            SeqDistanceType.ALLELE_HAMMING,
            SeqDistanceType.MLVA_HAMMING,
        }
    )
    REF_SEQ_BASED = frozenset(
        {
            SeqDistanceType.SNP_HAMMING,
        }
    )


class SeqDistanceResultFormat(Enum):
    SEQ_DISTANCE_RESULT_FORMAT1 = "SEQ_DISTANCE_RESULT_FORMAT1"


class SeqDistanceFormat(Enum):
    PROFILE_DISTANCE_MAP = "PROFILE_DISTANCE_MAP"


class SeqFileFormat(Enum):
    FASTA = "FASTA"


class ReadsFileFormat(Enum):
    FASTQ = "FASTQ"


class FileFormat(Enum):
    FASTA = "FASTA"
    FASTQ = "FASTQ"


class FileCompression(Enum):
    NONE = "NONE"
    GZIP = "GZIP"
