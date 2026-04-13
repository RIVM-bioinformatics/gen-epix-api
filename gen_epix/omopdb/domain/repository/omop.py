import abc
from datetime import datetime
from uuid import UUID

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import model


class BaseOmopRepository(BaseRepository):

    @abc.abstractmethod
    def get_person_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        """
        Retrieve a list of person IDs for Persons, including their linked data, modified
        in the specified range. At least one of modified_since or modified_until must be
        provided.

        modified_since is inclusive, modified_until is exclusive.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_full_persons_by_person_ids(
        self,
        person_ids: list[UUID],
    ) -> list[model.FullPerson]:
        """
        Retrieve all relevant data for the specified person_ids, and construct FullPersons.
        """
        raise NotImplementedError()
