"""Implement seqdb sequence service behavior for SeqDistance retrieval (and Phylogenetic tree calculation)."""

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain import command, model
from gen_epix.seqdb.domain.repository.seq import BaseSeqRepository
from gen_epix.seqdb.domain.service.seq import BaseSeqService


def seq_service_retrieve_seq_distances_by_seq_profiles(
    self: BaseSeqService,
    cmd: command.RetrieveSeqDistancesBySeqProfilesCommand,
) -> list[model.SeqDistance]:
    """Retrieve stored distance records for sequence profiles and a protocol."""
    user_id = cmd.user.id if cmd.user else None
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    with repository.uow() as uow:
        return repository.crud(
            uow,
            user_id,
            model.SeqDistance,
            CrudOperation.READ_ALL,
            filter=CompositeFilter(
                filters=[
                    UuidSetFilter(
                        key="seq_profile_id",
                        members=frozenset(cmd.seq_profile_ids),
                    ),
                    EqualsUuidFilter(
                        key="protocol_id",
                        value=cmd.protocol_id,
                    ),
                ],
                operator=LogicalOperator.AND,
            ),
        )
