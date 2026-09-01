"""Provide seqdb functionality for domain.enum."""

# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules
from __future__ import annotations

import datetime
import uuid
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, cast

import ulid

from gen_epix.commondb.domain.enum import RoleSet as RoleSet

if TYPE_CHECKING:
    from pydantic import GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core import core_schema as _cs


class IntEnumWithJsonSchemaMixin:
    """Include enum member names in generated JSON schemas for readability."""

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: _cs.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """Add enum member names to the generated Pydantic JSON schema."""
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        enum_cls = cast(type[IntEnum], cls)
        json_schema["x-enum-varnames"] = [e.name for e in enum_cls]
        return json_schema


class TimestampFactory(Enum):
    """Provide timestamp-generation strategies used by seqdb models."""

    DATETIME_NOW = lambda: datetime.datetime.now(datetime.timezone.utc)


class IdFactory(Enum):
    """Provide identifier-generation strategies used by seqdb models."""

    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid


class ServiceType(Enum):
    """Identify services available within the seqdb application."""

    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"
    SEQ = "SEQ"
    FILE = "FILE"


class RepositoryType(Enum):
    """Identify supported seqdb persistence backend implementations."""

    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class Role(Enum):
    """Define seqdb application roles for command-centric authorization."""

    ROOT = "SEQDB_ROOT"
    APP_ADMIN = "SEQDB_APP_ADMIN"
    ORG_ADMIN = "SEQDB_ORG_ADMIN"
    REFDATA_ADMIN = "SEQDB_REFDATA_ADMIN"
    ORG_USER = "SEQDB_ORG_USER"
    GUEST = "SEQDB_GUEST"
    ROLE1 = "SEQDB_ROLE1"


class TreeAlgorithm(Enum):
    """Define supported phylogenetic-tree and clustering algorithms."""

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
    """Group tree algorithms by their computational approach."""

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


class TaxonRank(Enum):
    """Define supported ranks in a taxonomic hierarchy."""

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


class QualityControlResult(IntEnumWithJsonSchemaMixin, IntEnum):
    """Represent ordered quality-control outcomes for sequence data."""

    PENDING = 1
    FAIL = 2
    WARN = 3
    PASS = 4

    def is_usable(self) -> bool:
        """Return whether this result permits downstream use of the data."""
        return self in {QualityControlResult.PASS, QualityControlResult.WARN}

    def get_sort_key(self) -> int:
        """Return an ordering key for quality-control results.

        The key equals the enum value. Higher values represent better quality, while
        ``PENDING`` is the lowest-quality temporary state.
        """
        return self.value


class QualityControlResultSet(Enum):
    """Group quality-control results into reusable result sets."""

    USABLE = frozenset(
        {
            QualityControlResult.PASS,
            QualityControlResult.WARN,
        }
    )
    ALL = frozenset(
        {
            QualityControlResult.PENDING,
            QualityControlResult.FAIL,
            QualityControlResult.WARN,
            QualityControlResult.PASS,
        }
    )


class LocusType(Enum):
    """Classify the biological feature represented by a locus."""

    GENE = "GENE"
    INTERGENIC_REGION = "INTERGENIC_REGION"
    TANDEM_REPEAT = "TANDEM_REPEAT"
    PCR = "PCR"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class SeqAlphabet(Enum):
    """Define standard sequence alphabets and their variants."""

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
    """Map a DNA ambiguity code to its represented nucleotides."""

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
    """Map a nucleotide to itself and all ambiguity codes containing it."""

    A = frozenset("arwmdhvn")
    C = frozenset("cysmbhvn")
    G = frozenset("grskbdvn")
    T = frozenset("tywkbdhn")


class SeqFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of sequence content."""

    HASH_ONLY = 1  # Only the hash code of the sequence is known or stored
    STR_DNA = 2  # String of IUPAC DNA characters without gaps
    STR_DNA_INCL_GAP = 3  # String of IUPAC DNA characters including gaps
    NEXTCLADE = 4


class SeqProfileFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of sequence profiles."""

    LOCUS_PROFILE_FORMAT1 = 1
    NEXTCLADE = 2
    ORDERED_ALLELE_IDS = 3
    ORDERED_REPEAT_NUMBERS = 4
    KMER_FREQUENCY_MAP = 5


class SeqClassificationFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of sequence classifications."""

    PRIMARY_CATEGORY_ONLY = 1


class SeqTaxonomyFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of sequence taxonomy results."""

    TAXONOMY_FORMAT1 = 1


class PcrResultFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of PCR results."""

    PCR_RESULT_FORMAT1 = 1


class AstResultFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of AST results."""

    AST_RESULT_FORMAT1 = 1


class ProtocolType(IntEnumWithJsonSchemaMixin, IntEnum):
    """Classify the laboratory or analytical purpose of a protocol."""

    PCR_MEASUREMENT = 1
    AST_MEASUREMENT = 2
    SEQUENCING = 3
    ASSEMBLY = 4
    TAXONOMY = 5
    SEQ_CLASSIFICATION = 6
    SEQ_PROFILE = 7
    SEQ_DISTANCE = 8
    AST_PREDICTION = 9


