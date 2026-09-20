from typing import Any

from gen_epix.commondb.domain import command
from gen_epix.commondb.domain.policy.pdp import BasePolicyDecisionPoint
from gen_epix.commondb.domain.service import BaseAbacService


class PolicyDecisionPoint(BasePolicyDecisionPoint):
    """Encapsulates the Policy Decision Point (PDP) for commondb."""

    def __init__(self, abac_service: BaseAbacService, **kwargs: Any) -> None:
        """Initialize the PDP with necessary configurations."""
        super().__init__(**kwargs)
        self.abac_service = abac_service

    def is_exempted(self, cmd: command.Command) -> bool:
        """Check if the command is exempted from ABAC policies based on the user's roles.

        Args:
            cmd: The command to check for exemption.

        Returns:
            bool: True if the command is exempted, False otherwise.
        """
        user = self.get_command_user(cmd)
        if user is None:
            return True
        exempted_role_set = self.abac_service.ABAC_EXEMPTED_ROLE_SET_MAP.get(type(cmd))
        if exempted_role_set is None:
            return False
        has_exempted_role = bool(
            user.roles & {x.value for x in exempted_role_set.value}
        )
        return has_exempted_role

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
