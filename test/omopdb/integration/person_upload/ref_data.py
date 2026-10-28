from dataclasses import dataclass
from uuid import UUID

from gen_epix.omopdb.domain import model


@dataclass(frozen=True)
class RefData:
    """The user, concept and identifier issuer the tests upload persons with."""

    root_user: model.User
    concept_id: UUID
    identifier_issuer_id: UUID
