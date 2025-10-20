from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity


class File(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="files",
        table_name="file",
        persistable=True,
    )
    id: UUID | None = Field(description="The id of the file.")
    size_bytes: int = Field(description="The size of the file in bytes.")
    hash_sha256: bytes = Field(description="The SHA256 hash of the file.")
    content: bytes = Field(description="The content of the file.")
