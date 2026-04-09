from datetime import datetime
from typing import cast
from uuid import UUID

import sqlalchemy as sa

from gen_epix.fastapp.repositories import SARepository, SAUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import enum, model
from gen_epix.omopdb.domain.repository.omop import BaseOmopRepository
from gen_epix.omopdb.repositories import sa_model as sa_model


class OmopSARepository(SARepository, BaseOmopRepository):

    def get_person_ids_modified_in_range(
        self,
        uow: BaseUnitOfWork,
        modified_since: datetime | None = None,
        modified_until: datetime | None = None,
    ) -> list[UUID]:
        assert isinstance(uow, SAUnitOfWork)
        modified_person_ids: set[UUID] = set()
        for model_class in [model.Person] + model.FullPerson.DATA_CLASSES:
            sa_model_class = sa_model.SA_MODELS_BY_SERVICE_TYPE[enum.ServiceType.OMOP][
                model_class
            ]
            conditions = []
            if modified_since is not None:
                conditions.append(sa_model_class.modified_at >= modified_since)  # type: ignore[attr-defined]
            if modified_until is not None:
                conditions.append(sa_model_class.modified_at < modified_until)  # type: ignore[attr-defined]
            stmt = sa.select(sa_model_class.person_id).where(*conditions)  # type: ignore[attr-defined]
            modified_person_ids.update(row[0] for row in uow.session.execute(stmt))
        return sorted(modified_person_ids)

    def get_full_persons_by_person_ids(
        self,
        person_ids: list[UUID],
    ) -> list[model.FullPerson]:
        if not person_ids:
            return []

        # Initialize some
        person_id_set = set(person_ids)
        model_classes = (
            [model.Person, model.PersonIdentifier]
            + model.FullPerson.DATA_CLASSES
            + model.FullPerson.IDENTIFIER_CLASSES
        )
        db: dict[type[model.Model], dict[UUID, list[model.Model]]] = {
            model_class: {person_id: [] for person_id in person_ids}
            for model_class in model_classes
        }

        # Retrieve all data and create FullPersons
        with self.uow() as uow:
            assert isinstance(uow, SAUnitOfWork)
            # Retrieve all data per person
            for model_class in model_classes:
                sa_model_class = sa_model.SA_MODELS_BY_SERVICE_TYPE[
                    enum.ServiceType.OMOP
                ][model_class]
                id_field_name = (
                    "person_id"
                    if model_class in [model.Person] + model.FullPerson.DATA_CLASSES
                    else "internal_id"
                )
                id_field = getattr(sa_model_class, id_field_name)
                stmt: sa.Select = sa.select(sa_model_class).where(
                    id_field.in_(person_id_set)  # type: ignore[attr-defined]
                )
                mapper = self.get_mapper(model_class)
                objs_by_person = db[model_class]
                for row in uow.session.execute(stmt):
                    obj = cast(model.Model, mapper.load(row[0]))
                    person_id = cast(UUID, getattr(obj, id_field_name))
                    objs_by_person[person_id].append(obj)

            # Create FullPersons
            class_field_map = (
                model.FullPerson.DATA_CLASS_FIELD_MAP
                | model.FullPerson.IDENTIFIER_FIELD_MAP
                | {model.PersonIdentifier: "person_identifiers"}
            )
            full_persons: list[model.FullPerson] = []
            for person_id in person_ids:
                persons = db[model.Person][person_id]
                if not persons:
                    continue
                person = cast(model.Person, persons[0])
                full_person_kwargs = {}
                for model_class, field_name in class_field_map.items():
                    full_person_kwargs[field_name] = db[model_class][person_id]
                full_persons.append(
                    model.FullPerson(
                        id=person_id,
                        person=person,
                        **full_person_kwargs,  # type: ignore[arg-type]
                    )
                )

            return full_persons
