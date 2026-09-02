"""OmopDB base model with optional UUID identity metadata."""

from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model.base import ModelNoId as ModelNoId


class Model(ModelNoId):
    """Represents the shared model contract with an optional OmopDB object ID."""

    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )
