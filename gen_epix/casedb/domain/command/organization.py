from typing import ClassVar

import gen_epix.commondb.domain.command as common_command
from gen_epix.casedb.domain import enum, model
from gen_epix.commondb.util import copy_model_field


# Non-CRUD commands
class InviteUserCommand(common_command.InviteUserCommand):
    roles: set[enum.Role] = copy_model_field(common_command.InviteUserCommand, "roles")  # type: ignore[assignment]


# CRUD commands
class UserCrudCommand(common_command.UserCrudCommand):
    MODEL_CLASS: ClassVar = model.User


class UserInvitationCrudCommand(common_command.UserInvitationCrudCommand):
    MODEL_CLASS: ClassVar = model.UserInvitation
