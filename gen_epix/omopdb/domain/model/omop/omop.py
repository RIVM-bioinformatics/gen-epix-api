from datetime import date, datetime
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.commondb.domain.model import Model
from gen_epix.fastapp.domain import Entity, create_links
from gen_epix.omopdb.domain.model.omop.base import DataLineageMixin


class Location(Model):
    """The LOCATION table represents a generic way to capture physical location or address information of Persons and Care Sites. **New to CDM v6.0** The LOCATION table now includes latitude and longitude."""

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
    latitude: float | None = Field(
        default=None,
        description="User guidance:\nThe geocoded latitude.\nETL conventions:\nNone",
    )
    longitude: float | None = Field(
        default=None,
        description="User guidance:\nThe geocoded longitude.\nETL conventions:\nNone",
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


class CdmSource(Model):
    """The CDM_SOURCE table contains detail about the source database and the process used to transform the data into the OMOP Common Data Model."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="CdmSources",
        table_name="cdm_source",
        persistable=True,
        id_field_name="cdm_source_id",
    )
    cdm_source_name: str = Field(
        description="User guidance:\nThe name of the CDM instance.\nETL conventions:\nNone",
        max_length=255,
    )
    cdm_source_abbreviation: str | None = Field(
        default=None,
        description="User guidance:\nThe abbreviation of the CDM instance.\nETL conventions:\nNone",
        max_length=25,
    )
    cdm_holder: str | None = Field(
        default=None,
        description="User guidance:\nThe holder of the CDM instance.\nETL conventions:\nNone",
        max_length=255,
    )
    source_description: str | None = Field(
        default=None,
        description="User guidance:\nThe description of the CDM instance.\nETL conventions:\nNone",
    )
    source_documentation_reference: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=255,
    )
    cdm_etl_reference: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nPut the link to the CDM version used.",
        max_length=255,
    )
    source_release_date: date | None = Field(
        default=None,
        description="User guidance:\nThe release date of the source data.\nETL conventions:\nNone",
    )
    cdm_release_date: date | None = Field(
        default=None,
        description="User guidance:\nThe release data of the CDM instance.\nETL conventions:\nNone",
    )
    cdm_version: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=10,
    )
    vocabulary_version: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=20,
    )
    cdm_source_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class Vocabulary(Model):
    """The VOCABULARY table includes a list of the Vocabularies collected from various sources or created de novo by the OMOP community. This reference table is populated with a single record for each Vocabulary source and includes a descriptive name and other associated attributes for the Vocabulary."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Vocabularys",
        table_name="vocabulary",
        persistable=True,
        id_field_name="vocabulary_id",
    )
    vocabulary_id: UUID = Field(
        description="User guidance:\nA unique identifier for each Vocabulary, such\r\nas ICD9CM, SNOMED, Visit.\nETL conventions:\nNone"
    )
    vocabulary_name: str = Field(
        description="User guidance:\nThe name describing the vocabulary, for\r\nexample International Classification of\r\nDiseases, Ninth Revision, Clinical\r\nModification, Volume 1 and 2 (NCHS) etc.\nETL conventions:\nNone",
        max_length=255,
    )
    vocabulary_reference: str = Field(
        description="User guidance:\nExternal reference to documentation or\r\navailable download of the about the\r\nvocabulary.\nETL conventions:\nNone",
        max_length=255,
    )
    vocabulary_version: str | None = Field(
        default=None,
        description="User guidance:\nVersion of the Vocabulary as indicated in\r\nthe source.\nETL conventions:\nNone",
        max_length=255,
    )
    vocabulary_concept_id: UUID = Field(
        description="User guidance:\nA Concept that represents the Vocabulary the VOCABULARY record belongs to.\nETL conventions:\nNone"
    )


class Domain(Model):
    """The DOMAIN table includes a list of OMOP-defined Domains the Concepts of the Standardized Vocabularies can belong to. A Domain defines the set of allowable Concepts for the standardized fields in the CDM tables. For example, the "Condition" Domain contains Concepts that describe a condition of a patient, and these Concepts can only be stored in the condition_concept_id field of the CONDITION_OCCURRENCE and CONDITION_ERA tables. This reference table is populated with a single record for each Domain and includes a descriptive name for the Domain."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Domains",
        table_name="domain",
        persistable=True,
        id_field_name="domain_id",
    )
    domain_id: UUID = Field(
        description="User guidance:\nA unique key for each domain.\nETL conventions:\nNone"
    )
    domain_name: str = Field(
        description="User guidance:\nThe name describing the Domain, e.g.\r\nCondition, Procedure, Measurement\r\netc.\nETL conventions:\nNone",
        max_length=255,
    )
    domain_concept_id: UUID = Field(
        description="User guidance:\nA Concept representing the Domain Concept the DOMAIN record belongs to.\nETL conventions:\nNone"
    )


class ConceptClass(Model):
    """The CONCEPT_CLASS table is a reference table, which includes a list of the classifications used to differentiate Concepts within a given Vocabulary. This reference table is populated with a single record for each Concept Class."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ConceptClasss",
        table_name="concept_class",
        persistable=True,
        id_field_name="concept_class_id",
    )
    concept_class_id: UUID = Field(
        description="User guidance:\nA unique key for each class.\nETL conventions:\nNone"
    )
    concept_class_name: str = Field(
        description="User guidance:\nThe name describing the Concept Class, e.g.\r\nClinical Finding, Ingredient, etc.\nETL conventions:\nNone",
        max_length=255,
    )
    concept_class_concept_id: UUID = Field(
        description="User guidance:\nA Concept that represents the Concept Class.\nETL conventions:\nNone"
    )


class Concept(Model):
    """The Standardized Vocabularies contains records, or Concepts, that uniquely identify each fundamental unit of meaning used to express clinical information in all domain tables of the CDM. Concepts are derived from vocabularies, which represent clinical information across a domain (e.g. conditions, drugs, procedures) through the use of codes and associated descriptions. Some Concepts are designated Standard Concepts, meaning these Concepts can be used as normative expressions of a clinical entity within the OMOP Common Data Model and within standardized analytics. Each Standard Concept belongs to one domain, which defines the location where the Concept would be expected to occur within data tables of the CDM.

    Concepts can represent broad categories (like 'Cardiovascular disease'), detailed clinical elements ('Myocardial infarction of the anterolateral wall') or modifying characteristics and attributes that define Concepts at various levels of detail (severity of a disease, associated morphology, etc.).

    Records in the Standardized Vocabularies tables are derived from national or international vocabularies such as SNOMED-CT, RxNorm, and LOINC, or custom Concepts defined to cover various aspects of observational data analysis.
    """

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Concepts",
        table_name="concept",
        persistable=True,
        id_field_name="concept_id",
        links=create_links(
            {
                1: ("domain_id", Domain, None),
                2: ("vocabulary_id", Vocabulary, None),
                3: ("concept_class_id", ConceptClass, None),
            }
        ),
    )
    concept_id: UUID = Field(
        description="User guidance:\nA unique identifier for each Concept across all domains.\nETL conventions:\nNone"
    )
    concept_name: str = Field(
        description="User guidance:\nAn unambiguous, meaningful and descriptive name for the Concept.\nETL conventions:\nNone",
        max_length=255,
    )
    domain_id: UUID = Field(
        description="User guidance:\nA foreign key to the [DOMAIN](https://ohdsi.github.io/CommonDataModel/cdm60.html#domain) table the Concept belongs to.\nETL conventions:\nNone"
    )
    vocabulary_id: UUID = Field(
        description="User guidance:\nA foreign key to the [VOCABULARY](https://ohdsi.github.io/CommonDataModel/cdm60.html#vocabulary)\r\ntable indicating from which source the\r\nConcept has been adapted.\nETL conventions:\nNone"
    )
    concept_class_id: UUID = Field(
        description="User guidance:\nThe attribute or concept class of the\r\nConcept. Examples are 'Clinical Drug',\r\n'Ingredient', 'Clinical Finding' etc.\nETL conventions:\nNone"
    )
    standard_concept: str | None = Field(
        default=None,
        description="User guidance:\nThis flag determines where a Concept is\r\na Standard Concept, i.e. is used in the\r\ndata, a Classification Concept, or a\r\nnon-standard Source Concept. The\r\nallowable values are 'S' (Standard\r\nConcept) and 'C' (Classification\r\nConcept), otherwise the content is NULL.\nETL conventions:\nNone",
        max_length=1,
    )
    concept_code: str = Field(
        description="User guidance:\nThe concept code represents the identifier\r\nof the Concept in the source vocabulary,\r\nsuch as SNOMED-CT concept IDs,\r\nRxNorm RXCUIs etc. Note that concept\r\ncodes are not unique across vocabularies.\nETL conventions:\nNone",
        max_length=50,
    )
    valid_start_date: date = Field(
        description="User guidance:\nThe date when the Concept was first\r\nrecorded. The default value is\r\n1-Jan-1970, meaning, the Concept has no\r\n(known) date of inception.\nETL conventions:\nNone"
    )
    valid_end_date: date = Field(
        description="User guidance:\nThe date when the Concept became\r\ninvalid because it was deleted or\r\nsuperseded (updated) by a new concept.\r\nThe default value is 31-Dec-2099,\r\nmeaning, the Concept is valid until it\r\nbecomes deprecated.\nETL conventions:\nNone"
    )
    invalid_reason: str | None = Field(
        default=None,
        description="User guidance:\nReason the Concept was invalidated.\r\nPossible values are D (deleted), U\r\n(replaced with an update) or NULL when\r\nvalid_end_date has the default value.\nETL conventions:\nNone",
        max_length=1,
    )


class Relationship(Model):
    """The RELATIONSHIP table provides a reference list of all types of relationships that can be used to associate any two Concepts in the CONCEPT_RELATIONSHIP table, the respective reverse relationships, and their hierarchical characteristics. Note, that Concepts representing relationships between the clinical facts, used for filling in the FACT_RELATIONSHIP table are stored in the CONCEPT table and belong to the Relationship Domain."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Relationships",
        table_name="relationship",
        persistable=True,
        id_field_name="relationship_id",
        links=create_links({1: ("relationship_concept_id", Concept, None)}),
    )
    relationship_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    relationship_name: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=255
    )
    is_hierarchical: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=1
    )
    defines_ancestry: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=1
    )
    reverse_relationship_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    relationship_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )


class ConceptRelationship(Model):
    """The CONCEPT_RELATIONSHIP table contains records that define direct relationships between any two Concepts and the nature or type of the relationship. Each type of a relationship is defined in the RELATIONSHIP table."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ConceptRelationships",
        table_name="concept_relationship",
        persistable=True,
        id_field_name="concept_relationship_id",
        links=create_links(
            {
                1: ("concept_id_1", Concept, None),
                2: ("concept_id_2", Concept, None),
                3: ("relationship_id", Relationship, None),
            }
        ),
    )
    concept_id_1: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    concept_id_2: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    relationship_id: UUID = Field(
        description="User guidance:\nThe relationship between CONCEPT_ID_1 and CONCEPT_ID_2. Please see the [Vocabulary Conventions](https://ohdsi.github.io/CommonDataModel/dataModelConventions.html#concept_relationships). for more information.\nETL conventions:\nNone"
    )
    valid_start_date: date = Field(
        description="User guidance:\nThe date when the relationship is first recorded.\nETL conventions:\nNone"
    )
    valid_end_date: date = Field(
        description="User guidance:\nThe date when the relationship is invalidated.\nETL conventions:\nNone"
    )
    invalid_reason: str | None = Field(
        default=None,
        description="User guidance:\nReason the relationship was invalidated. Possible values are 'D' (deleted), 'U' (updated) or NULL.\nETL conventions:\nNone",
        max_length=1,
    )
    concept_relationship_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class ConceptAncestor(Model):
    """The CONCEPT_ANCESTOR table is designed to simplify observational analysis by providing the complete hierarchical relationships between Concepts. Only direct parent-child relationships between Concepts are stored in the CONCEPT_RELATIONSHIP table. To determine higher-level ancestry connections, all individual direct relationships would have to be navigated at analysis time. The CONCEPT_ANCESTOR table includes records for all parent-child relationships, as well as grandparent-grandchild relationships and those of any other level of lineage for Standard or Classification concepts. Using the CONCEPT_ANCESTOR table allows for querying for all descendants of a hierarchical concept, and the other way around. For example, drug ingredients and drug products, beneath them in the hierarchy, are all descendants of a drug class ancestor. This table is entirely derived from the CONCEPT, CONCEPT_RELATIONSHIP, and RELATIONSHIP tables."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ConceptAncestors",
        table_name="concept_ancestor",
        persistable=True,
        id_field_name="concept_ancestor_id",
        links=create_links(
            {
                1: ("ancestor_concept_id", Concept, None),
                2: ("descendant_concept_id", Concept, None),
            }
        ),
    )
    ancestor_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id for the higher-level concept\r\nthat forms the ancestor in the relationship.\nETL conventions:\nNone"
    )
    descendant_concept_id: UUID = Field(
        description="User guidance:\nThe Concept Id for the lower-level concept\r\nthat forms the descendant in the\r\nrelationship.\nETL conventions:\nNone"
    )
    min_levels_of_separation: int = Field(
        description="User guidance:\nThe minimum separation in number of\r\nlevels of hierarchy between ancestor and\r\ndescendant concepts. This is an attribute\r\nthat is used to simplify hierarchic analysis.\nETL conventions:\nNone"
    )
    max_levels_of_separation: int = Field(
        description="User guidance:\nThe maximum separation in number of\r\nlevels of hierarchy between ancestor and\r\ndescendant concepts. This is an attribute\r\nthat is used to simplify hierarchic analysis.\nETL conventions:\nNone"
    )
    concept_ancestor_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class ConceptSynonym(Model):
    """The CONCEPT_SYNONYM table captures alternative terms, synonyms, and translations of Concept Name into various languages linked to specific concepts, providing users with a comprehensive view of how Concepts may be expressed or referenced."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ConceptSynonyms",
        table_name="concept_synonym",
        persistable=True,
        id_field_name="concept_synonym_id",
        links=create_links(
            {
                1: ("concept_id", Concept, None),
                2: ("language_concept_id", Concept, None),
            }
        ),
    )
    concept_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    concept_synonym_name: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=1000
    )
    language_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    concept_synonym_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class DrugStrength(Model):
    """The DRUG_STRENGTH table contains structured content about the amount or concentration and associated units of a specific ingredient contained within a particular drug product. This table is supplemental information to support standardized analysis of drug utilization."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="DrugStrengths",
        table_name="drug_strength",
        persistable=True,
        id_field_name="drug_strength_id",
        links=create_links(
            {
                1: ("drug_concept_id", Concept, None),
                2: ("ingredient_concept_id", Concept, None),
                3: ("amount_unit_concept_id", Concept, None),
                4: ("numerator_unit_concept_id", Concept, None),
                5: ("denominator_unit_concept_id", Concept, None),
            }
        ),
    )
    drug_concept_id: UUID = Field(
        description="User guidance:\nThe Concept representing the Branded Drug or Clinical Drug Product.\nETL conventions:\nNone"
    )
    ingredient_concept_id: UUID = Field(
        description="User guidance:\nThe Concept representing the active ingredient contained within the drug product.\nETL conventions:\nCombination Drugs will have more than one record in this table, one for each active Ingredient."
    )
    amount_value: float | None = Field(
        default=None,
        description="User guidance:\nThe numeric value or the amount of active ingredient contained within the drug product.\nETL conventions:\nNone",
    )
    amount_unit_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Concept representing the Unit of measure for the amount of active ingredient contained within the drug product.\nETL conventions:\nNone",
    )
    numerator_value: float | None = Field(
        default=None,
        description="User guidance:\nThe concentration of the active ingredient contained within the drug product.\nETL conventions:\nNone",
    )
    numerator_unit_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Concept representing the Unit of measure for the concentration of active ingredient.\nETL conventions:\nNone",
    )
    denominator_value: float | None = Field(
        default=None,
        description="User guidance:\nThe amount of total liquid (or other divisible product, such as ointment, gel, spray, etc.).\nETL conventions:\nNone",
    )
    denominator_unit_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Concept representing the denominator unit for the concentration of active ingredient.\nETL conventions:\nNone",
    )
    box_size: int | None = Field(
        default=None,
        description="User guidance:\nThe number of units of Clinical Branded Drug or Quantified Clinical or Branded Drug contained in a box as dispensed to the patient.\nETL conventions:\nNone",
    )
    valid_start_date: date = Field(
        description="User guidance:\nThe date when the Concept was first\r\nrecorded. The default value is\r\n1-Jan-1970.\nETL conventions:\nNone"
    )
    valid_end_date: date = Field(
        description="User guidance:\nThe date when then Concept became invalid.\nETL conventions:\nNone"
    )
    invalid_reason: str | None = Field(
        default=None,
        description="User guidance:\nReason the concept was invalidated. Possible values are D (deleted), U (replaced with an update) or NULL when valid_end_date has the default value.\nETL conventions:\nNone",
        max_length=1,
    )
    drug_strength_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class SourceToConceptMap(Model):
    """The source to concept map table is a legacy data structure within the OMOP Common Data Model, recommended for use in ETL processes to maintain local source codes which are not available as Concepts in the Standardized Vocabularies, and to establish mappings for each source code into a Standard Concept as target_concept_ids that can be used to populate the Common Data Model tables. The SOURCE_TO_CONCEPT_MAP table is no longer populated with content within the Standardized Vocabularies published to the OMOP community."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="SourceToConceptMaps",
        table_name="source_to_concept_map",
        persistable=True,
        id_field_name="source_to_concept_map_id",
        links=create_links(
            {
                1: ("source_concept_id", Concept, None),
                2: ("target_concept_id", Concept, None),
                3: ("target_vocabulary_id", Vocabulary, None),
            }
        ),
    )
    source_code: str = Field(
        description="User guidance:\nThe source code being translated\r\ninto a Standard Concept.\nETL conventions:\nNone",
        max_length=50,
    )
    source_concept_id: UUID = Field(
        description="User guidance:\nA foreign key to the Source\r\nConcept that is being translated\r\ninto a Standard Concept.\nETL conventions:\nThis is either 0 or should be a number above 2 billion, which are the Concepts reserved for site-specific codes and mappings."
    )
    source_vocabulary_id: UUID = Field(
        description="User guidance:\nA foreign key to the\r\nVOCABULARY table defining the\r\nvocabulary of the source code that\r\nis being translated to a Standard\r\nConcept.\nETL conventions:\nNone"
    )
    source_code_description: str | None = Field(
        default=None,
        description="User guidance:\nAn optional description for the\r\nsource code. This is included as a\r\nconvenience to compare the\r\ndescription of the source code to\r\nthe name of the concept.\nETL conventions:\nNone",
        max_length=255,
    )
    target_concept_id: UUID = Field(
        description="User guidance:\nThe target Concept\r\nto which the source code is being\r\nmapped.\nETL conventions:\nNone"
    )
    target_vocabulary_id: UUID = Field(
        description="User guidance:\nThe Vocabulary of the target Concept.\nETL conventions:\nNone"
    )
    valid_start_date: date = Field(
        description="User guidance:\nThe date when the mapping\r\ninstance was first recorded.\nETL conventions:\nNone"
    )
    valid_end_date: date = Field(
        description="User guidance:\nThe date when the mapping\r\ninstance became invalid because it\r\nwas deleted or superseded\r\n(updated) by a new relationship.\r\nDefault value is 31-Dec-2099.\nETL conventions:\nNone"
    )
    invalid_reason: str | None = Field(
        default=None,
        description="User guidance:\nReason the mapping instance was\r\ninvalidated. Possible values are D\r\n(deleted), U (replaced with an\r\nupdate) or NULL when\r\nvalid_end_date has the default\r\nvalue.\nETL conventions:\nNone",
        max_length=1,
    )
    source_to_concept_map_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class Metadata(Model):
    """The METADATA table contains metadata information about a dataset that has been transformed to the OMOP Common Data Model."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Metadatas",
        table_name="metadata",
        persistable=True,
        id_field_name="metadata_id",
        links=create_links(
            {
                1: ("metadata_concept_id", Concept, None),
                2: ("metadata_type_concept_id", Concept, None),
                3: ("value_as_concept_id", Concept, None),
            }
        ),
    )
    metadata_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_type_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    name: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=250
    )
    value_as_string: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=250,
    )
    value_as_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_date: date | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_datetime: datetime | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    metadata_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
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
        description="User guidance:\nNone\nETL conventions:\nAssign an id to each unique combination of location_id and place_of_service_source_value."
    )
    care_site_name: str | None = Field(
        default=None,
        description="User guidance:\nThe name of the care_site as it appears in the source data\nETL conventions:\nNone",
        max_length=255,
    )
    place_of_service_concept_id: UUID = Field(
        description="User guidance:\nThis is a high-level way of characterizing a Care Site. Typically, however, Care Sites can provide care in multiple settings (inpatient, outpatient, etc.) and this granularity should be reflected in the visit.\nETL conventions:\nChoose the concept in the visit domain that best represents the setting in which healthcare is provided in the Care Site. If most visits in a Care Site are Inpatient, then the place_of_service_concept_id should represent Inpatient. If information is present about a unique Care Site (e.g. Pharmacy) then a Care Site record should be created. If this information is not available then set to 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=2&pageSize=15&query=)."
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
    """The PROVIDER table contains a list of uniquely identified healthcare providers. These are individuals providing hands-on healthcare to patients, such as physicians, nurses, midwives, physical therapists etc."""

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
        description="User guidance:\nNone\nETL conventions:\nThis field is not necessary as it is not necessary to have the actual identity of the Provider. Rather, the idea is to uniquely and anonymously identify providers of care across the database.",
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
    specialty_concept_id: UUID = Field(
        description="User guidance:\nThis field either represents the most common specialty that occurs in the data or the most specific concept that represents all specialties listed, should the provider have more than one. This includes physician specialties such as internal medicine, emergency medicine, etc. and allied health professionals such as nurses, midwives, and pharmacists.\nETL conventions:\nIf a Provider has more than one Specialty, there are two options: 1. Choose a concept_id which is a common ancestor to the multiple specialties, or, 2. Choose the specialty that occurs most often for the provider. Concepts in this field should be Standard with a domain of Provider. If not available, set to 0. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Provider&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    care_site_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is the CARE_SITE_ID for the location that the provider primarily practices in.\nETL conventions:\nIf a Provider has more than one Care Site, the main or most often exerted CARE_SITE_ID should be recorded.",
    )
    year_of_birth: int | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    gender_concept_id: UUID = Field(
        description="User guidance:\nThis field represents the recorded gender of the provider in the source data.\nETL conventions:\nIf given, put a concept from the gender domain representing the recorded gender of the provider. If not available, set to 0. [Accepted Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    provider_source_value: str | None = Field(
        default=None,
        description="User guidance:\nUse this field to link back to providers in the source data. This is typically used for error checking of ETL logic.\nETL conventions:\nSome use cases require the ability to link back to providers in the source data. This field allows for the storing of the provider identifier as it appears in the source.",
        max_length=50,
    )
    specialty_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is the kind of provider or specialty as it appears in the source data. This includes physician specialties such as internal medicine, emergency medicine, etc. and allied health professionals such as nurses, midwives, and pharmacists.\nETL conventions:\nPut the kind of provider as it appears in the source data. This field is up to the discretion of the ETL-er as to whether this should be the coded value from the source or the text description of the lookup value.",
        max_length=50,
    )
    specialty_source_concept_id: UUID = Field(
        description="User guidance:\nThis is often zero as many sites use proprietary codes to store physician speciality.\nETL conventions:\nIf the source data codes provider specialty in an OMOP supported vocabulary store the concept_id here. If not available, set to 0."
    )
    gender_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis is provider's gender as it appears in the source data.\nETL conventions:\nPut the provider's gender as it appears in the source data. This field is up to the discretion of the ETL-er as to whether this should be the coded value from the source or the text description of the lookup value.",
        max_length=50,
    )
    gender_source_concept_id: UUID = Field(
        description="User guidance:\nThis is often zero as many sites use proprietary codes to store provider gender.\nETL conventions:\nIf the source data codes provider gender in an OMOP supported vocabulary store the concept_id here. If not available, set to 0."
    )


class Person(Model, DataLineageMixin):
    """This table serves as the central identity management for all Persons in the database. It contains records that uniquely identify each person or patient, and some demographic information."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Persons",
        table_name="person",
        persistable=True,
        id_field_name="person_id",
        links=create_links(
            {
                1: ("gender_concept_id", Concept, None),
                2: ("race_concept_id", Concept, None),
                3: ("ethnicity_concept_id", Concept, None),
                4: ("location_id", Location, None),
                5: ("provider_id", Provider, None),
                6: ("care_site_id", CareSite, None),
                7: ("gender_source_concept_id", Concept, None),
                8: ("race_source_concept_id", Concept, None),
                9: ("ethnicity_source_concept_id", Concept, None),
                10: ("person_type_concept_id", Concept, None),
            }
        ),
    )
    person_id: UUID = Field(
        description="User guidance:\nIt is assumed that every person with a different unique identifier is in fact a different person and should be treated independently.\nETL conventions:\nAny person linkage that needs to occur to uniquely identify Persons ought to be done prior to writing this table. This identifier can be the original id from the source data provided if it is an integer, otherwise it can be an autogenerated number."
    )
    gender_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field is meant to capture the biological sex at birth of the Person. This field should not be used to study gender identity issues.\nETL conventions:\nUse the gender or sex value present in the data under the assumption that it is the biological sex at birth. If the source data captures gender identity it should be stored in the [OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm60.html#observation) table. [Accepted gender concepts](http://athena.ohdsi.org/search-terms/terms?domain=Gender&standardConcept=Standard&page=1&pageSize=15&query=)",
    )
    year_of_birth: int | None = Field(
        default=None,
        description="User guidance:\nCompute age using year_of_birth.\nETL conventions:\nFor data sources with date of birth, the year should be extracted. For data sources where the year of birth is not available, the approximate year of birth could be derived based on age group categorization, if available. If no year of birth is available all the person's data should be dropped from the CDM instance.",
    )
    month_of_birth: int | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nFor data sources that provide the precise date of birth, the month should be extracted and stored in this field.",
    )
    day_of_birth: int | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nFor data sources that provide the precise date of birth, the day should be extracted and stored in this field.",
    )
    birth_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis field is not required but highly encouraged. For data sources that provide the precise datetime of birth, that value should be stored in this field. If birth_datetime is not provided in the source, use the following logic to infer the date: If day_of_birth is null and month_of_birth is not null then use the first of the month in that year. If month_of_birth is null or if day_of_birth AND month_of_birth are both null and the person has records during their year of birth then use the date of the earliest record, otherwise use the 15th of June of that year. If time of birth is not given use midnight (00:00:0000).",
    )
    death_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nThis field is the death date to be used in analysis, as determined by the ETL logic. Any additional information about a Person's death is stored in the [OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm60.html#observation) table with the concept_id [4306655](https://athena.ohdsi.org/search-terms/terms/4306655) or in the CONDITION_OCCURRENCE .\nETL conventions:\nIf there are multiple dates of death given for a Person, choose the one that is deemed most reliable. This may be a discharge from the hospital where the Person is listed as deceased or it could be latest death date provided. If a patient has clinical activity more than 60 days after the death date given in the source, it is a viable option to drop the death record as it may have been falsely reported. Similarly, if the death record is from a reputable source (e.g. government provided information) it is also a viable option to remove event records that occur in the data > 60 days after death.",
    )
    race_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field captures race or ethnic background of the person.\nETL conventions:\nOnly use this field if you have information about race or ethnic background. The Vocabulary contains Concepts about the main races and ethnic backgrounds in a hierarchical system. Due to the imprecise nature of human races and ethnic backgrounds, this is not a perfect system. Mixed races are not supported. If a clear race or ethnic background cannot be established, use Concept_Id 0. [Accepted Race Concepts](http://athena.ohdsi.org/search-terms/terms?domain=Race&standardConcept=Standard&page=1&pageSize=15&query=).",
    )
    ethnicity_concept_id: UUID | None = Field(
        default=None,
        description='User guidance:\nThis field captures Ethnicity as defined by the Office of Management and Budget (OMB) of the US Government: it distinguishes only between "Hispanic" and "Not Hispanic". Races and ethnic backgrounds are not stored here.\nETL conventions:\nOnly use this field if you have US-based data and a source of this information. Do not attempt to infer Ethnicity from the race or ethnic background of the Person. [Accepted ethnicity concepts](http://athena.ohdsi.org/search-terms/terms?domain=Ethnicity&standardConcept=Standard&page=1&pageSize=15&query=)',
    )
    location_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe location refers to the physical address of the person. This field should capture the last known location of the person.  Any prior locations are captured in the [LOCATION_HISTORY](https://ohdsi.github.io/CommonDataModel/cdm60.html#location_history) table.\nETL conventions:\nPut the location_id from the LOCATION table here that represents the most granular location information for the person. This could represent anything from postal code or parts thereof, state, or county for example. Since many databases contain deidentified data, it is common that the precision of the location is reduced to prevent re-identification. This field should capture the last known location. Any prior locations are captured in the [LOCATION_HISTORY](https://ohdsi.github.io/CommonDataModel/cdm60.html#location_history) table.",
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Provider refers to the last known primary care provider (General Practitioner).\nETL conventions:\nPut the provider_id from the PROVIDER table of the last known general practitioner of the person. If there are multiple providers, it is up to the ETL to decide which to put here.",
    )
    care_site_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Care Site refers to where the Provider typically provides the primary care.\nETL conventions:\nNone",
    )
    person_source_value: str | None = Field(
        default=None,
        description="User guidance:\nUse this field to link back to persons in the source data. This is typically used for error checking of ETL logic.\nETL conventions:\nSome use cases require the ability to link back to persons in the source data. This field allows for the storing of the person value as it appears in the source. This field is not required but strongly recommended.",
        max_length=50,
    )
    gender_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field is used to store the biological sex of the person from the source data. It is not intended for use in standard analytics but for reference only.\nETL conventions:\nPut the biological sex of the person as it appears in the source data.",
        max_length=50,
    )
    gender_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nDue to the small number of options, this tends to be zero.\nETL conventions:\nIf the source data codes biological sex in a non-standard vocabulary, store the concept_id here, otherwise set to 0.",
    )
    race_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field is used to store the race of the person from the source data. It is not intended for use in standard analytics but for reference only.\nETL conventions:\nPut the race of the person as it appears in the source data.",
        max_length=50,
    )
    race_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nDue to the small number of options, this tends to be zero.\nETL conventions:\nIf the source data codes race in an OMOP supported vocabulary store the concept_id here, otherwise set to 0.",
    )
    ethnicity_source_value: str | None = Field(
        default=None,
        description='User guidance:\nThis field is used to store the ethnicity of the person from the source data. It is not intended for use in standard analytics but for reference only.\nETL conventions:\nIf the person has an ethnicity other than the OMB standard of "Hispanic" or "Not Hispanic" store that value from the source data here.',
        max_length=50,
    )
    ethnicity_source_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nDue to the small number of options, this tends to be zero.\nETL conventions:\nIf the source data codes ethnicity in an OMOP supported vocabulary, store the concept_id here, otherwise set to 0.",
    )
    # TODO: should not be nullable, to be updated later
    provided_by_organization_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The id of the Organization that provided the data for this Person.\nETL conventions:\nNone",
    )
    # TODO: should not be nullable, to be updated later
    person_type_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The conceptual type of Person under study, e.g. human, animal or environment, since data from non-human origin are also in scope.\nETL conventions:\nNone",
    )


class ObservationPeriod(Model, DataLineageMixin):
    """This table contains records which define spans of time during which two conditions are expected to hold: (i) Clinical Events that happened to the Person are recorded in the Event tables, and (ii) absence of records indicate such Events did not occur during this span of time."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ObservationPeriods",
        table_name="observation_period",
        persistable=True,
        id_field_name="observation_period_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("period_type_concept_id", Concept, None),
            }
        ),
    )
    observation_period_id: UUID = Field(
        description="User guidance:\nA Person can have multiple discrete Observation Periods which are identified by the Observation_Period_Id.\nETL conventions:\nAssign a unique observation_period_id to each discrete Observation Period for a Person."
    )
    person_id: UUID = Field(
        description="User guidance:\nThe Person ID of the PERSON record for which the Observation Period is recorded.\nETL conventions:\nNone"
    )
    observation_period_start_date: date = Field(
        description="User guidance:\nUse this date to determine the start date of the Observation Period\nETL conventions:\nIt is often the case that the idea of Observation Periods does not exist in source data. In those cases, the observation_period_start_date can be inferred as the earliest Event date available for the Person. In insurance claim data, the Observation Period can be considered as the time period the Person is enrolled with a payer. If a Person switches plans but stays with the same payer, and therefore capturing of data continues, that change would be captured in [PAYER_PLAN_PERIOD](https://ohdsi.github.io/CommonDataModel/cdm60.html#payer_plan_period)."
    )
    observation_period_end_date: date = Field(
        description="User guidance:\nUse this date to determine the end date of the period for which we can assume that all events for a Person are recorded.\nETL conventions:\nIt is often the case that the idea of Observation Periods does not exist in source data. In those cases, the observation_period_end_date can be inferred as the last Event date available for the Person. In insurance claim data, the Observation Period can be considered as the time period the Person is enrolled with a payer."
    )
    period_type_concept_id: UUID = Field(
        description="User guidance:\nThis field can be used to determine the provenance of the Observation Period as in whether the period was determined from an insurance enrollment file, EHR healthcare encounters, or other sources.\nETL conventions:\nChoose the observation_period_type_concept_id that best represents how the period was determined. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    observation_period_start_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    observation_period_end_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


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


class VisitOccurrence(Model, DataLineageMixin):
    """This table contains Events where Persons engage with the healthcare system for a duration of time. They are often also called "Encounters". Visits are defined by a configuration of circumstances under which they occur, such as (i) whether the patient comes to a healthcare institution, the other way around, or the interaction is remote, (ii) whether and what kind of trained medical staff is delivering the service during the Visit, and (iii) whether the Visit is transient or for a longer period involving a stay in bed."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="VisitOccurrences",
        table_name="visit_occurrence",
        persistable=True,
        id_field_name="visit_occurrence_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("visit_concept_id", Concept, None),
                3: ("visit_type_concept_id", Concept, None),
                4: ("provider_id", Provider, None),
                5: ("care_site_id", CareSite, None),
                6: ("visit_source_concept_id", Concept, None),
                7: ("admitted_from_concept_id", Concept, None),
                8: ("discharge_to_concept_id", Concept, None),
            }
        ),
    )
    visit_occurrence_id: UUID = Field(
        description="User guidance:\nUse this to identify unique interactions between a person and the health care system. This identifier links across the other CDM event tables to associate events with a visit.\nETL conventions:\nThis should be populated by creating a unique identifier for each unique interaction between a person and the healthcare system where the person receives a medical good or service over a span of time."
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    visit_concept_id: UUID = Field(
        description='User guidance:\nThis field contains a concept id representing the kind of visit, like inpatient or outpatient. All concepts in this field should be standard and belong to the Visit domain.\nETL conventions:\nPopulate this field based on the kind of visit that took place for the person. For example this could be "Inpatient Visit", "Outpatient Visit", "Ambulatory Visit", etc. This table will contain standard concepts in the Visit domain. These concepts are arranged in a hierarchical structure to facilitate cohort definitions by rolling up to generally familiar Visits adopted in most healthcare systems worldwide.'
    )
    visit_start_date: date | None = Field(
        default=None,
        description="User guidance:\nFor inpatient visits, the start date is typically the admission date. For outpatient visits the start date and end date will be the same.\nETL conventions:\nWhen populating visit_start_date, you should think about the patient experience to make decisions on how to define visits. In the case of an inpatient visit this should be the date the patient was admitted to the hospital or institution. In all other cases this should be the date of the patient-provider interaction.",
    )
    visit_start_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nIf no time is given for the start date of a visit, set it to midnight (00:00:0000)."
    )
    visit_end_date: date | None = Field(
        default=None,
        description='User guidance:\nFor inpatient visits the end date is typically the discharge date.\nETL conventions:\nVisit end dates are mandatory. If end dates are not provided in the source there are three ways in which to derive them:\r\nOutpatient Visit: visit_end_datetime = visit_start_datetime\r\nEmergency Room Visit: visit_end_datetime = visit_start_datetime\r\nInpatient Visit: Usually there is information about discharge. If not, you should be able to derive the end date from the sudden decline of activity or from the absence of inpatient procedures/drugs.\r\nNon-hospital institution Visits: Particularly for claims data, if end dates are not provided assume the visit is for the duration of month that it occurs.\r\nFor Inpatient Visits ongoing at the date of ETL, put date of processing the data into visit_end_datetime and visit_type_concept_id with 32220 "Still patient" to identify the visit as incomplete.\r\nAll other Visits: visit_end_datetime = visit_start_datetime. If this is a one-day visit the end date should match the start date.',
    )
    visit_end_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nIf no time is given for the end date of a visit, set it to midnight (00:00:0000)."
    )
    visit_type_concept_id: UUID = Field(
        description="User guidance:\nUse this field to understand the provenance of the visit record, or where the record comes from.\nETL conventions:\nPopulate this field based on the provenance of the visit record, as in whether it came from an EHR record or billing claim."
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThere will only be one provider per visit record and the ETL document should clearly state how they were chosen (attending, admitting, etc.). If there are multiple providers associated with a visit in the source, this can be reflected in the event tables (CONDITION_OCCURRENCE, PROCEDURE_OCCURRENCE, etc.) or in the VISIT_DETAIL table.\nETL conventions:\nIf there are multiple providers associated with a visit, you will need to choose which one to put here. The additional providers can be stored in the visit_detail table.",
    )
    care_site_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field provides information about the care site where the visit took place.\nETL conventions:\nThere should only be one care site associated with a visit.",
    )
    visit_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the kind of visit that took place (inpatient, outpatient, emergency, etc.)\nETL conventions:\nIf there is information about the kind of visit in the source data that value should be stored here. If a visit is an amalgamation of visits from the source then use a hierarchy to choose the visit source value, such as IP -> ER-> OP. This should line up with the logic chosen to determine how visits are created.",
        max_length=50,
    )
    visit_source_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf the visit source value is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If not available set to 0."
    )
    admitted_from_concept_id: UUID = Field(
        description="User guidance:\nUse this field to determine where the patient was admitted from. This concept is part of the visit domain and can indicate if a patient was admitted to the hospital from a long-term care facility, for example.\nETL conventions:\nIf available, map the admitted_from_source_value to a standard concept in the visit domain. If not available set to 0."
    )
    admitted_from_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating where a person was admitted from. Typically this applies only to visits that have a length of stay, like inpatient visits or long-term care visits.",
        max_length=50,
    )
    discharge_to_concept_id: UUID = Field(
        description="User guidance:\nUse this field to determine where the patient was discharged to after a visit. This concept is part of the visit domain and can indicate if a patient was discharged to home or sent to a long-term care facility, for example.\nETL conventions:\nIf available, map the discharge_to_source_value to a standard concept in the visit domain. If not available set to 0."
    )
    discharge_to_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating where a person was discharged to after a visit, as in they went home or were moved to long-term care. Typically this applies only to visits that have a length of stay of a day or more.",
        max_length=50,
    )
    preceding_visit_occurrence_id: UUID | None = Field(
        default=None,
        description='User guidance:\nUse this field to find the visit that occurred for the person prior to the given visit. There could be a few days or a few years in between.\nETL conventions:\nThe preceding_visit_id can be used to link a visit immediately preceding the current visit. Note this is not symmetrical, and there is no such thing as a "following_visit_id".',
    )


class VisitDetail(Model, DataLineageMixin):
    """The VISIT_DETAIL table is an optional table used to represents details of each record in the parent VISIT_OCCURRENCE table. A good example of this would be the movement between units in a hospital during an inpatient stay or claim lines associated with a one insurance claim. For every record in the VISIT_OCCURRENCE table there may be 0 or more records in the VISIT_DETAIL table with a 1:n relationship where n may be 0. The VISIT_DETAIL table is structurally very similar to VISIT_OCCURRENCE table and belongs to the visit domain."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="VisitDetails",
        table_name="visit_detail",
        persistable=True,
        id_field_name="visit_detail_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("visit_detail_concept_id", Concept, None),
                3: ("visit_detail_type_concept_id", Concept, None),
                4: ("provider_id", Provider, None),
                5: ("care_site_id", CareSite, None),
                6: ("visit_detail_source_concept_id", Concept, None),
                7: ("admitted_from_concept_id", Concept, None),
                8: ("discharge_to_concept_id", Concept, None),
                9: ("visit_occurrence_id", VisitOccurrence, None),
            }
        ),
    )
    visit_detail_id: UUID = Field(
        description="User guidance:\nUse this to identify unique interactions between a person and the health care system. This identifier links across the other CDM event tables to associate events with a visit detail.\nETL conventions:\nThis should be populated by creating a unique identifier for each unique interaction between a person and the healthcare system where the person receives a medical good or service over a span of time."
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    visit_detail_concept_id: UUID = Field(
        description='User guidance:\nThis field contains a concept id representing the kind of visit detail, like inpatient or outpatient. All concepts in this field should be standard and belong to the Visit domain.\nETL conventions:\nPopulate this field based on the kind of visit that took place for the person. For example this could be "Inpatient Visit", "Outpatient Visit", "Ambulatory Visit", etc. This table will contain standard concepts in the Visit domain. These concepts are arranged in a hierarchical structure to facilitate cohort definitions by rolling up to generally familiar Visits adopted in most healthcare systems worldwide. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=).'
    )
    visit_detail_start_date: date = Field(
        description="User guidance:\nThis is the date of the start of the encounter. This may or may not be equal to the date of the Visit the Visit Detail is associated with.\nETL conventions:\nWhen populating visit_start_date, you should think about the patient experience to make decisions on how to define visits. Most likely this should be the date of the patient-provider interaction."
    )
    visit_detail_start_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf no time is given for the start date of a visit, set it to midnight (00:00:0000).",
    )
    visit_detail_end_date: date = Field(
        description='User guidance:\nThis the end date of the patient-provider interaction.\nETL conventions:\nVisit Detail end dates are mandatory. If end dates are not provided in the source there are three ways in which to derive them:<br>\r\n- Outpatient Visit Detail: visit_detail_end_datetime = visit_detail_start_datetime\r\n- Emergency Room Visit Detail: visit_detail_end_datetime = visit_detail_start_datetime\r\n- Inpatient Visit Detail: Usually there is information about discharge. If not, you should be able to derive the end date from the sudden decline of activity or from the absence of inpatient procedures/drugs.\r\n- Non-hospital institution Visit Details: Particularly for claims data, if end dates are not provided assume the visit is for the duration of month that it occurs.<br>\r\nFor Inpatient Visit Details ongoing at the date of ETL, put date of processing the data into visit_detai_end_datetime and visit_detail_type_concept_id with 32220 "Still patient" to identify the visit as incomplete.\r\nAll other Visits Details: visit_detail_end_datetime = visit_detail_start_datetime.'
    )
    visit_detail_end_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf no time is given for the end date of a visit, set it to midnight (00:00:0000).",
    )
    visit_detail_type_concept_id: UUID = Field(
        description="User guidance:\nUse this field to understand the provenance of the visit detail record, or where the record comes from.\nETL conventions:\nPopulate this field based on the provenance of the visit detail record, as in whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThere will only be one provider per  **visit** record and the ETL document should clearly state how they were chosen (attending, admitting, etc.). This is a typical reason for leveraging the VISIT_DETAIL table as even though each VISIT_DETAIL record can only have one provider, there is no limit to the number of VISIT_DETAIL records that can be associated to a VISIT_OCCURRENCE record.\nETL conventions:\nThe additional providers associated to a Visit can be stored in this table where each VISIT_DETAIL record represents a different provider.",
    )
    care_site_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field provides information about the Care Site where the Visit Detail took place.\nETL conventions:\nThere should only be one Care Site associated with a Visit Detail.",
    )
    visit_detail_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the kind of visit detail that took place (inpatient, outpatient, emergency, etc.)\nETL conventions:\nIf there is information about the kind of visit detail in the source data that value should be stored here. If a visit is an amalgamation of visits from the source then use a hierarchy to choose the VISIT_DETAIL_SOURCE_VALUE, such as IP -> ER-> OP. This should line up with the logic chosen to determine how visits are created.",
        max_length=50,
    )
    visit_detail_source_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf the VISIT_DETAIL_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If not available, map to 0."
    )
    admitted_from_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating where a person was admitted from. Typically this applies only to visits that have a length of stay, like inpatient visits or long-term care visits.",
        max_length=50,
    )
    admitted_from_concept_id: UUID = Field(
        description="User guidance:\nUse this field to determine where the patient was admitted from. This concept is part of the visit domain and can indicate if a patient was admitted to the hospital from a long-term care facility, for example.\nETL conventions:\nIf available, map the admitted_from_source_value to a standard concept in the visit domain. If not available, map to 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    discharge_to_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating where a person was discharged to after a visit, as in they went home or were moved to long-term care. Typically this applies only to visits that have a length of stay of a day or more.",
        max_length=50,
    )
    discharge_to_concept_id: UUID = Field(
        description="User guidance:\nUse this field to determine where the patient was discharged to after a visit detail record. This concept is part of the visit domain and can indicate if a patient was discharged to home or sent to a long-term care facility, for example.\nETL conventions:\nIf available, map the DISCHARGE_TO_SOURCE_VALUE to a Standard Concept in the Visit domain. If not available, set to 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    preceding_visit_detail_id: UUID | None = Field(
        default=None,
        description='User guidance:\nUse this field to find the visit detail that occurred for the person prior to the given visit detail record. There could be a few days or a few years in between.\nETL conventions:\nThe PRECEDING_VISIT_DETAIL_ID can be used to link a visit immediately preceding the current Visit Detail. Note this is not symmetrical, and there is no such thing as a "following_visit_id".',
    )
    visit_detail_parent_id: UUID | None = Field(
        default=None,
        description="User guidance:\nUse this field to find the visit detail that subsumes the given visit detail record. This is used in the case that a visit detail record needs to be nested beyond the VISIT_OCCURRENCE/VISIT_DETAIL relationship.\nETL conventions:\nIf there are multiple nested levels to how Visits are represented in the source, the VISIT_DETAIL_PARENT_ID can be used to record this relationship.",
    )
    visit_occurrence_id: UUID = Field(
        description="User guidance:\nUse this field to link the VISIT_DETAIL record to its VISIT_OCCURRENCE.\nETL conventions:\nPut the VISIT_OCCURRENCE_ID that subsumes the VISIT_DETAIL record here."
    )


class ConditionOccurrence(Model, DataLineageMixin):
    """This table contains records of Events of a Person suggesting the presence of a disease or medical condition stated as a diagnosis, a sign, or a symptom, which is either observed by a Provider or reported by the patient."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ConditionOccurrences",
        table_name="condition_occurrence",
        persistable=True,
        id_field_name="condition_occurrence_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("condition_concept_id", Concept, None),
                3: ("condition_type_concept_id", Concept, None),
                4: ("condition_status_concept_id", Concept, None),
                5: ("provider_id", Provider, None),
                6: ("visit_occurrence_id", VisitOccurrence, None),
                7: ("visit_detail_id", VisitDetail, None),
                8: ("condition_source_concept_id", Concept, None),
            }
        ),
    )
    condition_occurrence_id: UUID = Field(
        description="User guidance:\nThe unique key given to a condition record for a person. Refer to the ETL for how duplicate conditions during the same visit were handled.\nETL conventions:\nEach instance of a condition present in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same condition within the same visit. It is valid to keep these duplicates and assign them individual, unique, CONDITION_OCCURRENCE_IDs, though it is up to the ETL how they should be handled."
    )
    person_id: UUID = Field(
        description="User guidance:\nThe PERSON_ID of the PERSON for whom the condition is recorded.\nETL conventions:\nNone"
    )
    condition_concept_id: UUID = Field(
        description='User guidance:\nThe CONDITION_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source value which represents a condition\nETL conventions:\nThe CONCEPT_ID that the CONDITION_SOURCE_VALUE maps to. Only records whose source values map to concepts with a domain of "Condition" should go in this table. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition&standardConcept=Standard&page=1&pageSize=15&query=).'
    )
    condition_start_date: date = Field(
        description="User guidance:\nUse this date to determine the start date of the condition\nETL conventions:\nMost often data sources do not have the idea of a start date for a condition. Rather, if a source only has one date associated with a condition record it is acceptable to use that date for both the CONDITION_START_DATE and the CONDITION_END_DATE."
    )
    condition_start_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    condition_end_date: date | None = Field(
        default=None,
        description="User guidance:\nUse this date to determine the end date of the condition\nETL conventions:\nMost often data sources do not have the idea of a start date for a condition. Rather, if a source only has one date associated with a condition record it is acceptable to use that date for both the CONDITION_START_DATE and the CONDITION_END_DATE.",
    )
    condition_end_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    condition_type_concept_id: UUID = Field(
        description="User guidance:\nThis field can be used to determine the provenance of the Condition record, as in whether the condition was from an EHR system, insurance claim, registry, or other sources.\nETL conventions:\nChoose the condition_type_concept_id that best represents the provenance of the record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    condition_status_concept_id: UUID = Field(
        description="User guidance:\nThis concept represents the point during the visit the diagnosis was given (admitting diagnosis, final diagnosis), whether the diagnosis was determined due to laboratory findings, if the diagnosis was exclusionary, or if it was a preliminary diagnosis, among others.\nETL conventions:\nChoose the Concept in the Condition Status domain that best represents the point during the visit when the diagnosis was given. These can include admitting diagnosis, principal diagnosis, and secondary diagnosis. If not available, set to 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Condition+Status&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    stop_reason: str | None = Field(
        default=None,
        description="User guidance:\nThe Stop Reason indicates why a Condition is no longer valid with respect to the purpose within the source data. Note that a Stop Reason does not necessarily imply that the condition is no longer occurring.\nETL conventions:\nThis information is often not populated in source data and it is a valid etl choice to leave it blank if the information does not exist.",
        max_length=20,
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe provider associated with condition record, e.g. the provider who made the diagnosis or the provider who recorded the symptom.\nETL conventions:\nThe ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record, for example the admitting vs attending physician on an EHR record.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe visit during which the condition occurred.\nETL conventions:\nDepending on the structure of the source data, this may have to be determined based on dates. If a CONDITION_START_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the CONDITION_OCCURRENCE record.",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe VISIT_DETAIL record during which the condition occurred. For example, if the person was in the ICU at the time of the diagnosis the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.\nETL conventions:\nSame rules apply as for the VISIT_OCCURRENCE_ID.",
    )
    condition_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the condition that occurred. For example, this could be an ICD10 or Read code.\nETL conventions:\nThis code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    condition_source_concept_id: UUID = Field(
        description="User guidance:\nThis is the concept representing the condition source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Condition necessary for a given analytic use case. Consider using CONDITION_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network.\nETL conventions:\nIf the CONDITION_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If not available, set to 0."
    )
    condition_status_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the condition status.\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating when and how a diagnosis was given to a patient. This source value is mapped to a standard concept which is stored in the CONDITION_STATUS_CONCEPT_ID field.",
        max_length=50,
    )
    condition_start_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    condition_end_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


class ProcedureOccurrence(Model, DataLineageMixin):
    """This table contains records of activities or processes ordered by, or carried out by, a healthcare provider on the patient with a diagnostic or therapeutic purpose."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="ProcedureOccurrences",
        table_name="procedure_occurrence",
        persistable=True,
        id_field_name="procedure_occurrence_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("procedure_concept_id", Concept, None),
                3: ("procedure_type_concept_id", Concept, None),
                4: ("modifier_concept_id", Concept, None),
                5: ("provider_id", Provider, None),
                6: ("visit_occurrence_id", VisitOccurrence, None),
                7: ("visit_detail_id", VisitDetail, None),
                8: ("procedure_source_concept_id", Concept, None),
            }
        ),
    )
    procedure_occurrence_id: UUID = Field(
        description="User guidance:\nThe unique key given to a procedure record for a person. Refer to the ETL for how duplicate procedures during the same visit were handled.\nETL conventions:\nEach instance of a procedure occurrence in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same procedure within the same visit. It is valid to keep these duplicates and assign them individual, unique, PROCEDURE_OCCURRENCE_IDs, though it is up to the ETL how they should be handled."
    )
    person_id: UUID = Field(
        description="User guidance:\nThe PERSON_ID of the PERSON for whom the procedure is recorded. This may be a system generated code.\nETL conventions:\nNone"
    )
    procedure_concept_id: UUID = Field(
        description='User guidance:\nThe PROCEDURE_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source value which represents a procedure\nETL conventions:\nThe CONCEPT_ID that the PROCEDURE_SOURCE_VALUE maps to. Only records whose source values map to standard concepts with a domain of "Procedure" should go in this table. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Procedure&standardConcept=Standard&page=1&pageSize=15&query=).'
    )
    procedure_date: date | None = Field(
        default=None,
        description="User guidance:\nUse this date to determine the date the procedure occurred.\nETL conventions:\nIf a procedure lasts more than a day, then it should be recorded as a separate record for each day the procedure occurred, this logic is in lieu of the procedure_end_date, which will be added in a future version of the CDM.",
    )
    procedure_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nThis is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)"
    )
    procedure_type_concept_id: UUID = Field(
        description="User guidance:\nThis field can be used to determine the provenance of the Procedure record, as in whether the procedure was from an EHR system, insurance claim, registry, or other sources.\nETL conventions:\nChoose the PROCEDURE_TYPE_CONCEPT_ID that best represents the provenance of the record, for example whether it came from an EHR record or billing claim. If a procedure is recorded as an EHR encounter, the PROCEDURE_TYPE_CONCEPT would be 'EHR encounter record'. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    modifier_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe modifiers are intended to give additional information about the procedure but as of now the vocabulary is under review.\nETL conventions:\nIt is up to the ETL to choose how to map modifiers if they exist in source data. These concepts are typically distinguished by 'Modifier' concept classes (e.g., 'CPT4 Modifier' as part of the 'CPT4' vocabulary). If there is more than one modifier on a record, one should be chosen that pertains to the procedure rather than provider. If not available, set to 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?conceptClass=CPT4+Modifier&conceptClass=HCPCS+Modifier&vocabulary=CPT4&vocabulary=HCPCS&standardConcept=Standard&page=1&pageSize=15&query=).",
    )
    quantity: int | None = Field(
        default=None,
        description="User guidance:\nIf the quantity value is omitted, a single procedure is assumed.\nETL conventions:\nIf a Procedure has a quantity of '0' in the source, this should default to '1' in the ETL. If there is a record in the source it can be assumed the exposure occurred at least once",
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe provider associated with the procedure record, e.g. the provider who performed the Procedure.\nETL conventions:\nThe ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record, for example the admitting vs attending physician on an EHR record.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe visit during which the procedure occurred.\nETL conventions:\nDepending on the structure of the source data, this may have to be determined based on dates. If a PROCEDURE_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the Visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the PROCEDURE_OCCURRENCE record.",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe VISIT_DETAIL record during which the Procedure occurred. For example, if the Person was in the ICU at the time of the Procedure the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.\nETL conventions:\nSame rules apply as for the VISIT_OCCURRENCE_ID.",
    )
    procedure_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the procedure that occurred. For example, this could be an CPT4 or OPCS4 code.\nETL conventions:\nUse this value to look up the source concept id and then map the source concept id to a standard concept id.",
        max_length=50,
    )
    procedure_source_concept_id: UUID = Field(
        description="User guidance:\nThis is the concept representing the procedure source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Procedure necessary for a given analytic use case. Consider using PROCEDURE_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network.\nETL conventions:\nIf the PROCEDURE_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If not available, set to 0."
    )
    modifier_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThe original modifier code from the source is stored here for reference.",
        max_length=50,
    )
    procedure_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


class DrugExposure(Model, DataLineageMixin):
    """This table captures records about the exposure to a Drug ingested or otherwise introduced into the body. A Drug is a biochemical substance formulated in such a way that when administered to a Person it will exert a certain biochemical effect on the metabolism. Drugs include prescription and over-the-counter medicines, vaccines, and large-molecule biologic therapies. Radiological devices ingested or applied locally do not count as Drugs."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="DrugExposures",
        table_name="drug_exposure",
        persistable=True,
        id_field_name="drug_exposure_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("drug_concept_id", Concept, None),
                3: ("drug_type_concept_id", Concept, None),
                4: ("route_concept_id", Concept, None),
                5: ("provider_id", Provider, None),
                6: ("visit_occurrence_id", VisitOccurrence, None),
                7: ("visit_detail_id", VisitDetail, None),
                8: ("drug_source_concept_id", Concept, None),
            }
        ),
    )
    drug_exposure_id: UUID = Field(
        description="User guidance:\nThe unique key given to records of drug dispensings or administrations for a person. Refer to the ETL for how duplicate drugs during the same visit were handled.\nETL conventions:\nEach instance of a drug dispensing or administration present in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same drug within the same visit. It is valid to keep these duplicates and assign them individual, unique, DRUG_EXPOSURE_IDs, though it is up to the ETL how they should be handled."
    )
    person_id: UUID = Field(
        description="User guidance:\nThe PERSON_ID of the PERSON for whom the drug dispensing or administration is recorded. This may be a system generated code.\nETL conventions:\nNone"
    )
    drug_concept_id: UUID = Field(
        description="User guidance:\nThe DRUG_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source concept id which represents a drug product or molecule otherwise introduced to the body. The drug concepts can have a varying degree of information about drug strength and dose. This information is relevant in the context of quantity and administration information in the subsequent fields plus strength information from the DRUG_STRENGTH table, provided as part of the standard vocabulary download.\nETL conventions:\nThe CONCEPT_ID that the DRUG_SOURCE_VALUE maps to. The concept id should be derived either from mapping from the source concept id or by picking the drug concept representing the most amount of detail you have. Records whose source values map to standard concepts with a domain of Drug should go in this table. When the Drug Source Value of the code cannot be translated into Standard Drug Concept IDs, a Drug exposure entry is stored with only the corresponding SOURCE_CONCEPT_ID and DRUG_SOURCE_VALUE and a DRUG_CONCEPT_ID of 0. The Drug Concept with the most detailed content of information is preferred during the mapping process. These are indicated in the CONCEPT_CLASS_ID field of the Concept and are recorded in the following order of precedence: Branded Pack, Clinical Pack, Branded Drug, Clinical Drug, Branded Drug Component, Clinical Drug Component, Branded Drug Form, Clinical Drug Form, and only if no other information is available 'Ingredient'. Note: If only the drug class is known, the DRUG_CONCEPT_ID field should contain 0. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Drug&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    drug_exposure_start_date: date = Field(
        description="User guidance:\nUse this date to determine the start date of the drug record.\nETL conventions:\nValid entries include a start date of a prescription, the date a prescription was filled, or the date on which a Drug administration was recorded. It is a valid ETL choice to use the date the drug was ordered as the DRUG_EXPOSURE_START_DATE."
    )
    drug_exposure_start_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    drug_exposure_end_date: date = Field(
        description="User guidance:\nThe DRUG_EXPOSURE_END_DATE denotes the day the drug exposure ended for the patient.\nETL conventions:\nIf this information is not explicitly available in the data, infer the end date from start date and duration.<br>For detailed conventions for how to populate this field, please see the [THEMIS repository](https://ohdsi.github.io/Themis/tag_drug_exposure.html)."
    )
    drug_exposure_end_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    verbatim_end_date: date | None = Field(
        default=None,
        description="User guidance:\nThis is the end date of the drug exposure as it appears in the source data, if it is given\nETL conventions:\nPut the end date or discontinuation date as it appears from the source data or leave blank if unavailable.",
    )
    drug_type_concept_id: UUID = Field(
        description="User guidance:\nYou can use the TYPE_CONCEPT_ID to delineate between prescriptions written vs. prescriptions dispensed vs. medication history vs. patient-reported exposure, etc.\nETL conventions:\nChoose the drug_type_concept_id that best represents the provenance of the record, for example whether it came from a record of a prescription written or physician administered drug. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    stop_reason: str | None = Field(
        default=None,
        description="User guidance:\nThe reason a person stopped a medication as it is represented in the source. Reasons include regimen completed, changed, removed, etc. This field will be retired in v6.0.\nETL conventions:\nThis information is often not populated in source data and it is a valid etl choice to leave it blank if the information does not exist.",
        max_length=20,
    )
    refills: int | None = Field(
        default=None,
        description="User guidance:\nThis is only filled in when the record is coming from a prescription written this field is meant to represent intended refills at time of the prescription.\nETL conventions:\nNone",
    )
    quantity: float | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nTo find the dose form of a drug the RELATIONSHIP table can be used where the relationship_id is 'Has dose form'. If liquid, quantity stands for the total amount dispensed or ordered of ingredient in the units given by the drug_strength table. If the unit from the source data does not align with the unit in the DRUG_STRENGTH table the quantity should be converted to the correct unit given in DRUG_STRENGTH. For clinical drugs with fixed dose forms (tablets etc.) the quantity is the number of units/tablets/capsules prescribed or dispensed (can be partial, but then only 1/2 or 1/3, not 0.01). Clinical drugs with divisible dose forms (injections) the quantity is the amount of ingredient the patient got. For example, if the injection is 2mg/mL but the patient got 80mL then quantity is reported as 160.\r\nQuantified clinical drugs with divisible dose forms (prefilled syringes), the quantity is the amount of ingredient similar to clinical drugs. Please see [how to calculate drug dose](https://ohdsi.github.io/CommonDataModel/drug_dose.html) for more information.\r\n",
    )
    days_supply: int | None = Field(
        default=None,
        description="User guidance:\nThe number of days of supply of the medication as recorded in the original prescription or dispensing record. Days supply can differ from actual drug duration (i.e. prescribed days supply vs actual exposure).\nETL conventions:\nThe field should be left empty if the source data does not contain a verbatim days_supply, and should not be calculated from other fields.\x0b\x0bNegative values are not allowed. Several actions are possible: 1) record is not trustworthy and we remove the record entirely. 2) we trust the record and leave days_supply empty or 3) record needs to be combined with other record (e.g. reversal of prescription). High values (>365 days) should be investigated. If considered an error in the source data (e.g. typo), the value needs to be excluded to prevent creation of unrealistic long eras.",
    )
    sig: str | None = Field(
        default=None,
        description="User guidance:\nThis is the verbatim instruction for the drug as written by the provider.\nETL conventions:\nPut the written out instructions for the drug as it is verbatim in the source, if available.",
    )
    route_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThe standard CONCEPT_ID that the ROUTE_SOURCE_VALUE maps to in the route domain. This is meant to represent the route of administration of the drug. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Route&standardConcept=Standard&page=1&pageSize=15&query=)",
    )
    lot_number: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=50,
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Provider associated with drug record, e.g. the provider who wrote the prescription or the provider who administered the drug.\nETL conventions:\nThe ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record, for example the ordering vs administering physician on an EHR record.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit during which the drug was prescribed, administered or dispensed.\nETL conventions:\nTo populate this field drug exposures must be explicitly initiated in the visit.",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe VISIT_DETAIL record during which the drug exposure occurred. For example, if the person was in the ICU at the time of the drug administration the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.\nETL conventions:\nSame rules apply as for the VISIT_OCCURRENCE_ID.",
    )
    drug_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the drug exposure that occurred. For example, this could be an NDC or Gemscript code.\nETL conventions:\nThis code is mapped to a Standard Drug Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    drug_source_concept_id: UUID = Field(
        description="User guidance:\nThis is the concept representing the drug source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Drug necessary for a given analytic use case. Consider using DRUG_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network.\nETL conventions:\nIf the DRUG_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If unavailable, set to 0."
    )
    route_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the drug route.\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating when and how a drug was given to a patient. This source value is mapped to a standard concept which is stored in the ROUTE_CONCEPT_ID field.",
        max_length=50,
    )
    dose_unit_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the dose unit of the drug given.\nETL conventions:\nThis information may be called something different in the source data but the field is meant to contain a value indicating the unit of dosage of drug given to the patient. This is an older column and will be deprecated in an upcoming version.",
        max_length=50,
    )
    drug_exposure_start_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    drug_exposure_end_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


class DeviceExposure(Model, DataLineageMixin):
    """The Device domain captures information about a person's exposure to a foreign physical object or instrument which is used for diagnostic or therapeutic purposes through a mechanism beyond chemical action. Devices include implantable objects (e.g. pacemakers, stents, artificial joints), medical equipment and supplies (e.g. bandages, crutches, syringes), other instruments used in medical procedures (e.g. sutures, defibrillators) and material used in clinical care (e.g. adhesives, body material, dental material, surgical material)."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="DeviceExposures",
        table_name="device_exposure",
        persistable=True,
        id_field_name="device_exposure_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("device_concept_id", Concept, None),
                3: ("device_type_concept_id", Concept, None),
                4: ("provider_id", Provider, None),
                5: ("visit_occurrence_id", VisitOccurrence, None),
                6: ("visit_detail_id", VisitDetail, None),
                7: ("device_source_concept_id", Concept, None),
            }
        ),
    )
    device_exposure_id: UUID = Field(
        description="User guidance:\nThe unique key given to records a person's exposure to a foreign physical object or instrument.\nETL conventions:\nEach instance of an exposure to a foreign object or device present in the source data should be assigned this unique key."
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    device_concept_id: UUID = Field(
        description="User guidance:\nThe DEVICE_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies. This is the standard concept mapped from the source concept id which represents a foreign object or instrument the person was exposed to.\nETL conventions:\nThe CONCEPT_ID that the DEVICE_SOURCE_VALUE maps to."
    )
    device_exposure_start_date: date = Field(
        description="User guidance:\nUse this date to determine the start date of the device record.\nETL conventions:\nValid entries include a start date of a procedure to implant a device, the date of a prescription for a device, or the date of device administration."
    )
    device_exposure_start_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    device_exposure_end_date: date | None = Field(
        default=None,
        description="User guidance:\nThe DEVICE_EXPOSURE_END_DATE denotes the day the device exposure ended for the patient, if given.\nETL conventions:\nPut the end date or discontinuation date as it appears from the source data or leave blank if unavailable.",
    )
    device_exposure_end_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    device_type_concept_id: UUID = Field(
        description="User guidance:\nYou can use the TYPE_CONCEPT_ID to denote the provenance of the record, as in whether the record is from administrative claims or EHR. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=).\nETL conventions:\nChoose the device_type_concept_id that best represents the provenance of the record, for example whether it came from a record of a prescription written or physician administered drug."
    )
    unique_device_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is the Unique Device Identification number for devices regulated by the FDA, if given.\nETL conventions:\nFor medical devices that are regulated by the FDA, a Unique Device Identification (UDI) is provided if available in the data source and is recorded in the UNIQUE_DEVICE_ID field.",
    )
    quantity: int | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Provider associated with device record, e.g. the provider who wrote the prescription or the provider who implanted the device.\nETL conventions:\nThe ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit during which the device was prescribed or given.\nETL conventions:\nTo populate this field device exposures must be explicitly initiated in the visit.",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit Detail during which the device was prescribed or given.\nETL conventions:\nTo populate this field device exposures must be explicitly initiated in the visit detail record.",
    )
    device_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the device exposure that occurred. For example, this could be an NDC or Gemscript code.\nETL conventions:\nThis code is mapped to a Standard Device Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    device_source_concept_id: UUID = Field(
        description="User guidance:\nThis is the concept representing the device source value and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Device necessary for a given analytic use case. Consider using DEVICE_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network.\nETL conventions:\nIf the DEVICE_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If unavailable, set to 0."
    )
    device_exposure_start_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    device_exposure_end_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


class Measurement(Model, DataLineageMixin):
    """The MEASUREMENT table contains records of Measurements, i.e. structured values (numerical or categorical) obtained through systematic and standardized examination or testing of a Person or Person's sample. The MEASUREMENT table contains both orders and results of such Measurements as laboratory tests, vital signs, quantitative findings from pathology reports, etc. Measurements are stored as attribute value pairs, with the attribute as the Measurement Concept and the value representing the result. The value can be a Concept (stored in VALUE_AS_CONCEPT), or a numerical value (VALUE_AS_NUMBER) with a Unit (UNIT_CONCEPT_ID). The Procedure for obtaining the sample is housed in the PROCEDURE_OCCURRENCE table, though it is unnecessary to create a PROCEDURE_OCCURRENCE record for each measurement if one does not exist in the source data. Measurements differ from Observations in that they require a standardized test or some other activity to generate a quantitative or qualitative result. If there is no result, it is assumed that the lab test was conducted but the result was not captured."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Measurements",
        table_name="measurement",
        persistable=True,
        id_field_name="measurement_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("measurement_concept_id", Concept, None),
                3: ("measurement_type_concept_id", Concept, None),
                4: ("operator_concept_id", Concept, None),
                5: ("value_as_concept_id", Concept, None),
                6: ("unit_concept_id", Concept, None),
                7: ("provider_id", Provider, None),
                8: ("visit_occurrence_id", VisitOccurrence, None),
                9: ("visit_detail_id", VisitDetail, None),
                10: ("measurement_source_concept_id", Concept, None),
            }
        ),
    )
    measurement_id: UUID = Field(
        description="User guidance:\nThe unique key given to a Measurement record for a Person. Refer to the ETL for how duplicate Measurements during the same Visit were handled.\nETL conventions:\nEach instance of a measurement present in the source data should be assigned this unique key. In some cases, a person can have multiple records of the same measurement within the same visit. It is valid to keep these duplicates and assign them individual, unique, MEASUREMENT_IDs, though it is up to the ETL how they should be handled."
    )
    person_id: UUID = Field(
        description="User guidance:\nThe PERSON_ID of the PERSON for whom the measurement is recorded. This may be a system generated code.\nETL conventions:\nNone"
    )
    measurement_concept_id: UUID = Field(
        description='User guidance:\nThe MEASUREMENT_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies.\nETL conventions:\nThe CONCEPT_ID that the MEASUREMENT_SOURCE_CONCEPT_ID maps to. Only records whose SOURCE_CONCEPT_IDs map to Standard Concepts with a domain of "Measurement" should go in this table.'
    )
    measurement_date: date = Field(
        description="User guidance:\nUse this date to determine the date of the measurement.\nETL conventions:\nIf there are multiple dates in the source data associated with a record such as order_date, draw_date, and result_date, choose the one that is closest to the date the sample was drawn from the patient."
    )
    measurement_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis is not required, though it is in v6. If a source does not specify datetime the convention is to set the time to midnight (00:00:0000)",
    )
    measurement_time: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis is present for backwards compatibility and will be deprecated in an upcoming version.",
        max_length=10,
    )
    measurement_type_concept_id: UUID = Field(
        description="User guidance:\nThis field can be used to determine the provenance of the Measurement record, as in whether the measurement was from an EHR system, insurance claim, registry, or other sources.\nETL conventions:\nChoose the MEASUREMENT_TYPE_CONCEPT_ID that best represents the provenance of the record, for example whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    operator_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe meaning of Concept [4172703](https://athena.ohdsi.org/search-terms/terms/4172703) for '=' is identical to omission of a OPERATOR_CONCEPT_ID value. Since the use of this field is rare, it's important when devising analyses to not to forget testing for the content of this field for values different from =.\nETL conventions:\nThe operator_concept_id explictly refers to the value of the measurement. Operators are <, <=, =, >=, > and these concepts belong to the 'Meas Value Operator' domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Meas+Value+Operator&standardConcept=Standard&page=1&pageSize=15&query=).",
    )
    value_as_number: float | None = Field(
        default=None,
        description="User guidance:\nThis is the numerical value of the Result of the Measurement, if available. Note that measurements such as blood pressures will be split into their component parts i.e. one record for systolic, one record for diastolic.\nETL conventions:\nIf there is a negative value coming from the source, set the VALUE_AS_NUMBER to NULL, with the exception of the following Measurements (listed as LOINC codes):<br>-  [1925-7](https://athena.ohdsi.org/search-terms/terms/3003396) Base excess in Arterial blood by calculation - [1927-3](https://athena.ohdsi.org/search-terms/terms/3002032) Base excess in Venous blood by calculation - [8632-2](https://athena.ohdsi.org/search-terms/terms/3006277) QRS-Axis - [11555-0](https://athena.ohdsi.org/search-terms/terms/3012501) Base excess in Blood by calculation - [1926-5](https://athena.ohdsi.org/search-terms/terms/3003129) Base excess in Capillary blood by calculation - [28638-5](https://athena.ohdsi.org/search-terms/terms/3004959) Base excess in Arterial cord blood by calculation [28639-3](https://athena.ohdsi.org/search-terms/terms/3007435) Base excess in Venous cord blood by calculation",
    )
    value_as_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nIf the raw data gives a categorial result for measurements those values are captured and mapped to standard concepts in the 'Meas Value' domain.\nETL conventions:\nIf the raw data provides categorial results as well as continuous results for measurements, it is a valid ETL choice to preserve both values. The continuous value should go in the VALUE_AS_NUMBER field and the categorical value should be mapped to a standard concept in the 'Meas Value' domain and put in the VALUE_AS_CONCEPT_ID field. This is also the destination for the 'Maps to value' relationship.",
    )
    unit_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThere is currently no recommended unit for individual measurements, i.e. it is not mandatory to represent Hemoglobin a1C measurements as a percentage. UNIT_SOURCE_VALUES should be mapped to a Standard Concept in the Unit domain that best represents the unit as given in the source data.\nETL conventions:\nThere is no standardization requirement for units associated with MEASUREMENT_CONCEPT_IDs, however, it is the responsibility of the ETL to choose the most plausible unit.",
    )
    range_low: float | None = Field(
        default=None,
        description="User guidance:\nRanges have the same unit as the VALUE_AS_NUMBER. These ranges are provided by the source and should remain NULL if not given.\nETL conventions:\nIf reference ranges for upper and lower limit of normal as provided (typically by a laboratory) these are stored in the RANGE_HIGH and RANGE_LOW fields. This should be set to NULL if not provided.",
    )
    range_high: float | None = Field(
        default=None,
        description="User guidance:\nRanges have the same unit as the VALUE_AS_NUMBER. These ranges are provided by the source and should remain NULL if not given.\nETL conventions:\nIf reference ranges for upper and lower limit of normal as provided (typically by a laboratory) these are stored in the RANGE_HIGH and RANGE_LOW fields. This should be set to NULL if not provided.",
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe provider associated with measurement record, e.g. the provider who ordered the test or the provider who recorded the result.\nETL conventions:\nThe ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record. For example the admitting vs attending physician on an EHR record.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe visit during which the Measurement occurred.\nETL conventions:\nDepending on the structure of the source data, this may have to be determined based on dates. If a MEASUREMENT_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the measurement record. If a measurement is related to a visit explicitly in the source data, it is possible that the result date of the Measurement falls outside of the bounds of the Visit dates.",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe VISIT_DETAIL record during which the Measurement occurred. For example, if the Person was in the ICU at the time the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.\nETL conventions:\nSame rules apply as for the VISIT_OCCURRENCE_ID.",
    )
    measurement_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the Measurement that occurred. For example, this could be an ICD10 or Read code.\nETL conventions:\nThis code is mapped to a Standard Measurement Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    measurement_source_concept_id: UUID = Field(
        description="User guidance:\nThis is the concept representing the MEASUREMENT_SOURCE_VALUE and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Measurement necessary for a given analytic use case. Consider using MEASUREMENT_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network.\nETL conventions:\nIf the MEASUREMENT_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If not available, set to 0."
    )
    unit_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the unit of the Measurement that occurred.\nETL conventions:\nThis code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    value_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim result value of the Measurement from the source data .\nETL conventions:\nIf both a continuous and categorical result are given in the source data such that both VALUE_AS_NUMBER and VALUE_AS_CONCEPT_ID are both included, store the verbatim value that was mapped to VALUE_AS_CONCEPT_ID here.",
        max_length=50,
    )
    measurement_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    derived_from_specimen_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The specimen from which this measurement was derived.\nETL conventions:\nNone",
    )


class Observation(Model, DataLineageMixin):
    """The OBSERVATION table captures clinical facts about a Person obtained in the context of examination, questioning or a procedure. Any data that cannot be represented by any other domains, such as social and lifestyle facts, medical history, family history, etc. are recorded here. **New to CDM v6.0** An Observation can now be linked to other records in the CDM instance using the fields OBSERVATION_EVENT_ID and OBS_EVENT_FIELD_CONCEPT_ID. To link another record to an Observation, the primary key goes in OBSERVATION_EVENT_ID (CONDITION_OCCURRENCE_ID, DRUG_EXPOSURE_ID, etc.) and the Concept representing the field where the OBSERVATION_EVENT_ID was taken from go in the OBS_EVENT_FIELD_CONCEPT_ID. For example, a CONDITION_OCCURRENCE of Asthma might be linked to an Observation of a family history of Asthma. In this case the CONDITION_OCCURRENCE_ID of the Asthma record would go in OBSERVATION_EVENT_ID of the family history record and the CONCEPT_ID [1147127](https://athena.ohdsi.org/search-terms/terms/1147127) would go in OBS_EVENT_FIELD_CONCEPT_ID to denote that the OBSERVATION_EVENT_ID represents a CONDITION_OCCURRENCE_ID."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Observations",
        table_name="observation",
        persistable=True,
        id_field_name="observation_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("observation_concept_id", Concept, None),
                3: ("observation_type_concept_id", Concept, None),
                4: ("value_as_concept_id", Concept, None),
                5: ("qualifier_concept_id", Concept, None),
                6: ("unit_concept_id", Concept, None),
                7: ("provider_id", Provider, None),
                8: ("visit_occurrence_id", VisitOccurrence, None),
                9: ("visit_detail_id", VisitDetail, None),
                10: ("observation_source_concept_id", Concept, None),
                11: ("obs_event_field_concept_id", Concept, None),
            }
        ),
    )
    observation_id: UUID = Field(
        description="User guidance:\nThe unique key given to an Observation record for a Person. Refer to the ETL for how duplicate Observations during the same Visit were handled.\nETL conventions:\nEach instance of an observation present in the source data should be assigned this unique key."
    )
    person_id: UUID = Field(
        description="User guidance:\nThe PERSON_ID of the Person for whom the Observation is recorded. This may be a system generated code.\nETL conventions:\nNone"
    )
    observation_concept_id: UUID = Field(
        description="User guidance:\nThe OBSERVATION_CONCEPT_ID field is recommended for primary use in analyses, and must be used for network studies.\nETL conventions:\nThe CONCEPT_ID that the OBSERVATION_SOURCE_CONCEPT_ID maps to. There is no specified domain that the Concepts in this table must adhere to. The only rule is that records with Concepts in the Condition, Procedure, Drug, Measurement, or Device domains MUST go to the corresponding table."
    )
    observation_date: date | None = Field(
        default=None,
        description="User guidance:\nThe date of the Observation. Depending on what the Observation represents this could be the date of a lab test, the date of a survey, or the date a patient's family history was taken.\nETL conventions:\nFor some observations the ETL may need to make a choice as to which date to choose.",
    )
    observation_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nIf no time is given set to midnight (00:00:00)."
    )
    observation_type_concept_id: UUID = Field(
        description="User guidance:\nThis field can be used to determine the provenance of the Observation record, as in whether the measurement was from an EHR system, insurance claim, registry, or other sources.\nETL conventions:\nChoose the OBSERVATION_TYPE_CONCEPT_ID that best represents the provenance of the record, for example whether it came from an EHR record or billing claim. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Type+Concept&standardConcept=Standard&page=1&pageSize=15&query=)."
    )
    value_as_number: float | None = Field(
        default=None,
        description="User guidance:\nThis is the numerical value of the Result of the Observation, if applicable and available. It is not expected that all Observations will have numeric results, rather, this field is here to house values should they exist.\nETL conventions:\nNone",
    )
    value_as_string: str | None = Field(
        default=None,
        description="User guidance:\nThis is the categorical value of the Result of the Observation, if applicable and available.\nETL conventions:\nNone",
        max_length=60,
    )
    value_as_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nIt is possible that some records destined for the Observation table have two clinical ideas represented in one source code. This is common with ICD10 codes that describe a family history of some Condition, for example. In OMOP the Vocabulary breaks these two clinical ideas into two codes; one becomes the OBSERVATION_CONCEPT_ID and the other becomes the VALUE_AS_CONCEPT_ID. It is important when using the Observation table to keep this possibility in mind and to examine the VALUE_AS_CONCEPT_ID field for relevant information.\nETL conventions:\nNote that the value of VALUE_AS_CONCEPT_ID may be provided through mapping from a source Concept which contains the content of the Observation. In those situations, the CONCEPT_RELATIONSHIP table in addition to the 'Maps to' record contains a second record with the relationship_id set to 'Maps to value'. For example, ICD10 [Z82.4](https://athena.ohdsi.org/search-terms/terms/45581076) 'Family history of ischaemic heart disease and other diseases of the circulatory system' has a 'Maps to' relationship to [4167217](https://athena.ohdsi.org/search-terms/terms/4167217) 'Family history of clinical finding' as well as a 'Maps to value' record to [134057](https://athena.ohdsi.org/search-terms/terms/134057) 'Disorder of cardiovascular system'.",
    )
    qualifier_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis field contains all attributes specifying the clinical fact further, such as as degrees, severities, drug-drug interaction alerts etc.\nETL conventions:\nUse your best judgement as to what Concepts to use here and if they are necessary to accurately represent the clinical record. There is no restriction on the domain of these Concepts, they just need to be Standard.",
    )
    unit_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThere is currently no recommended unit for individual observation concepts. UNIT_SOURCE_VALUES should be mapped to a Standard Concept in the Unit domain that best represents the unit as given in the source data.\nETL conventions:\nThere is no standardization requirement for units associated with OBSERVATION_CONCEPT_IDs, however, it is the responsibility of the ETL to choose the most plausible unit.",
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe provider associated with the observation record, e.g. the provider who ordered the test or the provider who recorded the result.\nETL conventions:\nThe ETL may need to make a choice as to which PROVIDER_ID to put here. Based on what is available this may or may not be different than the provider associated with the overall VISIT_OCCURRENCE record. For example the admitting vs attending physician on an EHR record.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe visit during which the Observation occurred.\nETL conventions:\nDepending on the structure of the source data, this may have to be determined based on dates. If an OBSERVATION_DATE occurs within the start and end date of a Visit it is a valid ETL choice to choose the VISIT_OCCURRENCE_ID from the visit that subsumes it, even if not explicitly stated in the data. While not required, an attempt should be made to locate the VISIT_OCCURRENCE_ID of the observation record. If an observation is related to a visit explicitly in the source data, it is possible that the result date of the Observation falls outside of the bounds of the Visit dates.",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe VISIT_DETAIL record during which the Observation occurred. For example, if the Person was in the ICU at the time the VISIT_OCCURRENCE record would reflect the overall hospital stay and the VISIT_DETAIL record would reflect the ICU stay during the hospital visit.\nETL conventions:\nSame rules apply as for the VISIT_OCCURRENCE_ID.",
    )
    observation_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the Observation that occurred. For example, this could be an ICD10 or Read code.\nETL conventions:\nThis code is mapped to a Standard Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    observation_source_concept_id: UUID = Field(
        description="User guidance:\nThis is the concept representing the OBSERVATION_SOURCE_VALUE and may not necessarily be standard. This field is discouraged from use in analysis because it is not required to contain Standard Concepts that are used across the OHDSI community, and should only be used when Standard Concepts do not adequately represent the source detail for the Observation necessary for a given analytic use case. Consider using OBSERVATION_CONCEPT_ID instead to enable standardized analytics that can be consistent across the network.\nETL conventions:\nIf the OBSERVATION_SOURCE_VALUE is coded in the source data using an OMOP supported vocabulary put the concept id representing the source value here. If not available, set to 0."
    )
    unit_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the unit of the Observation that occurred.\nETL conventions:\nThis code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    qualifier_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThis field houses the verbatim value from the source data representing the qualifier of the Observation that occurred.\nETL conventions:\nThis code is mapped to a Standard Condition Concept in the Standardized Vocabularies and the original code is stored here for reference.",
        max_length=50,
    )
    observation_event_id: UUID | None = Field(
        default=None,
        description="User guidance:\nIf the Observation record is related to another record in the database, this field is the primary key of the linked record.\nETL conventions:\nPut the primary key of the linked record, if applicable, here. See the [ETL Conventions for the OBSERVATION](https://ohdsi.github.io/CommonDataModel/cdm60.html#observation) table for more details.",
    )
    obs_event_field_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nIf the Observation record is related to another record in the database, this field is the CONCEPT_ID that identifies which table the primary key of the linked record came from.\nETL conventions:\nPut the CONCEPT_ID that identifies which table and field the OBSERVATION_EVENT_ID came from.",
    )
    value_as_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nIt is possible that some Observation records might store a result as a date value.\nETL conventions:\nNone",
    )
    observation_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    value_as_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )


class Specimen(Model, DataLineageMixin):
    """The specimen domain contains the records identifying biological samples from a person."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Specimens",
        table_name="specimen",
        persistable=True,
        id_field_name="specimen_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("specimen_concept_id", Concept, None),
                3: ("specimen_type_concept_id", Concept, None),
                4: ("unit_concept_id", Concept, None),
                5: ("anatomic_site_concept_id", Concept, None),
                6: ("disease_status_concept_id", Concept, None),
                7: ("derived_from_specimen_concept_id", Concept, None),
            }
        ),
    )
    specimen_id: UUID = Field(
        description="User guidance:\nUnique identifier for each specimen.\nETL conventions:\nNone"
    )
    person_id: UUID = Field(
        description="User guidance:\nThe person from whom the specimen is collected.\nETL conventions:\nNone"
    )
    specimen_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nThe standard CONCEPT_ID that the SPECIMEN_SOURCE_VALUE maps to in the specimen domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Specimen&standardConcept=Standard&page=1&pageSize=15&query=)"
    )
    specimen_type_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nPut the source of the specimen record, as in an EHR system. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=)."
    )
    specimen_date: date = Field(
        description="User guidance:\nThe date the specimen was collected.\nETL conventions:\nNone"
    )
    specimen_datetime: datetime | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    quantity: float | None = Field(
        default=None,
        description="User guidance:\nThe amount of specimen collected from the person.\nETL conventions:\nNone",
    )
    unit_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe unit for the quantity of the specimen.\nETL conventions:\nMap the UNIT_SOURCE_VALUE to a Standard Concept in the Unit domain. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?domain=Unit&standardConcept=Standard&page=1&pageSize=15&query=)",
    )
    anatomic_site_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is the site on the body where the specimen is from.\nETL conventions:\nMap the ANATOMIC_SITE_SOURCE_VALUE to a Standard Concept in the Spec Anatomic Site domain. This should be coded at the lowest level of granularity [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Spec+Anatomic+Site&conceptClass=Body+Structure&page=4&pageSize=15&query=)",
    )
    disease_status_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    specimen_source_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is the identifier for the specimen from the source system.\nETL conventions:\nNone",
    )
    specimen_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=50,
    )
    unit_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis unit for the quantity of the specimen, as represented in the source.",
        max_length=50,
    )
    anatomic_site_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThis is the site on the body where the specimen was taken from, as represented in the source.",
        max_length=50,
    )
    disease_status_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nNone",
        max_length=50,
    )
    specimen_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    derived_from_specimen_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The source specimen from which this specimen was derived.\nETL conventions:\nNone",
    )
    derived_from_specimen_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. The protocol used to derive this specimen from the source specimen.\nETL conventions:\nNone",
    )


