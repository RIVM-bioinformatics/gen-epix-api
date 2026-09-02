"""Configure organization services with casedb-specific user models."""

from typing import Any

from gen_epix.casedb.domain import model
from gen_epix.commondb.services import OrganizationService as CommonOrganizationService


class OrganizationService(CommonOrganizationService):
    """Encapsulates organization operations using casedb user model types."""

    def __init__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize organization handling with casedb model specializations.

        Args:
            *args: Positional arguments for the common organization service.
            **kwargs: Keyword arguments for the common organization service.
        """
        super().__init__(
            *args,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            user_invitation_constraints_class=model.UserInvitationConstraints,
        )
