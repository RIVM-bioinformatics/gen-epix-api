from typing import ClassVar

from gen_epix.common.domain import enum
from gen_epix.fastapp.services import auth


# Non-CRUD commands
class GetIdentityProvidersCommand(auth.GetIdentityProvidersCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.AUTH


# CRUD commands
