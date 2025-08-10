from typing import ClassVar

import gen_epix.casedb.domain.model.subject as model
from gen_epix.common.domain.command import CrudCommand

# Non-CRUD


# CRUD


class SubjectCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.Subject


class SubjectIdentifierCrudCommand(CrudCommand):
    MODEL_CLASS: ClassVar = model.SubjectIdentifier