class ProtocolTypeSet(Enum):
    """Group protocol types by required reference-data relationships."""

    AST_MEASUREMENT = frozenset({ProtocolType.AST_MEASUREMENT})
    PCR_MEASUREMENT = frozenset({ProtocolType.PCR_MEASUREMENT})
    SEQUENCING = frozenset({ProtocolType.SEQUENCING})
    ASSEMBLY = frozenset({ProtocolType.ASSEMBLY})
    SEQ_CLASSIFICATION = frozenset({ProtocolType.SEQ_CLASSIFICATION})
    TAXONOMY = frozenset({ProtocolType.TAXONOMY})
    CLASSIFICATION = frozenset({ProtocolType.SEQ_CLASSIFICATION, ProtocolType.TAXONOMY})
    SEQ_PROFILE = frozenset(
        {
            ProtocolType.SEQ_PROFILE,
        }
    )
    SEQ_DISTANCE = frozenset({ProtocolType.SEQ_DISTANCE})
    HAS_REF_SEQ = frozenset()  # type: ignore[var-annotated]
    HAS_OPTIONAL_REF_SEQ = frozenset(
        {
            ProtocolType.ASSEMBLY,
            ProtocolType.SEQ_CLASSIFICATION,
            ProtocolType.SEQ_PROFILE,
            ProtocolType.SEQ_DISTANCE,
        }
    )
    HAS_SEQ_CATEGORY_SET = frozenset(
        {
            ProtocolType.SEQ_CLASSIFICATION,
        }
    )
    HAS_OPTIONAL_SEQ_CATEGORY_SET = frozenset()  # type: ignore[var-annotated]
    HAS_LOCUS_SET = frozenset()  # type: ignore[var-annotated]
    HAS_OPTIONAL_LOCUS_SET = frozenset(
        {
            ProtocolType.PCR_MEASUREMENT,
            ProtocolType.SEQ_CLASSIFICATION,
            ProtocolType.SEQ_PROFILE,
            ProtocolType.SEQ_DISTANCE,
        }
    )
    IS_SEQ_DISTANCE = frozenset({ProtocolType.SEQ_DISTANCE})


class SeqProfileType(IntEnumWithJsonSchemaMixin, IntEnum):
    """Classify the biological representation used by a sequence profile."""

    SNP = 1
    LOCUS = 2
    ALLELE = 3
    MLVA = 4
    KMER = 5


class SeqProfileTypeSet(Enum):
    """Group sequence-profile types by their required reference data."""

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


class SeqDistanceType(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported algorithms for calculating profile distances."""

    SNP_HAMMING = 1
    ALLELE_HAMMING = 2
    MLVA_HAMMING = 3
    MLVA_EUCLIDEAN = 4
    KMER_EUCLIDEAN = 5


class SeqDistanceTypeSet(Enum):
    """Group distance algorithms by profile representation and metric."""

    ALLELE_PROFILE_BASED = frozenset({SeqDistanceType.ALLELE_HAMMING})
    SNP_PROFILE_BASED = frozenset({SeqDistanceType.SNP_HAMMING})
    KMER_PROFILE_BASED = frozenset({SeqDistanceType.KMER_EUCLIDEAN})
    MLVA_PROFILE_BASED = frozenset(
        {SeqDistanceType.MLVA_HAMMING, SeqDistanceType.MLVA_EUCLIDEAN}
    )
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
            SeqDistanceType.MLVA_EUCLIDEAN,
        }
    )
    REF_SEQ_BASED = frozenset(
        {
            SeqDistanceType.SNP_HAMMING,
        }
    )


class SeqDistanceFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported serialized representations of sequence distances."""

    PROFILE_DISTANCE_MAP = 1


class ReadsFileFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported read-file formats."""

    FASTQ = 1


class SeqFileFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported assembled-sequence file formats."""

    FASTA = 2


class FileFormat(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify all supported biological file formats."""

    FASTQ = 1
    FASTA = 2


class FileCompression(IntEnumWithJsonSchemaMixin, IntEnum):
    """Identify supported compression methods for biological files."""

    NONE = 1
    GZIP = 2


class SeqRankingStrategy(Enum):
    """Define how a representative sequence is selected per sample."""

    QC_RESULT_THEN_SCORE_THEN_CREATED = "QC_RESULT_THEN_SCORE_THEN_CREATED"


class SeqProfileRankingStrategy(Enum):
    """Define how a representative profile is selected per sample."""

    QC_RESULT_THEN_SCORE_THEN_CREATED = "QC_RESULT_THEN_SCORE_THEN_CREATED"


class SeqClassificationRankingStrategy(Enum):
    """Define how a representative classification is selected per sample."""

    QC_RESULT_THEN_SCORE_THEN_CREATED = "QC_RESULT_THEN_SCORE_THEN_CREATED"
