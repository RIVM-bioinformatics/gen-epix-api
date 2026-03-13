from datetime import UTC, datetime
from uuid import UUID

from pydantic import Field

from gen_epix import fastapp


class ModelNoId(fastapp.Model):

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

    def set_modified(self, user_id: UUID) -> None:
        now = datetime.now(UTC)
        self.modified_at = now
        self.modified_by = user_id

    def set_created(self, user_id: UUID) -> None:
        now = datetime.now(UTC)
        self.modified_at = now
        self.modified_by = user_id
        self.created_at = now


class Model(ModelNoId):
    id: UUID | None = Field(
        default=None,
        description="The unique identifier for the object.",
    )
