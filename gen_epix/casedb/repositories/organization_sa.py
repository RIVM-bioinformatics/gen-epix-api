"""Provide casedb SQLAlchemy persistence behavior for organization data."""

from typing import Any

from sqlalchemy import Engine

from gen_epix.casedb.domain import model
from gen_epix.commondb.repositories import (
    OrganizationSARepository as CommonOrganizationSARepository,
)
from gen_epix.commondb.repositories import (
    sa_model,
)


class OrganizationSARepository(CommonOrganizationSARepository):
    """Encapsulates casedb persistence behavior for SQL organization data."""

    def __init__(
        self,
        engine: Engine,
        **kwargs: Any,
    ):
        """Initialize the repository with casedb SQLAlchemy model types.

        Args:
            engine: SQLAlchemy engine backing organization persistence.
            **kwargs: Additional commondb repository configuration.
        """
        super().__init__(
            engine,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
            sa_user_class=sa_model.User,
            sa_user_invitation_class=sa_model.UserInvitation,
            **kwargs,
        )
