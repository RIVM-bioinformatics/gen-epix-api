"""Retrieve OMOP persons by identifier or modification-time query.

The public service functions delegate person lookups to the OMOP repository.
Identifier retrieval returns complete person records; query retrieval returns
matching identifiers within a repository-managed unit of work.
"""

from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.omop.base import BaseOmopService


def omop_service_retrieve_persons_by_id(
    self: BaseOmopService, cmd: command.RetrievePersonsByIdCommand
) -> list[model.FullPerson]:
    """Retrieve full person records for the requested identifiers.

    All linked data for each requested person is included. An empty identifier
    list returns an empty result without querying the repository.
    """
    person_ids = cmd.person_ids or []
    if person_ids == []:
        return []
    full_persons: list[model.FullPerson] = (
        self.repository.get_full_persons_by_person_ids(person_ids)
    )
    return full_persons


def omop_service_retrieve_persons_by_query(
    self: BaseOmopService, cmd: command.RetrievePersonsByQueryCommand
) -> model.PersonQueryResult:
    """Retrieve person IDs matching a query.

    The IDs can then be used to retrieve the corresponding person data.
    """
    # At present, the query only contains modified_since and modified_until, but in the
    # future it may be expanded with other fields.
    person_query = cmd.person_query
    with self.repository.uow() as uow:
        person_ids = self.repository.get_person_ids_modified_in_range(
            uow=uow,
            modified_since=person_query.modified_since,
            modified_until=person_query.modified_until,
        )
    return model.PersonQueryResult(
        person_query=person_query,
        person_ids=person_ids,
        is_max_results_exceeded=False,  # This service does not currently support max_results, so it can never be exceeded
    )
