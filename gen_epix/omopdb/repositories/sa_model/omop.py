from datetime import date, datetime
from typing import Type
from uuid import UUID

import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped

from gen_epix.commondb.repositories.sa_model import (
    RowMetadataMixin,
    create_mapped_column,
    create_table_args,
)
from gen_epix.omopdb.domain import DOMAIN, enum, model
from gen_epix.omopdb.repositories.sa_model.base import DataLineageMixin

Base: Type = orm.declarative_base(name=enum.ServiceType.OMOP.value)


class Location(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Location)

    location_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Location, "location_id"
    )
    address_1: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Location, "address_1"
    )
    address_2: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Location, "address_2"
    )
    city: Mapped[str | None] = create_mapped_column(DOMAIN, model.Location, "city")
    state: Mapped[str | None] = create_mapped_column(DOMAIN, model.Location, "state")
    zip: Mapped[str | None] = create_mapped_column(DOMAIN, model.Location, "zip")
    county: Mapped[str | None] = create_mapped_column(DOMAIN, model.Location, "county")
    location_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Location, "location_source_value"
    )
    latitude: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Location, "latitude"
    )
    longitude: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Location, "longitude"
    )


class CohortDefinition(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CohortDefinition)

    cohort_definition_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "cohort_definition_id"
    )
    cohort_definition_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "cohort_definition_name"
    )
    cohort_definition_description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "cohort_definition_description"
    )
    definition_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "definition_type_concept_id"
    )
    cohort_definition_syntax: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "cohort_definition_syntax"
    )
    subject_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "subject_concept_id"
    )
    cohort_initiation_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.CohortDefinition, "cohort_initiation_date"
    )


class Cohort(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Cohort)

    cohort_definition_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cohort, "cohort_definition_id"
    )
    subject_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Cohort, "subject_id")
    cohort_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.Cohort, "cohort_start_date"
    )
    cohort_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.Cohort, "cohort_end_date"
    )
    cohort_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Cohort, "cohort_id")


class CdmSource(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CdmSource)

    cdm_source_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_source_name"
    )
    cdm_source_abbreviation: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_source_abbreviation"
    )
    cdm_holder: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_holder"
    )
    source_description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "source_description"
    )
    source_documentation_reference: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "source_documentation_reference"
    )
    cdm_etl_reference: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_etl_reference"
    )
    source_release_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "source_release_date"
    )
    cdm_release_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_release_date"
    )
    cdm_version: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_version"
    )
    vocabulary_version: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CdmSource, "vocabulary_version"
    )
    cdm_source_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CdmSource, "cdm_source_id"
    )


class Vocabulary(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Vocabulary)

    vocabulary_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Vocabulary, "vocabulary_id"
    )
    vocabulary_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.Vocabulary, "vocabulary_name"
    )
    vocabulary_reference: Mapped[str] = create_mapped_column(
        DOMAIN, model.Vocabulary, "vocabulary_reference"
    )
    vocabulary_version: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Vocabulary, "vocabulary_version"
    )
    vocabulary_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Vocabulary, "vocabulary_concept_id"
    )


class Domain(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Domain)

    domain_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Domain, "domain_id")
    domain_name: Mapped[str] = create_mapped_column(DOMAIN, model.Domain, "domain_name")
    domain_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Domain, "domain_concept_id"
    )


class ConceptClass(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptClass)

    concept_class_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptClass, "concept_class_id"
    )
    concept_class_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.ConceptClass, "concept_class_name"
    )
    concept_class_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptClass, "concept_class_concept_id"
    )


class Concept(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Concept)

    concept_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Concept, "concept_id")
    concept_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.Concept, "concept_name"
    )
    domain_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Concept, "domain_id")
    vocabulary_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Concept, "vocabulary_id"
    )
    concept_class_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Concept, "concept_class_id"
    )
    standard_concept: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Concept, "standard_concept"
    )
    concept_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.Concept, "concept_code"
    )
    valid_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.Concept, "valid_start_date"
    )
    valid_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.Concept, "valid_end_date"
    )
    invalid_reason: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Concept, "invalid_reason"
    )


