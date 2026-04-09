from datetime import datetime
from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.seqdb.domain.model.seq.classification import (
    SeqClassification,
    SeqTaxonomy,
)
from gen_epix.seqdb.domain.model.seq.pheno import AstMeasurement, PcrMeasurement
from gen_epix.seqdb.domain.model.seq.profile import SeqProfile, SeqProfileIdentifier
from gen_epix.seqdb.domain.model.seq.reads import ReadSet, ReadSetIdentifier
from gen_epix.seqdb.domain.model.seq.sample import Sample, SampleIdentifier
from gen_epix.seqdb.domain.model.seq.seq import Seq, SeqIdentifier


class SampleQuery(Model):
    """
    A query for retrieving samples. All constraints are optional, but at least one
    criterion must be provided.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="sample_queries",
        persistable=False,
    )
    label: str | None = Field(default=None, description="Label for the query.")
    modified_since: datetime | None = Field(
        default=None,
        description=(
            "Lower bound of the last-modified datetime range to filter by "
            "(inclusive)."
        ),
    )
    modified_until: datetime | None = Field(
        default=None,
        description=(
            "Upper bound of the last-modified datetime range to filter by "
            "(exclusive)."
        ),
    )

    @model_validator(mode="after")
    def _validate_some_criteria(self) -> Self:
        if self.modified_since is None and self.modified_until is None:
            raise ValueError("At least one criterion must be provided")
        return self


class SampleQueryResult(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="sample_query_results",
        persistable=False,
    )
    sample_query: SampleQuery = Field(
        description="The sample query that was executed, provided back."
    )
    sample_ids: list[UUID] = Field(description="IDs of samples matching the query.")
    is_max_results_exceeded: bool = Field(
        description="Whether the number of results was limited."
    )


class FullSample(Model):
    """
    A comprehensive sample view with all sample-linked data and identifiers.
    """

    NAME: ClassVar = "FullSample"
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="full_samples",
        persistable=False,
    )
    DATA_CLASSES: ClassVar[list[type[Model]]] = [
        ReadSet,
        Seq,
        SeqTaxonomy,
        SeqClassification,
        SeqProfile,
        PcrMeasurement,
        AstMeasurement,
    ]
    DATA_CLASS_FIELD_MAP: ClassVar[dict[type[Model], str]] = {
        ReadSet: "read_sets",
        Seq: "seqs",
        SeqTaxonomy: "seq_taxonomies",
        SeqClassification: "seq_classifications",
        SeqProfile: "seq_profiles",
        PcrMeasurement: "pcr_measurements",
        AstMeasurement: "ast_measurements",
    }
    IDENTIFIER_CLASSES: ClassVar[list[type[Model]]] = [
        ReadSetIdentifier,
        SeqIdentifier,
        SeqProfileIdentifier,
    ]
    DATA_IDENTIFIER_CLASS_MAP: ClassVar[dict[type[Model], type[Model]]] = {
        ReadSet: ReadSetIdentifier,
        Seq: SeqIdentifier,
        SeqProfile: SeqProfileIdentifier,
    }
    IDENTIFIER_FIELD_MAP: ClassVar[dict[type[Model], str]] = {
        ReadSetIdentifier: "read_set_identifiers",
        SeqIdentifier: "seq_identifiers",
        SeqProfileIdentifier: "seq_profile_identifiers",
    }

    sample: Sample = Field(description="The sample for which linked data are included.")
    sample_identifiers: list[SampleIdentifier] = Field(
        default_factory=list,
        description="Identifiers associated with the sample.",
    )
    read_sets: list[ReadSet] = Field(
        default_factory=list,
        description="Read sets linked to the sample.",
    )
    read_set_identifiers: list[ReadSetIdentifier] = Field(
        default_factory=list,
        description="Identifiers linked to retrieved read sets.",
    )
    seqs: list[Seq] = Field(
        default_factory=list,
        description="Sequences linked to the sample.",
    )
    seq_identifiers: list[SeqIdentifier] = Field(
        default_factory=list,
        description="Identifiers linked to retrieved sequences.",
    )
    seq_taxonomies: list[SeqTaxonomy] = Field(
        default_factory=list,
        description="Taxonomy records linked to the sample.",
    )
    seq_classifications: list[SeqClassification] = Field(
        default_factory=list,
        description="Classification records linked to the sample.",
    )
    seq_profiles: list[SeqProfile] = Field(
        default_factory=list,
        description="Sequence profiles linked to the sample.",
    )
    seq_profile_identifiers: list[SeqProfileIdentifier] = Field(
        default_factory=list,
        description="Identifiers linked to retrieved sequence profiles.",
    )
    pcr_measurements: list[PcrMeasurement] = Field(
        default_factory=list,
        description="PCR measurements linked to the sample.",
    )
    ast_measurements: list[AstMeasurement] = Field(
        default_factory=list,
        description="AST measurements linked to the sample.",
    )
