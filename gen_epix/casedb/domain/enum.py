# pylint: disable=wildcard-import, unused-import
# because this is a package, and imported as such in other modules

from enum import Enum


from gen_epix.commondb.domain.enum import RoleSet as RoleSet


class ServiceType(Enum):
    AUTH = "AUTH"
    ORGANIZATION = "ORGANIZATION"
    SYSTEM = "SYSTEM"
    RBAC = "RBAC"
    ABAC = "ABAC"
    GEO = "GEO"
    ONTOLOGY = "ONTOLOGY"
    SEQDB = "SEQDB"
    CASE = "CASE"


class RepositoryType(Enum):
    DICT = "DICT"
    SA_SQLITE = "SA_SQLITE"
    SA_SQL = "SA_SQL"


class RegionRelationType(Enum):
    IS_SEPARATE_FROM = "IS_SEPARATE_FROM"
    IS_ADJACENT_TO = "IS_ADJACENT_TO"
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
    ROOT = "CASEDB_ROOT"
    APP_ADMIN = "CASEDB_APP_ADMIN"
    ORG_ADMIN = "CASEDB_ORG_ADMIN"
    REFDATA_ADMIN = "CASEDB_REFDATA_ADMIN"
    ORG_USER = "CASEDB_ORG_USER"
    GUEST = "CASEDB_GUEST"
    ROLE1 = "CASEDB_ROLE1"


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


class ConceptRelationType(Enum):
    CONTAINS = "CONTAINS"


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
    REGULAR_LANGUAGE = "REGULAR_LANGUAGE"
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
    ID_PERSON = "ID_PERSON"
    ID_CASE = "ID_CASE"
    ID_SAMPLE = "ID_SAMPLE"
    ID_EVENT = "ID_EVENT"
    ID_GENETIC_SEQUENCE = "ID_GENETIC_SEQUENCE"
    DECIMAL_0 = "DECIMAL_0"
    DECIMAL_1 = "DECIMAL_1"
    DECIMAL_2 = "DECIMAL_2"
    DECIMAL_3 = "DECIMAL_3"
    DECIMAL_4 = "DECIMAL_4"
    DECIMAL_5 = "DECIMAL_5"
    DECIMAL_6 = "DECIMAL_6"
    GENETIC_READS = "GENETIC_READS"
    GENETIC_SEQUENCE = "GENETIC_SEQUENCE"
    GENETIC_PROFILE = "GENETIC_PROFILE"
    GENETIC_DISTANCE = "GENETIC_DISTANCE"
    ORGANIZATION = "ORGANIZATION"
    OTHER = "OTHER"