class Relationship(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Relationship)

    relationship_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Relationship, "relationship_id"
    )
    relationship_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.Relationship, "relationship_name"
    )
    is_hierarchical: Mapped[str] = create_mapped_column(
        DOMAIN, model.Relationship, "is_hierarchical"
    )
    defines_ancestry: Mapped[str] = create_mapped_column(
        DOMAIN, model.Relationship, "defines_ancestry"
    )
    reverse_relationship_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Relationship, "reverse_relationship_id"
    )
    relationship_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Relationship, "relationship_concept_id"
    )


class ConceptRelationship(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptRelationship)

    concept_id_1: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "concept_id_1"
    )
    concept_id_2: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "concept_id_2"
    )
    relationship_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "relationship_id"
    )
    valid_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "valid_start_date"
    )
    valid_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "valid_end_date"
    )
    invalid_reason: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "invalid_reason"
    )
    concept_relationship_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptRelationship, "concept_relationship_id"
    )


class ConceptAncestor(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptAncestor)

    ancestor_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptAncestor, "ancestor_concept_id"
    )
    descendant_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptAncestor, "descendant_concept_id"
    )
    min_levels_of_separation: Mapped[int] = create_mapped_column(
        DOMAIN, model.ConceptAncestor, "min_levels_of_separation"
    )
    max_levels_of_separation: Mapped[int] = create_mapped_column(
        DOMAIN, model.ConceptAncestor, "max_levels_of_separation"
    )
    concept_ancestor_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptAncestor, "concept_ancestor_id"
    )


class ConceptSynonym(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConceptSynonym)

    concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptSynonym, "concept_id"
    )
    concept_synonym_name: Mapped[str] = create_mapped_column(
        DOMAIN, model.ConceptSynonym, "concept_synonym_name"
    )
    language_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptSynonym, "language_concept_id"
    )
    concept_synonym_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConceptSynonym, "concept_synonym_id"
    )


class DrugStrength(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DrugStrength)

    drug_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugStrength, "drug_concept_id"
    )
    ingredient_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugStrength, "ingredient_concept_id"
    )
    amount_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "amount_value"
    )
    amount_unit_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "amount_unit_concept_id"
    )
    numerator_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "numerator_value"
    )
    numerator_unit_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "numerator_unit_concept_id"
    )
    denominator_value: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "denominator_value"
    )
    denominator_unit_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "denominator_unit_concept_id"
    )
    box_size: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "box_size"
    )
    valid_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.DrugStrength, "valid_start_date"
    )
    valid_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.DrugStrength, "valid_end_date"
    )
    invalid_reason: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugStrength, "invalid_reason"
    )
    drug_strength_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugStrength, "drug_strength_id"
    )


class SourceToConceptMap(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SourceToConceptMap)

    source_code: Mapped[str] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "source_code"
    )
    source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "source_concept_id"
    )
    source_vocabulary_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "source_vocabulary_id"
    )
    source_code_description: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "source_code_description"
    )
    target_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "target_concept_id"
    )
    target_vocabulary_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "target_vocabulary_id"
    )
    valid_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "valid_start_date"
    )
    valid_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "valid_end_date"
    )
    invalid_reason: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "invalid_reason"
    )
    source_to_concept_map_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SourceToConceptMap, "source_to_concept_map_id"
    )


class Metadata(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Metadata)

    metadata_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Metadata, "metadata_concept_id"
    )
    metadata_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Metadata, "metadata_type_concept_id"
    )
    name: Mapped[str] = create_mapped_column(DOMAIN, model.Metadata, "name")
    value_as_string: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Metadata, "value_as_string"
    )
    value_as_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Metadata, "value_as_concept_id"
    )
    metadata_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Metadata, "metadata_date"
    )
    metadata_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Metadata, "metadata_datetime"
    )
    metadata_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Metadata, "metadata_id"
    )


class CareSite(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.CareSite)

    care_site_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CareSite, "care_site_id"
    )
    care_site_name: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CareSite, "care_site_name"
    )
    place_of_service_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.CareSite, "place_of_service_concept_id"
    )
    location_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.CareSite, "location_id"
    )
    care_site_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CareSite, "care_site_source_value"
    )
    place_of_service_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.CareSite, "place_of_service_source_value"
    )
    site_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.CareSite, "site_id"
    )


class Provider(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Provider)

    provider_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Provider, "provider_id"
    )
    provider_name: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Provider, "provider_name"
    )
    npi: Mapped[str | None] = create_mapped_column(DOMAIN, model.Provider, "npi")
    dea: Mapped[str | None] = create_mapped_column(DOMAIN, model.Provider, "dea")
    specialty_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Provider, "specialty_concept_id"
    )
    care_site_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Provider, "care_site_id"
    )
    year_of_birth: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.Provider, "year_of_birth"
    )
    gender_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Provider, "gender_concept_id"
    )
    provider_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Provider, "provider_source_value"
    )
    specialty_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Provider, "specialty_source_value"
    )
    specialty_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Provider, "specialty_source_concept_id"
    )
    gender_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Provider, "gender_source_value"
    )
    gender_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Provider, "gender_source_concept_id"
    )


class Person(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Person)

    person_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Person, "person_id")
    gender_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "gender_concept_id"
    )
    year_of_birth: Mapped[int] = create_mapped_column(
        DOMAIN, model.Person, "year_of_birth"
    )
    month_of_birth: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.Person, "month_of_birth"
    )
    day_of_birth: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.Person, "day_of_birth"
    )
    birth_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Person, "birth_datetime"
    )
    death_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Person, "death_datetime"
    )
    race_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "race_concept_id"
    )
    ethnicity_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "ethnicity_concept_id"
    )
    location_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Person, "location_id"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Person, "provider_id"
    )
    care_site_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Person, "care_site_id"
    )
    person_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Person, "person_source_value"
    )
    gender_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Person, "gender_source_value"
    )
    gender_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "gender_source_concept_id"
    )
    race_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Person, "race_source_value"
    )
    race_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "race_source_concept_id"
    )
    ethnicity_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Person, "ethnicity_source_value"
    )
    ethnicity_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "ethnicity_source_concept_id"
    )
    provided_by_organization_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "provided_by_organization_id"
    )
    person_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Person, "person_type_concept_id"
    )


class ObservationPeriod(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ObservationPeriod)

    observation_period_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "observation_period_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "person_id"
    )
    observation_period_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "observation_period_start_date"
    )
    observation_period_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "observation_period_end_date"
    )
    period_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "period_type_concept_id"
    )
    observation_period_start_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "observation_period_start_iso_interval"
    )
    observation_period_end_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ObservationPeriod, "observation_period_end_iso_interval"
    )


class PayerPlanPeriod(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.PayerPlanPeriod)

    payer_plan_period_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "payer_plan_period_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "person_id"
    )
    contract_person_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "contract_person_id"
    )
    payer_plan_period_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "payer_plan_period_start_date"
    )
    payer_plan_period_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "payer_plan_period_end_date"
    )
    payer_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "payer_concept_id"
    )
    payer_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "payer_source_value"
    )
    payer_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "payer_source_concept_id"
    )
    plan_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "plan_concept_id"
    )
    plan_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "plan_source_value"
    )
    plan_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "plan_source_concept_id"
    )
    contract_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "contract_concept_id"
    )
    contract_source_value: Mapped[str] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "contract_source_value"
    )
    contract_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "contract_source_concept_id"
    )
    sponsor_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "sponsor_concept_id"
    )
    sponsor_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "sponsor_source_value"
    )
    sponsor_source_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "sponsor_source_concept_id"
    )
    family_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "family_source_value"
    )
    stop_reason_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "stop_reason_concept_id"
    )
    stop_reason_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "stop_reason_source_value"
    )
    stop_reason_source_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.PayerPlanPeriod, "stop_reason_source_concept_id"
    )


class VisitOccurrence(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.VisitOccurrence)

    visit_occurrence_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_occurrence_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "person_id"
    )
    visit_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_concept_id"
    )
    visit_start_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_start_date"
    )
    visit_start_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_start_datetime"
    )
    visit_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_end_date"
    )
    visit_end_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_end_datetime"
    )
    visit_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_type_concept_id"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "provider_id"
    )
    care_site_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "care_site_id"
    )
    visit_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_source_value"
    )
    visit_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "visit_source_concept_id"
    )
    admitted_from_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "admitted_from_concept_id"
    )
    admitted_from_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "admitted_from_source_value"
    )
    discharge_to_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "discharge_to_concept_id"
    )
    discharge_to_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "discharge_to_source_value"
    )
    preceding_visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitOccurrence, "preceding_visit_occurrence_id"
    )


class VisitDetail(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.VisitDetail)

    visit_detail_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "person_id"
    )
    visit_detail_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_concept_id"
    )
    visit_detail_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_start_date"
    )
    visit_detail_start_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_start_datetime"
    )
    visit_detail_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_end_date"
    )
    visit_detail_end_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_end_datetime"
    )
    visit_detail_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_type_concept_id"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "provider_id"
    )
    care_site_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "care_site_id"
    )
    visit_detail_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_source_value"
    )
    visit_detail_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_source_concept_id"
    )
    admitted_from_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "admitted_from_source_value"
    )
    admitted_from_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "admitted_from_concept_id"
    )
    discharge_to_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "discharge_to_source_value"
    )
    discharge_to_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "discharge_to_concept_id"
    )
    preceding_visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "preceding_visit_detail_id"
    )
    visit_detail_parent_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_detail_parent_id"
    )
    visit_occurrence_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.VisitDetail, "visit_occurrence_id"
    )


class ConditionOccurrence(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConditionOccurrence)

    condition_occurrence_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_occurrence_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "person_id"
    )
    condition_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_concept_id"
    )
    condition_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_start_date"
    )
    condition_start_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_start_datetime"
    )
    condition_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_end_date"
    )
    condition_end_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_end_datetime"
    )
    condition_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_type_concept_id"
    )
    condition_status_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_status_concept_id"
    )
    stop_reason: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "stop_reason"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "visit_detail_id"
    )
    condition_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_source_value"
    )
    condition_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_source_concept_id"
    )
    condition_status_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_status_source_value"
    )
    condition_start_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_start_iso_interval"
    )
    condition_end_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ConditionOccurrence, "condition_end_iso_interval"
    )


class ProcedureOccurrence(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ProcedureOccurrence)

    procedure_occurrence_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_occurrence_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "person_id"
    )
    procedure_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_concept_id"
    )
    procedure_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_date"
    )
    procedure_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_datetime"
    )
    procedure_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_type_concept_id"
    )
    modifier_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "modifier_concept_id"
    )
    quantity: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "quantity"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "visit_detail_id"
    )
    procedure_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_source_value"
    )
    procedure_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_source_concept_id"
    )
    modifier_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "modifier_source_value"
    )
    procedure_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.ProcedureOccurrence, "procedure_iso_interval"
    )


class DrugExposure(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DrugExposure)

    drug_exposure_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugExposure, "person_id"
    )
    drug_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_concept_id"
    )
    drug_exposure_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_start_date"
    )
    drug_exposure_start_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_start_datetime"
    )
    drug_exposure_end_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_end_date"
    )
    drug_exposure_end_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_end_datetime"
    )
    verbatim_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "verbatim_end_date"
    )
    drug_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_type_concept_id"
    )
    stop_reason: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "stop_reason"
    )
    refills: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "refills"
    )
    quantity: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "quantity"
    )
    days_supply: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "days_supply"
    )
    sig: Mapped[str | None] = create_mapped_column(DOMAIN, model.DrugExposure, "sig")
    route_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "route_concept_id"
    )
    lot_number: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "lot_number"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "visit_detail_id"
    )
    drug_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_source_value"
    )
    drug_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_source_concept_id"
    )
    route_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "route_source_value"
    )
    dose_unit_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "dose_unit_source_value"
    )
    drug_exposure_start_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_start_iso_interval"
    )
    drug_exposure_end_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugExposure, "drug_exposure_end_iso_interval"
    )


