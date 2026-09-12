"""Provide abstract commondb attribute-based access-control policy contracts.

These policies depend on an ABAC service to determine organization scope before
concrete implementations allow reads, user updates, or administration actions.
"""

import abc
from collections.abc import Callable
from typing import Any
from uuid import UUID

from gen_epix.commondb.domain.command import Command
from gen_epix.commondb.domain.service import BaseAbacService
from gen_epix.fastapp.model import Policy


class BaseAbacPolicy(Policy):
    """Encapsulates a base policy that holds the ABAC service used for scope decisions."""

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any):
        """Initialize the policy with its ABAC service and configuration properties.

        Args:
            abac_service: Service that resolves organization-level permissions.
            **kwargs: Policy-specific configuration properties.
        """
        super().__init__()
        self.abac_service = abac_service
        self.props = kwargs


class BaseIsOrganizationAdminPolicy(BaseAbacPolicy):
    """Encapsulates organization-administration scope resolution for commands."""

    @abc.abstractmethod
    def register_retrieve_organization_ids_handler(
        self,
        command_class: type[Command],
        handler: Callable[[Command], set[UUID]],
    ) -> None:
        """Register an organization-scope resolver for a command class.

        Args:
            command_class: The command type that requires organization scoping.
            handler: Resolves permitted organization IDs from a command instance.

        Raises:
            NotImplementedError: Always; concrete policies provide registration.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def retrieve_organization_ids(self, cmd: Command) -> set[UUID]:
        """Resolve the organization IDs addressed by a command.

        Args:
            cmd: The command to scope to organizations.

        Returns:
            The organization IDs relevant to the command.

        Raises:
            NotImplementedError: Always; concrete policies provide resolution.
        """
        raise NotImplementedError()


class BaseReadOrganizationResultsOnlyPolicy(BaseAbacPolicy):
    """Encapsulates a policy that limits reads to the user's organization results."""

    pass


class BaseReadSelfResultsOnlyPolicy(BaseAbacPolicy):
    """Encapsulates a policy that limits reads to results owned by the current user."""

    pass


class BaseReadUserPolicy(BaseAbacPolicy):
    """Encapsulates a policy governing which user records a caller may read."""

    pass


class BaseUpdateUserPolicy(BaseAbacPolicy):
    """Encapsulates a policy governing which user records a caller may update."""

    pass
