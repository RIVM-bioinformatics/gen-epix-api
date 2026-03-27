# omopdb — Detailed Entity-Relationship Diagram

Auto-generated from domain model definitions.  Contains **69** persistable entities with their field definitions.

```mermaid
erDiagram
    %% omopdb — all persistable entities (detailed)

    %% Relationships
    OrganizationSetMember }o--|| OrganizationSet : "organization_set_id"
    OrganizationSetMember }o--|| Organization : "organization_id"
    DataCollectionSetMember }o--|| DataCollectionSet : "data_collection_set_id"
    DataCollectionSetMember }o--|| DataCollection : "data_collection_id"
    OrganizationIdentifierIssuerLink }o--|| Organization : "organization_id"
    OrganizationIdentifierIssuerLink }o--|| IdentifierIssuer : "identifier_issuer_id"
    Site }o--|| Organization : "organization_id"
    Contact }o--|| Site : "site_id"
    User }o--|| Organization : "organization_id"
    UserInvitation }o--|| Organization : "organization_id"
    UserInvitation }o--|| User : "invited_by_user_id"
    OrganizationAdminPolicy }o--|| Organization : "organization_id"
    OrganizationAdminPolicy }o--|| User : "user_id"
    Concept }o--|| Domain : "domain_id"
    Concept }o--|| Vocabulary : "vocabulary_id"
    Concept }o--|| ConceptClass : "concept_class_id"
    Relationship }o--|| Concept : "relationship_concept_id"
    ConceptRelationship }o--|| Concept : "concept_id_1"
    ConceptRelationship }o--|| Concept : "concept_id_2"
    ConceptRelationship }o--|| Relationship : "relationship_id"
    ConceptAncestor }o--|| Concept : "ancestor_concept_id"
    ConceptAncestor }o--|| Concept : "descendant_concept_id"
    ConceptSynonym }o--|| Concept : "concept_id"
    ConceptSynonym }o--|| Concept : "language_concept_id"
    SourceToConceptMap }o--|| Concept : "source_concept_id"
    SourceToConceptMap }o--|| Concept : "target_concept_id"
    SourceToConceptMap }o--|| Vocabulary : "target_vocabulary_id"
    DrugStrength }o--|| Concept : "drug_concept_id"
    DrugStrength }o--|| Concept : "ingredient_concept_id"
    DrugStrength }o--|| Concept : "amount_unit_concept_id"
    DrugStrength }o--|| Concept : "numerator_unit_concept_id"
    DrugStrength }o--|| Concept : "denominator_unit_concept_id"
    CareSite }o--|| Concept : "place_of_service_concept_id"
    CareSite }o--|| Location : "location_id"
    Provider }o--|| Concept : "specialty_concept_id"
    Provider }o--|| CareSite : "care_site_id"
    Provider }o--|| Concept : "gender_concept_id"
    Provider }o--|| Concept : "specialty_source_concept_id"
    Provider }o--|| Concept : "gender_source_concept_id"
    Metadata }o--|| Concept : "metadata_concept_id"
    Metadata }o--|| Concept : "metadata_type_concept_id"
    Metadata }o--|| Concept : "value_as_concept_id"
    Person }o--|| Concept : "gender_concept_id"
    Person }o--|| Concept : "race_concept_id"
    Person }o--|| Concept : "ethnicity_concept_id"
    Person }o--|| Location : "location_id"
    Person }o--|| Provider : "provider_id"
    Person }o--|| CareSite : "care_site_id"
    Person }o--|| Concept : "gender_source_concept_id"
    Person }o--|| Concept : "race_source_concept_id"
    Person }o--|| Concept : "ethnicity_source_concept_id"
    Person }o--|| Concept : "person_type_concept_id"
    PersonIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    PersonIdentifier }o--|| Person : "internal_id"
    ObservationPeriod }o--|| Person : "person_id"
    ObservationPeriod }o--|| Concept : "period_type_concept_id"
    ObservationPeriodIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    ObservationPeriodIdentifier }o--|| ObservationPeriod : "internal_id"
    VisitOccurrence }o--|| Person : "person_id"
    VisitOccurrence }o--|| Concept : "visit_concept_id"
    VisitOccurrence }o--|| Concept : "visit_type_concept_id"
    VisitOccurrence }o--|| Provider : "provider_id"
    VisitOccurrence }o--|| CareSite : "care_site_id"
    VisitOccurrence }o--|| Concept : "visit_source_concept_id"
    VisitOccurrence }o--|| Concept : "admitted_from_concept_id"
    VisitOccurrence }o--|| Concept : "discharged_to_concept_id"
    VisitOccurrenceIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    VisitOccurrenceIdentifier }o--|| VisitOccurrence : "internal_id"
    VisitDetail }o--|| Person : "person_id"
    VisitDetail }o--|| Concept : "visit_detail_concept_id"
    VisitDetail }o--|| Concept : "visit_detail_type_concept_id"
    VisitDetail }o--|| Provider : "provider_id"
    VisitDetail }o--|| CareSite : "care_site_id"
    VisitDetail }o--|| Concept : "visit_detail_source_concept_id"
    VisitDetail }o--|| Concept : "admitted_from_concept_id"
    VisitDetail }o--|| Concept : "discharged_to_concept_id"
    VisitDetail }o--|| VisitOccurrence : "visit_occurrence_id"
    VisitDetailIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    VisitDetailIdentifier }o--|| VisitDetail : "internal_id"
    ConditionOccurrence }o--|| Person : "person_id"
    ConditionOccurrence }o--|| Concept : "condition_concept_id"
    ConditionOccurrence }o--|| Concept : "condition_type_concept_id"
    ConditionOccurrence }o--|| Concept : "condition_status_concept_id"
    ConditionOccurrence }o--|| Provider : "provider_id"
    ConditionOccurrence }o--|| VisitOccurrence : "visit_occurrence_id"
    ConditionOccurrence }o--|| VisitDetail : "visit_detail_id"
    ConditionOccurrence }o--|| Concept : "condition_source_concept_id"
    ConditionOccurrenceIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    ConditionOccurrenceIdentifier }o--|| ConditionOccurrence : "internal_id"
    ProcedureOccurrence }o--|| Person : "person_id"
    ProcedureOccurrence }o--|| Concept : "procedure_concept_id"
    ProcedureOccurrence }o--|| Concept : "procedure_type_concept_id"
    ProcedureOccurrence }o--|| Concept : "modifier_concept_id"
    ProcedureOccurrence }o--|| Provider : "provider_id"
    ProcedureOccurrence }o--|| VisitOccurrence : "visit_occurrence_id"
    ProcedureOccurrence }o--|| VisitDetail : "visit_detail_id"
    ProcedureOccurrence }o--|| Concept : "procedure_source_concept_id"
    ProcedureOccurrenceIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    ProcedureOccurrenceIdentifier }o--|| ProcedureOccurrence : "internal_id"
    DrugExposure }o--|| Person : "person_id"
    DrugExposure }o--|| Concept : "drug_concept_id"
    DrugExposure }o--|| Concept : "drug_type_concept_id"
    DrugExposure }o--|| Concept : "route_concept_id"
    DrugExposure }o--|| Provider : "provider_id"
    DrugExposure }o--|| VisitOccurrence : "visit_occurrence_id"
    DrugExposure }o--|| VisitDetail : "visit_detail_id"
    DrugExposure }o--|| Concept : "drug_source_concept_id"
    DrugExposureIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    DrugExposureIdentifier }o--|| DrugExposure : "internal_id"
    DeviceExposure }o--|| Person : "person_id"
    DeviceExposure }o--|| Concept : "device_concept_id"
    DeviceExposure }o--|| Concept : "device_type_concept_id"
    DeviceExposure }o--|| Provider : "provider_id"
    DeviceExposure }o--|| VisitOccurrence : "visit_occurrence_id"
    DeviceExposure }o--|| VisitDetail : "visit_detail_id"
    DeviceExposure }o--|| Concept : "device_source_concept_id"
    DeviceExposure }o--|| Concept : "unit_concept_id"
    DeviceExposure }o--|| Concept : "unit_source_concept_id"
    DeviceExposureIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    DeviceExposureIdentifier }o--|| DeviceExposure : "internal_id"
    Measurement }o--|| Person : "person_id"
    Measurement }o--|| Concept : "measurement_concept_id"
    Measurement }o--|| Concept : "measurement_type_concept_id"
    Measurement }o--|| Concept : "operator_concept_id"
    Measurement }o--|| Concept : "value_as_concept_id"
    Measurement }o--|| Concept : "unit_concept_id"
    Measurement }o--|| Provider : "provider_id"
    Measurement }o--|| VisitOccurrence : "visit_occurrence_id"
    Measurement }o--|| VisitDetail : "visit_detail_id"
    Measurement }o--|| Concept : "measurement_source_concept_id"
    Measurement }o--|| Concept : "unit_source_concept_id"
    Measurement }o--|| Concept : "meas_event_field_concept_id"
    MeasurementIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    MeasurementIdentifier }o--|| Measurement : "internal_id"
    Observation }o--|| Person : "person_id"
    Observation }o--|| Concept : "observation_concept_id"
    Observation }o--|| Concept : "observation_type_concept_id"
    Observation }o--|| Concept : "value_as_concept_id"
    Observation }o--|| Concept : "qualifier_concept_id"
    Observation }o--|| Concept : "unit_concept_id"
    Observation }o--|| Provider : "provider_id"
    Observation }o--|| VisitOccurrence : "visit_occurrence_id"
    Observation }o--|| VisitDetail : "visit_detail_id"
    Observation }o--|| Concept : "observation_source_concept_id"
    Observation }o--|| Concept : "obs_event_field_concept_id"
    ObservationIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    ObservationIdentifier }o--|| Observation : "internal_id"
    Specimen }o--|| Person : "person_id"
    Specimen }o--|| Concept : "specimen_concept_id"
    Specimen }o--|| Concept : "specimen_type_concept_id"
    Specimen }o--|| Concept : "unit_concept_id"
    Specimen }o--|| Concept : "anatomic_site_concept_id"
    Specimen }o--|| Concept : "disease_status_concept_id"
    Specimen }o--|| Concept : "derived_from_specimen_concept_id"
    SpecimenIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    SpecimenIdentifier }o--|| Specimen : "internal_id"
    Note }o--|| Person : "person_id"
    Note }o--|| Concept : "note_type_concept_id"
    Note }o--|| Concept : "note_class_concept_id"
    Note }o--|| Concept : "encoding_concept_id"
    Note }o--|| Concept : "language_concept_id"
    Note }o--|| Provider : "provider_id"
    Note }o--|| VisitOccurrence : "visit_occurrence_id"
    Note }o--|| VisitDetail : "visit_detail_id"
    Note }o--|| Concept : "note_event_field_concept_id"
    NoteIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    NoteIdentifier }o--|| Note : "internal_id"
    NoteNlp }o--|| Concept : "section_concept_id"
    NoteNlp }o--|| Concept : "note_nlp_concept_id"
    NoteNlp }o--|| Concept : "note_nlp_source_concept_id"
    NoteNlpIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    NoteNlpIdentifier }o--|| NoteNlp : "internal_id"
    FactRelationship }o--|| Concept : "domain_concept_id_1"
    FactRelationship }o--|| Concept : "domain_concept_id_2"
    FactRelationship }o--|| Concept : "relationship_concept_id"
    Death }o--|| Person : "person_id"
    Death }o--|| Concept : "death_type_concept_id"
    Death }o--|| Concept : "cause_concept_id"
    Death }o--|| Concept : "cause_source_concept_id"
    DeathIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    DeathIdentifier }o--|| Death : "internal_id"
    MeasurementRelation }o--|| Person : "person_id"
    MeasurementRelation }o--|| Measurement : "from_measurement_id"
    MeasurementRelation }o--|| Measurement : "to_measurement_id"
    MeasurementRelation }o--|| Concept : "measurement_relation_concept_id"
    MeasurementRelationIdentifier }o--|| IdentifierIssuer : "identifier_issuer_id"
    MeasurementRelationIdentifier }o--|| MeasurementRelation : "internal_id"
    PayerPlanPeriod }o--|| Person : "person_id"
    PayerPlanPeriod }o--|| Concept : "payer_concept_id"
    PayerPlanPeriod }o--|| Concept : "payer_source_concept_id"
    PayerPlanPeriod }o--|| Concept : "plan_concept_id"
    PayerPlanPeriod }o--|| Concept : "plan_source_concept_id"
    PayerPlanPeriod }o--|| Concept : "sponsor_concept_id"
    PayerPlanPeriod }o--|| Concept : "sponsor_source_concept_id"
    PayerPlanPeriod }o--|| Concept : "stop_reason_concept_id"
    PayerPlanPeriod }o--|| Concept : "stop_reason_source_concept_id"
    Cost }o--|| Domain : "cost_domain_id"
    Cost }o--|| Concept : "cost_type_concept_id"
    Cost }o--|| Concept : "currency_concept_id"
    Cost }o--|| Concept : "revenue_code_concept_id"
    Cost }o--|| Concept : "drg_concept_id"
    ConditionEra }o--|| Person : "person_id"
    ConditionEra }o--|| Concept : "condition_concept_id"
    DrugEra }o--|| Person : "person_id"
    DrugEra }o--|| Concept : "drug_concept_id"
    DoseEra }o--|| Person : "person_id"
    DoseEra }o--|| Concept : "drug_concept_id"
    DoseEra }o--|| Concept : "unit_concept_id"
    Episode }o--|| Person : "person_id"
    Episode }o--|| Concept : "episode_concept_id"
    Episode }o--|| Concept : "episode_object_concept_id"
    Episode }o--|| Concept : "episode_type_concept_id"
    Episode }o--|| Concept : "episode_source_concept_id"
    EpisodeEvent }o--|| Episode : "episode_id"
    EpisodeEvent }o--|| Concept : "episode_event_field_concept_id"

    %% Entity definitions
    Outage {
        UUID id PK
        string description
        timestamp active_from
        timestamp active_to
        timestamp visible_from
        timestamp visible_to
        bool is_active
        bool is_visible
    }

    Organization {
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationSet {
        UUID id PK
        string name
        string description
    }

    OrganizationSetMember {
        UUID id PK
        UUID organization_set_id FK
        UUID organization_id FK
    }

    DataCollection {
        UUID id PK
        string name
        string description
    }

    DataCollectionSet {
        UUID id PK
        string name
        string description
    }

    DataCollectionSetMember {
        UUID id PK
        UUID data_collection_set_id FK
        UUID data_collection_id FK
    }

    IdentifierIssuer {
        UUID id PK
        string code
        string name
        string description
    }

    OrganizationIdentifierIssuerLink {
        UUID id PK
        UUID organization_id FK
        UUID identifier_issuer_id FK
    }

    Site {
        UUID id PK
        UUID organization_id FK
        string name
    }

    Contact {
        UUID id PK
        UUID site_id FK
        string name
        string email
        string phone
    }

    User {
        UUID id PK
        string key
        string email
        string name
        string description
        bool is_active
        set[string] roles
        UUID organization_id FK
    }

    UserInvitation {
        UUID id PK
        string key
        string email
        string name
        string description
        string token
        timestamp expires_at
        set[string] roles
        UUID invited_by_user_id FK
        UUID organization_id FK
    }

    OrganizationAdminPolicy {
        UUID id PK
        UUID organization_id FK
        UUID user_id FK
        bool is_active
    }

    Vocabulary {
        UUID vocabulary_id PK
        string vocabulary_str_id
        string vocabulary_name
        string vocabulary_reference
        string vocabulary_version
        UUID vocabulary_concept_id
    }

    Domain {
        UUID domain_id PK
        string domain_str_id
        string domain_name
        UUID domain_concept_id
    }

    ConceptClass {
        UUID concept_class_id PK
        string concept_class_str_id
        string concept_class_name
        UUID concept_class_concept_id
    }

    Concept {
        UUID concept_id PK
        int concept_int_id
        string concept_name
        UUID domain_id FK
        UUID vocabulary_id FK
        UUID concept_class_id FK
        string standard_concept
        string concept_code
        date valid_start_date
        date valid_end_date
        string invalid_reason
    }

    Relationship {
        UUID relationship_id PK
        string relationship_name
        string is_hierarchical
        string defines_ancestry
        UUID reverse_relationship_id
        UUID relationship_concept_id FK
    }

    ConceptRelationship {
        UUID concept_relationship_id PK
        UUID concept_id_1 FK
        UUID concept_id_2 FK
        UUID relationship_id FK
        date valid_start_date
        date valid_end_date
        string invalid_reason
    }

    ConceptAncestor {
        UUID concept_ancestor_id PK
        UUID ancestor_concept_id FK
        UUID descendant_concept_id FK
        int min_levels_of_separation
        int max_levels_of_separation
    }

    ConceptSynonym {
        UUID concept_synonym_id PK
        UUID concept_id FK
        string concept_synonym_name
        UUID language_concept_id FK
    }

    SourceToConceptMap {
        UUID source_to_concept_map_id PK
        string source_code
        UUID source_concept_id FK
        UUID source_vocabulary_id
        string source_code_description
        UUID target_concept_id FK
        UUID target_vocabulary_id FK
        date valid_start_date
        date valid_end_date
        string invalid_reason
    }

    DrugStrength {
        UUID drug_strength_id PK
        UUID drug_concept_id FK
        UUID ingredient_concept_id FK
        float amount_value
        UUID amount_unit_concept_id FK
        float numerator_value
        UUID numerator_unit_concept_id FK
        float denominator_value
        UUID denominator_unit_concept_id FK
        int box_size
        date valid_start_date
        date valid_end_date
        string invalid_reason
    }

    Location {
        UUID location_id PK
        string address_1
        string address_2
        string city
        string state
        string zip
        string county
        string location_source_value
        UUID country_concept_id
        string country_source_value
        float latitude
        float longitude
    }

    CareSite {
        UUID care_site_id PK
        string care_site_name
        UUID place_of_service_concept_id FK
        UUID location_id FK
        string care_site_source_value
        string place_of_service_source_value
        UUID site_id
    }

    Provider {
        UUID provider_id PK
        string provider_name
        string npi
        string dea
        UUID specialty_concept_id FK
        UUID care_site_id FK
        int year_of_birth
        UUID gender_concept_id FK
        string provider_source_value
        string specialty_source_value
        UUID specialty_source_concept_id FK
        string gender_source_value
        UUID gender_source_concept_id FK
    }

    CdmSource {
        string cdm_source_name
        string cdm_source_abbreviation
        string cdm_holder
        string source_description
        string source_documentation_reference
        string cdm_etl_reference
        date source_release_date
        date cdm_release_date
        string cdm_version
        UUID cdm_version_concept_id
        string vocabulary_version
        UUID cdm_source_id PK
    }

    Metadata {
        UUID metadata_id PK
        UUID metadata_concept_id FK
        UUID metadata_type_concept_id FK
        string name
        string value_as_string
        UUID value_as_concept_id FK
        float value_as_number
        date metadata_date
        timestamp metadata_datetime
    }

    Person {
        UUID provenance_id
        string source_traceback
        UUID person_id PK
        UUID gender_concept_id FK
        int year_of_birth
        int month_of_birth
        int day_of_birth
        timestamp birth_datetime
        UUID race_concept_id FK
        UUID ethnicity_concept_id FK
        UUID location_id FK
        UUID provider_id FK
        UUID care_site_id FK
        string person_source_value
        string gender_source_value
        UUID gender_source_concept_id FK
        string race_source_value
        UUID race_source_concept_id FK
        string ethnicity_source_value
        UUID ethnicity_source_concept_id FK
        UUID person_type_concept_id FK
        UUID provided_by_organization_id
    }

    PersonIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    ObservationPeriod {
        UUID provenance_id
        string source_traceback
        UUID observation_period_id PK
        UUID person_id FK
        date observation_period_start_date
        date observation_period_end_date
        UUID period_type_concept_id FK
        string observation_period_start_iso_interval
        string observation_period_end_iso_interval
        UUID provided_by_organization_id
    }

    ObservationPeriodIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    VisitOccurrence {
        UUID provenance_id
        string source_traceback
        UUID visit_occurrence_id PK
        UUID person_id FK
        UUID visit_concept_id FK
        date visit_start_date
        timestamp visit_start_datetime
        date visit_end_date
        timestamp visit_end_datetime
        UUID visit_type_concept_id FK
        UUID provider_id FK
        UUID care_site_id FK
        string visit_source_value
        UUID visit_source_concept_id FK
        UUID admitted_from_concept_id FK
        string admitted_from_source_value
        UUID discharged_to_concept_id FK
        string discharged_to_source_value
        UUID preceding_visit_occurrence_id
        UUID provided_by_organization_id
    }

    VisitOccurrenceIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    VisitDetail {
        UUID provenance_id
        string source_traceback
        UUID visit_detail_id PK
        UUID person_id FK
        UUID visit_detail_concept_id FK
        date visit_detail_start_date
        timestamp visit_detail_start_datetime
        date visit_detail_end_date
        timestamp visit_detail_end_datetime
        UUID visit_detail_type_concept_id FK
        UUID provider_id FK
        UUID care_site_id FK
        string visit_detail_source_value
        UUID visit_detail_source_concept_id FK
        UUID admitted_from_concept_id FK
        string admitted_from_source_value
        string discharged_to_source_value
        UUID discharged_to_concept_id FK
        UUID preceding_visit_detail_id
        UUID parent_visit_detail_id
        UUID visit_occurrence_id FK
        UUID provided_by_organization_id
    }

    VisitDetailIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    ConditionOccurrence {
        UUID provenance_id
        string source_traceback
        UUID condition_occurrence_id PK
        UUID person_id FK
        UUID condition_concept_id FK
        date condition_start_date
        timestamp condition_start_datetime
        date condition_end_date
        timestamp condition_end_datetime
        UUID condition_type_concept_id FK
        UUID condition_status_concept_id FK
        string stop_reason
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string condition_source_value
        UUID condition_source_concept_id FK
        string condition_status_source_value
        string condition_start_iso_interval
        string condition_end_iso_interval
        UUID provided_by_organization_id
    }

    ConditionOccurrenceIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    ProcedureOccurrence {
        UUID provenance_id
        string source_traceback
        UUID procedure_occurrence_id PK
        UUID person_id FK
        UUID procedure_concept_id FK
        date procedure_date
        timestamp procedure_datetime
        date procedure_end_date
        timestamp procedure_end_datetime
        UUID procedure_type_concept_id FK
        UUID modifier_concept_id FK
        int quantity
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string procedure_source_value
        UUID procedure_source_concept_id FK
        string modifier_source_value
        string procedure_iso_interval
        UUID provided_by_organization_id
    }

    ProcedureOccurrenceIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    DrugExposure {
        UUID provenance_id
        string source_traceback
        UUID drug_exposure_id PK
        UUID person_id FK
        UUID drug_concept_id FK
        date drug_exposure_start_date
        timestamp drug_exposure_start_datetime
        date drug_exposure_end_date
        timestamp drug_exposure_end_datetime
        date verbatim_end_date
        UUID drug_type_concept_id FK
        string stop_reason
        int refills
        float quantity
        int days_supply
        string sig
        UUID route_concept_id FK
        string lot_number
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string drug_source_value
        UUID drug_source_concept_id FK
        string route_source_value
        string dose_unit_source_value
        string drug_exposure_start_iso_interval
        string drug_exposure_end_iso_interval
        UUID provided_by_organization_id
    }

    DrugExposureIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    DeviceExposure {
        UUID provenance_id
        string source_traceback
        UUID device_exposure_id PK
        UUID person_id FK
        UUID device_concept_id FK
        date device_exposure_start_date
        timestamp device_exposure_start_datetime
        date device_exposure_end_date
        timestamp device_exposure_end_datetime
        UUID device_type_concept_id FK
        UUID unique_device_id
        UUID production_id
        int quantity
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string device_source_value
        UUID device_source_concept_id FK
        UUID unit_concept_id FK
        string unit_source_value
        UUID unit_source_concept_id FK
        string device_exposure_start_iso_interval
        string device_exposure_end_iso_interval
        UUID provided_by_organization_id
    }

    DeviceExposureIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Measurement {
        UUID provenance_id
        string source_traceback
        UUID measurement_id PK
        UUID person_id FK
        UUID measurement_concept_id FK
        date measurement_date
        timestamp measurement_datetime
        string measurement_time
        UUID measurement_type_concept_id FK
        UUID operator_concept_id FK
        float value_as_number
        UUID value_as_concept_id FK
        UUID unit_concept_id FK
        float range_low
        float range_high
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string measurement_source_value
        UUID measurement_source_concept_id FK
        string unit_source_value
        UUID unit_source_concept_id FK
        string value_source_value
        UUID measurement_event_id
        UUID meas_event_field_concept_id FK
        string measurement_iso_interval
        UUID derived_from_specimen_id
        UUID provided_by_organization_id
    }

    MeasurementIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Observation {
        UUID provenance_id
        string source_traceback
        UUID observation_id PK
        UUID person_id FK
        UUID observation_concept_id FK
        date observation_date
        timestamp observation_datetime
        UUID observation_type_concept_id FK
        float value_as_number
        string value_as_string
        UUID value_as_concept_id FK
        UUID qualifier_concept_id FK
        UUID unit_concept_id FK
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string observation_source_value
        UUID observation_source_concept_id FK
        string unit_source_value
        string qualifier_source_value
        string value_source_value
        UUID observation_event_id
        UUID obs_event_field_concept_id FK
        string observation_iso_interval
        string value_as_iso_interval
        UUID provided_by_organization_id
    }

    ObservationIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Specimen {
        UUID provenance_id
        string source_traceback
        UUID specimen_id PK
        UUID person_id FK
        UUID specimen_concept_id FK
        UUID specimen_type_concept_id FK
        date specimen_date
        timestamp specimen_datetime
        float quantity
        UUID unit_concept_id FK
        UUID anatomic_site_concept_id FK
        UUID disease_status_concept_id FK
        string specimen_source_id
        string specimen_source_value
        string unit_source_value
        string anatomic_site_source_value
        string disease_status_source_value
        string specimen_iso_interval
        UUID derived_from_specimen_id
        UUID derived_from_specimen_concept_id FK
        UUID provided_by_organization_id
    }

    SpecimenIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    Note {
        UUID provenance_id
        string source_traceback
        UUID note_id PK
        UUID person_id FK
        date note_date
        timestamp note_datetime
        UUID note_type_concept_id FK
        UUID note_class_concept_id FK
        string note_title
        string note_text
        UUID encoding_concept_id FK
        UUID language_concept_id FK
        UUID provider_id FK
        UUID visit_occurrence_id FK
        UUID visit_detail_id FK
        string note_source_value
        UUID note_event_id
        UUID note_event_field_concept_id FK
        UUID provided_by_organization_id
    }

    NoteIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    NoteNlp {
        UUID provenance_id
        string source_traceback
        UUID note_nlp_id PK
        UUID note_id
        UUID section_concept_id FK
        string snippet
        string lexical_variant
        UUID note_nlp_concept_id FK
        UUID note_nlp_source_concept_id FK
        string nlp_system
        date nlp_date
        timestamp nlp_datetime
        string term_exists
        string term_temporal
        string term_modifiers
        string offset
    }

    NoteNlpIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    FactRelationship {
        UUID domain_concept_id_1 FK
        int fact_id_1
        UUID domain_concept_id_2 FK
        int fact_id_2
        UUID relationship_concept_id FK
        UUID fact_relationship_id PK
    }

    Death {
        UUID provenance_id
        string source_traceback
        UUID death_id PK
        UUID person_id FK
        date death_date
        timestamp death_datetime
        UUID death_type_concept_id FK
        UUID cause_concept_id FK
        string cause_source_value
        UUID cause_source_concept_id FK
        UUID provided_by_organization_id
    }

    DeathIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    MeasurementRelation {
        UUID measurement_relation_id PK
        UUID person_id FK
        UUID from_measurement_id FK
        UUID to_measurement_id FK
        UUID measurement_relation_concept_id FK
    }

    MeasurementRelationIdentifier {
        UUID id PK
        UUID identifier_issuer_id FK
        string external_id
        UUID internal_id FK
    }

    PayerPlanPeriod {
        UUID provenance_id
        string source_traceback
        UUID payer_plan_period_id PK
        UUID person_id FK
        date payer_plan_period_start_date
        date payer_plan_period_end_date
        UUID payer_concept_id FK
        string payer_source_value
        UUID payer_source_concept_id FK
        UUID plan_concept_id FK
        string plan_source_value
        UUID plan_source_concept_id FK
        UUID sponsor_concept_id FK
        string sponsor_source_value
        UUID sponsor_source_concept_id FK
        string family_source_value
        UUID stop_reason_concept_id FK
        string stop_reason_source_value
        UUID stop_reason_source_concept_id FK
        UUID provided_by_organization_id
    }

    Cost {
        UUID provenance_id
        string source_traceback
        UUID cost_id PK
        UUID cost_event_id
        UUID cost_domain_id FK
        UUID cost_type_concept_id FK
        UUID currency_concept_id FK
        float total_charge
        float total_cost
        float total_paid
        float paid_by_payer
        float paid_by_patient
        float paid_patient_copay
        float paid_patient_coinsurance
        float paid_patient_deductible
        float paid_by_primary
        float paid_ingredient_cost
        float paid_dispensing_fee
        UUID payer_plan_period_id
        float amount_allowed
        UUID revenue_code_concept_id FK
        string revenue_code_source_value
        UUID drg_concept_id FK
        string drg_source_value
        UUID provided_by_organization_id
    }

    ConditionEra {
        UUID provenance_id
        string source_traceback
        UUID condition_era_id PK
        UUID person_id FK
        UUID condition_concept_id FK
        date condition_era_start_date
        date condition_era_end_date
        int condition_occurrence_count
    }

    DrugEra {
        UUID provenance_id
        string source_traceback
        UUID drug_era_id PK
        UUID person_id FK
        UUID drug_concept_id FK
        date drug_era_start_date
        date drug_era_end_date
        int drug_exposure_count
        int gap_days
        string drug_era_start_iso_interval
        string drug_era_end_iso_interval
    }

    DoseEra {
        UUID provenance_id
        string source_traceback
        UUID dose_era_id PK
        UUID person_id FK
        UUID drug_concept_id FK
        UUID unit_concept_id FK
        float dose_value
        date dose_era_start_date
        date dose_era_end_date
    }

    CohortDefinition {
        UUID cohort_definition_id PK
        string cohort_definition_name
        string cohort_definition_description
        UUID definition_type_concept_id
        string cohort_definition_syntax
        UUID subject_concept_id
        date cohort_initiation_date
    }

    Cohort {
        UUID cohort_definition_id
        UUID subject_id
        date cohort_start_date
        date cohort_end_date
        UUID cohort_id PK
    }

    Episode {
        UUID provenance_id
        string source_traceback
        UUID episode_id PK
        UUID person_id FK
        UUID episode_concept_id FK
        date episode_start_date
        timestamp episode_start_datetime
        date episode_end_date
        timestamp episode_end_datetime
        UUID episode_parent_id
        int episode_number
        UUID episode_object_concept_id FK
        UUID episode_type_concept_id FK
        string episode_source_value
        UUID episode_source_concept_id FK
    }

    EpisodeEvent {
        UUID provenance_id
        string source_traceback
        UUID episode_id FK
        UUID event_id
        UUID episode_event_field_concept_id FK
        UUID episode_event_id PK
    }

```
