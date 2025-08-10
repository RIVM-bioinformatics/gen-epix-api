from gen_epix.common.domain import enum
from gen_epix.common.domain.command.base import Command

# Non-CRUD commands


class GetOwnPermissionsCommand(Command):
    SERVICE_TYPE = enum.ServiceType.RBAC


# CRUD commands
