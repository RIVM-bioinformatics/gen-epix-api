from typing import ClassVar

import gen_epix.common.domain.command as common_command
from gen_epix.seqdb.domain import enum, model


class UserCrudCommand(common_command.UserCrudCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    MODEL_CLASS: ClassVar = model.User


class UserInvitationCrudCommand(common_command.UserInvitationCrudCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    MODEL_CLASS: ClassVar = model.UserInvitation
