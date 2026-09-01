"""Define seqdb domain models for domain.model.seq.category."""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity, create_keys, create_links


class SeqCategorySet(Model):
    """Group related sequence categories under a stable code and name."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="seq_category_sets",
        table_name="seq_category_set",
        persistable=True,
        keys=create_keys({1: "code", 2: "name"}),
    )
    code: str = Field(description="The code of the category set", max_length=255)
    name: str = Field(description="The name of the category set", max_length=255)


class SeqCategory(Model):
    """Classify a sequence within a named sequence category set."""

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
    seq_category_set: SeqCategorySet | None = Field(
        default=None, description="The sequence category set"
    )