class DeviceExposure(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DeviceExposure)

    device_exposure_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "person_id"
    )
    device_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_concept_id"
    )
    device_exposure_start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_start_date"
    )
    device_exposure_start_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_start_datetime"
    )
    device_exposure_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_end_date"
    )
    device_exposure_end_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_end_datetime"
    )
    device_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_type_concept_id"
    )
    unique_device_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "unique_device_id"
    )
    quantity: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "quantity"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "visit_detail_id"
    )
    device_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_source_value"
    )
    device_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_source_concept_id"
    )
    device_exposure_start_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_start_iso_interval"
    )
    device_exposure_end_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DeviceExposure, "device_exposure_end_iso_interval"
    )


class Measurement(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Measurement)

    measurement_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Measurement, "person_id"
    )
    measurement_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_concept_id"
    )
    measurement_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_date"
    )
    measurement_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_datetime"
    )
    measurement_time: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_time"
    )
    measurement_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_type_concept_id"
    )
    operator_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "operator_concept_id"
    )
    value_as_number: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Measurement, "value_as_number"
    )
    value_as_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "value_as_concept_id"
    )
    unit_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "unit_concept_id"
    )
    range_low: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Measurement, "range_low"
    )
    range_high: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Measurement, "range_high"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "visit_detail_id"
    )
    measurement_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_source_value"
    )
    measurement_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_source_concept_id"
    )
    unit_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Measurement, "unit_source_value"
    )
    value_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Measurement, "value_source_value"
    )
    measurement_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Measurement, "measurement_iso_interval"
    )
    derived_from_specimen_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Measurement, "derived_from_specimen_id"
    )


class Observation(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Observation)

    observation_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Observation, "observation_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Observation, "person_id"
    )
    observation_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Observation, "observation_concept_id"
    )
    observation_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Observation, "observation_date"
    )
    observation_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.Observation, "observation_datetime"
    )
    observation_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Observation, "observation_type_concept_id"
    )
    value_as_number: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Observation, "value_as_number"
    )
    value_as_string: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Observation, "value_as_string"
    )
    value_as_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "value_as_concept_id"
    )
    qualifier_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "qualifier_concept_id"
    )
    unit_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "unit_concept_id"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "visit_detail_id"
    )
    observation_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Observation, "observation_source_value"
    )
    observation_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Observation, "observation_source_concept_id"
    )
    unit_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Observation, "unit_source_value"
    )
    qualifier_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Observation, "qualifier_source_value"
    )
    observation_event_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "observation_event_id"
    )
    obs_event_field_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Observation, "obs_event_field_concept_id"
    )
    value_as_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Observation, "value_as_datetime"
    )
    observation_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Observation, "observation_iso_interval"
    )
    value_as_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Observation, "value_as_iso_interval"
    )


class Specimen(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Specimen)

    specimen_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Specimen, "person_id")
    specimen_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_concept_id"
    )
    specimen_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_type_concept_id"
    )
    specimen_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_date"
    )
    specimen_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_datetime"
    )
    quantity: Mapped[float | None] = create_mapped_column(
        DOMAIN, model.Specimen, "quantity"
    )
    unit_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Specimen, "unit_concept_id"
    )
    anatomic_site_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Specimen, "anatomic_site_concept_id"
    )
    disease_status_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Specimen, "disease_status_concept_id"
    )
    specimen_source_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_source_id"
    )
    specimen_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_source_value"
    )
    unit_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Specimen, "unit_source_value"
    )
    anatomic_site_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Specimen, "anatomic_site_source_value"
    )
    disease_status_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Specimen, "disease_status_source_value"
    )
    specimen_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Specimen, "specimen_iso_interval"
    )
    derived_from_specimen_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Specimen, "derived_from_specimen_id"
    )
    derived_from_specimen_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Specimen, "derived_from_specimen_concept_id"
    )


class Note(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Note)

    note_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Note, "note_id")
    person_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Note, "person_id")
    note_event_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Note, "note_event_id"
    )
    note_event_field_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Note, "note_event_field_concept_id"
    )
    note_date: Mapped[date] = create_mapped_column(DOMAIN, model.Note, "note_date")
    note_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.Note, "note_datetime"
    )
    note_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Note, "note_type_concept_id"
    )
    note_class_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Note, "note_class_concept_id"
    )
    note_title: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Note, "note_title"
    )
    note_text: Mapped[str] = create_mapped_column(DOMAIN, model.Note, "note_text")
    encoding_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Note, "encoding_concept_id"
    )
    language_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Note, "language_concept_id"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Note, "provider_id"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Note, "visit_occurrence_id"
    )
    visit_detail_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Note, "visit_detail_id"
    )
    note_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Note, "note_source_value"
    )


class ConditionEra(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.ConditionEra)

    condition_era_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionEra, "condition_era_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionEra, "person_id"
    )
    condition_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.ConditionEra, "condition_concept_id"
    )
    condition_era_start_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.ConditionEra, "condition_era_start_datetime"
    )
    condition_era_end_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.ConditionEra, "condition_era_end_datetime"
    )
    condition_occurrence_count: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.ConditionEra, "condition_occurrence_count"
    )


class DrugEra(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DrugEra)

    drug_era_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_era_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.DrugEra, "person_id")
    drug_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_concept_id"
    )
    drug_era_start_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_era_start_datetime"
    )
    drug_era_end_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_era_end_datetime"
    )
    drug_exposure_count: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_exposure_count"
    )
    gap_days: Mapped[int | None] = create_mapped_column(
        DOMAIN, model.DrugEra, "gap_days"
    )
    drug_era_start_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_era_start_iso_interval"
    )
    drug_era_end_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.DrugEra, "drug_era_end_iso_interval"
    )


class DoseEra(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.DoseEra)

    dose_era_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DoseEra, "dose_era_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.DoseEra, "person_id")
    drug_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DoseEra, "drug_concept_id"
    )
    unit_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.DoseEra, "unit_concept_id"
    )
    dose_value: Mapped[float] = create_mapped_column(
        DOMAIN, model.DoseEra, "dose_value"
    )
    dose_era_start_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.DoseEra, "dose_era_start_datetime"
    )
    dose_era_end_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.DoseEra, "dose_era_end_datetime"
    )


class NoteNlp(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.NoteNlp)

    note_nlp_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.NoteNlp, "note_nlp_id"
    )
    note_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.NoteNlp, "note_id")
    section_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "section_concept_id"
    )
    snippet: Mapped[str | None] = create_mapped_column(DOMAIN, model.NoteNlp, "snippet")
    offset: Mapped[str | None] = create_mapped_column(DOMAIN, model.NoteNlp, "offset")
    lexical_variant: Mapped[str] = create_mapped_column(
        DOMAIN, model.NoteNlp, "lexical_variant"
    )
    note_nlp_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "note_nlp_concept_id"
    )
    note_nlp_source_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "note_nlp_source_concept_id"
    )
    nlp_system: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "nlp_system"
    )
    nlp_date: Mapped[date] = create_mapped_column(DOMAIN, model.NoteNlp, "nlp_date")
    nlp_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "nlp_datetime"
    )
    term_exists: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "term_exists"
    )
    term_temporal: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "term_temporal"
    )
    term_modifiers: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.NoteNlp, "term_modifiers"
    )


