# pylint: disable=too-few-public-methods
# This module defines base classes, methods are added later


from typing import ClassVar, Self
from uuid import UUID

from pydantic import model_validator

from gen_epix.fastapp.services import auth
from gen_epix.seqdb.domain import DOMAIN, enum
from gen_epix.seqdb.domain.command.base import Command


# auth
class GetIdentityProvidersCommand(auth.GetIdentityProvidersCommand):
    SERVICE_TYPE: ClassVar = enum.ServiceType.AUTH


# organization
class RetrieveCompleteUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION


class InviteUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    email: str
    roles: set[enum.Role]


class RegisterInvitedUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION
    token: str


class UpdateUserCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.ORGANIZATION

    tgt_user_id: UUID
    is_active: bool | None
    roles: set[enum.Role] | None
    data_collection_ids: set[UUID] | None
    organization_id: UUID | None


# system
class RetrieveOutagesCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SYSTEM
    pass


class RetrieveCompleteContigCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ


class RetrieveCompleteAlleleProfileCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ


class RetrieveCompleteSnpProfileCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ


class RetrieveCompleteSeqCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ

    seq_ids: list[UUID]


class RetrieveCompleteSampleCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ


class RetrievePhylogeneticTreeCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ

    seq_distance_protocol_id: UUID
    tree_algorithm: enum.TreeAlgorithm
    seq_ids: list[UUID]
    leaf_names: list[str] | None

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        if self.leaf_names is not None and len(self.leaf_names) != len(self.seq_ids):
            raise ValueError(
                "leaf_codes must be None or have the same length as seq_ids"
            )
        return self


class RetrieveMultipleAlignmentCommand(Command):
    SERVICE_TYPE: ClassVar = enum.ServiceType.SEQ


DOMAIN.register_locals(locals())
