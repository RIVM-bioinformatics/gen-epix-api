from datetime import datetime
from typing import cast
from uuid import UUID

import sqlalchemy as sa

import gen_epix.omopdb.repositories.sa_model.omop as sa_model
from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import model
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository


class OmopSARepository(SARepository, BaseOmopRepository):

    def get_person_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        conditions = []
        if modified_since is not None:
            conditions.append(sa_model.Person.modified_at >= modified_since)
        if modified_until is not None:
            conditions.append(sa_model.Person.modified_at <= modified_until)

        stmt = sa.select(sa_model.Person.person_id).where(*conditions)
        assert isinstance(uow, SAUnitOfWork)
        return [row[0] for row in uow.session.execute(stmt)]

    def _get_person_by_person_id(
        self,
        uow: SAUnitOfWork,
        person_id: UUID,
    ) -> model.Person:
        stmt = sa.select(sa_model.Person).where(sa_model.Person.person_id == person_id)
        row = uow.session.execute(stmt).one()
        return cast(model.Person, self.get_mapper(model.Person).load(row[0]))

    def _get_observations_by_person_id(
        self,
        uow: SAUnitOfWork,
        person_id: UUID,
    ) -> list[model.Observation]:
        stmt = sa.select(sa_model.Observation).where(
            sa_model.Observation.person_id == person_id
        )
        mapper = self.get_mapper(model.Observation)
        return cast(
            list[model.Observation],
            [mapper.load(row[0]) for row in uow.session.execute(stmt)],
        )

    def _get_measurements_by_person_id(
        self,
        uow: SAUnitOfWork,
        person_id: UUID,
    ) -> list[model.Measurement]:
        stmt = sa.select(sa_model.Measurement).where(
            sa_model.Measurement.person_id == person_id
        )
        mapper = self.get_mapper(model.Measurement)
        return cast(
            list[model.Measurement],
            [mapper.load(row[0]) for row in uow.session.execute(stmt)],
        )

    def _get_specimens_by_person_id(
        self,
        uow: SAUnitOfWork,
        person_id: UUID,
    ) -> list[model.Specimen]:
        stmt = sa.select(sa_model.Specimen).where(
            sa_model.Specimen.person_id == person_id
        )
        mapper = self.get_mapper(model.Specimen)
        return cast(
            list[model.Specimen],
            [mapper.load(row[0]) for row in uow.session.execute(stmt)],
        )

    def _get_measurement_relations_by_person_id(
        self,
        uow: SAUnitOfWork,
        person_id: UUID,
    ) -> list[model.MeasurementRelation]:
        stmt = sa.select(sa_model.MeasurementRelation).where(
            sa_model.MeasurementRelation.person_id == person_id
        )
        mapper = self.get_mapper(model.MeasurementRelation)
        return cast(
            list[model.MeasurementRelation],
            [mapper.load(row[0]) for row in uow.session.execute(stmt)],
        )

    def get_full_persons_by_person_ids(
        self,
        person_ids: list[UUID],
    ) -> list[model.FullPerson]:
        with self.uow() as uow:
            assert isinstance(uow, SAUnitOfWork)
            full_persons: list[model.FullPerson] = []
            for person_id in person_ids:
                person = self._get_person_by_person_id(uow, person_id)
                observations = self._get_observations_by_person_id(uow, person_id)
                measurements = self._get_measurements_by_person_id(uow, person_id)
                specimens = self._get_specimens_by_person_id(uow, person_id)
                measurement_relations = self._get_measurement_relations_by_person_id(
                    uow, person_id
                )
                full_persons.append(
                    model.FullPerson(
                        **person.model_dump(),
                        observations=observations,
                        measurements=measurements,
                        specimens=specimens,
                        measurement_relations=measurement_relations,
                    )
                )
            return full_persons
