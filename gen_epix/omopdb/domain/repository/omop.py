"""Repository contract for querying OMOP persons and cohort specimens."""

import abc
from datetime import datetime
from uuid import UUID

from gen_epix.fastapp import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import model


class BaseOmopRepository(BaseRepository):
    """Define persistence operations for OmopDB person and specimen queries."""

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

        `modified_since` is inclusive and `modified_until` is exclusive.

        Args:
            uow: Unit of work used for the query.
            modified_since: Inclusive lower timestamp bound.
            modified_until: Exclusive upper timestamp bound.

        Returns:
            Identifiers of persons modified within the requested interval.

        Raises:
            NotImplementedError: Always, until a repository implements the query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_full_persons_by_person_ids(
        self,
        person_ids: list[UUID],
    ) -> list[model.FullPerson]:
        """
        Retrieve all relevant data for the specified person IDs as full persons.

        Args:
            person_ids: Identifiers of persons to retrieve.

        Returns:
            Fully populated person records.

        Raises:
            NotImplementedError: Always, until a repository implements the query.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_specimen_ids_by_cohort_ids(
        self,
        cohort_definition_id: UUID,
        cohort_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]:
        """
        Return specimen IDs grouped by cohort ID for a cohort definition.

        Args:
            cohort_definition_id: Cohort definition constraining the query.
            cohort_ids: Cohort identifiers to include.

        Returns:
            Specimen identifiers grouped by cohort identifier.

        Raises:
            NotImplementedError: Always, until a repository implements the query.
        """
        raise NotImplementedError()
