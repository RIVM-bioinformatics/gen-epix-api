# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


import json
from datetime import datetime
from typing import Any, ClassVar, Iterable, Self
from uuid import UUID

from pydantic import Field, field_serializer, field_validator, model_validator

from gen_epix import fastapp
from gen_epix.casedb.domain import enum, exc
from gen_epix.casedb.domain.model.geo import RegionSet
from gen_epix.casedb.domain.model.ontology import ConceptSet, Disease, EtiologicalAgent
from gen_epix.casedb.domain.model.subject import Subject
from gen_epix.common.domain.model import DataCollection, Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.filter import TypedCompositeFilter, TypedDatetimeRangeFilter

_SERVICE_TYPE = enum.ServiceType.CASE
_ENTITY_KWARGS = {
    "schema_name": _SERVICE_TYPE.value.lower(),
}


class GeneticDistanceProtocol(Model):

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="genetic_distance_protocols",
        table_name="genetic_distance_protocol",
        persistable=True,
        keys=create_keys({1: "seqdb_seq_distance_protocol_id", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    seqdb_seq_distance_protocol_id: UUID = Field(
        description="The ID of the protocol in seqdb"
    )
    name: str = Field(description="The name of the protocol", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the protocol"
    )
    seqdb_max_stored_distance: float | None = Field(
        default=None,
        description="The maximum distance that is stored in seqdb for this protocol",
    )
    min_scale_unit: float = Field(description="The minimum unit to be shown in a scale")


class TreeAlgorithmClass(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="tree_algorithm_classes",
        table_name="tree_algorithm_class",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        **_ENTITY_KWARGS,
    )
    code: str = Field(
        description="The code of the tree algorithm class", max_length=255
    )
    name: str = Field(
        description="The name of the tree algorithm class", max_length=255
    )
    is_seq_based: bool = Field(
        description="Whether the sequence or alignment is needed as input"
    )
    is_dist_based: bool = Field(
        description="Whether the distance between sequences is needed as input"
    )
    rank: int | None = Field(
        default=None,
        description="The rank of the tree algorithm class, if relevant.",
    )


class TreeAlgorithm(Model):
    """
    See https://en.wikipedia.org/wiki/Hierarchical_clustering,
    https://en.wikipedia.org/wiki/Neighbor_joining,
     https://en.wikipedia.org/wiki/Computational_phylogenetics,
     https://en.wikipedia.org/wiki/Spanning_tree
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="tree_algorithms",
        table_name="tree_algorithm",
        persistable=True,
        keys=create_keys({1: "seqdb_tree_algorithm_id", 2: "code", 3: "name"}),
        links=create_links(
            {
                1: (
                    "tree_algorithm_class_id",
                    TreeAlgorithmClass,
                    "tree_algorithm_class",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    tree_algorithm_class_id: UUID = Field(
        description="The ID of the tree algorithm class. FOREIGN KEY"
    )
    tree_algorithm_class: TreeAlgorithmClass | None = Field(
        default=None, description="The class of algorithm"
    )
    seqdb_tree_algorithm_id: UUID = Field(
        description="The ID of the tree algorithm in seqdb"
    )
    code: enum.TreeAlgorithmType = Field(description="The code of the tree algorithm")
    name: str = Field(description="The name of the tree algorithm", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the tree algorithm"
    )
    is_ultrametric: bool = Field(description="Whether the tree is ultrametric")
    rank: int | None = Field(
        default=None,
        description="The rank of the tree algorithm, if relevant.",
    )


class Dim(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="dims",
        table_name="dim",
        persistable=True,
        keys=create_keys({1: "code"}),
        **_ENTITY_KWARGS,
    )
    dim_type: enum.DimType = Field(description="The type of dimension.")
    code: str = Field(description="The code for the dimension.", max_length=255)
    label: str = Field(description="The label for the dimension.")
    rank: int | None = Field(
        default=None,
        description="The rank of the dimension, if relevant.",
    )
    col_code_prefix: str | None = Field(
        default=None,
        description=(
            "The column code prefix used to compose a full column code,"
            " if different from the code field."
        ),
    )
    description: str | None = Field(
        default=None, description="Description of the dimension."
    )
    props: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties of the dimension."
    )

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, value: Any) -> str:
        return str(value)


class Col(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="cols",
        table_name="col",
        persistable=True,
        keys=create_keys({1: ("dim_id", "code")}),
        links=create_links(
            {
                1: ("dim_id", Dim, "dim"),
                2: ("concept_set_id", ConceptSet, "concept_set"),
                3: ("region_set_id", RegionSet, "region_set"),
                4: (
                    "genetic_distance_protocol_id",
                    GeneticDistanceProtocol,
                    "genetic_distance_protocol",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    dim_id: UUID = Field(description="The ID of the dimension. FOREIGN KEY")
    dim: Dim | None = Field(default=None, description="The dimension")
    code_suffix: str | None = Field(
        default=None,
        description=(
            "The code suffix for the column used to compose a full column code,"
            " if needed in addition to the dimension column code prefix. See code field."
        ),
    )
    code: str = Field(
        description=(
            "The code for the column, "
            "equal to the dimension column code prefix dot code_suffix"
            " (dot code_suffix only if the latter is not null)."
        ),
        max_length=255,
    )
    rank_in_dim: int | None = Field(
        default=None,
        description="The rank of the column within the dimension, if relevant.",
    )
    label: str | None = Field(
        default=None,
        description="The label for the column, if different from the code.",
    )
    col_type: enum.ColType = Field(
        description="The type of the data stored in the column."
    )
    concept_set_id: UUID | None = Field(
        default=None,
        description=(
            "The ID of the concept set for the column in case of type"
            " NOMINAL, ORDINAL, INTERVAL. FOREIGN KEY"
        ),
    )
    concept_set: ConceptSet | None = Field(default=None, description="The concept set.")
    region_set_id: UUID | None = Field(
        default=None,
        description="The ID of the region set for the column in case of type GEO. FOREIGN KEY",
    )
    region_set: RegionSet | None = Field(default=None, description="The region set.")
    genetic_distance_protocol_id: UUID | None = Field(
        default=None,
        description=(
            "The ID of the genetic distance protocol"
            " that produces the input for the tree algorithm. FOREIGN KEY"
        ),
    )
    genetic_distance_protocol: GeneticDistanceProtocol | None = Field(
        default=None, description="The genetic distance protocol"
    )
    description: str | None = Field(
        default=None, description="Description of the column."
    )
    props: dict[str, Any] = Field(
        default_factory=dict, description="Additional properties of the column."
    )

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, value: Any) -> str:
        return str(value)

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.col_type in {
            enum.ColType.NOMINAL,
            enum.ColType.ORDINAL,
            enum.ColType.INTERVAL,
            enum.ColType.REGEX,
            enum.ColType.CONTEXT_FREE_GRAMMAR_JSON,
            enum.ColType.CONTEXT_FREE_GRAMMAR_XML,
        }:
            if self.concept_set_id is None:
                raise exc.InvalidArgumentsError(
                    f"No concept_set_id provided for col_type {self.col_type.value}"
                )
        if self.col_type == enum.ColType.GEO_REGION:
            if self.region_set_id is None:
                raise exc.InvalidArgumentsError(
                    f"No region_set_id provided for col_type {self.col_type.value}"
                )
        if self.col_type == enum.ColType.GENETIC_DISTANCE:
            if self.genetic_distance_protocol_id is None:
                raise exc.InvalidArgumentsError(
                    f"No genetic_distance_protocol_id provided for col_type {self.col_type.value}"
                )
        return self


class CaseType(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_types",
        table_name="case_type",
        persistable=True,
        keys=create_keys({1: "name"}),
        links=create_links(
            {
                1: ("disease_id", Disease, "disease"),
                2: ("etiological_agent_id", EtiologicalAgent, "etiological_agent"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    name: str = Field(description="The name of the case type", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the case type"
    )
    disease_id: UUID | None = Field(
        default=None, description="The ID of the disease. FOREIGN KEY"
    )
    disease: Disease | None = Field(default=None, description="The disease")
    etiological_agent_id: UUID | None = Field(
        default=None, description="The ID of the etiological agent. FOREIGN KEY"
    )
    etiological_agent: EtiologicalAgent | None = Field(
        default=None, description="The etiological agent"
    )


class CaseTypeSetCategory(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_set_categories",
        table_name="case_type_set_category",
        persistable=True,
        keys=create_keys({1: "name"}),
        **_ENTITY_KWARGS,
    )
    name: str = Field(
        description="The name of the case type set category", max_length=255
    )
    description: str | None = Field(
        default=None, description="The description of the case type set category"
    )
    rank: int = Field(description="The rank of the case type set category")
    purpose: enum.CaseTypeSetCategoryPurpose = Field(
        default=enum.CaseTypeSetCategoryPurpose.CONTENT,
        description="The purpose of the case type set category",
    )

    @field_serializer("purpose")
    def _serialize_purpose(self, value: enum.CaseTypeSetCategoryPurpose) -> str:
        return value.value


class CaseTypeSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_sets",
        table_name="case_type_set",
        persistable=True,
        keys=create_keys({1: ("case_type_set_category_id", "name")}),
        links=create_links(
            {
                1: (
                    "case_type_set_category_id",
                    CaseTypeSetCategory,
                    "case_type_set_category",
                )
            }
        ),
        **_ENTITY_KWARGS,
    )
    name: str = Field(description="The name of the case type set", max_length=255)
    description: str | None = Field(
        default=None, description="The description of the case type set"
    )
    case_type_set_category_id: UUID = Field(
        description="The id of the category of the case type set. FOREIGN KEY"
    )
    case_type_set_category: CaseTypeSetCategory | None = Field(
        default=None, description="The category of the case type set"
    )
    rank: float = Field(
        description="The rank of the case type set, establishing a partial order"
    )


class CaseTypeSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_set_members",
        table_name="case_type_set_member",
        persistable=True,
        keys=create_keys({1: ("case_type_set_id", "case_type_id")}),
        links=create_links(
            {
                1: ("case_type_set_id", CaseTypeSet, "case_type_set"),
                2: ("case_type_id", CaseType, "case_type"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_type_set_id: UUID = Field(
        description="The ID of the case type set. FOREIGN KEY"
    )
    case_type_set: CaseTypeSet | None = Field(
        default=None, description="The case type set"
    )
    case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The case type")


class CaseTypeCol(Model):  # type: ignore
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_cols",
        table_name="case_type_col",
        persistable=True,
        keys=create_keys({1: ("case_type_id", "col_id", "occurrence")}),
        links=create_links(
            {
                1: ("case_type_id", CaseType, "case_type"),
                2: ("col_id", Col, "col"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The case type")
    col_id: UUID = Field(description="The ID of the column. FOREIGN KEY")
    col: Col | None = Field(default=None, description="The column")
    occurrence: int | None = Field(
        default=None,
        description=(
            "The index of the occurrence of the column for this case type."
            " E.g. for first and second vaccination date it would be 1 and 2."
            " Empty or 1 if only a single occurrence."
        ),
    )
    code: str = Field(
        description=(
            "The code for the case type column, "
            "equal to the column code and, if present, dot 'x' occurrence. "
            "E.g. 'Host.Vaccination.Date.COVID19.x1' for occurrence=1, "
            "'Specimen.Sampling.Date' for occurrence null"
        ),
        max_length=255,
    )
    rank: int | None = Field(
        default=None,
        description=(
            "The rank of the column for this case type for ordering, "
            "if different from the general dimension and column rank."
        ),
    )
    label: str | None = Field(
        default=None,
        description=(
            "The label of the column for this case type,"
            " if different from the general column label."
        ),
    )
    description: str | None = Field(
        default=None, description="Description of the case type column."
    )
    min_value: float | None = Field(
        default=None, description="The minimum value for a numeric column"
    )
    max_value: float | None = Field(
        default=None, description="The maximum value for a numeric column"
    )
    min_datetime: datetime | None = Field(
        default=None, description="The minimum datetime for a time column"
    )
    max_datetime: datetime | None = Field(
        default=None, description="The maximum datetime for a time column"
    )
    min_length: int | None = Field(
        default=None, description="The minimum length for a text column, if not empty"
    )
    max_length: int | None = Field(
        default=None, description="The maximum length for a text column, if not empty"
    )
    pattern: str | None = Field(
        default=None,
        description="The regular expression for a text column, if not empty",
    )
    ncbi_taxid: str | None = Field(
        default=None,
        description=(
            "The NCBI taxid for the column, if the column is a genetic sequence"
        ),
        pattern=r"^NCBI:txid\d+$",
    )
    genetic_sequence_case_type_col_id: UUID | None = Field(
        default=None,
        description=(
            "The ID of the genetic sequence case type column, "
            "if this is a genetic sequence column. FOREIGN KEY"
        ),
    )
    tree_algorithm_codes: set[enum.TreeAlgorithmType] | None = Field(
        default=None,
        description=(
            "The set of tree algorithms that can be used for the case type column"
        ),
    )
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties of the case type column.",
    )

    @field_validator("code", mode="before")
    @classmethod
    def validate_code(cls, value: Any) -> str:
        return str(value)

    @field_validator("tree_algorithm_codes", mode="before")
    @classmethod
    def validate_tree_algorithm_codes(
        cls, value: Iterable[enum.TreeAlgorithmType] | str | None
    ) -> set[enum.TreeAlgorithmType] | None:
        if value is None or isinstance(value, set):
            return value
        if isinstance(value, str):
            return {enum.TreeAlgorithmType[x] for x in json.loads(value)}
        return set(value)

    @field_serializer("tree_algorithm_codes")
    def serialize_tree_algorithm_codes(
        self, value: list[enum.TreeAlgorithmType] | None, _info: Any
    ) -> list[str] | None:
        return None if value is None else [x.value for x in value]


class CaseTypeColSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_col_sets",
        table_name="case_type_col_set",
        persistable=True,
        keys=create_keys({1: "name"}),
        # links=get_links({
        #     1: ("case_type_id", CaseType, "case_type"),
        # }),
        **_ENTITY_KWARGS,
    )
    # case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    # case_type: CaseType | None = Field(default=None, description="The case type")
    name: str = Field(
        description="The name of a case type column set, UNIQUE", max_length=255
    )
    description: str | None = Field(
        default=None, description="The description of the case type column set"
    )


class CaseTypeColSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_col_set_members",
        table_name="case_type_col_set_member",
        persistable=True,
        keys=create_keys({1: ("case_type_col_set_id", "case_type_col_id")}),
        links=create_links(
            {
                1: ("case_type_col_set_id", CaseTypeColSet, "case_type_col_set"),
                2: ("case_type_col_id", CaseTypeCol, "case_type_col"),  # type: ignore
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_type_col_set_id: UUID = Field(
        description="The ID of the case type column set. FOREIGN KEY"
    )
    case_type_col_set: CaseTypeColSet | None = Field(
        default=None, description="The case type column set"
    )
    case_type_col_id: UUID = Field(
        description="The ID of the case type column. FOREIGN KEY"
    )
    case_type_col: CaseTypeCol | None = Field(  # type: ignore
        default=None, description="The case type column"
    )


class Case(Model):
    """
    A class representing a case.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="cases",
        table_name="case",
        persistable=True,
        links=create_links(
            {
                1: ("case_type_id", CaseType, "case_type"),
                2: ("subject_id", Subject, "subject"),
                3: (
                    "created_in_data_collection_id",
                    DataCollection,
                    "created_in_data_collection",
                ),
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The case type")
    subject_id: UUID | None = Field(
        default=None, description="The ID of the subject. FOREIGN KEY"
    )
    subject: Subject | None = Field(default=None, description="The subject")
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the case was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case was created"
    )
    count: int | None = Field(
        default=None, description="The number of cases, if applicable", gt=0
    )
    case_date: datetime = Field(description="The date of the case")
    content: dict[UUID, str] = Field(
        description="The column data of the case as {col_id: str_value}"
    )

    @field_serializer("content")
    def serialize_content(self, value: dict[UUID, str | float | None], _info):
        return {str(x): y for x, y in value.items()}


class CaseDataCollectionLink(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_data_collection_links",
        table_name="case_data_collection_link",
        persistable=True,
        keys=create_keys({1: ("case_id", "data_collection_id")}),
        links=create_links(
            {
                1: ("case_id", Case, "case"),
                2: ("data_collection_id", DataCollection, "data_collection"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_id: UUID = Field(description="The ID of the case. FOREIGN KEY")
    case: Case | None = Field(default=None, description="The case")
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )


class CaseSetCategory(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_categories",
        table_name="case_set_category",
        persistable=True,
        keys=create_keys({1: "name"}),
        **_ENTITY_KWARGS,
    )
    name: str = Field(
        description="The name of the case set category, UNIQUE", max_length=255
    )
    description: str | None = Field(
        description="The description of the case set category"
    )


class CaseSetStatus(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_statuses",
        table_name="case_set_status",
        persistable=True,
        keys=create_keys({1: "name"}),
        **_ENTITY_KWARGS,
    )
    name: str = Field(
        description="The name of the case set status, UNIQUE", max_length=255
    )
    description: str | None = Field(
        description="The description of the case set status"
    )


class CaseSet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_sets",
        table_name="case_set",
        persistable=True,
        keys=create_keys({1: "name"}),
        links=create_links(
            {
                1: ("case_type_id", CaseType, "case_type"),
                2: (
                    "created_in_data_collection_id",
                    DataCollection,
                    "created_in_data_collection",
                ),
                3: ("case_set_category_id", CaseSetCategory, "case_set_category"),
                4: ("case_set_status_id", CaseSetStatus, "case_set_status"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_type_id: UUID = Field(description="The ID of the case type. FOREIGN KEY")
    case_type: CaseType | None = Field(default=None, description="The case type")
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the case set was created. FOREIGN KEY",
    )
    created_in_data_collection: DataCollection | None = Field(
        default=None, description="The data collection where the case set was created"
    )
    name: str = Field(description="The name of a case set, UNIQUE", max_length=255)
    description: str = Field(description="The description of a case set")
    created_at: datetime = Field(
        description="The datetime of the case set creation",
        default_factory=datetime.now,
    )
    case_set_category_id: UUID = Field(
        description="The id of the category of the case set"
    )
    case_set_category: CaseSetCategory | None = Field(
        default=None, description="The category of the case set"
    )
    case_set_status_id: UUID = Field(description="The id of the status of the case set")
    case_set_status: CaseSetStatus | None = Field(
        default=None, description="The status of the case set"
    )


class CaseSetMember(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_members",
        table_name="case_set_member",
        persistable=True,
        keys=create_keys({1: ("case_set_id", "case_id")}),
        links=create_links(
            {1: ("case_set_id", CaseSet, "case_set"), 2: ("case_id", Case, "case")}
        ),
        **_ENTITY_KWARGS,
    )
    case_set_id: UUID = Field(description="The ID of the case set. FOREIGN KEY")
    case_set: CaseSet | None = Field(default=None, description="The case set")
    case_id: UUID = Field(description="The ID of the case. FOREIGN KEY")
    case: Case | None = Field(default=None, description="The case")
    classification: enum.CaseClassification | None = Field(
        default=None, description="The classification of the case"
    )


class CaseSetDataCollectionLink(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_data_collection_links",
        table_name="case_set_data_collection_link",
        persistable=True,
        keys=create_keys({1: ("case_set_id", "data_collection_id")}),
        links=create_links(
            {
                1: ("case_set_id", CaseSet, "case_set"),
                2: ("data_collection_id", DataCollection, "data_collection"),
            }
        ),
        **_ENTITY_KWARGS,
    )
    case_set_id: UUID = Field(description="The ID of the case set. FOREIGN KEY")
    case_set: CaseSet | None = Field(default=None, description="The case set")
    data_collection_id: UUID = Field(
        description="The ID of the data collection. FOREIGN KEY"
    )
    data_collection: DataCollection | None = Field(
        default=None, description="The data collection"
    )


# Non-persistable models


class CaseTypeDim(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_dims",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    id: UUID = Field(description="The ID of the first case type column.")
    dim_id: UUID = Field(description="The ID of the dimension. FOREIGN KEY")
    occurrence: int | None = Field(
        default=None,
        description=(
            "The index of the occurrence of the dimension for this case type."
            " E.g. for first and second vaccination time it would be 1 and 2."
            " Empty if only a single occurrence."
        ),
    )
    rank: int = Field(
        default=None,
        description="The rank of the case type dimension for ordering",
    )
    case_type_col_order: list[UUID] = Field(
        description="The order of the case type columns"
    )


class CaseTypeStat(fastapp.Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_type_stats",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    case_type_id: UUID = Field(description="The ID of the case type.")
    n_cases: int | None = Field(
        default=None, description="The number of cases for the case type."
    )
    first_case_month: str | None = Field(
        default=None, description="The ISO year and month of the first case."
    )
    last_case_month: str | None = Field(
        default=None, description="The ISO year and month of the last case."
    )


class CaseSetStat(fastapp.Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_stats",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    case_set_id: UUID = Field(description="The ID of the case set.")
    n_cases: int | None = Field(
        default=None, description="The number of cases in the case set."
    )
    n_own_cases: int | None = Field(
        default=None, description="The number of own cases in the case set."
    )
    first_case_month: str | None = Field(
        default=None, description="The ISO year and month of the first case."
    )
    last_case_month: str | None = Field(
        default=None, description="The ISO year and month of the last case."
    )


class CaseQuery(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_queries",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    label: str | None = Field(default=None, description="The label for the query.")
    case_type_ids: set[UUID] | None = Field(
        default=None,
        description="The IDs of the case type(s) that the case must belong to. Not applied if not provided.",
    )
    case_set_ids: set[UUID] | None = Field(
        default=None,
        description="The IDs of the case set(s) that the case must belong to. Not applied if not provided.",
    )
    datetime_range_filter: TypedDatetimeRangeFilter | None = Field(
        default=None,
        description="The datetime range filter to apply to the case date. Not applied if not provided.",
    )
    # TODO: add data_collection_id
    filter: TypedCompositeFilter | None = Field(
        default=None, description="The filter to apply. Not applied if not provided."
    )


class CaseSetQuery(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_queries",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    label: str = Field(description="The label for the query.")
    filter: TypedCompositeFilter = Field(description="The filter to apply.")


class BaseCaseRights(Model):
    created_in_data_collection_id: UUID = Field(
        description="The ID of the data collection where the item was created",
    )
    case_type_id: UUID = Field(description="The ID of the case type")
    data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections in which the item is currently shared, including the created_in_data_collection_id",
    )
    is_full_access: bool = Field(
        description="Whether the user has full access to the item, i.e. all rights on all data collections",
    )
    add_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections to which the item is allowed to be added",
    )
    remove_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections from which the item is allowed to be removed. If remove_data_collection_ids is equal to data_collection_ids, the item is allowed to be deleted",
    )
    can_delete: bool = Field(
        description="Whether the item can be deleted.",
    )
    shared_in_data_collection_ids: set[UUID] = Field(
        description="The IDs of the data collections in which the item is currently shared, excluding the created_in_data_collection_id",
    )


class CaseRights(BaseCaseRights):
    """
    Describes all the rights that a user has on one particular case, based on the data
    collections in which it is currently shared.
    """

    NAME: ClassVar = "CaseRights"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_rights",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    case_id: UUID = Field(description="The ID of the case")
    read_case_type_col_ids: set[UUID] = Field(
        description="The IDs of the case type columns that are allowed to be read for the case",
    )
    write_case_type_col_ids: set[UUID] = Field(
        description="The IDs of the case type columns that are allowed to be written for the case",
    )


class CaseSetRights(BaseCaseRights):
    """
    Describes all the rights that a user has on one particular case set, based on the
    data collections in which it is currently shared.
    """

    NAME: ClassVar = "CaseSetRights"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="case_set_rights",
        persistable=False,
        **_ENTITY_KWARGS,
    )
    case_set_id: UUID = Field(description="The ID of the case set")
    read_case_set: bool = Field(
        description="Whether the case set is allowed to be read",
    )
    write_case_set: bool = Field(
        description="Whether the case set is allowed to be written",
    )
