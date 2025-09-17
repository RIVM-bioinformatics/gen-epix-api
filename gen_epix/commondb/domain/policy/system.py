from typing import Any

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.service.system import BaseSystemService
from gen_epix.fastapp import PermissionType, Policy


class BaseHasSystemOutagePolicy(Policy):
    """
    Policy that checks if the system has a current outage

    """

    def __init__(
        self,
        system_service: BaseSystemService,
        **kwargs: Any,
    ):
        self.system_service = system_service
        self.props = kwargs
        self.outage_update_permission = system_service.app.domain.get_permission(
            command.OutageCrudCommand, PermissionType.UPDATE
        )
