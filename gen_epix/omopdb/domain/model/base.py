from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Model as ServiceModel


class Model(ServiceModel):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )
