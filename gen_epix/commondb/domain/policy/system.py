"""Provide a policy contract that protects commands during system outages."""

from typing import Any

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.service.system import BaseSystemService
from gen_epix.fastapp import PermissionType, Policy


class BaseHasSystemOutagePolicy(Policy):
    """Define a policy that restricts commands while a system outage is active."""

    def __init__(
        self,
        system_service: BaseSystemService,
        **kwargs: Any,
    ):
        """Initialize the policy with outage state and its update permission.

        Args:
            system_service: Service that exposes current system outage state.
            **kwargs: Policy-specific configuration properties.
        """
        self.system_service = system_service
        self.props = kwargs
        self.outage_update_permission = system_service.app.domain.get_permission(
            command.OutageCrudCommand, PermissionType.UPDATE
        )
