"""Provide seqdb persistence behavior for repositories.organization_dict."""

from collections.abc import Hashable, Iterable

from gen_epix.commondb.repositories import (
    OrganizationDictRepository as CommonOrganizationDictRepository,
)
from gen_epix.fastapp import Entity
from gen_epix.seqdb.domain import model
from gen_epix.seqdb.domain.model import Model


class OrganizationDictRepository(CommonOrganizationDictRepository):
    """Encapsulates seqdb persistence behavior for organization dictionaries."""

    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[type[Model], dict[Hashable, Model]],
        **kwargs: Any,
    ):
        """Initialize the repository with seqdb user and invitation model types.

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
