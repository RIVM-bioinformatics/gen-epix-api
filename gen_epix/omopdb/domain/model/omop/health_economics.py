"""
Health economics domain - OMOP CDM v6.0 health economics tables.

This module contains classes for payer plan periods and cost information.

Classes:
- PayerPlanPeriod: Time periods of insurance coverage
- Cost: Financial cost information for clinical events
"""

from datetime import date
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.omop.base import DataLineageMixin
from gen_epix.omopdb.domain.model.omop.clinical_data import Person
from gen_epix.omopdb.domain.model.omop.ontology import Concept


class PayerPlanPeriod(Model, DataLineageMixin):
    """The PAYER_PLAN_PERIOD table captures details of the period of time that a Person is continuously enrolled under a specific health Plan benefit structure from a given Payer. Each Person receiving healthcare is typically covered by a health benefit plan, which pays for (fully or partially), or directly provides, the care. These benefit plans are provided by payers, such as health insurances or state or government agencies. In each plan the details of the health benefits are defined for the Person or her family, and the health benefit Plan might change over time typically with increasing utilization (reaching certain cost thresholds such as deductibles), plan availability and purchasing choices of the Person. The unique combinations of Payer organizations, health benefit Plans and time periods in which they are valid for a Person are recorded in this table."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="PayerPlanPeriods",
        table_name="payer_plan_period",
        persistable=True,
        id_field_name="payer_plan_period_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("contract_person_id", Person, None),
                3: ("payer_concept_id", Concept, None),
                4: ("payer_source_concept_id", Concept, None),
                5: ("plan_concept_id", Concept, None),
                6: ("plan_source_concept_id", Concept, None),
                7: ("contract_concept_id", Concept, None),
                8: ("contract_source_concept_id", Concept, None),
                9: ("sponsor_concept_id", Concept, None),
                10: ("sponsor_source_concept_id", Concept, None),
                11: ("stop_reason_concept_id", Concept, None),
                12: ("stop_reason_source_concept_id", Concept, None),
            }
        ),
    )
    payer_plan_period_id: UUID = Field(
        description="User guidance:\nA unique identifier for each unique combination of a Person, Payer, Plan, and Period of time.\nETL conventions:\nNone"
    )
    person_id: UUID = Field(
        description="User guidance:\nThe Person covered by the Plan.\nETL conventions:\nA single Person can have multiple, overlapping, PAYER_PLAN_PERIOD records"
    )
    contract_person_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Person who is the primary subscriber/contract owner for Plan.\nETL conventions:\nThis may or may not be the same as the PERSON_ID. For example, if a mother has her son on her plan and the PAYER_PLAN_PERIOD record is the for son, the sons's PERSON_ID would go in PAYER_PLAN_PERIOD.PERSON_ID and the mother's PERSON_ID would go in PAYER_PLAN_PERIOD.CONTRACT_PERSON_ID.",
    )
    payer_plan_period_start_date: date = Field(
        description="User guidance:\nStart date of Plan coverage.\nETL conventions:\nNone"
    )
    payer_plan_period_end_date: date = Field(
        description="User guidance:\nEnd date of Plan coverage.\nETL conventions:\nNone"
    )
    payer_concept_id: UUID = Field(
        description="User guidance:\nThis field represents the organization who reimburses the provider which administers care to the Person.\nETL conventions:\nMap the Payer directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. The point is to stratify on this information and identify if Persons have the same payer, though the name of the Payer is not necessary. If not available, set to 0. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Payer&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    payer_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is the Payer as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    payer_source_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the Payer in an OMOP supported vocabulary store the concept_id here. If not available, set to 0."
    )
    plan_concept_id: UUID = Field(
        description="User guidance:\nThis field represents the specific health benefit Plan the Person is enrolled in.\nETL conventions:\nMap the Plan directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. The point is to stratify on this information and identify if Persons have the same health benefit Plan though the name of the Plan is not necessary. If not available, set to 0. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    plan_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is the health benefit Plan of the Person as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    plan_source_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the Plan in an OMOP supported vocabulary store the concept_id here. If not available, set to 0."
    )
    contract_concept_id: UUID = Field(
        description="User guidance:\nThis field represents the relationship between the PERSON_ID and CONTRACT_PERSON_ID. It should be read as PERSON_ID is the *CONTRACT_CONCEPT_ID* of the CONTRACT_PERSON_ID. So if CONTRACT_CONCEPT_ID represents the relationship 'Stepdaughter' then the Person for whom PAYER_PLAN_PERIOD record was recorded is the stepdaughter of the CONTRACT_PERSON_ID.\nETL conventions:\nIf available, use this field to represent the relationship between the PERSON_ID and the CONTRACT_PERSON_ID. If the Person for whom the PAYER_PLAN_PERIOD record was recorded is the stepdaughter of the CONTRACT_PERSON_ID then CONTRACT_CONCEPT_ID would be [4330864](https://athena.ohdsi.org/search-terms/terms/4330864). If not available, set to 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Relationship&page=12&pageSize=15&query=)."
    )
    contract_source_value: str = Field(
        description="User guidance:\nThis is the relationship of the PERSON_ID to CONTRACT_PERSON_ID as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    contract_source_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the relationship between the PERSON_ID and CONTRACT_PERSON_ID in an OMOP supported vocabulary store the concept_id here. If not available, set to 0."
    )
    sponsor_concept_id: UUID = Field(
        description="User guidance:\nThis field represents the sponsor of the Plan who finances the Plan. This includes self-insured, small group health plan and large group health plan.\nETL conventions:\nMap the sponsor directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. The point is to stratify on this information and identify if Persons have the same sponsor though the name of the sponsor is not necessary. If not available, set to 0. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Sponsor&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    sponsor_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe Plan sponsor as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    sponsor_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the sponsor in an OMOP supported vocabulary store the concept_id here.",
    )
    family_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe common identifier for all people (often a family) that covered by the same policy.\nETL conventions:\nOften these are the common digits of the enrollment id of the policy members.",
        max_length=50,
    )
    stop_reason_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field represents the reason the Person left the Plan, if known.\nETL conventions:\nMap the stop reason directly to a standard CONCEPT_ID. If one does not exists please contact the vocabulary team. There is no global controlled vocabulary available for this information. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan+Stop+Reason&standardConcept=Standard&page=1&pageSize=15&query=).",
    )
    stop_reason_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe Plan stop reason as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    stop_reason_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the stop reason in an OMOP supported vocabulary store the concept_id here.",
    )


class Cost(Model, DataLineageMixin):
    """The COST table captures records containing the cost of any medical event recorded in one of the OMOP clinical event tables such as DRUG_EXPOSURE, PROCEDURE_OCCURRENCE, VISIT_OCCURRENCE, VISIT_DETAIL, DEVICE_OCCURRENCE, OBSERVATION or MEASUREMENT.

    Each record in the cost table account for the amount of money transacted for the clinical event. So, the COST table may be used to represent both receivables (charges) and payments (paid), each transaction type represented by its COST_CONCEPT_ID. The COST_TYPE_CONCEPT_ID field will use concepts in the Standardized Vocabularies to designate the source (provenance) of the cost data. A reference to the health plan information in the PAYER_PLAN_PERIOD table is stored in the record for information used for the adjudication system to determine the persons benefit for the clinical event.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Costs",
        table_name="cost",
        persistable=True,
        id_field_name="cost_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("cost_event_field_concept_id", Concept, None),
                3: ("cost_concept_id", Concept, None),
                4: ("cost_type_concept_id", Concept, None),
                5: ("cost_source_concept_id", Concept, None),
                6: ("currency_concept_id", Concept, None),
                7: ("revenue_code_concept_id", Concept, None),
                8: ("drg_concept_id", Concept, None),
                9: ("payer_plan_period_id", PayerPlanPeriod, None),
            }
        ),
    )
    cost_id: UUID = Field(
        description="User guidance:\nA unique identifier for each COST record.\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    cost_event_id: UUID = Field(
        description="User guidance:\nIf the Cost record is related to another record in the database, this field is the primary key of the linked record.\nETL conventions:\nPut the primary key of the linked record, if applicable, here."
    )
    cost_event_field_concept_id: UUID = Field(
        description="User guidance:\nIf the Cost record is related to another record in the database, this field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.\nETL conventions:\nPut the CONCEPT_ID that identifies which table and field the COST_EVENT_ID came from."
    )
    cost_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key that refers to a Standard Cost Concept identifier in the Standardized Vocabularies belonging to the 'Cost' vocabulary.\nETL conventions:\nNone",
    )
    cost_type_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key identifier to a concept in the CONCEPT table for the provenance or the source of the COST data and belonging to the 'Type Concept' vocabulary\nETL conventions:\nNone",
    )
    cost_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key to a Cost Concept that refers to the code used in the source.\nETL conventions:\nNone",
    )
    cost_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe source value for the cost as it appears in the source data\nETL conventions:\nNone",
        max_length=50,
    )
    currency_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key identifier to the concept representing the 3-letter code used to delineate international currencies, such as USD for US Dollar. These belong to the 'Currency' vocabulary\nETL conventions:\nNone",
    )
    cost: float | None = Field(
        default=None,
        description="User guidance:\nThe actual financial cost amount\nETL conventions:\nNone",
    )
    incurred_date: date | None = Field(
        default=None,
        description="User guidance:\nThe first date of service of the clinical event corresponding to the cost as in table capturing the information (e.g. date of visit, date of procedure, date of condition, date of drug etc).\nETL conventions:\nNone",
    )
    billed_date: date | None = Field(
        default=None,
        description="User guidance:\nThe date a bill was generated for a service or encounter\nETL conventions:\nNone",
    )
    paid_date: date | None = Field(
        default=None,
        description="User guidance:\nThe date payment was received for a service or encounter\nETL conventions:\nNone",
    )
    revenue_code_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key referring to a Standard Concept ID in the Standardized Vocabularies for Revenue codes belonging to the 'Revenue Code' vocabulary.\nETL conventions:\nNone",
    )
    drg_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key referring to a Standard Concept ID in the Standardized Vocabularies for DRG codes belonging to the 'DRG' vocabulary.\nETL conventions:\nNone",
    )
    revenue_code_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe source value for the Revenue code as it appears in the source data, stored here for reference.\nETL conventions:\nNone",
        max_length=50,
    )
    drg_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe source value for the 3-digit DRG source code as it appears in the source data, stored here for reference.\nETL conventions:\nNone",
        max_length=50,
    )
    payer_plan_period_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA foreign key to the PAYER_PLAN_PERIOD table, where the details of the Payer, Plan and Family are stored. Record the payer_plan_id that relates to the payer who contributed to the paid_by_payer field.\nETL conventions:\nNone",
    )
