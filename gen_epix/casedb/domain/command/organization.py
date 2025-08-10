from typing import ClassVar

import gen_epix.common.domain.command as common_command
from gen_epix.casedb.domain import enum, model


class UserCrudCommand(common_command.UserCrudCommand):
    MODEL_CLASS: ClassVar = model.User


class UserInvitationCrudCommand(common_command.UserInvitationCrudCommand):
    MODEL_CLASS: ClassVar = model.UserInvitation
