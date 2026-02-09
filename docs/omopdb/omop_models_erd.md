# OMOPDB SQLAlchemy Models - Entity Relationship Diagrams

This document contains simplified ERDs showing different functional areas of the OMOPDB SQLAlchemy models based on the OMOP Common Data Model.

## 1. Person and Demographics

```mermaid
erDiagram
    Person ||--o{ ObservationPeriod : "has observation periods"
    Person }o--|| Location : "lives at"
    Person }o--|| Provider : "primary care provider"
    Person }o--|| CareSite : "primary care site"
    
    Person ||--o{ LocationHistory : "location history"
    LocationHistory }o--|| Location : "historical location"
    
    Person ||--o{ PayerPlanPeriod : "insurance periods"
```

## 2. Healthcare Visits and Care

```mermaid
erDiagram
    Person ||--o{ VisitOccurrence : "has visits"
    VisitOccurrence ||--o{ VisitDetail : "has visit details"
    
    VisitOccurrence }o--|| Provider : "attending provider"
    VisitOccurrence }o--|| CareSite : "care site"
    VisitDetail }o--|| Provider : "detail provider"
    VisitDetail }o--|| CareSite : "detail care site"
    
    CareSite }o--|| Location : "located at"
    Provider }o--|| CareSite : "works at"
    Provider }o--|| Location : "located at"
```

## 3. Clinical Events and Conditions

```mermaid
erDiagram
    Person ||--o{ ConditionOccurrence : "has conditions"
    Person ||--o{ ProcedureOccurrence : "has procedures"
    Person ||--o{ DeviceExposure : "exposed to devices"
    Person ||--o{ Specimen : "specimens collected"
    
    VisitOccurrence ||--o{ ConditionOccurrence : "conditions during visit"
    VisitOccurrence ||--o{ ProcedureOccurrence : "procedures during visit"
    VisitOccurrence ||--o{ DeviceExposure : "devices during visit"
    VisitOccurrence ||--o{ Specimen : "specimens during visit"
    
    ConditionOccurrence }o--|| Provider : "diagnosed by"
    ProcedureOccurrence }o--|| Provider : "performed by"
```

## 4. Drug Exposures and Medications

```mermaid
erDiagram
    Person ||--o{ DrugExposure : "drug exposures"
    
    VisitOccurrence ||--o{ DrugExposure : "drugs during visit"
    DrugExposure }o--|| Provider : "prescribed by"
    
    DrugStrength ||--o{ DrugExposure : "drug strength reference"
```

## 5. Measurements and Observations

```mermaid
erDiagram
    Person ||--o{ Measurement : "has measurements"
    Person ||--o{ Observation : "has observations"
    Person ||--o{ Note : "clinical notes"
    
    VisitOccurrence ||--o{ Measurement : "measurements during visit"
    VisitOccurrence ||--o{ Observation : "observations during visit"
    VisitOccurrence ||--o{ Note : "notes during visit"
    
    Measurement }o--|| Provider : "measured by"
    Observation }o--|| Provider : "observed by"
    Note }o--|| Provider : "authored by"
    
    Measurement ||--o{ MeasurementRelation : "related measurements"
    Note ||--o{ NoteNlp : "NLP analysis"
```

## 6. Eras and Cohorts

```mermaid
erDiagram
    Person ||--o{ ConditionEra : "condition eras"
    Person ||--o{ DrugEra : "drug eras" 
    Person ||--o{ DoseEra : "dose eras"
    
    Person ||--o{ Cohort : "cohort membership"
    Cohort }o--|| CohortDefinition : "defined by"
```

## 7. OMOP Vocabulary and Concepts

```mermaid
erDiagram
    Vocabulary ||--o{ Concept : "contains concepts"
    Domain ||--o{ Concept : "concept domain"
    ConceptClass ||--o{ Concept : "concept class"
    
    Concept ||--o{ ConceptSynonym : "has synonyms"
    Concept ||--o{ ConceptRelationship : "source concept"
    Concept ||--o{ ConceptRelationship : "target concept"
    ConceptRelationship }o--|| Relationship : "relationship type"
    
    Concept ||--o{ ConceptAncestor : "descendant concepts"
    Concept ||--o{ ConceptAncestor : "ancestor concepts"
    
    Concept ||--o{ SourceToConceptMap : "mapped to"
```

## 8. Cost and Survey Data

```mermaid
erDiagram
    Person ||--o{ Cost : "healthcare costs"
    Person ||--o{ SurveyConduct : "survey participation"
    
    VisitOccurrence ||--o{ Cost : "visit costs"
    DrugExposure ||--o{ Cost : "drug costs"
    ProcedureOccurrence ||--o{ Cost : "procedure costs"
```

## 9. System Metadata and Relationships

```mermaid
erDiagram
    CdmSource
    Metadata
    FactRelationship
```

## Key Model Groups

### 👥 **Core Person Data**
- **Person** - Demographics and basic information
- **ObservationPeriod** - Time periods when person was observable
- **LocationHistory** - Residential history

### 🏥 **Healthcare Delivery**
- **VisitOccurrence** - Healthcare visits and encounters
- **VisitDetail** - Detailed visit components
- **Provider** - Healthcare providers
- **CareSite** - Healthcare facilities

### 🩺 **Clinical Events**
- **ConditionOccurrence** - Diagnoses and conditions
- **ProcedureOccurrence** - Medical procedures
- **DeviceExposure** - Medical device usage
- **Specimen** - Laboratory specimens

### 💊 **Medications**
- **DrugExposure** - Drug prescriptions and administrations
- **DrugStrength** - Drug formulation information

### 📊 **Measurements & Observations**
- **Measurement** - Laboratory values, vital signs
- **Observation** - Clinical observations and assessments
- **Note** - Clinical notes and documentation

### 📈 **Longitudinal Analysis**
- **ConditionEra** - Continuous condition periods
- **DrugEra** - Continuous drug exposure periods
- **DoseEra** - Continuous dose periods

### 👨‍👩‍👧‍👦 **Cohorts and Studies**
- **Cohort** - Patient cohort membership
- **CohortDefinition** - Cohort inclusion criteria

### 📚 **Vocabulary System**
- **Vocabulary** - Standard vocabularies (SNOMED, ICD, etc.)
- **Concept** - Standardized medical concepts
- **ConceptRelationship** - Relationships between concepts
- **Domain** - Concept domains (Condition, Drug, etc.)

All clinical event entities include standardized concept references for interoperability and use the OMOP Common Data Model structure for healthcare data analysis.