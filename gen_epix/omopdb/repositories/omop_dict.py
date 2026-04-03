from datetime import datetime
from uuid import UUID

from gen_epix.fastapp.repositories import DictRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class OmopDictRepository(DictRepository, BaseOmopRepository):

    def get_person_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:

        df: dict[UUID, model.Person] = self.db[model.Person]  # type: ignore[assignment]
        modified_person_ids: list[UUID] = []
        for person_id, person in df.items():
            if person.modified_at is None:
                continue
            # Check if person's modified_at falls within specified range(s)
            if modified_since and person.modified_at < modified_since:
                continue
            if modified_until and person.modified_at > modified_until:
                continue
            modified_person_ids.append(person_id)

        return modified_person_ids

    def get_observations_by_person_id(
        self,
        person_id: UUID,
    ) -> list[model.Observation]:

        all_observations: dict[UUID, model.Observation] = self.db[model.Observation]  # type: ignore[assignment]
        return [x for x in all_observations.values() if x.person_id == person_id]

    def get_measurements_by_person_id(
        self,
        person_id: UUID,
    ) -> list[model.Measurement]:

        all_measurements: dict[UUID, model.Measurement] = self.db[model.Measurement]  # type: ignore[assignment]
        return [x for x in all_measurements.values() if x.person_id == person_id]

    def get_specimens_by_person_id(
        self,
        person_id: UUID,
    ) -> list[model.Specimen]:

        all_specimens: dict[UUID, model.Specimen] = self.db[model.Specimen]  # type: ignore[assignment]
        return [x for x in all_specimens.values() if x.person_id == person_id]

    def get_measurement_relations_by_person_id(
        self,
        person_id: UUID,
    ) -> list[model.MeasurementRelation]:

        all_measurement_relations: dict[UUID, model.MeasurementRelation] = self.db[model.MeasurementRelation]  # type: ignore[assignment]
        return [
            x for x in all_measurement_relations.values() if x.person_id == person_id
        ]

    def get_full_persons_by_person_ids(
        self,
        person_ids: list[UUID],
    ) -> list[model.FullPerson]:

        full_persons: list[model.FullPerson] = []
        for person_id in person_ids:
            person: model.Person = self.db[model.Person][person_id]  # type: ignore[assignment]
            person_observations = self.get_observations_by_person_id(person_id)
            person_measurements = self.get_measurements_by_person_id(person_id)
            person_specimens = self.get_specimens_by_person_id(person_id)
            person_measurement_relations = self.get_measurement_relations_by_person_id(
                person_id
            )
            full_persons.append(
                model.FullPerson(
                    # Person required fields (since FullPerson inherits from Person)
                    person_id=person_id,
                    gender_concept_id=person.gender_concept_id,
                    year_of_birth=person.year_of_birth,
                    race_concept_id=person.race_concept_id,
                    ethnicity_concept_id=person.ethnicity_concept_id,
                    person_type_concept_id=person.person_type_concept_id,
                    # FullPerson-specific fields
                    observations=person_observations,
                    measurements=person_measurements,
                    specimens=person_specimens,
                    measurement_relations=person_measurement_relations,
                )
            )

        return full_persons
