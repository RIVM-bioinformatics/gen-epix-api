from typing import ClassVar

from gen_epix.commondb.domain.command import CrudCommand
from gen_epix.seqdb.domain import model


class FileCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.File
