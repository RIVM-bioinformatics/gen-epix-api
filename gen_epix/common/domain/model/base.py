from uuid import UUID

from pydantic import Field

from gen_epix import fastapp


class Model(fastapp.Model):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )
