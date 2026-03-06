from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model.base import ModelNoId as ModelNoId


class Model(ModelNoId):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )
