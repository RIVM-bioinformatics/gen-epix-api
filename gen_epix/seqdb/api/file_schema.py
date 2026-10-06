"""Request and response models of the seqdb file API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from gen_epix.seqdb.domain import command, enum
from gen_epix.util import copy_model_field


class CreateFileRequestBody(PydanticBaseModel):
    """Represents a base64-encoded file creation request."""

    content: str = Field(description="The content of the file as base64 encoded bytes.")
    format: enum.FileFormat = copy_model_field(command.CreateFileCommand, "format")
    compression: enum.FileCompression = copy_model_field(
        command.CreateFileCommand, "compression"
    )