class Cost(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.Cost)

    cost_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Cost, "cost_id")
    person_id: Mapped[UUID] = create_mapped_column(DOMAIN, model.Cost, "person_id")
    cost_event_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Cost, "cost_event_id"
    )
    cost_event_field_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.Cost, "cost_event_field_concept_id"
    )
    cost_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "cost_concept_id"
    )
    cost_type_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "cost_type_concept_id"
    )
    cost_source_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "cost_source_concept_id"
    )
    cost_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Cost, "cost_source_value"
    )
    currency_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "currency_concept_id"
    )
    cost: Mapped[float | None] = create_mapped_column(DOMAIN, model.Cost, "cost")
    incurred_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Cost, "incurred_date"
    )
    billed_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Cost, "billed_date"
    )
    paid_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.Cost, "paid_date"
    )
    revenue_code_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "revenue_code_concept_id"
    )
    drg_concept_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "drg_concept_id"
    )
    revenue_code_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Cost, "revenue_code_source_value"
    )
    drg_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.Cost, "drg_source_value"
    )
    payer_plan_period_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.Cost, "payer_plan_period_id"
    )


class LocationHistory(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.LocationHistory)

    location_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocationHistory, "location_id"
    )
    relationship_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocationHistory, "relationship_type_concept_id"
    )
    domain_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocationHistory, "domain_id"
    )
    entity_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocationHistory, "entity_id"
    )
    start_date: Mapped[date] = create_mapped_column(
        DOMAIN, model.LocationHistory, "start_date"
    )
    end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.LocationHistory, "end_date"
    )
    start_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.LocationHistory, "start_iso_interval"
    )
    end_iso_interval: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.LocationHistory, "end_iso_interval"
    )
    location_history_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.LocationHistory, "location_history_id"
    )


class SurveyConduct(Base, DataLineageMixin, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.SurveyConduct)

    survey_conduct_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_conduct_id"
    )
    person_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "person_id"
    )
    survey_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_concept_id"
    )
    survey_start_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_start_date"
    )
    survey_start_datetime: Mapped[datetime | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_start_datetime"
    )
    survey_end_date: Mapped[date | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_end_date"
    )
    survey_end_datetime: Mapped[datetime] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_end_datetime"
    )
    provider_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "provider_id"
    )
    assisted_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "assisted_concept_id"
    )
    respondent_type_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "respondent_type_concept_id"
    )
    timing_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "timing_concept_id"
    )
    collection_method_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "collection_method_concept_id"
    )
    assisted_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "assisted_source_value"
    )
    respondent_type_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "respondent_type_source_value"
    )
    timing_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "timing_source_value"
    )
    collection_method_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "collection_method_source_value"
    )
    survey_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_source_value"
    )
    survey_source_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_source_concept_id"
    )
    survey_source_identifier: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_source_identifier"
    )
    validated_survey_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "validated_survey_concept_id"
    )
    validated_survey_source_value: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "validated_survey_source_value"
    )
    survey_version_number: Mapped[str | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "survey_version_number"
    )
    visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "visit_occurrence_id"
    )
    response_visit_occurrence_id: Mapped[UUID | None] = create_mapped_column(
        DOMAIN, model.SurveyConduct, "response_visit_occurrence_id"
    )


class FactRelationship(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.FactRelationship)

    domain_concept_id_1: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.FactRelationship, "domain_concept_id_1"
    )
    fact_id_1: Mapped[int] = create_mapped_column(
        DOMAIN, model.FactRelationship, "fact_id_1"
    )
    domain_concept_id_2: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.FactRelationship, "domain_concept_id_2"
    )
    fact_id_2: Mapped[int] = create_mapped_column(
        DOMAIN, model.FactRelationship, "fact_id_2"
    )
    relationship_concept_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.FactRelationship, "relationship_concept_id"
    )
    fact_relationship_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.FactRelationship, "fact_relationship_id"
    )


class MeasurementRelation(Base, RowMetadataMixin):
    __tablename__, __table_args__ = create_table_args(model.MeasurementRelation)

    measurement_relation_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MeasurementRelation, "measurement_relation_id"
    )
    from_measurement_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MeasurementRelation, "from_measurement_id"
    )
    to_measurement_id: Mapped[UUID] = create_mapped_column(
        DOMAIN, model.MeasurementRelation, "to_measurement_id"
    )
