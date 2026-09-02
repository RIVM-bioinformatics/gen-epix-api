"""Define seqdb domain models for domain.model.seq.classification."""

from typing import ClassVar, Self
from uuid import UUID

from pydantic import Field, model_validator

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ContentMixin, QualityMixin
from gen_epix.seqdb.domain.model.seq.category import SeqCategory
from gen_epix.seqdb.domain.model.seq.protocol import HasProtocolMixin, Protocol
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.seq import HasSeqMixin, Seq
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class SeqClassification(
    Model,
    HasSampleMixin,
    HasSeqMixin,
    HasProtocolMixin,
    ContentMixin[enum.SeqClassificationFormat],
    QualityMixin,
):
    """Represents a sequence classification produced by a protocol.

    Model validation: Content-hash validation is not implemented yet, so the
    model currently accepts content unchanged after its inherited validation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_classifications",
        table_name="seq_classification",
        persistable=True,
        keys=create_keys({1: ("seq_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: (
                    "protocol_id",
                    Protocol,
                    "protocol",
                ),
                4: ("primary_category_id", SeqCategory, "primary_category"),
            }
        ),
    )
    primary_category_id: UUID = Field(description="The ID of the category. FOREIGN KEY")
    primary_category: SeqCategory | None = Field(
        default=None, description="The primary category."
    )

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Reserve post-validation for future content-hash verification."""
        # TODO: implement content hash validation
        return self


class AstPrediction(
    Model,
    HasSampleMixin,
    HasSeqMixin,
    HasProtocolMixin,
    ContentMixin[enum.AstResultFormat],
    QualityMixin,
):
    """Represents an antimicrobial-susceptibility prediction for a sequence.

    Model validation: Content-hash validation is not implemented yet, so the
    model currently accepts content unchanged after its inherited validation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_predictions",
        table_name="ast_prediction",
        persistable=True,
        keys=create_keys({1: ("seq_id", "protocol_id")}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("protocol_id", Protocol, "protocol"),
            }
        ),
    )

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Reserve post-validation for future content-hash verification."""
        # TODO: implement content hash validation
        return self


class SeqTaxonomy(
    Model,
    HasSampleMixin,
    HasSeqMixin,
    HasProtocolMixin,
    ContentMixin[enum.SeqTaxonomyFormat],
    QualityMixin,
):
    """Represents a taxonomy assignment produced for a sequence by a protocol.

    Model validation: Content-hash validation is not implemented yet, so the
    model currently accepts content unchanged after its inherited validation.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_taxonomies",
        table_name="seq_taxonomy",
        persistable=True,
        keys=create_keys({1: "seq_id", 2: "protocol_id"}),
        links=create_links(
            {
                1: ("sample_id", Sample, "sample"),
                2: ("seq_id", Seq, "seq"),
                3: ("protocol_id", Protocol, "protocol"),
                4: ("primary_taxon_id", Taxon, "primary_taxon"),
            }
        ),
    )
    format: enum.SeqTaxonomyFormat = Field(
        default=enum.SeqTaxonomyFormat.TAXONOMY_FORMAT1,
        description="The representation format of the taxonomy.",
    )
    primary_taxon_id: UUID = Field(
        description="The unique identifier for the primary taxon. FOREIGN KEY"
    )
    primary_taxon: Taxon | None = Field(default=None, description="The primary taxon.")

    @model_validator(mode="after")
    def _validate_content(self) -> Self:
        """Reserve post-validation for future content-hash verification."""
        # TODO: implement content hash validation
        return self
