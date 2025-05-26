from gen_epix.fastapp import PermissionType, Policy
from gen_epix.seqdb.domain import command
from gen_epix.seqdb.domain.service.system import BaseSystemService


class BaseHasSystemOutagePolicy(Policy):
    """
    Policy that checks if the system has a current outage

    """

    def __init__(
        self,
        system_service: BaseSystemService,
        **kwargs: dict,
    ):
        self.system_service = system_service
        self.props = kwargs
        self.outage_update_permission = system_service.app.domain.get_permission(
            command.OutageCrudCommand, PermissionType.UPDATE
        )
