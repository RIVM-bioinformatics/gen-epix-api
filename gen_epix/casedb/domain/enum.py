# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules

from enum import Enum


class ServiceType(Enum):
    GEO = "GEO"
    ONTOLOGY = "ONTOLOGY"
    ORGANIZATION = "ORGANIZATION"
    AUTH = "AUTH"
    RBAC = "RBAC"
    SEQDB = "SEQDB"
    SUBJECT = "SUBJECT"
    CASE = "CASE"
    ABAC = "ABAC"
    SYSTEM = "SYSTEM"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class RegionRelationType(Enum):
    IS_SEPARATE_FROM = "IS_SEPARATE_FROM"
    IS_ADJACENT_TO = "IS_ADJACENT_TO"
    IS_CONTAINED_IN = "IS_CONTAINED_IN"
    OVERLAPS_WITH = "OVERLAPS_WITH"
    CONTAINS = "CONTAINS"


class TreeAlgorithmType(Enum):
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


class ColRelation(Enum):
    IS_UNRELATED_TO = 0
    AGGREGATES_VALUE = 1
    AGGREGATES_COLUMN = 2


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


class CaseRight(Enum):
    ADD_CASE = "ADD_CASE"
    REMOVE_CASE = "REMOVE_CASE"
    READ_CASE = "READ_CASE"
    WRITE_CASE = "WRITE_CASE"
    ADD_CASE_SET = "ADD_CASE_SET"
    REMOVE_CASE_SET = "REMOVE_CASE_SET"
    READ_CASE_SET = "READ_CASE_SET"
    WRITE_CASE_SET = "WRITE_CASE_SET"


class CaseRightSet(Enum):
    SHARE = frozenset(
        {
            CaseRight.ADD_CASE,
            CaseRight.REMOVE_CASE,
            CaseRight.ADD_CASE_SET,
            CaseRight.REMOVE_CASE_SET,
        }
    )
    CONTENT = frozenset(
        {
            CaseRight.READ_CASE,
            CaseRight.WRITE_CASE,
            CaseRight.READ_CASE_SET,
            CaseRight.WRITE_CASE_SET,
        }
    )
    ADD = frozenset(
        {
            CaseRight.ADD_CASE,
            CaseRight.ADD_CASE_SET,
        }
    )
    REMOVE = frozenset(
        {
            CaseRight.REMOVE_CASE,
            CaseRight.REMOVE_CASE_SET,
        }
    )
    CASE = frozenset(
        {
            CaseRight.ADD_CASE,
            CaseRight.REMOVE_CASE,
            CaseRight.READ_CASE,
            CaseRight.WRITE_CASE,
        }
    )
    CASE_CONTENT = frozenset(
        {
            CaseRight.READ_CASE,
            CaseRight.WRITE_CASE,
        }
    )
    CASE_SET = frozenset(
        {
            CaseRight.ADD_CASE_SET,
            CaseRight.REMOVE_CASE_SET,
            CaseRight.READ_CASE_SET,
            CaseRight.WRITE_CASE_SET,
        }
    )
    CASE_SET_CONTENT = frozenset(
        {
            CaseRight.READ_CASE_SET,
            CaseRight.WRITE_CASE_SET,
        }
    )


class CaseClassification(Enum):
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"
    CONFIRMED = "CONFIRMED"


class CaseTypeSetCategoryPurpose(Enum):
    CONTENT = "CONTENT"
    SECURITY = "SECURITY"


class ConceptSetType(Enum):
    CONTEXT_FREE_GRAMMAR_JSON = "CONTEXT_FREE_GRAMMAR_JSON"
    CONTEXT_FREE_GRAMMAR_XML = "CONTEXT_FREE_GRAMMAR_XML"
    REGULAR_LANGUAGE = "REGULAR_LANGUAGE"
    NOMINAL = "NOMINAL"
    ORDINAL = "ORDINAL"
    INTERVAL = "INTERVAL"


class DimType(Enum):
    TEXT = "TEXT"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    TIME = "TIME"
    GEO = "GEO"
    ORGANIZATION = "ORGANIZATION"
    OTHER = "OTHER"


