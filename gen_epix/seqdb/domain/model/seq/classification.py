from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.category import SeqCategory
from gen_epix.seqdb.domain.model.seq.protocol import Protocol
from gen_epix.seqdb.domain.model.seq.sample import HasSampleMixin, Sample
from gen_epix.seqdb.domain.model.seq.seq import Seq
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class SeqClassification(Model, HasSampleMixin):
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
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    protocol_id: UUID = Field(description="The ID of the protocol. FOREIGN KEY")
    protocol: Protocol = Field(description="The protocol.")
    primary_category_id: UUID | None = Field(
        description="The ID of the category. FOREIGN KEY"
    )
    primary_category: SeqCategory = Field(description="The primary category.")
    classification: str = Field(description="The classification of the sequence.")
    classification_format: enum.SeqClassificationFormat = Field(
        default=enum.SeqClassificationFormat.SEQ_CLASSIFICATION_FORMAT1,
        description="The representation format of the classification.",
    )
    classification_hash: UUID = Field(
        description="The first SHA256 hash of the sorted list of category ids as bytes.",
    )


class AstPrediction(Model, HasSampleMixin):
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
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    ast_result: str = Field(description="The result of the AST prediction.")
    ast_result_format: enum.AstResultFormat = Field(
        default=enum.AstResultFormat.AST_RESULT_FORMAT1,
        description="The representation format of the AST result.",
    )


class SeqTaxonomy(Model, HasSampleMixin):
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
    seq_id: UUID | None = Field(
        description="The unique identifier for the sequence that the result was derived from, if available. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    protocol_id: UUID = Field(
        description="The unique identifier for the protocol. FOREIGN KEY"
    )
    protocol: Protocol | None = Field(default=None, description="The protocol.")
    primary_taxon_id: UUID = Field(
        description="The unique identifier for the primary taxon. FOREIGN KEY"
    )
    primary_taxon: Taxon | None = Field(default=None, description="The primary taxon.")
    taxonomy: str = Field(description="The taxonomy results of the sequence.")
    taxonomy_format: enum.TaxonomyFormat = Field(
        default=enum.TaxonomyFormat.TAXONOMY_FORMAT1,
        description="The representation format of the taxonomy.",
    )
    taxonomy_hash: UUID = Field(
        description="The first 128 bits of the SHA256 hash of the sorted list of taxon ids as bytes.",
    )
