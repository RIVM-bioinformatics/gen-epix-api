"""OmopDB specialization of shared organization command handling."""

from typing import Any

from gen_epix.commondb.services import OrganizationService as CommonOrganizationService
from gen_epix.omopdb.domain import model


class OrganizationService(CommonOrganizationService):
    """Encapsulates handling of organization commands using OmopDB user and invitation models."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize the shared service with OmopDB model classes."""
        super().__init__(
            *args,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            user_invitation_constraints_class=model.UserInvitationConstraints,
        )
