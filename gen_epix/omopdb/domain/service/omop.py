from abc import abstractmethod
from uuid import UUID

from gen_epix.fastapp import BaseService, CrudOperation
from gen_epix.filter.composite import CompositeFilter
from gen_epix.filter.equals_uuid import EqualsUuidFilter
from gen_epix.filter.uuid_set import UuidSetFilter
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.domain.enum import ServiceType
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class BaseOmopService(BaseService[BaseOmopRepository]):
    SERVICE_TYPE = ServiceType.OMOP

    def register_handlers(self) -> None:
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
        """Upload persons in batch."""
        raise NotImplementedError()

    @abstractmethod
    def retrieve_persons_by_id(
        self, cmd: command.RetrievePersonsByIdCommand
    ) -> list[model.FullPerson]:
        """Retrieve persons by their IDs."""
        raise NotImplementedError()

    @abstractmethod
    def retrieve_persons_by_query(
        self, cmd: command.RetrievePersonsByQueryCommand
    ) -> model.PersonQueryResult:
        """Retrieve persons matching query criteria."""
        raise NotImplementedError()

    def retrieve_specimen_ids_by_cohort_ids(
        self, cmd: command.RetrieveSpecimenIdsByCohortIdsCommand
    ) -> model.SpecimenIdsByCohortResult:
        """
        Retrieve specimen IDs grouped by cohort ID.

        Looks up cohorts by cohort_definition_id and the given cohort_ids, then
        fetches the full person record for each cohort subject to collect their
        specimens.
        """
        cohorts: list[model.Cohort] = self.app.handle(
            command.CohortCrudCommand(
                user=cmd.user,
                operation=CrudOperation.READ_ALL,
                query_filter=CompositeFilter(
                    filters=[
                        EqualsUuidFilter(
                            key="cohort_definition_id",
                            value=cmd.cohort_definition_id,
                        ),
                        UuidSetFilter(
                            key="cohort_id",
                            members=frozenset(cmd.cohort_ids),
                        ),
                    ],
                ),
            )
        )
        # subject_id is the person_id equivalent; cohort_id is the case_id equivalent
        person_id_to_cohort_id: dict[UUID, UUID] = {
            c.subject_id: c.cohort_id  # type: ignore[misc]
            for c in cohorts
            if c.cohort_id is not None
        }
        if not person_id_to_cohort_id:
            return model.SpecimenIdsByCohortResult(specimen_ids_by_cohort_id={})
        full_persons: list[model.FullPerson] = self.app.handle(
            command.RetrievePersonsByIdCommand(
                user=cmd.user,
                person_ids=list(person_id_to_cohort_id.keys()),
            )
        )
        specimen_ids_by_cohort_id: dict[UUID, list[UUID]] = {}
        for full_person in full_persons:
            person_id = full_person.person.person_id
            cohort_id = person_id_to_cohort_id.get(person_id)  # type: ignore[arg-type]
            if cohort_id is None:
                continue
            specimen_ids_by_cohort_id[cohort_id] = [
                s.specimen_id  # type: ignore[misc]
                for s in full_person.specimens
                if s.specimen_id is not None
            ]
        return model.SpecimenIdsByCohortResult(
            specimen_ids_by_cohort_id=specimen_ids_by_cohort_id
        )
