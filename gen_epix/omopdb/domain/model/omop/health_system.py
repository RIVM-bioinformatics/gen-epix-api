"""OMOP CDM v6.0 - Standardized Health System Models

This module contains the health system domain models representing physical
locations and healthcare providers as defined in the OMOP Common Data Model.

Domain: health_system
Tables: Location, Care_site, Provider
"""

from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.omop.ontology import Concept


class Location(Model):
    """The LOCATION table represents a generic way to capture physical location or address information of Persons and Care Sites."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Locations",
        table_name="location",
        persistable=True,
        id_field_name="location_id",
    )
    location_id: UUID = Field(
        description="User guidance:\nThe unique key given to a unique Location.\nETL conventions:\nEach instance of a Location in the source data should be assigned this unique key."
    )
    address_1: str | None = Field(
        default=None,
        description="User guidance:\nThis is the first line of the address.\nETL conventions:\nNone",
        max_length=50,
    )
    address_2: str | None = Field(
        default=None,
        description="User guidance:\nThis is the second line of the address\nETL conventions:\nNone",
        max_length=50,
    )
    city: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=50,
    )
    state: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=2,
    )
    zip: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nZip codes are handled as strings of up to 9 characters length. For US addresses, these represent either a 3-digit abbreviated Zip code as provided by many sources for patient protection reasons, the full 5-digit Zip or the 9-digit (ZIP + 4) codes. Unless for specific reasons analytical methods should expect and utilize only the first 3 digits. For international addresses, different rules apply.",
        max_length=9,
    )
    county: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=20,
    )
    location_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nPut the verbatim value for the location here, as it shows up in the source.",
        max_length=50,
    )
    country_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Concept Id representing the country. Values should conform to the [Geography](https://athena.ohdsi.org/search-terms/terms?domain=Geography&standardConcept=Standard&page=1&pageSize=15&query=&boosts) domain.\nETL conventions:\nNone",
    )
    country_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe name of the country.\nETL conventions:\nNone",
        max_length=80,
    )
    latitude: float | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nMust be between -90 and 90.",
    )
    longitude: float | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nMust be between -180 and 180.",
    )


class CareSite(Model):
    """The CARE_SITE table contains a list of uniquely identified institutional (physical or organizational) units where healthcare delivery is practiced (offices, wards, hospitals, clinics, etc.)."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="CareSites",
        table_name="care_site",
        persistable=True,
        id_field_name="care_site_id",
        links=create_links(
            {
                1: ("place_of_service_concept_id", Concept, None),
                2: ("location_id", Location, None),
            }
        ),
    )
    care_site_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nAssign an ID to each combination of a location and nature of the site - the latter could be the Place of Service, name or another characteristic in your source data."
    )
    care_site_name: str | None = Field(
        default=None,
        description="User guidance:\nThe name of the care_site as it appears in the source data\nETL conventions:\nNone",
        max_length=255,
    )
    place_of_service_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is a high-level way of characterizing a Care Site. Typically, however, Care Sites can provide care in multiple settings (inpatient, outpatient, etc.) and this granularity should be reflected in the visit.\nETL conventions:\nChoose the concept in the visit domain that best represents the setting in which healthcare is provided in the Care Site. If most visits in a Care Site are Inpatient, then the place_of_service_concept_id should represent Inpatient. If information is present about a unique Care Site (e.g. Pharmacy) then a Care Site record should be created. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=2&pageSize=15&query=). For information about how to populate this field please see the [THEMIS Conventions](https://ohdsi.github.io/Themis/tag_place_of_service.html).",
    )
    location_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe location_id from the LOCATION table representing the physical location of the care_site.\nETL conventions:\nNone",
    )
    care_site_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe identifier of the care_site as it appears in the source data. This could be an identifier separate from the name of the care_site.\nETL conventions:\nNone",
        max_length=50,
    )
    place_of_service_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nPut the place of service of the care_site as it appears in the source data.",
        max_length=50,
    )
    site_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The id of the Site corresponding to the CareSite.\nETL conventions:\nNone",
    )


class Provider(Model):
    """The PROVIDER table contains a list of uniquely identified healthcare providers; duplication is not allowed. These are individuals providing hands-on healthcare to patients, such as physicians, nurses, midwives, physical therapists etc."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Providers",
        table_name="provider",
        persistable=True,
        id_field_name="provider_id",
        links=create_links(
            {
                1: ("specialty_concept_id", Concept, None),
                2: ("care_site_id", CareSite, None),
                3: ("gender_concept_id", Concept, None),
                4: ("specialty_source_concept_id", Concept, None),
                5: ("gender_source_concept_id", Concept, None),
            }
        ),
    )
    provider_id: UUID = Field(
        description="User guidance:\nIt is assumed that every provider with a different unique identifier is in fact a different person and should be treated independently.\nETL conventions:\nThis identifier can be the original id from the source data provided it is an integer, otherwise it can be an autogenerated number."
    )
    provider_name: str | None = Field(
        default=None,
        description="User guidance:\nThis field contains information that describes a healthcare provider.\nETL conventions:\nThis field is not required for identifying the Provider's actual identity. Instead, its purpose is to uniquely and/or anonymously identify providers of care across the database.",
        max_length=255,
    )
    npi: str | None = Field(
        default=None,
        description="User guidance:\nThis is the National Provider Number issued to health care providers in the US by the Centers for Medicare and Medicaid Services (CMS).\nETL conventions:\nNone",
        max_length=20,
    )
    dea: str | None = Field(
        default=None,
        description="User guidance:\nThis is the identifier issued by the DEA, a US federal agency, that allows a provider to write prescriptions for controlled substances.\nETL conventions:\nNone",
        max_length=20,
    )
    specialty_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field either represents the most common specialty that occurs in the data or the most specific concept that represents all specialties listed, should the provider have more than one. This includes physician specialties such as internal medicine, emergency medicine, etc. and allied health professionals such as nurses, midwives, and pharmacists.\nETL conventions:\nIf a Provider has more than one Specialty, there are two options: 1. Choose a concept_id which is a common ancestor to the multiple specialties, or, 2. Choose the specialty that occurs most often for the provider. Concepts in this field should be Standard with a domain of Provider. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Provider&standardConcept=Standard&page=1&pageSize=15&query=).",
    )
    care_site_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is the CARE_SITE_ID for the location that the provider primarily practices in.\nETL conventions:\nIf a Provider has more than one Care Site, the main or most often exerted CARE_SITE_ID should be recorded.",
    )
    year_of_birth: int | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    gender_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field represents the recorded gender of the provider in the source data.\nETL conventions:\nIf given, put a concept from the gender domain representing the recorded gender of the provider. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=).",
    )
    provider_source_value: str | None = Field(
        default=None,
        description="User guidance:\nUse this field to link back to providers in the source data. This is typically used for error checking of ETL logic.\nETL conventions:\nSome use cases require the ability to link back to providers in the source data. This field allows for the storing of the provider identifier as it appears in the source.",
        max_length=50,
    )
    specialty_source_value: str | None = Field(
        default=None,
        description='User guidance:\nThis refers to the specific type of healthcare provider or field of expertise listed in the source data, encompassing physician specialties like internal medicine, emergency medicine, etc., as well as allied health professionals such as nurses, midwives, and pharmacists. It covers medical specialties like surgery, internal medicine, and radiology, while other services like prosthetics, acupuncture, and physical therapy fall under the domain of "Service."\nETL conventions:\nThe type of provider and their specialty should be entered as they appear in the source data. The decision to use either the coded value or the text description is left to the discretion of the ETL-er.',
        max_length=50,
    )
    specialty_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is often zero as many sites use proprietary codes to store physician speciality.\nETL conventions:\nIf the source data codes provider specialty in an OMOP supported vocabulary store the concept_id here.",
    )
    gender_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is provider's gender as it appears in the source data.\nETL conventions:\nPut the provider's gender as it appears in the source data. This field is up to the discretion of the ETL-er as to whether this should be the coded value from the source or the text description of the lookup value.",
        max_length=50,
    )
    gender_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is often zero as many sites use proprietary codes to store provider gender.\nETL conventions:\nIf the source data codes provider gender in an OMOP supported vocabulary store the concept_id here.",
    )
