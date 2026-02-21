"""
Derived domain - OMOP CDM v6.0 derived element tables.

This module contains classes for derived analytical constructs like condition eras,
drug eras, and dose eras.

Classes:
- ConditionEra: Time spans when a condition is assumed to be present
- DrugEra: Time spans when a drug exposure is assumed to be present
- DoseEra: Time spans when a specific drug dose is assumed to be present
"""

from datetime import date, datetime
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.omop.base import DataLineageMixin
from gen_epix.omopdb.domain.model.omop.ontology import Concept


class ConditionEra(Model, DataLineageMixin):
    """A Condition Era is defined as a span of time when the Person is assumed to have a given condition. Similar to Drug Eras, Condition Eras are chronological periods of Condition Occurrence. Combining individual Condition Occurrences into a single Condition Era serves two purposes:

    - It allows aggregation of chronic conditions that require frequent ongoing care, instead of treating each Condition Occurrence as an independent event.
    - It allows aggregation of multiple, closely timed doctor visits for the same Condition to avoid double-counting the Condition Occurrences.
    For example, consider a Person who visits her Primary Care Physician (PCP) and who is referred to a specialist. At a later time, the Person visits the specialist, who confirms the PCP's original diagnosis and provides the appropriate treatment to resolve the condition. These two independent doctor visits should be aggregated into one Condition Era.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ConditionEras",
        table_name="condition_era",
        persistable=True,
        id_field_name="condition_era_id",
        links=create_links(
            {
                1: ("person_id", "Person", None),
                2: ("condition_concept_id", Concept, None),
            }
        ),
    )
    condition_era_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    condition_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id representing the Condition.\nETL conventions:\nNone"
    )
    condition_era_start_datetime: datetime = Field(
        description="User guidance:\nThe start date for the Condition Era\r\nconstructed from the individual\r\ninstances of Condition Occurrences.\r\nIt is the start date of the very first\r\nchronologically recorded instance of\r\nthe condition with at least 31 days since any prior record of the same Condition.\nETL conventions:\nNone"
    )
    condition_era_end_datetime: datetime = Field(
        description="User guidance:\nThe end date for the Condition Era\r\nconstructed from the individual\r\ninstances of Condition Occurrences.\r\nIt is the end date of the final\r\ncontinuously recorded instance of the\r\nCondition.\nETL conventions:\nNone"
    )
    condition_occurrence_count: int | None = Field(
        default=None,
        description="User guidance:\nThe number of individual Condition\r\nOccurrences used to construct the\r\ncondition era.\nETL conventions:\nNone",
    )


class DrugEra(Model, DataLineageMixin):
    """A Drug Era is defined as a span of time when the Person is assumed to be exposed to a particular active ingredient. A Drug Era is not the same as a Drug Exposure: Exposures are individual records corresponding to the source when Drug was delivered to the Person, while successive periods of Drug Exposures are combined under certain rules to produce continuous Drug Eras."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="DrugEras",
        table_name="drug_era",
        persistable=True,
        id_field_name="drug_era_id",
        links=create_links(
            {1: ("person_id", "Person", None), 2: ("drug_concept_id", Concept, None)}
        ),
    )
    drug_era_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    drug_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id representing the specific drug ingredient.\nETL conventions:\nNone"
    )
    drug_era_start_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nThe Drug Era Start Date is the start date of the first Drug Exposure for a given ingredient, with at least 31 days since the previous exposure."
    )
    drug_era_end_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nThe Drug Era End Date is the end date of the last Drug Exposure. The End Date of each Drug Exposure is either taken from the field drug_exposure_end_date or, as it is typically not available, inferred using the following rules:\r\nFor pharmacy prescription data, the date when the drug was dispensed plus the number of days of supply are used to extrapolate the End Date for the Drug Exposure. Depending on the country-specific healthcare system, this supply information is either explicitly provided in the day_supply field or inferred from package size or similar information.\r\nFor Procedure Drugs, usually the drug is administered on a single date (i.e., the administration date).\r\nA standard Persistence Window of 30 days (gap, slack) is permitted between two subsequent such extrapolated DRUG_EXPOSURE records to be considered to be merged into a single Drug Era."
    )
    drug_exposure_count: int | None = Field(
        default=None,
        description="User guidance:\nThe count of grouped DRUG_EXPOSURE records that were included in the DRUG_ERA row.\nETL conventions:\nNone",
    )
    gap_days: int | None = Field(
        default=None,
        description='User guidance:\nNone\nETL conventions:\nThe Gap Days determine how many total drug-free days are observed between all Drug Exposure events that contribute to a DRUG_ERA record. It is assumed that the drugs are "not stockpiled" by the patient, i.e. that if a new drug prescription or refill is observed (a new DRUG_EXPOSURE record is written), the remaining supply from the previous events is abandoned.   The difference between Persistence Window and Gap Days is that the former is the maximum drug-free time allowed between two subsequent DRUG_EXPOSURE records, while the latter is the sum of actual drug-free days for the given Drug Era under the above assumption of non-stockpiling.',
    )
    drug_era_start_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    drug_era_end_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


