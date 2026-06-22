from datetime import date, datetime
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
        """See parent class method"""

        modified_since = modified_since or datetime.min
        modified_until = modified_until or datetime.max
        modified_person_ids: set[UUID] = set()
        for model_class in [model.Person] + model.FullPerson.DATA_CLASSES:
            for obj in self.db[model_class].values():
                assert isinstance(obj, model_class)
                person_id: UUID = obj.person_id  # type: ignore[attr-defined]
                modified_at: datetime = obj.modified_at  # type: ignore[attr-defined]
                if modified_at < modified_since:
                    continue
                if modified_at >= modified_until:
                    continue
                modified_person_ids.add(person_id)
        return sorted(modified_person_ids)

    def get_specimen_ids_by_cohort_ids(
        self,
        cohort_definition_id: UUID,
        cohort_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]:
        """See parent class method"""
        cohort_id_set = frozenset(cohort_ids)
        person_id_to_cohorts: dict[UUID, list[tuple[UUID, date, date]]] = {}
        for cohort in self.db[model.Cohort].values():
            assert isinstance(cohort, model.Cohort)
            if cohort.cohort_id is None:
                continue
            if cohort.cohort_definition_id != cohort_definition_id:
                continue
            if cohort.cohort_id not in cohort_id_set:
                continue
            person_id_to_cohorts.setdefault(cohort.subject_id, []).append(
                (cohort.cohort_id, cohort.cohort_start_date, cohort.cohort_end_date)
            )
        result: dict[UUID, list[UUID]] = {}
        for specimen in self.db[model.Specimen].values():
            assert isinstance(specimen, model.Specimen)
            if specimen.specimen_id is None or specimen.specimen_date is None:
                continue
            for cohort_id, start, end in person_id_to_cohorts.get(
                specimen.person_id, []
            ):
                if start <= specimen.specimen_date <= end:
                    result.setdefault(cohort_id, []).append(specimen.specimen_id)
        return result

    def get_full_persons_by_person_ids(
        self,
        person_ids: list[UUID],
    ) -> list[model.FullPerson]:
        """See parent class method"""
        # Retrieve all data per person
        person_id_set = set(person_ids)
        model_classes = (
            model.FullPerson.DATA_CLASSES
            + list(model.FullPerson.IDENTIFIER_CLASSES)
            + [model.PersonIdentifier]
        )
        db: dict[model.Model, dict[UUID, list[model.Model]]] = {  # type: ignore[assignment]
            x: {y: [] for y in person_ids} for x in model_classes  # type: ignore[misc]
        }
        # Group DATA_CLASSES and PersonIdentifier using their direct person_id / internal_id
        # fields, which both equal the person's UUID. IDENTIFIER_CLASSES that link via a
        # DATA_CLASS entity (e.g. SpecimenIdentifier → Specimen) need a reverse lookup
        # because their internal_id is the intermediate entity's ID, not the person's ID.
        directly_grouped = set(model.FullPerson.DATA_CLASSES) | {model.PersonIdentifier}
        for model_class in model_classes:
            if model_class not in directly_grouped:
                continue
            objs_by_person = db[model_class]  # type: ignore[index]
            id_field_name = (
                "person_id"
                if model_class in model.FullPerson.DATA_CLASSES
                else "internal_id"
            )
            for obj in self.db[model_class].values():
                person_id: UUID = getattr(obj, id_field_name)  # type: ignore[assignment]
                if person_id in person_id_set:  # type: ignore[union-attr]
                    objs_by_person[person_id].append(obj)  # type: ignore[arg-type]

        # SpecimenIdentifier.internal_id is the specimen_id, not the person_id.
        # Build a reverse index from specimen_id → person_id using the already-grouped
        # Specimen objects, then use it to associate SpecimenIdentifiers with persons.
        specimen_id_to_person_id: dict[UUID, UUID] = {
            spec.specimen_id: person_id  # type: ignore[union-attr,attr-defined]
            for person_id, specs in db[model.Specimen].items()  # type: ignore[index]
            for spec in specs
            if spec.specimen_id is not None  # type: ignore[union-attr,attr-defined]
        }
        for obj in self.db[model.SpecimenIdentifier].values():
            person_id = specimen_id_to_person_id.get(obj.internal_id)  # type: ignore[union-attr,attr-defined,assignment]
            if person_id is not None:
                db[model.SpecimenIdentifier][person_id].append(obj)  # type: ignore[index,arg-type]

        # Create FullPersons
        full_persons: list[model.FullPerson] = []
        class_field_map = (
            model.FullPerson.DATA_CLASS_FIELD_MAP
            | model.FullPerson.IDENTIFIER_FIELD_MAP
            | {model.PersonIdentifier: "person_identifiers"}
        )
        for person_id in person_ids:
            person: model.Person = self.db[model.Person][person_id]  # type: ignore[assignment]
            full_person_kwargs = {}
            for model_class, field_name in class_field_map.items():
                full_person_kwargs[field_name] = db[model_class][person_id]  # type: ignore[index,arg-type]
            full_persons.append(
                model.FullPerson(
                    id=person_id,
                    person=person,
                    **full_person_kwargs,  # type: ignore[arg-type]
                )
            )
        return full_persons
