from abc import abstractmethod
from typing import Any
from uuid import UUID

from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.service.abac import BaseAbacService
from gen_epix.fastapp.pdp import PolicyDecisionPoint as FastappPolicyDecisionPoint


class BasePolicyDecisionPoint(FastappPolicyDecisionPoint):
    """Encapsulates Policy Decision Point (PDP) logic including for ABAC policies.

    In addition to the regular PDP logic, this centralizes the decision-making logic
    for ABAC policies that are intended to be applied during command execution either
    for performance reasons or because there is no good alternative to implement them
    otherwise.

    The PDP determines and applies access rights based on user roles, permissions, and
    other attributes. For the ABAC logic, it mainly forms a wrapper around the ABAC
    service's functionality that can easily be injected into other code.

    This class defines the interface and must be subclassed by concrete PDP
    implementations, and the instance injected during construction of the App as the
    App's PDP, so that it is readily available for use by the App's components at Policy
    Enforcement Points (PEPs).
    """

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any) -> None:
        """Initialize the PDP with necessary configurations."""
        super().__init__(**kwargs)
        self.abac_service = abac_service

    def get_command_user(self, cmd: command.Command) -> model.User | None:
        """Retrieve the user associated with the command.

        Raises:
            exc.ServiceException: If the command has a user without an ID.

        Returns:
            model.User|None: The user if available, otherwise None.
        """
        if cmd.user is None:
            return None
        if cmd.user.id is None:
            raise exc.ServiceException(
                "63980159", message="Command user must have an ID."
            )
        return cmd.user

    def get_command_user_id(self, cmd: command.Command) -> UUID | None:
        """Retrieve the user ID associated with the command.

        Raises:
            exc.ServiceException: If the command has a user without an ID.

        Returns:
            UUID|None: The user ID if available, otherwise None.
        """
        if cmd.user is None:
            return None
        if cmd.user.id is None:
            raise exc.ServiceException(
                "e61b3c09", message="Command user must have an ID."
            )
        return cmd.user.id

    @abstractmethod
    def is_exempted(self, cmd: command.Command) -> bool:
        """Check if the command is exempted from ABAC policies.

        Args:
            cmd: The command to check for exemption.

        Returns:
            bool: True if the command is exempted, False otherwise.

        Raises:
            NotImplementedError: If the exemption check is not implemented for the command type.
        """
        raise NotImplementedError()

    @abstractmethod
    def is_allowed(self, cmd: command.Command) -> bool:
        """Check if the command is allowed based on the ABAC policies.

        Args:
            cmd: The command to check for allowance.

        Returns:
            bool: True if the command is allowed, False otherwise.

        Raises:
            NotImplementedError: If the allowance check is not implemented for the command type.
        """
        raise NotImplementedError()
