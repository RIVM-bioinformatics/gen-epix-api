# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules
from __future__ import annotations

import datetime
import uuid
from enum import Enum

import ulid


class TimestampFactory(Enum):
    DATETIME_NOW = lambda: datetime.datetime.now()


class IdFactory(Enum):
    UUID4 = uuid.uuid4
    ULID = lambda: ulid.api.new().uuid


class ServiceType(Enum):
    ORGANIZATION = "ORGANIZATION"
    AUTH = "AUTH"
    RBAC = "RBAC"
    SEQ = "SEQ"
    ABAC = "ABAC"
    SYSTEM = "SYSTEM"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class Role(Enum):
    ROOT = "ROOT"
    APP_ADMIN = "APP_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    METADATA_ADMIN = "METADATA_ADMIN"
    ORG_USER = "ORG_USER"
    GUEST = "GUEST"
    ROLE1 = "ROLE1"


class RoleSet(Enum):
    ALL = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.METADATA_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        }
    )
    GE_APP_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN})
    GE_ORG_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN, Role.ORG_ADMIN})
    GE_METADATA_ADMIN = frozenset({Role.ROOT, Role.APP_ADMIN, Role.METADATA_ADMIN})
    GE_ORG_USER = frozenset({Role.ROOT, Role.APP_ADMIN, Role.ORG_ADMIN, Role.ORG_USER})
    GE_GUEST = frozenset(
        {
            Role.ROOT,
            Role.APP_ADMIN,
            Role.ORG_ADMIN,
            Role.ORG_USER,
            Role.GUEST,
        }
    )
    APPLICATION = frozenset({Role.APP_ADMIN})
    ORGANIZATION = frozenset({Role.APP_ADMIN, Role.ORG_ADMIN})
    METADATA = frozenset({Role.METADATA_ADMIN})
    OPERATIONAL = frozenset({Role.ORG_USER, Role.GUEST})


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


class ConceptSetType(Enum):
    CONTEXT_FREE_GRAMMAR_JSON = "CONTEXT_FREE_GRAMMAR_JSON"
    CONTEXT_FREE_GRAMMAR_XML = "CONTEXT_FREE_GRAMMAR_XML"
    REGULAR_LANGUAGE = "REGULAR_LANGUAGE"
    NOMINAL = "NOMINAL"
    ORDINAL = "ORDINAL"
    INTERVAL = "INTERVAL"


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
    SUBSPECIES = "SUBSPECIES"
    STRAIN = "STRAIN"
    CLADE = "CLADE"
    TRIBE = "TRIBE"


class QualityControlResult(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"

    def is_usable(self) -> bool:
        return self in {QualityControlResult.PASS, QualityControlResult.WARN}


class SeqFormat(Enum):
    HASH_ONLY = "HASH_ONLY"  # Only the hash code of the sequence is known or stored
    STR_DNA5 = "STR_DNA5"  # String of ACTGN


class AlignmentFormat(Enum):
    CIGAR = "CIGAR"


class AlleleProfileFormat(Enum):
    SORTED_ALLELE_IDS = "SORTED_ALLELE_IDS"


class SnpProfileFormat(Enum):
    REF_ALN_SEQ = "REF_ALN_SEQ"


class KmerProfileFormat(Enum):
    KMER_PROFILE_FORMAT1 = "KMER_PROFILE_FORMAT1"


class SeqClassificationFormat(Enum):
    SEQ_CLASSIFICATION_FORMAT1 = "SEQ_CLASSIFICATION_FORMAT1"


class TaxonomyFormat(Enum):
    TAXONOMY_FORMAT1 = "TAXONOMY_FORMAT1"


class PcrResultFormat(Enum):
    PCR_RESULT_FORMAT1 = "PCR_RESULT_FORMAT1"


class AstResultFormat(Enum):
    AST_RESULT_FORMAT1 = "AST_RESULT_FORMAT1"


class SeqDistanceProtocolType(Enum):
    ALLELE_HAMMING = "ALLELE_HAMMING"
    SNP_HAMMING = "SNP_HAMMING"
    KMER_EUCLIDEAN = "KMER_EUCLIDEAN"
    OTHER = "OTHER"


class SeqDistanceProtocolTypeSet(Enum):
    ALLELE_BASED = frozenset({SeqDistanceProtocolType.ALLELE_HAMMING})
    SNP_BASED = frozenset({SeqDistanceProtocolType.SNP_HAMMING})
    KMER_BASED = frozenset({SeqDistanceProtocolType.KMER_EUCLIDEAN})


class SeqDistanceResultFormat(Enum):
    SEQ_DISTANCE_RESULT_FORMAT1 = "SEQ_DISTANCE_RESULT_FORMAT1"


class SeqDistanceFormat(Enum):
    SEQ_ID_DISTANCE_DICT = "SEQ_ID_DISTANCE_DICT"
    PROFILE_ID_DISTANCE_DICT = "PROFILE_ID_DISTANCE_DICT"
