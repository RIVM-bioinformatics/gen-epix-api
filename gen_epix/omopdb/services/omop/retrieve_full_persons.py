from datetime import datetime

import gen_epix.omopdb.domain.command as command
import gen_epix.omopdb.domain.model as model
from gen_epix.omopdb.services.omop.base import BaseOmopService


def omop_service_retrieve_full_persons(
    self: BaseOmopService, cmd: command.RetrieveFullPersonsCommand
) -> list[model.FullPerson]:
    """
    Retrieve all relevant FullPersons, containing all Person-linked data.
    The (modified_since, modified_until) range is only used to identify the Persons.
    If some of their data are outside of this range, it is to be included nonetheless.
    """
    person_ids = cmd.person_ids or []
    modified_since = cmd.modified_since
    modified_until = cmd.modified_until

    # validate if person_ids are unique
    if len(set(person_ids)) != len(person_ids):
        raise ValueError("person_ids must be unique")

    # validate if modified_since is before modified_until
    if modified_since and modified_until and modified_since > modified_until:
        raise ValueError("modified_since must be before modified_until")

    # validate that either person_ids or modified_since/modified_until is provided (but not both)
    has_person_ids = bool(person_ids)
    has_modified_range = modified_since or modified_until

    if not (has_person_ids or has_modified_range):
        raise ValueError(
            "Either person_ids or modified_since/modified_until must be provided"
        )
    if has_person_ids and has_modified_range:
        raise ValueError(
            "Cannot provide both person_ids and modified_since/modified_until"
        )

    # validate that modified values are datetime values
    if modified_since and not isinstance(modified_since, datetime):
        raise ValueError("modified_since must be a datetime value")
    if modified_until and not isinstance(modified_until, datetime):
        raise ValueError("modified_until must be a datetime value")

    if person_ids == []:

        with self.repository.uow() as uow:
            person_ids = self.repository.get_person_ids_modified_in_range(
                uow=uow,
                modified_since=modified_since,
                modified_until=modified_until,
            )

    if person_ids == []:
        return []

    full_persons: list[model.FullPerson] = (
        self.repository.get_full_persons_by_person_ids(person_ids)
    )

    return full_persons
