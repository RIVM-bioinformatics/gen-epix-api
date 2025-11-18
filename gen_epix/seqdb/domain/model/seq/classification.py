from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links
from gen_epix.seqdb.domain import enum
from gen_epix.seqdb.domain.model.seq.base import ProtocolMixin
from gen_epix.seqdb.domain.model.seq.pheno import AstProtocol
from gen_epix.seqdb.domain.model.seq.seq import Seq
from gen_epix.seqdb.domain.model.seq.taxon import Taxon


class SeqClassificationProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_classification_protocols",
        table_name="seq_classification_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )
    is_taxonomic: bool = Field(
        description="Whether the category is based on phylogeny or not"
    )


class SeqCategorySet(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_category_sets",
        table_name="seq_category_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the category set", max_length=255)
    name: str = Field(description="The name of the category set", max_length=255)


class SeqCategory(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_categories",
        table_name="seq_category",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
        links=create_links(
            {
                1: (
                    "seq_category_set_id",
                    SeqCategorySet,
                    "seq_category_set",
                )
            }
        ),
    )
    code: str = Field(description="The code of the category", max_length=255)
    name: str = Field(description="The name of the category", max_length=255)
    seq_category_set_id: UUID = Field(
        description="The ID of the sequence category set. FOREIGN KEY"
    )
    seq_category_set: SeqCategorySet = Field(description="The sequence category set")


class SeqClassification(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_classifications",
        table_name="seq_classification",
        persistable=True,
        keys=create_keys({1: ("seq_id", "seq_classification_protocol_id")}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: (
                    "seq_classification_protocol_id",
                    SeqClassificationProtocol,
                    "seq_classification_protocol",
                ),
                3: ("primary_category_id", SeqCategory, "primary_category"),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    seq_classification_protocol_id: UUID = Field(
        description="The ID of the sequence classification protocol. FOREIGN KEY"
    )
    seq_classification_protocol: SeqClassificationProtocol = Field(
        description="The sequence classification protocol."
    )
    primary_category_id: UUID | None = Field(
        description="The ID of the category. FOREIGN KEY"
    )
    primary_category: SeqCategory = Field(description="The primary category.")
    classification: str = Field(description="The classification of the sequence.")
    classification_format: enum.SeqClassificationFormat = Field(
        default=enum.SeqClassificationFormat.SEQ_CLASSIFICATION_FORMAT1,
        description="The representation format of the classification.",
    )
    classification_hash: bytes = Field(
        description="The SHA256 hash of the sorted list of category ids as bytes.",
        min_length=32,
        max_length=32,
    )


class AstPrediction(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ast_predictions",
        table_name="ast_prediction",
        persistable=True,
        keys=create_keys({1: ("seq_id", "ast_protocol_id")}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("ast_protocol_id", AstProtocol, "ast_protocol"),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    ast_protocol_id: UUID = Field(
        description="The unique identifier for the AST protocol. FOREIGN KEY"
    )
    ast_protocol: AstProtocol | None = Field(
        default=None, description="The AST protocol."
    )
    ast_result: str = Field(description="The result of the AST prediction.")
    ast_result_format: enum.AstResultFormat = Field(
        default=enum.AstResultFormat.AST_RESULT_FORMAT1,
        description="The representation format of the AST result.",
    )


class TaxonomyProtocol(Model, ProtocolMixin):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="taxonomy_protocols",
        table_name="taxonomy_protocol",
        persistable=True,
        keys=create_keys({1: "code", 2: ("name", "version")}),
    )


class SeqTaxonomy(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_taxonomies",
        table_name="seq_taxonomy",
        persistable=True,
        keys=create_keys({1: "seq_id", 2: "taxonomy_protocol_id"}),
        links=create_links(
            {
                1: ("seq_id", Seq, "seq"),
                2: ("taxonomy_protocol_id", TaxonomyProtocol, "taxonomy_protocol"),
                3: ("primary_taxon_id", Taxon, "primary_taxon"),
            }
        ),
    )
    seq_id: UUID = Field(
        description="The unique identifier for the sequence. FOREIGN KEY"
    )
    seq: Seq | None = Field(default=None, description="The sequence.")
    taxonomy_protocol_id: UUID = Field(
        description="The unique identifier for the taxonomy protocol. FOREIGN KEY"
    )
    taxonomy_protocol: TaxonomyProtocol | None = Field(
        default=None, description="The taxonomy protocol."
    )
    primary_taxon_id: UUID = Field(
        description="The unique identifier for the primary taxon. FOREIGN KEY"
    )
    primary_taxon: Taxon | None = Field(default=None, description="The primary taxon.")
    taxonomy: str = Field(description="The taxonomy results of the sequence.")
    taxonomy_format: enum.TaxonomyFormat = Field(
        default=enum.TaxonomyFormat.TAXONOMY_FORMAT1,
        description="The representation format of the taxonomy.",
    )
    taxonomy_hash: bytes = Field(
        description="The SHA256 hash of the sorted list of taxon ids as bytes.",
        min_length=32,
        max_length=32,
    )
