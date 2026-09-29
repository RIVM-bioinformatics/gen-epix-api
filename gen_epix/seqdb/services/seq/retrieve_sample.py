"""Implement seqdb sequence service behavior for services.seq.retrieve_sample."""

import gen_epix.seqdb.domain.command as command
import gen_epix.seqdb.domain.model as model
from gen_epix.fastapp import CrudOperation
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.seqdb.domain.repository import BaseSeqRepository
from gen_epix.seqdb.domain.service import BaseSeqService


def seq_service_retrieve_samples_by_id(
    self: BaseSeqService,
    cmd: command.RetrieveSamplesByIdCommand,
) -> list[model.FullSample]:
    """Retrieve all relevant FullSample records for the requested sample IDs."""
    sample_ids = cmd.sample_ids or []
    if not sample_ids:
        return []
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    return repository.get_full_samples_by_sample_ids(sample_ids)


def seq_service_retrieve_sample_identifiers_by_id(
    self: BaseSeqService,
    cmd: command.RetrieveSampleIdentifiersByIdCommand,
) -> list[model.SampleIdentifier]:
    """Retrieve only SampleIdentifier records for the requested sample IDs."""
    sample_ids = cmd.sample_ids or []
    if not sample_ids:
        return []
    user_id = cmd.user.id if cmd.user else None
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    with repository.uow() as uow:
        return repository.crud(
            uow,
            user_id,
            model.SampleIdentifier,
            CrudOperation.READ_ALL,
            filter=UuidSetFilter(key="internal_id", members=frozenset(sample_ids)),
        )


def seq_service_retrieve_samples_by_query(
    self: BaseSeqService,
    cmd: command.RetrieveSamplesByQueryCommand,
) -> model.SampleQueryResult:
    """Retrieve sample IDs based on query filters."""
    sample_query = cmd.sample_query
    repository: BaseSeqRepository = self.repository  # type: ignore[assignment]
    with repository.uow() as uow:
        sample_ids = repository.get_sample_ids_modified_in_range(
            uow=uow,
            modified_since=sample_query.modified_since,
            modified_until=sample_query.modified_until,
        )
    return model.SampleQueryResult(
        sample_query=sample_query,
        sample_ids=sample_ids,
        is_max_results_exceeded=False,
    )
