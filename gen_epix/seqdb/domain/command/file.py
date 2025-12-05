from typing import ClassVar

from pydantic import Field

from gen_epix.commondb.domain.command import Command, CrudCommand
from gen_epix.seqdb.domain import enum, model


# Non-CRUD commands
class CreateFileCommand(Command):
    """
    Create a file. The given expected format and compression are used to verify the
    file content.
    """

    file: model.File = Field(description="The file to create.")
    format: enum.FileFormat = Field(description="The expected format of the file.")
    compression: enum.FileCompression = Field(
        default=enum.FileCompression.NONE,
        description="The expected compression of the file.",
    )


# CRUD commands
class FileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.File