class ColTypeSet(Enum):
    ID = frozenset(
        {
            ColType.ID_PERSON,
            ColType.ID_SAMPLE,
            ColType.ID_CASE,
            ColType.ID_EVENT,
            ColType.ID_GENETIC_SEQUENCE,
        }
    )
    LANGUAGE = frozenset(
        {
            ColType.CONTEXT_FREE_GRAMMAR_JSON,
            ColType.CONTEXT_FREE_GRAMMAR_XML,
            ColType.REGULAR_LANGUAGE,
        }
    )
    CONTEXT_FREE_GRAMMAR = frozenset(
        {
            ColType.CONTEXT_FREE_GRAMMAR_JSON,
            ColType.CONTEXT_FREE_GRAMMAR_XML,
        }
    )
    ENTITY = frozenset(
        {
            ColType.GENETIC_SEQUENCE,
            ColType.GENETIC_DISTANCE,
            ColType.ORGANIZATION,
        }
    )
    REGULAR_LANGUAGE = frozenset(
        {
            ColType.REGULAR_LANGUAGE,
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
        }
    )
    STRING_SET = frozenset(
        {
            ColType.NOMINAL,
            ColType.ORDINAL,
            ColType.INTERVAL,
        }
    )
    TIME = frozenset(
        {
            ColType.TIME_DAY,
            ColType.TIME_WEEK,
            ColType.TIME_MONTH,
            ColType.TIME_QUARTER,
            ColType.TIME_YEAR,
        }
    )
    GEO = frozenset({ColType.GEO_LATLON, ColType.GEO_REGION})
    NUMBER = frozenset(
        {
            ColType.DECIMAL_0,
            ColType.DECIMAL_1,
            ColType.DECIMAL_2,
            ColType.DECIMAL_3,
            ColType.DECIMAL_4,
            ColType.DECIMAL_5,
            ColType.DECIMAL_6,
        }
    )
    GENETIC = frozenset(
        {
            ColType.GENETIC_READS,
            ColType.GENETIC_SEQUENCE,
            ColType.GENETIC_PROFILE,
            ColType.GENETIC_DISTANCE,
        }
    )
    ORGANIZATION = frozenset({ColType.ORGANIZATION})
    OTHER = frozenset({ColType.OTHER})
    HAS_CONCEPT_SET = frozenset(
        {
            ColType.NOMINAL,
            ColType.ORDINAL,
            ColType.INTERVAL,
        }
    )
    HAS_REGION_SET = frozenset({ColType.GEO_REGION})
    HAS_GENETIC_DISTANCE_PROTOCOL = frozenset({ColType.GENETIC_DISTANCE})
    HAS_REGEX = frozenset({ColType.REGULAR_LANGUAGE})
    HAS_SCHEMA = frozenset(
        {
            ColType.CONTEXT_FREE_GRAMMAR_JSON,
            ColType.CONTEXT_FREE_GRAMMAR_XML,
        }
    )
    COL_TYPES_STR_LIKE = frozenset(
        {
            ColType.TIME_WEEK,
            ColType.TIME_MONTH,
            ColType.TIME_QUARTER,
            ColType.TIME_YEAR,
            ColType.GEO_REGION,
            ColType.NOMINAL,
            ColType.ORDINAL,
            ColType.INTERVAL,
            ColType.TEXT,
            ColType.ID_PERSON,
            ColType.ID_SAMPLE,
            ColType.ID_CASE,
            ColType.ID_EVENT,
            ColType.ID_GENETIC_SEQUENCE,
            ColType.ORGANIZATION,
            ColType.OTHER,
        }
    )


# !FIXME: make sure the data reflects these definitions or these definitions are changed accordingly
class DimColTypeSet(Enum):
    TEXT = frozenset(
        ColTypeSet.LANGUAGE.value.union(
            {ColType.TEXT},
            ColTypeSet.STRING_SET.value,
            ColTypeSet.GENETIC.value,
        )
    )
    IDENTIFIER = ColTypeSet.ID.value
    NUMBER = ColTypeSet.NUMBER.value.union(
        {ColType.INTERVAL, ColType.NOMINAL, ColType.ORDINAL}
    )
    TIME = ColTypeSet.TIME.value
    GEO = ColTypeSet.GEO.value
    ORGANIZATION = ColTypeSet.ORGANIZATION.value
    OTHER = frozenset(
        ColTypeSet.LANGUAGE.value.union(
            {ColType.TEXT},
            ColTypeSet.STRING_SET.value,
            ColTypeSet.GENETIC.value,
            ColTypeSet.OTHER.value,
        )
    )


class ColTypeOrder(Enum):
    # Relies on dict order guaranteed
    TIME_RESOLUTION_DESC = {
        ColType.TIME_DAY: 1,
        ColType.TIME_WEEK: 2,
        ColType.TIME_MONTH: 3,
        ColType.TIME_QUARTER: 4,
        ColType.TIME_YEAR: 5,
    }

class FeatureFlag(Enum):
    UPDATE_OWN_ORGANIZATION = "UPDATE_OWN_ORGANIZATION"
    DISABLE_UPLOAD = "UPLOAD_ENABLED"