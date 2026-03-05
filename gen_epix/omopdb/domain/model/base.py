from datetime import datetime
from uuid import UUID

from dateutil.tz import UTC
from pydantic import Field

# from gen_epix.commondb.domain.model.base import ModelNoId
from gen_epix.fastapp import Model as FastappModel


class ModelNoId(FastappModel):

    created_at: datetime | None = Field(
        default=None,
        description="The UTC datetime when the object was created.",
    )
    modified_at: datetime | None = Field(
        default=None,
        description="The UTC datetime when the object was last modified.",
    )
    modified_by: UUID | None = Field(
        default=None,
        description="The ID of the user who last modified the object.",
    )

    def set_modified(self, user_id: UUID, override: bool = False) -> None:
        if self.modified_at is None or override:
            now = datetime.now(UTC)
            self.modified_at = now
            self.modified_by = user_id

    def set_created(self, user_id: UUID, override: bool = False) -> None:
        if self.created_at is None or override:
            now = datetime.now(UTC)
            self.modified_at = now
            self.modified_by = user_id
            self.created_at = now


class Model(ModelNoId):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the obj.",
    )
