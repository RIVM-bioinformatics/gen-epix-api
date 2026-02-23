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
from gen_epix.omopdb.domain.model.omop.clinical_data import Person
from gen_epix.omopdb.domain.model.omop.ontology import Concept


class ConditionEra(Model, DataLineageMixin):
    """A Condition Era is defined as a span of time when the Person is assumed to have a given condition. Similar to Drug Eras, Condition Eras are chronological periods of Condition Occurrence and every Condition Occurrence record should be part of a Condition Era. Combining individual Condition Occurrences into a single Condition Era serves two purposes:

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
            {1: ("person_id", Person, None), 2: ("condition_concept_id", Concept, None)}
        ),
    )
    condition_era_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    condition_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id representing the Condition.\nETL conventions:\nNone"
    )
    condition_era_start_date: date = Field(
        description="User guidance:\nThe start date for the Condition Era\r\nconstructed from the individual\r\ninstances of Condition Occurrences.\r\nIt is the start date of the very first\r\nchronologically recorded instance of\r\nthe condition with at least 31 days since any prior record of the same Condition.\nETL conventions:\nNone"
    )
    condition_era_end_date: date = Field(
        description="User guidance:\nThe end date for the Condition Era\r\nconstructed from the individual\r\ninstances of Condition Occurrences.\r\nIt is the end date of the final\r\ncontinuously recorded instance of the\r\nCondition.\nETL conventions:\nNone"
    )
    condition_occurrence_count: int | None = Field(
        default=None,
        description="User guidance:\nThe number of individual Condition\r\nOccurrences used to construct the\r\ncondition era.\nETL conventions:\nNone",
    )


class DrugEra(Model, DataLineageMixin):
    """A Drug Era is defined as a span of time when the Person is assumed to be exposed to a particular active ingredient. A Drug Era is not the same as a Drug Exposure: Exposures are individual records corresponding to the source when Drug was delivered to the Person, while successive periods of Drug Exposures are combined under certain rules to produce continuous Drug Eras. Every record in the DRUG_EXPOSURE table should be part of a drug era based on the dates of exposure."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="DrugEras",
        table_name="drug_era",
        persistable=True,
        id_field_name="drug_era_id",
        links=create_links(
            {1: ("person_id", Person, None), 2: ("drug_concept_id", Concept, None)}
        ),
    )
    drug_era_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    drug_concept_id: UUID = Field(
        description="User guidance:\nThe drug_concept_id should conform to the concept class 'ingredient' as the drug_era is an era of time where a person is exposed to a particular drug ingredient.\nETL conventions:\nNone"
    )
    drug_era_start_date: date = Field(
        description="User guidance:\nNone\nETL conventions:\nThe Drug Era Start Date is the start date of the first Drug Exposure for a given ingredient, with at least 31 days since the previous exposure."
    )
    drug_era_end_date: date = Field(
        description="User guidance:\nNone\nETL conventions:\nThe Drug Era End Date is the end date of the last Drug Exposure. The End Date of each Drug Exposure is either taken from the field drug_exposure_end_date or, as it is typically not available, inferred using the following rules:\r\nFor pharmacy prescription data, the date when the drug was dispensed plus the number of days of supply are used to extrapolate the End Date for the Drug Exposure. Depending on the country-specific healthcare system, this supply information is either explicitly provided in the day_supply field or inferred from package size or similar information.\r\nFor Procedure Drugs, usually the drug is administered on a single date (i.e., the administration date).\r\nA standard Persistence Window of 30 days (gap, slack) is permitted between two subsequent such extrapolated DRUG_EXPOSURE records to be considered to be merged into a single Drug Era."
    )
    drug_exposure_count: int | None = Field(
        default=None,
        description="User guidance:\nThe count of grouped DRUG_EXPOSURE records that were included in the DRUG_ERA row\nETL conventions:\nNone",
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
                1: ("person_id", Person, None),
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
    dose_era_start_date: date = Field(
        description="User guidance:\nThe date the Person started on the specific dosage, with at least 31 days since any prior exposure.\nETL conventions:\nNone"
    )
    dose_era_end_date: date = Field(
        description="User guidance:\nNone\nETL conventions:\nThe date the Person was no longer exposed to the dosage of the specific drug ingredient. An era is ended if there are 31 days or more between dosage records."
    )


class CohortDefinition(Model):
    """The COHORT_DEFINITION table contains records defining a Cohort derived from the data through the associated description and syntax and upon instantiation (execution of the algorithm) placed into the COHORT table. Cohorts are a set of subjects that satisfy a given combination of inclusion criteria for a duration of time. The COHORT_DEFINITION table provides a standardized structure for maintaining the rules governing the inclusion of a subject into a cohort, and can store operational programming code to instantiate the cohort within the OMOP Common Data Model."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="CohortDefinitions",
        table_name="cohort_definition",
        persistable=True,
        id_field_name="cohort_definition_id",
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
    """The subject of a cohort can have multiple, discrete records in the cohort table per cohort_definition_id, subject_id, and non-overlapping time periods. The definition of the cohort is contained within the COHORT_DEFINITION table. It is listed as part of the RESULTS schema because it is a table that users of the database as well as tools such as ATLAS need to be able to write to. The CDM and Vocabulary tables are all read-only so it is suggested that the COHORT and COHORT_DEFINTION tables are kept in a separate schema to alleviate confusion."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Cohorts",
        table_name="cohort",
        persistable=True,
        id_field_name="cohort_id",
    )
    cohort_definition_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
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


