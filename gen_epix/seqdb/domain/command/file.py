"""Define seqdb command objects for domain.command.file."""

from typing import ClassVar

from pydantic import Field

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.seqdb.domain import enum, model


# Non-CRUD commands
class CreateFileCommand(Command):
    """Represents file creation after validating its expected format and compression.

    The expected format and compression determine how the file content is verified.
    """

    file: model.File = Field(description="The file to create.")
    format: enum.FileFormat = Field(description="The expected format of the file.")
    compression: enum.FileCompression = Field(
        default=enum.FileCompression.NONE,
        description="The expected compression of the file.",
    )


# CRUD commands
class FileCrudCommand(CrudCommand):
    """Represents a standard CRUD operation on persisted seqdb file records."""

    MODEL_CLASS: ClassVar = model.File
