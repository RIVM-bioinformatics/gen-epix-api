"""Repository-backed workflows for retrieving OMOP persons and identifiers."""

import gen_epix.omopdb.domain.command as command
import gen_epix.omopdb.domain.model as model
from gen_epix.omopdb.services.omop.base import BaseOmopService


def omop_service_retrieve_persons_by_id(
    self: BaseOmopService, cmd: command.RetrievePersonsByIdCommand
) -> list[model.FullPerson]:
    """
    Retrieve all relevant FullPersons, containing all Person-linked data.
    The (modified_since, modified_until) range is only used to identify the Persons.
    If some of their data are outside of this range, it is to be included nonetheless.
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
    """
    Retrieve person IDs based on a query. These IDs can then be used to retrieve the
    actual data for these persons.
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
