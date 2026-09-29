"""Implement seqdb application service behavior for services.organization."""

from typing import Any

from gen_epix.commondb.services import OrganizationService as CommonOrganizationService
from gen_epix.seqdb.domain import model


class OrganizationService(CommonOrganizationService):
    """Encapsulates seqdb organization service behavior."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize organization operations with seqdb invitation constraints.

        Args:
            *args: Positional arguments accepted by the commondb service.
            **kwargs: Keyword arguments accepted by the commondb service.
        """
        super().__init__(
            *args,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            user_invitation_constraints_class=model.UserInvitationConstraints,
        )
