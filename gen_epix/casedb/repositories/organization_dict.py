"""Provide casedb dictionary persistence behavior for organization data."""

from collections.abc import Hashable, Iterable
from typing import Any

from gen_epix.casedb.domain import model
from gen_epix.casedb.domain.model import Model
from gen_epix.commondb.repositories import (
    OrganizationDictRepository as CommonOrganizationDictRepository,
)
from gen_epix.fastapp import Entity


class OrganizationDictRepository(CommonOrganizationDictRepository):
    """Encapsulates casedb persistence behavior for organization dictionaries."""

    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[type[Model], dict[Hashable, Model]],
        **kwargs: Any,
    ):
        """Initialize the repository with casedb user and invitation model types.

        Args:
            entities: Entity metadata available to the repository.
            db: Dictionary-backed persistent model store.
            **kwargs: Additional commondb repository configuration.
        """
        super().__init__(
            entities,
            db,
            **kwargs,
            user_class=model.User,
            user_invitation_class=model.UserInvitation,
        )
