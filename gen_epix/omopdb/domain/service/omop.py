"""Service contract for OmopDB person uploads and retrieval queries."""

from abc import abstractmethod

from gen_epix.fastapp import BaseService
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class BaseOmopService(BaseService[BaseOmopRepository]):
    """Define OmopDB command handlers and person-query operations."""

    SERVICE_TYPE = ServiceType.OMOP

    def register_handlers(self) -> None:
        """Register CRUD, upload, and person/specimen retrieval handlers."""
        self.register_default_crud_handlers()
        f = self.app.register_handler
        f(command.UploadPersonsCommand, self.upload_persons)
        f(command.RetrievePersonsByIdCommand, self.retrieve_persons_by_id)
        f(command.RetrievePersonsByQueryCommand, self.retrieve_persons_by_query)
        f(
            command.RetrieveSpecimenIdsByCohortIdsCommand,
            self.retrieve_specimen_ids_by_cohort_ids,
        )

    @abstractmethod
    def upload_persons(
        self, cmd: command.UploadPersonsCommand
    ) -> model.PersonBatchUploadResult:
        """Upload a batch of persons.

        Args:
            cmd: Command containing people and upload behavior.

        Returns:
            Result summarizing each person's upload outcome.

        Raises:
            NotImplementedError: Always, until a service implements uploads.
        """
        raise NotImplementedError()

    @abstractmethod
    def retrieve_persons_by_id(
        self, cmd: command.RetrievePersonsByIdCommand
    ) -> list[model.FullPerson]:
        """Retrieve full persons by their identifiers.

        Args:
            cmd: Command containing person identifiers.

        Returns:
            Fully populated persons matching the requested identifiers.

        Raises:
            NotImplementedError: Always, until a service implements retrieval.
        """
        raise NotImplementedError()

    @abstractmethod
    def retrieve_persons_by_query(
        self, cmd: command.RetrievePersonsByQueryCommand
    ) -> model.PersonQueryResult:
        """Retrieve persons matching a query.

        Args:
            cmd: Command containing person-query criteria.

        Returns:
            Person-query results and associated metadata.

        Raises:
            NotImplementedError: Always, until a service implements retrieval.
        """
        raise NotImplementedError()

    def retrieve_specimen_ids_by_cohort_ids(
        self, cmd: command.RetrieveSpecimenIdsByCohortIdsCommand
    ) -> model.SpecimenIdsByCohortResult:
        """Retrieve specimen IDs grouped by cohort ID."""
        specimen_ids_by_cohort_id = self.repository.get_specimen_ids_by_cohort_ids(
            cohort_definition_id=cmd.cohort_definition_id,
            cohort_ids=cmd.cohort_ids,
        )
        return model.SpecimenIdsByCohortResult(
            specimen_ids_by_cohort_id=specimen_ids_by_cohort_id
        )
