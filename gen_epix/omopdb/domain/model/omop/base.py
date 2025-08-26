from uuid import UUID

from pydantic import Field


class DataLineageMixin:
    provenance_id: UUID | None = Field(default=None, description="Provenance ID")
    source_traceback: str | None = Field(
        default=None, description="Source traceback", max_length=255
    )
