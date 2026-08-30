"""Define SeqDB domain models for domain.model.file."""

from typing import ClassVar

from pydantic import Field

from gen_epix.commondb.domain.model.base import Model
from gen_epix.fastapp.domain import Entity


class File(Model):
    ENTITY: ClassVar = Entity(
        snake_case_plural_name="files",
        table_name="file",
        persistable=True,
    )
    content: bytes = Field(description="The content of the file.")