class DoseEra(Model, DataLineageMixin):
    """A Dose Era is defined as a span of time when the Person is assumed to be exposed to a constant dose of a specific active ingredient."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="DoseEras",
        table_name="dose_era",
        persistable=True,
        id_field_name="dose_era_id",
        links=create_links(
            {
                1: ("person_id", "Person", None),
                2: ("drug_concept_id", Concept, None),
                3: ("unit_concept_id", Concept, None),
            }
        ),
    )
    dose_era_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    drug_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id representing the specific drug ingredient.\nETL conventions:\nNone"
    )
    unit_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id representing the unit of the specific drug ingredient.\nETL conventions:\nNone"
    )
    dose_value: float = Field(
        description="User guidance:\nThe numeric value of the dosage of the drug_ingredient.\nETL conventions:\nNone"
    )
    dose_era_start_datetime: datetime = Field(
        description="User guidance:\nThe date the Person started on the specific dosage, with at least 31 days since any prior exposure.\nETL conventions:\nNone"
    )
    dose_era_end_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nThe date the Person was no longer exposed to the dosage of the specific drug ingredient. An era is ended if there are 31 days or more between dosage records."
    )


class CohortDefinition(Model):
    """The COHORT_DEFINITION table contains records defining a Cohort derived from the data through the associated description and syntax and upon instantiation (execution of the algorithm) placed into the COHORT table. Cohorts are a set of subjects that satisfy a given combination of inclusion criteria for a duration of time. The COHORT_DEFINITION table provides a standardized structure for maintaining the rules governing the inclusion of a subject into a cohort, and can store operational programming code to instantiate the cohort within the OMOP Common Data Model."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="CohortDefinitions",
        table_name="cohort_definition",
        persistable=True,
        id_field_name="cohort_definition_id",
        links=create_links(
            {
                1: ("definition_type_concept_id", Concept, None),
                2: ("subject_concept_id", Concept, None),
            }
        ),
    )
    cohort_definition_id: UUID = Field(
        description="User guidance:\nThis is the identifier given to the cohort, usually by the ATLAS application\nETL conventions:\nNone"
    )
    cohort_definition_name: str = Field(
        description="User guidance:\nA short description of the cohort\nETL conventions:\nNone",
        max_length=255,
    )
    cohort_definition_description: str | None = Field(
        default=None,
        description="User guidance:\nA complete description of the cohort.\nETL conventions:\nNone",
    )
    definition_type_concept_id: UUID = Field(
        description="User guidance:\nType defining what kind of Cohort Definition the record represents and how the syntax may be executed.\nETL conventions:\nNone"
    )
    cohort_definition_syntax: str | None = Field(
        default=None,
        description="User guidance:\nSyntax or code to operationalize the Cohort Definition.\nETL conventions:\nNone",
    )
    subject_concept_id: UUID = Field(
        description="User guidance:\nThis field contains a Concept that represents the domain of the subjects that are members of the cohort (e.g., Person, Provider, Visit).\nETL conventions:\nNone"
    )
    cohort_initiation_date: date | None = Field(
        default=None,
        description="User guidance:\nA date to indicate when the Cohort was initiated in the COHORT table.\nETL conventions:\nNone",
    )


class Cohort(Model):
    """The COHORT table contains records of subjects that satisfy a given set of criteria for a duration of time. The definition of the cohort is contained within the COHORT_DEFINITION table. It is listed as part of the RESULTS schema because it is a table that users of the database as well as tools such as ATLAS need to be able to write to. The CDM and Vocabulary tables are all read-only so it is suggested that the COHORT and COHORT_DEFINTION tables are kept in a separate schema to alleviate confusion."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Cohorts",
        table_name="cohort",
        persistable=True,
        id_field_name="cohort_id",
        links=create_links({1: ("cohort_definition_id", CohortDefinition, None)}),
    )
    cohort_definition_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    subject_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    cohort_start_date: date = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    cohort_end_date: date = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    cohort_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )
