"""
Ontology domain - OMOP CDM v6.0 vocabulary tables.

This module contains the standardized vocabulary classes that form the basis of the OMOP CDM.
These tables store the controlled vocabularies, concept hierarchies, and mappings between
source codes and standard concepts.

Classes:
- Vocabulary: List of all vocabularies
- Domain: OMOP domains (Condition, Drug, etc.)
- ConceptClass: Classifications within vocabularies
- Concept: Core concept table with all standardized terms
- Relationship: Types of relationships between concepts
- ConceptRelationship: Direct relationships between two concepts
- ConceptAncestor: Hierarchical ancestry relationships
- ConceptSynonym: Alternative names and translations
- DrugStrength: Drug ingredient amounts and concentrations
- SourceToConceptMap: Legacy table for source-to-standard concept mappings
"""

from datetime import date
from typing import ClassVar
from uuid import UUID

from pydantic import Field

from gen_epix.fastapp import Model
from gen_epix.fastapp.domain import Entity, create_links


class Vocabulary(Model):
    """The VOCABULARY table includes a list of the Vocabularies integrated from various sources or created de novo in OMOP CDM. This reference table contains a single record for each Vocabulary and includes a descriptive name and other associated attributes for the Vocabulary."""

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
        description="User guidance:\nThe name describing the vocabulary, for\r\nexample, International Classification of\r\nDiseases, Ninth Revision, Clinical\r\nModification, Volume 1 and 2 (NCHS) etc.\nETL conventions:\nNone",
        max_length=255,
    )
    vocabulary_reference: str | None = Field(
        default=None,
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
    """The DOMAIN table includes a list of OMOP-defined Domains to which the Concepts of the Standardized Vocabularies can belong. A Domain represents a clinical definition whereby we assign matching Concepts for the standardized fields in the CDM tables. For example, the Condition Domain contains Concepts that describe a patient condition, and these Concepts can only be used in the condition_concept_id field of the CONDITION_OCCURRENCE and CONDITION_ERA tables. This reference table is populated with a single record for each Domain, including a Domain ID and a descriptive name for every Domain."""

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
    """The CONCEPT_CLASS table includes semantic categories that reference the source structure of each Vocabulary. Concept Classes represent so-called horizontal (e.g. MedDRA, RxNorm) or vertical levels (e.g. SNOMED) of the vocabulary structure. Vocabularies without any Concept Classes, such as HCPCS, use the vocabulary_id as the Concept Class. This reference table is populated with a single record for each Concept Class, which includes a Concept Class ID and a fully specified Concept Class name."""

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
    """The Standardized Vocabularies contains records, or Concepts, that uniquely identify each fundamental unit of meaning used to express clinical information in all domain tables of the CDM. Concepts are derived from vocabularies, which represent clinical information across a domain (e.g. conditions, drugs, procedures) through the use of codes and associated descriptions. Some Concepts are designated Standard Concepts, meaning these Concepts can be used as normative expressions of a clinical entity within the OMOP Common Data Model and standardized analytics. Each Standard Concept belongs to one Domain, which defines the location where the Concept would be expected to occur within the data tables of the CDM. Concepts can represent broad categories ('Cardiovascular disease'), detailed clinical elements ('Myocardial infarction of the anterolateral wall'), or modifying characteristics and attributes that define Concepts at various levels of detail (severity of a disease, associated morphology, etc.). Records in the Standardized Vocabularies tables are derived from national or international vocabularies such as SNOMED-CT, RxNorm, and LOINC, or custom OMOP Concepts defined to cover various aspects of observational data analysis."""

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
        description="User guidance:\nA foreign key to the [DOMAIN](https://ohdsi.github.io/CommonDataModel/cdm54.html#domain) table the Concept belongs to.\nETL conventions:\nNone"
    )
    vocabulary_id: UUID = Field(
        description="User guidance:\nA foreign key to the [VOCABULARY](https://ohdsi.github.io/CommonDataModel/cdm54.html#vocabulary)\r\ntable indicating from which source the\r\nConcept has been adapted.\nETL conventions:\nNone"
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
        description="User guidance:\nThe type of relationship captured by the\r\nrelationship record.\nETL conventions:\nNone"
    )
    relationship_name: str = Field(
        description="User guidance:\nNone\nETL conventions:\nNone", max_length=255
    )
    is_hierarchical: str = Field(
        description="User guidance:\nDefines whether a relationship defines\r\nconcepts into classes or hierarchies. Values\r\nare 1 for hierarchical relationship or 0 if not.\nETL conventions:\nNone",
        max_length=1,
    )
    defines_ancestry: str = Field(
        description="User guidance:\nDefines whether a hierarchical relationship\r\ncontributes to the concept_ancestor table.\r\nThese are subsets of the hierarchical\r\nrelationships. Valid values are 1 or 0.\nETL conventions:\nNone",
        max_length=1,
    )
    reverse_relationship_id: UUID = Field(
        description="User guidance:\nThe identifier for the relationship used to\r\ndefine the reverse relationship between two\r\nconcepts.\nETL conventions:\nNone"
    )
    relationship_concept_id: UUID = Field(
        description="User guidance:\nA foreign key that refers to an identifier in\r\nthe [CONCEPT](https://ohdsi.github.io/CommonDataModel/cdm54.html#concept) table for the unique\r\nrelationship concept.\nETL conventions:\nNone"
    )


class ConceptRelationship(Model):
    """The CONCEPT_RELATIONSHIP table contains records that define relationships between any two Concepts and the nature or type of the relationship. This table captures various types of relationships, including hierarchical, associative, and other semantic connections, enabling comprehensive analysis and interpretation of clinical concepts. Every kind of relationship is defined in the RELATIONSHIP table."""

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
    """The source to concept map table is recommended for use in ETL processes to maintain local source codes which are not available as Concepts in the Standardized Vocabularies, and to establish mappings for each source code into a Standard Concept as target_concept_ids that can be used to populate the Common Data Model tables. The SOURCE_TO_CONCEPT_MAP table is no longer populated with content within the Standardized Vocabularies published to the OMOP community. **There are OHDSI tools to help you populate this table; [Usagi](https://github.com/OHDSI/Usagi) and [Perseus](https://github.com/ohdsi/Perseus). You can read more about OMOP vocabulary mapping in [The Book of OHDSI Chapter 6.3](https://ohdsi.github.io/TheBookOfOhdsi/ExtractTransformLoad.html#step-2-create-the-code-mappings).**"""

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
        description="User guidance:\nReason the mapping instance was invalidated. Possible values are D (deleted), U (replaced with an update) or NULL when valid_end_date has the default value.\nETL conventions:\nNone",
        max_length=1,
    )
    source_to_concept_map_id: UUID = Field(
        description="User guidance:\nNot part of OMOP CDM. The primary key for this table.\nETL conventions:\nNone"
    )