class ColType(Enum):
    TEXT = "TEXT"
    CONTEXT_FREE_GRAMMAR_JSON = "CONTEXT_FREE_GRAMMAR_JSON"
    CONTEXT_FREE_GRAMMAR_XML = "CONTEXT_FREE_GRAMMAR_XML"
    REGEX = "REGEX"
    NOMINAL = "NOMINAL"
    ORDINAL = "ORDINAL"
    INTERVAL = "INTERVAL"
    TIME_DAY = "TIME_DAY"
    TIME_WEEK = "TIME_WEEK"
    TIME_MONTH = "TIME_MONTH"
    TIME_QUARTER = "TIME_QUARTER"
    TIME_YEAR = "TIME_YEAR"
    GEO_LATLON = "GEO_LATLON"
    GEO_REGION = "GEO_REGION"
    ID_DIRECT = "ID_DIRECT"
    ID_PSEUDONYMISED = "ID_PSEUDONYMISED"
    ID_ANONYMISED = "ID_ANONYMISED"
    DECIMAL_0 = "DECIMAL_0"
    DECIMAL_1 = "DECIMAL_1"
    DECIMAL_2 = "DECIMAL_2"
    DECIMAL_3 = "DECIMAL_3"
    DECIMAL_4 = "DECIMAL_4"
    DECIMAL_5 = "DECIMAL_5"
    DECIMAL_6 = "DECIMAL_6"
    GENETIC_SEQUENCE = "GENETIC_SEQUENCE"
    GENETIC_DISTANCE = "GENETIC_DISTANCE"
    ORGANIZATION = "ORGANIZATION"
    OTHER = "OTHER"


class ColTypeSet(Enum):
    ID = [ColType.ID_DIRECT, ColType.ID_PSEUDONYMISED]
    LANGUAGE = [
        ColType.CONTEXT_FREE_GRAMMAR_JSON,
        ColType.CONTEXT_FREE_GRAMMAR_XML,
        ColType.REGEX,
    ]
    CONTEXT_FREE_GRAMMAR = [
        ColType.CONTEXT_FREE_GRAMMAR_JSON,
        ColType.CONTEXT_FREE_GRAMMAR_XML,
        ColType.GENETIC_SEQUENCE,
        ColType.GENETIC_DISTANCE,
        ColType.ORGANIZATION,
    ]
    ENTITY = [
        ColType.GENETIC_SEQUENCE,
        ColType.GENETIC_DISTANCE,
        ColType.ORGANIZATION,
    ]
    REGULAR_LANGUAGE = [
        ColType.REGEX,
        ColType.NOMINAL,
        ColType.ORDINAL,
        ColType.INTERVAL,
        ColType.TIME_DAY,
        ColType.TIME_WEEK,
        ColType.TIME_MONTH,
        ColType.TIME_QUARTER,
        ColType.TIME_YEAR,
        ColType.GEO_LATLON,
        ColType.GEO_REGION,
        ColType.DECIMAL_0,
        ColType.DECIMAL_1,
        ColType.DECIMAL_2,
        ColType.DECIMAL_3,
        ColType.DECIMAL_4,
        ColType.DECIMAL_5,
        ColType.DECIMAL_6,
    ]
    STRING_SET = [
        ColType.NOMINAL,
        ColType.ORDINAL,
        ColType.INTERVAL,
    ]
    TIME = [
        ColType.TIME_DAY,
        ColType.TIME_WEEK,
        ColType.TIME_MONTH,
        ColType.TIME_QUARTER,
        ColType.TIME_YEAR,
    ]
    GEO = [ColType.GEO_LATLON, ColType.GEO_REGION]
    NUMBER = [
        ColType.DECIMAL_0,
        ColType.DECIMAL_1,
        ColType.DECIMAL_2,
        ColType.DECIMAL_3,
        ColType.DECIMAL_4,
        ColType.DECIMAL_5,
        ColType.DECIMAL_6,
    ]
    GENETIC = [ColType.GENETIC_SEQUENCE, ColType.GENETIC_DISTANCE]
    ORGANIZATION = [ColType.ORGANIZATION]
    OTHER = [ColType.OTHER]


class DimColTypes(Enum):
    TEXT = list(ColType)
    TIME = ColTypeSet.TIME
    GEO = ColTypeSet.GEO
    ORGANIZATION = ColTypeSet.ORGANIZATION
    NUMBER = ColTypeSet.NUMBER
    IDENTIFIER = ColTypeSet.ID
    OTHER = ColTypeSet.OTHER
