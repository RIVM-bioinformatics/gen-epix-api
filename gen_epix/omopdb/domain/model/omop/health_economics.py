"""
Health economics domain - OMOP CDM v6.0 health economics tables.

This module contains classes for payer plan periods and cost information.

Classes:
- PayerPlanPeriod: Time periods of insurance coverage
- Cost: Financial cost information for clinical events
"""

from datetime import date
from typing import Any, ClassVar
from uuid import UUID

from pydantic import Field, field_validator

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.omop.base import (
    DataLineageMixin, validate_int_for_uuid_field)
from gen_epix.omopdb.domain.model.omop.clinical_data import Person
from gen_epix.omopdb.domain.model.omop.ontology import Concept, Domain


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
                2: ("payer_concept_id", Concept, None),
                3: ("payer_source_concept_id", Concept, None),
                4: ("plan_concept_id", Concept, None),
                5: ("plan_source_concept_id", Concept, None),
                6: ("sponsor_concept_id", Concept, None),
                7: ("sponsor_source_concept_id", Concept, None),
                8: ("stop_reason_concept_id", Concept, None),
                9: ("stop_reason_source_concept_id", Concept, None),
            }
        ),
    )
    payer_plan_period_id: UUID | None = Field(
        default=None,
        description="User guidance:\nA unique identifier for each unique combination of a Person, Payer, Plan, and Period of time.\nETL conventions:\nNone",
    )
    person_id: UUID = Field(
        description="User guidance:\nThe Person covered by the Plan.\nETL conventions:\nA single Person can have multiple, overlapping, PAYER_PLAN_PERIOD records"
    )
    payer_plan_period_start_date: date = Field(
        description="User guidance:\nStart date of Plan coverage.\nETL conventions:\nNone"
    )
    payer_plan_period_end_date: date = Field(
        description="User guidance:\nEnd date of Plan coverage.\nETL conventions:\nNone"
    )
    payer_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field represents the organization who reimburses the provider which administers care to the Person.\nETL conventions:\nMap the payer directly to a standard CONCEPT_ID with the domain_id of 'Payer' ([Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Payer&standardConcept=Standard&page=1&pageSize=15&query=)). This vocabulary is not exhaustive so if there is a value missing, please see the [custom concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) page.",
    )
    payer_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is the Payer as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    payer_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the Payer in an OMOP supported vocabulary store the concept_id here.",
    )
    plan_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field represents the specific health benefit Plan the Person is enrolled in.\nETL conventions:\nMap the Plan directly to a standard CONCEPT_ID in the 'Plan' vocabulary ([Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan&standardConcept=Standard&page=1&pageSize=15&query=)). This vocabulary is not exhaustive so if there is a value missing, please see the [custom concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) page.",
    )
    plan_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is the health benefit Plan of the Person as it appears in the source data.\nETL conventions:\nNone",
        max_length=50,
    )
    plan_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf the source data codes the Plan in an OMOP supported vocabulary store the concept_id here.",
    )
    sponsor_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field represents the sponsor of the Plan who finances the Plan. This includes self-insured, small group health plan and large group health plan.\nETL conventions:\nMap the sponsor directly to a standard CONCEPT_ID with the domain_id of 'Sponsor' ([Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Sponsor&standardConcept=Standard&page=1&pageSize=15&query=)). This vocabulary is not exhaustive so if there is a value missing, please see the [custom concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) page.",
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
        description="User guidance:\nThis field represents the reason the Person left the Plan, if known.\nETL conventions:\nMap the stop reason directly to a standard CONCEPT_ID with a domain of 'Plan Stop Reason' ([Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Plan+Stop+Reason&standardConcept=Standard&page=1&pageSize=15&query=)). If one does not exist visit the [Custom Concepts](https://ohdsi.github.io/CommonDataModel/customConcepts.html) pate for more information.",
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

    @field_validator(
        "payer_concept_id",
        "payer_source_concept_id",
        "plan_concept_id",
        "plan_source_concept_id",
        "sponsor_concept_id",
        "sponsor_source_concept_id",
        "stop_reason_concept_id",
        "stop_reason_source_concept_id",
        mode="before",
    )
    @classmethod
    def _validate_int_for_uuid(cls, value: Any | None) -> UUID | None:
        return validate_int_for_uuid_field(value)


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
                1: ("cost_domain_id", Domain, None),
                2: ("cost_type_concept_id", Concept, None),
                3: ("currency_concept_id", Concept, None),
                4: ("revenue_code_concept_id", Concept, None),
                5: ("drg_concept_id", Concept, None),
            }
        ),
    )
    cost_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    cost_event_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    cost_domain_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    cost_type_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    currency_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    total_charge: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    total_cost: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    total_paid: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_by_payer: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_by_patient: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_patient_copay: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_patient_coinsurance: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_patient_deductible: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_by_primary: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_ingredient_cost: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    paid_dispensing_fee: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    payer_plan_period_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    amount_allowed: float | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    revenue_code_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    revenue_code_source_value: str | None = Field(
        default=None,
        description="User guidance:\nRevenue codes are a method to charge for a class of procedures and conditions in the U.S. hospital system.\nETL conventions:\nNone",
        max_length=50,
    )
    drg_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    drg_source_value: str | None = Field(
        default=None,
        description="User guidance:\nDiagnosis Related Groups are US codes used to classify hospital cases into one of approximately 500 groups.\nETL conventions:\nNone",
        max_length=3,
    )

    @field_validator(
        "cost_type_concept_id",
        "currency_concept_id",
        "revenue_code_concept_id",
        "drg_concept_id",
        mode="before",
    )
    @classmethod
    def _validate_int_for_uuid(cls, value: Any | None) -> UUID | None:
        return validate_int_for_uuid_field(value)