class Note(Model, DataLineageMixin):
    """The NOTE table captures unstructured information that was recorded by a provider about a patient in free text (in ASCII, or preferably in UTF8 format) notes on a given date. The type of note_text is CLOB or varchar(MAX) depending on RDBMS."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="Notes",
        table_name="note",
        persistable=True,
        id_field_name="note_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("note_event_field_concept_id", Concept, None),
                3: ("note_type_concept_id", Concept, None),
                4: ("note_class_concept_id", Concept, None),
                5: ("encoding_concept_id", Concept, None),
                6: ("language_concept_id", Concept, None),
                7: ("provider_id", Provider, None),
                8: ("visit_occurrence_id", VisitOccurrence, None),
                9: ("visit_detail_id", VisitDetail, None),
            }
        ),
    )
    note_id: UUID = Field(
        description="User guidance:\nA unique identifier for each note.\nETL conventions:\nNone"
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    note_event_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    note_event_field_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    note_date: date = Field(
        description="User guidance:\nThe date the note was recorded.\nETL conventions:\nNone"
    )
    note_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf time is not given set the time to midnight.",
    )
    note_type_concept_id: UUID = Field(
        description="User guidance:\nThe provenance of the note. Most likely this will be EHR.\nETL conventions:\nPut the source system of the note, as in EHR record. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&domain=Type+Concept&page=1&pageSize=15&query=)."
    )
    note_class_concept_id: UUID = Field(
        description="User guidance:\nA Standard Concept Id representing the HL7 LOINC\r\nDocument Type Vocabulary classification of the note.\nETL conventions:\nMap the note classification to a Standard Concept. For more information see the ETL Conventions in the description of the NOTE table. [AcceptedConcepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&conceptClass=Doc+Kind&conceptClass=Doc+Role&conceptClass=Doc+Setting&conceptClass=Doc+Subject+Matter&conceptClass=Doc+Type+of+Service&domain=Meas+Value&page=1&pageSize=15&query=). This Concept can alternatively be represented by concepts with the relationship 'Kind of (LOINC)' to [706391](https://athena.ohdsi.org/search-terms/terms/706391) (Note)."
    )
    note_title: str | None = Field(
        default=None,
        description="User guidance:\nThe title of the note.\nETL conventions:\nNone",
        max_length=250,
    )
    note_text: str = Field(
        description="User guidance:\nThe content of the note.\nETL conventions:\nNone"
    )
    encoding_concept_id: UUID = Field(
        description="User guidance:\nThis is the Concept representing the character encoding type.\nETL conventions:\nPut the Concept Id that represents the encoding character type here. Currently the only option is UTF-8 ([32678](https://athena.ohdsi.org/search-terms/terms/32678)). It the note is encoded in any other type, like ASCII then put 0."
    )
    language_concept_id: UUID = Field(
        description="User guidance:\nThe language of the note.\nETL conventions:\nUse Concepts that are descendants of the concept [4182347](https://athena.ohdsi.org/search-terms/terms/4182347) (World Languages)."
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Provider who wrote the note.\nETL conventions:\nThe ETL may need to make a determination on which provider to put here.",
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit during which the note was written.\nETL conventions:\nNone",
    )
    visit_detail_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit Detail during which the note was written.\nETL conventions:\nNone",
    )
    note_source_value: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThe source value mapped to the NOTE_CLASS_CONCEPT_ID.",
        max_length=50,
    )


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
            {1: ("person_id", Person, None), 2: ("drug_concept_id", Concept, None)}
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
    dose_era_start_datetime: datetime = Field(
        description="User guidance:\nThe date the Person started on the specific dosage, with at least 31 days since any prior exposure.\nETL conventions:\nNone"
    )
    dose_era_end_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nThe date the Person was no longer exposed to the dosage of the specific drug ingredient. An era is ended if there are 31 days or more between dosage records."
    )


class NoteNlp(Model, DataLineageMixin):
    """The NOTE_NLP table encodes all output of NLP on clinical notes. Each row represents a single extracted term from a note."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="NoteNlps",
        table_name="note_nlp",
        persistable=True,
        id_field_name="note_nlp_id",
        links=create_links(
            {
                1: ("note_id", Note, None),
                2: ("section_concept_id", Concept, None),
                3: ("note_nlp_concept_id", Concept, None),
                4: ("note_nlp_source_concept_id", Concept, None),
            }
        ),
    )
    note_nlp_id: UUID = Field(
        description="User guidance:\nA unique identifier for the NLP record.\nETL conventions:\nNone"
    )
    note_id: UUID = Field(
        description="User guidance:\nThis is the NOTE_ID for the NOTE record the NLP record is associated to.\nETL conventions:\nNone"
    )
    section_concept_id: UUID | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nThe SECTION_CONCEPT_ID should be used to represent the note section contained in the NOTE_NLP record. These concepts can be found as parts of document panels and are based on the type of note written, i.e. a discharge summary. These panels can be found as concepts with the relationship 'Subsumes' to CONCEPT_ID [45875957](https://athena.ohdsi.org/search-terms/terms/45875957).",
    )
    snippet: str | None = Field(
        default=None,
        description="User guidance:\nA small window of text surrounding the term\nETL conventions:\nNone",
        max_length=250,
    )
    offset: str | None = Field(
        default=None,
        description="User guidance:\nCharacter offset of the extracted term in the input note\nETL conventions:\nNone",
        max_length=50,
    )
    lexical_variant: str = Field(
        description="User guidance:\nRaw text extracted from the NLP tool.\nETL conventions:\nNone",
        max_length=250,
    )
    note_nlp_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    note_nlp_source_concept_id: UUID | None = Field(
        default=None, description="User guidance:\nNone\nETL conventions:\nNone"
    )
    nlp_system: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nName and version of the NLP system that extracted the term. Useful for data provenance.",
        max_length=250,
    )
    nlp_date: date = Field(
        description="User guidance:\nThe date of the note processing.\nETL conventions:\nNone"
    )
    nlp_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nThe date and time of the note processing.\nETL conventions:\nNone",
    )
    term_exists: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nTerm_exists is defined as a flag that indicates if the patient actually has or had the condition. Any of the following modifiers would make Term_exists false:\r\nNegation = true\r\nSubject = [anything other than the patient]\r\nConditional = true/li>\r\nRule_out = true\r\nUncertain = very low certainty or any lower certainties\r\nA complete lack of modifiers would make Term_exists true.\r\n",
        max_length=1,
    )
    term_temporal: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nTerm_temporal is to indicate if a condition is present or just in the past. The following would be past:<br><br>\r\n- History = true\r\n- Concept_date = anything before the time of the report",
        max_length=50,
    )
    term_modifiers: str | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nFor the modifiers that are there, they would have to have these values:<br><br>\r\n- Negation = false\r\n- Subject = patient\r\n- Conditional = false\r\n- Rule_out = false\r\n- Uncertain = true or high or moderate or even low (could argue about low). Term_modifiers will concatenate all modifiers for different types of entities (conditions, drugs, labs etc) into one string. Lab values will be saved as one of the modifiers.",
        max_length=2000,
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


class LocationHistory(Model, DataLineageMixin):
    """The LOCATION HISTORY table stores relationships between Persons or Care Sites and geographic locations over time. **This table is new to CDM v6.0**"""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="LocationHistorys",
        table_name="location_history",
        persistable=True,
        id_field_name="location_history_id",
        links=create_links(
            {
                1: ("location_id", Location, None),
                2: ("relationship_type_concept_id", Concept, None),
            }
        ),
    )
    location_id: UUID = Field(
        description="User guidance:\nThis is the LOCATION_ID for the LOCATION_HISTORY record.\nETL conventions:\nNone"
    )
    relationship_type_concept_id: UUID = Field(
        description="User guidance:\nThis is the relationship between the location and the entity (PERSON, PROVIDER, or CARE_SITE)\nETL conventions:\nConcepts in this field must be in the Location class. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&conceptClass=Location&page=1&pageSize=15&query=&boosts). If the DOMAIN_ID is CARE_SITE this should be 0 and when the domain is PROVIDER the value is [Office](https://athena.ohdsi.org/search-terms/terms/4121722)."
    )
    domain_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nThe domain of the entity that is related to the location. Either PERSON, PROVIDER, or CARE_SITE."
    )
    entity_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nThe unique identifier for the entity. References either person_id, provider_id, or care_site_id, depending on domain_id."
    )
    start_date: date = Field(
        description="User guidance:\nThe date the relationship started\nETL conventions:\nNone"
    )
    end_date: date | None = Field(
        default=None,
        description="User guidance:\nThe date the relationship ended\nETL conventions:\nNone",
    )
    start_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    end_iso_interval: str | None = Field(
        default=None,
        description="User guidance:\nNot part of OMOP CDM. See corresponding date variable. Allows for more uncertainty on the time.\nETL conventions:\nNone",
        max_length=55,
    )
    location_history_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class SurveyConduct(Model, DataLineageMixin):
    """The SURVEY_CONDUCT table is used to store an instance of a completed survey or questionnaire."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="SurveyConducts",
        table_name="survey_conduct",
        persistable=True,
        id_field_name="survey_conduct_id",
        links=create_links(
            {
                1: ("person_id", Person, None),
                2: ("survey_concept_id", Concept, None),
                3: ("provider_id", Provider, None),
                4: ("assisted_concept_id", Concept, None),
                5: ("respondent_type_concept_id", Concept, None),
                6: ("timing_concept_id", Concept, None),
                7: ("collection_method_concept_id", Concept, None),
                8: ("survey_source_concept_id", Concept, None),
                9: ("validated_survey_concept_id", Concept, None),
                10: ("visit_occurrence_id", VisitOccurrence, None),
                11: ("response_visit_occurrence_id", VisitOccurrence, None),
            }
        ),
    )
    survey_conduct_id: UUID = Field(
        description="User guidance:\nUnique identifier for each completed survey.\nETL conventions:\nFor each instance of a survey completion create a unique identifier."
    )
    person_id: UUID = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    survey_concept_id: UUID = Field(
        description="User guidance:\nThis is the Concept that represents the survey that was completed.\nETL conventions:\nPut the CONCEPT_ID that identifies the survey that the Person completed. There is no specified domain for this table but the concept class 'staging/scales' contains many common surveys. [Accepted Concepts](https://athena.ohdsi.org/search-terms/terms?standardConcept=Standard&conceptClass=Staging+%2F+Scales&page=5&pageSize=15&query=)."
    )
    survey_start_date: date | None = Field(
        default=None,
        description="User guidance:\nDate on which the survey was started.\nETL conventions:\nNone",
    )
    survey_start_datetime: datetime | None = Field(
        default=None,
        description="User guidance:\nNone\nETL conventions:\nIf no time given, set to midnight.",
    )
    survey_end_date: date | None = Field(
        default=None,
        description="User guidance:\nDate on which the survey was completed.\nETL conventions:\nNone",
    )
    survey_end_datetime: datetime = Field(
        description="User guidance:\nNone\nETL conventions:\nIf no time given, set to midnight."
    )
    provider_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThis is the Provider associated with the survey completion.\nETL conventions:\nThe ETL may need to make a choice as to which Provider to put here. This could either be the provider that ordered the survey or the provider who observed the completion of the survey.",
    )
    assisted_concept_id: UUID = Field(
        description="User guidance:\nThis is a Concept that represents whether the survey was completed with assistance or independently.\nETL conventions:\nThere is no specific domain or class for this field, just choose the one that best represents the value given in the source."
    )
    respondent_type_concept_id: UUID = Field(
        description="User guidance:\nThis is a Concept that represents who actually recorded the answers to the survey. For example, this could be the patient or a research associate.\nETL conventions:\nThere is no specific domain or class for this field, just choose the one that best represents the value given in the source."
    )
    timing_concept_id: UUID = Field(
        description="User guidance:\nThis is a Concept that represents the timing of the survey. For example this could be the 3-month follow-up appointment.\nETL conventions:\nThere is no specific domain or class for this field, just choose the one that best represents the value given in the source."
    )
    collection_method_concept_id: UUID = Field(
        description="User guidance:\nThis Concept represents how the responses were collected.\nETL conventions:\nUse the concepts that have the relationship 'Has Answer' with the CONCEPT_ID [42529316](https://athena.ohdsi.org/search-terms/terms/42529316)."
    )
    assisted_source_value: str | None = Field(
        default=None,
        description="User guidance:\nSource value representing whether patient required assistance to complete the survey. Example: 'Completed without assistance', 'Completed with assistance'.\nETL conventions:\nNone",
        max_length=50,
    )
    respondent_type_source_value: str | None = Field(
        default=None,
        description="User guidance:\nSource code representing role of person who completed the survey.\nETL conventions:\nNone",
        max_length=100,
    )
    timing_source_value: str | None = Field(
        default=None,
        description="User guidance:\nText string representing the timing of the survey. Example: Baseline, 6-month follow-up.\nETL conventions:\nNone",
        max_length=100,
    )
    collection_method_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe collection method as it appears in the source data.\nETL conventions:\nNone",
        max_length=100,
    )
    survey_source_value: str | None = Field(
        default=None,
        description="User guidance:\nThe survey name as it appears in the source data.\nETL conventions:\nNone",
        max_length=100,
    )
    survey_source_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf unavailable, set to 0."
    )
    survey_source_identifier: str | None = Field(
        default=None,
        description="User guidance:\nUnique identifier for each completed survey in source system.\nETL conventions:\nNone",
        max_length=100,
    )
    validated_survey_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nIf unavailable, set to 0."
    )
    validated_survey_source_value: str | None = Field(
        default=None,
        description="User guidance:\nSource value representing the validation status of the survey.\nETL conventions:\nNone",
        max_length=100,
    )
    survey_version_number: str | None = Field(
        default=None,
        description="User guidance:\nVersion number of the questionnaire or survey used.\nETL conventions:\nNone",
        max_length=20,
    )
    visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit during which the Survey occurred.\nETL conventions:\nNone",
    )
    response_visit_occurrence_id: UUID | None = Field(
        default=None,
        description="User guidance:\nThe Visit during which any treatment related to the Survey was carried out.\nETL conventions:\nNone",
    )


class FactRelationship(Model):
    """The FACT_RELATIONSHIP table contains records about the relationships between facts stored as records in any table of the CDM. Relationships can be defined between facts from the same domain, or different domains. Examples of Fact Relationships include: [Person relationships](https://athena.ohdsi.org/search-terms/terms?domain=Relationship&standardConcept=Standard&page=2&pageSize=15&query=) (parent-child), care site relationships (hierarchical organizational structure of facilities within a health system), indication relationship (between drug exposures and associated conditions), usage relationships (of devices during the course of an associated procedure), or facts derived from one another (measurements derived from an associated specimen)."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="FactRelationships",
        table_name="fact_relationship",
        persistable=True,
        id_field_name="fact_relationship_id",
        links=create_links(
            {
                1: ("domain_concept_id_1", Concept, None),
                2: ("domain_concept_id_2", Concept, None),
                3: ("relationship_concept_id", Concept, None),
            }
        ),
    )
    domain_concept_id_1: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    fact_id_1: int = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    domain_concept_id_2: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    fact_id_2: int = Field(description="User guidance:\nNone\nETL conventions:\nNone")
    relationship_concept_id: UUID = Field(
        description="User guidance:\nNone\nETL conventions:\nNone"
    )
    fact_relationship_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )


class MeasurementRelation(Model):
    """Not part of OMOP CDM. The MEASUREMENT_RELATION table contains a directed acyclic graph of Measurements that expresses how they were derived from one another so that this information can be used further."""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="measurement_relations",
        table_name="measurement_relation",
        persistable=True,
        id_field_name="measurement_relation_id",
        links=create_links(
            {
                1: ("from_measurement_id", Measurement, None),
                2: ("to_measurement_id", Measurement, None),
            }
        ),
    )
    measurement_relation_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )
    from_measurement_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The measurement from which the to measuremunt was derived.\nETL conventions:\nNone"
    )
    to_measurement_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The measurement that was derived.\nETL conventions:\nNone"
    )
