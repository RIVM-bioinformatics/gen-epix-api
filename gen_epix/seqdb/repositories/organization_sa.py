"""Provide seqdb persistence behavior for repositories.organization_sa."""

from typing import Any

from sqlalchemy import Engine

from gen_epix.commondb.repositories import (
    OrganizationSARepository as CommonOrganizationSARepository,
)
from gen_epix.commondb.repositories import sa_model
from gen_epix.seqdb.domain import model


class OrganizationSARepository(CommonOrganizationSARepository):
    """Encapsulates seqdb persistence behavior for SQL-based organization repositories."""

    def __init__(
        self,
        engine: Engine,
        **kwargs: Any,
    ):
        """Initialize the repository with seqdb SQLAlchemy model types.

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