class Episode(Model, DataLineageMixin):
    """The EPISODE table aggregates lower-level clinical events (VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, DEVICE_EXPOSURE) into a higher-level abstraction representing clinically and analytically relevant disease phases,outcomes and treatments. The EPISODE_EVENT table connects qualifying clinical events (VISIT_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, DEVICE_EXPOSURE) to the appropriate EPISODE entry. For example cancers including their development over time, their treatment, and final resolution."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Episodes",
        table_name="episode",
        persistable=True,
        id_field_name="episode_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("episode_concept_id", Concept, None),
                3: ("episode_object_concept_id", Concept, None),
                4: ("episode_type_concept_id", Concept, None),
                5: ("episode_source_concept_id", Concept, None),
            }
        ),
    )
    episode_id: UUID = Field(
        description="User guidance:\nA unique identifier for each Episode.\nETL conventions:\nNone"
    )
    person_id: UUID = Field(
        description="User guidance:\nThe PERSON_ID of the PERSON for whom the episode is recorded.\nETL conventions:\nNone"
    )
    episode_concept_id: UUID = Field(
        description="User guidance:\nThe EPISODE_CONCEPT_ID represents the kind abstraction related to the disease phase, outcome or treatment.\nETL conventions:\nChoose a concept in the Episode domain that best represents the ongoing disease phase, outcome, or treatment. Please see [article] for cancers and [article] for non-cancers describing how these are defined. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Episode&page=1&pageSize=15&query=)"
    )
    episode_start_date: date = Field(
        description="User guidance:\nThe date when the Episode beings.\nETL conventions:\nPlease see [article] for how to define an Episode start date."
    )
    episode_start_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nThe date and time when the Episode begins.\nETL conventions:\nNone",
    )
    episode_end_date: date | None = Field(
        default=None,
        description="User guidance:\nThe date when the instance of the Episode is considered to have ended.\nETL conventions:\nPlease see [article] for how to define an Episode end date.",
    )
    episode_end_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nThe date when the instance of the Episode is considered to have ended.\nETL conventions:\nNone",
    )
    episode_parent_id: UUID | None = Field(
        default=None,
        description="User guidance:\nUse this field to find the Episode that subsumes the given Episode record. This is used in the case that an Episode are nested into each other.\nETL conventions:\nIf there are multiple nested levels to how Episodes are represented, the EPISODE_PARENT_ID can be used to record this relationship.",
    )
    episode_number: int | None = Field(
        default=None,
        description="User guidance:\nFor sequences of episodes, this is used to indicate the order the episodes occurred. For example, lines of treatment could be indicated here.\nETL conventions:\nPlease see [article] for the details of how to count episodes.",
    )
    episode_object_concept_id: UUID = Field(
        description="User guidance:\nA Standard Concept representing the disease phase, outcome, or other abstraction of which the episode consists.  For example, if the EPISODE_CONCEPT_ID is [treatment regimen](https://athena.ohdsi.org/search-terms/terms/32531) then the EPISODE_OBJECT_CONCEPT_ID should contain the chemotherapy regimen concept, like [Afatinib monotherapy](https://athena.ohdsi.org/search-terms/terms/35804392).\nETL conventions:\nEpisode entries from the 'Disease Episode' concept class should have an episode_object_concept_id that comes from the Condition domain.  Episode entries from the 'Treatment Episode' concept class should have an episode_object_concept_id that scome from the 'Procedure' domain or 'Regimen' concept class."
    )
    episode_type_concept_id: UUID = Field(
        description="User guidance:\nThis field can be used to determine the provenance of the Episode record, as in whether the episode was from an EHR system, insurance claim, registry, or other sources.\nETL conventions:\nChoose the EPISODE_TYPE_CONCEPT_ID that best represents the provenance of the record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=). A more detailed explanation of each Type Concept can be found on the [vocabulary wiki](https://github.com/OHDSI/Vocabulary-v5.0/wiki/Vocab.-TYPE_CONCEPT)."
    )
    episode_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe source code for the Episode as it appears in the source data. This code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.\nETL conventions:\nNone",
        max_length=50,
    )
    episode_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key to a Episode Concept that refers to the code used in the source.\nETL conventions:\nGiven that the Episodes are user-defined it is unlikely that there will be a Source Concept available. If that is the case then set this field to zero.",
    )


class EpisodeEvent(Model, DataLineageMixin):
    """The EPISODE_EVENT table connects qualifying clinical events (such as CONDITION_OCCURRENCE, DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, MEASUREMENT) to the appropriate EPISODE entry. For example, linking the precise location of the metastasis (cancer modifier in MEASUREMENT) to the disease episode."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="EpisodeEvents",
        table_name="episode_event",
        persistable=True,
        id_field_name="episode_event_id",
        links=create_links(
            {
                1: ("episode_id", Episode, None),
                2: ("episode_event_field_concept_id", Concept, None),
            }
        ),
    )
    episode_id: UUID = Field(
        description="User guidance:\nUse this field to link the EPISODE_EVENT record to its EPISODE.\nETL conventions:\nPut the EPISODE_ID that subsumes the EPISODE_EVENT record here."
    )
    event_id: UUID = Field(
        description="User guidance:\nThis field is the primary key of the linked record in the database. For example, if the Episode Event is a Condition Occurrence, then the CONDITION_OCCURRENCE_ID of the linked record goes in this field.\nETL conventions:\nPut the primary key of the linked record here."
    )
    episode_event_field_concept_id: UUID = Field(
        description="User guidance:\nThis field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.\nETL conventions:\nPut the CONCEPT_ID that identifies which table and field the EVENT_ID came from. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?vocabulary=CDM&conceptClass=Field&page=1&pageSize=15&query=)"
    )
    episode_event_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )
