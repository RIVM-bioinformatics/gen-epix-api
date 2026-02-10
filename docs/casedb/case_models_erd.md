# CaseDB SQLAlchemy Models - Entity Relationship Diagrams

This document contains simplified ERDs showing different functional areas of the CaseDB SQLAlchemy models for epidemiological case management.

## 1. Core Case and Subject Management

```mermaid
erDiagram
    Subject ||--o{ Case : "has cases"
    Subject ||--o{ SubjectIdentifier : "has identifiers"
    
    Case }o--|| CaseType : "belongs to type"
    Case ||--o{ CaseDataCollectionLink : "linked to collections"
    
    Case ||--o{ CaseSetMember : "member of case sets"
    CaseSetMember }o--|| CaseSet : "belongs to set"
    
    CaseSet }o--|| CaseType : "contains cases of type"
    CaseSet }o--|| CaseSetCategory : "categorized by"
    CaseSet }o--|| CaseSetStatus : "has status"
    CaseSet ||--o{ CaseSetDataCollectionLink : "linked to collections"
```

## 2. Case Type Definition and Structure

```mermaid
erDiagram
    CaseType }o--|| Disease : "associated with disease"
    CaseType }o--|| EtiologicalAgent : "caused by agent"
    
    CaseType ||--o{ CaseTypeDim : "has dimensions"
    CaseTypeDim }o--|| Dim : "dimension definition"
    
    Dim ||--o{ Col : "has columns"
    Col }o--|| ConceptSet : "references concept set"
    Col }o--|| RegionSet : "references region set"
    Col }o--|| GeneticDistanceProtocol : "uses genetic distance"
    
    CaseType ||--o{ CaseTypeSet : "member of type sets"
    CaseTypeSet }o--|| CaseTypeSetCategory : "categorized by"
    
    CaseType ||--o{ CaseTypeColSet : "has column sets"
    CaseTypeColSet ||--o{ CaseTypeColSetMember : "contains columns"
    CaseTypeColSetMember }o--|| Col : "references column"
```

## 3. Disease and Etiology

```mermaid
erDiagram
    Disease ||--o{ Etiology : "has etiologies"
    EtiologicalAgent ||--o{ Etiology : "causes diseases"
    
    Disease ||--o{ CaseType : "associated with case types"
    EtiologicalAgent ||--o{ CaseType : "associated with case types"
```

## 4. Ontology and Concepts

```mermaid
erDiagram
    ConceptSet ||--o{ Concept : "contains concepts"
    
    Concept ||--o{ ConceptRelation : "source concept"
    Concept ||--o{ ConceptRelation : "target concept"
    
    ConceptSet ||--o{ Col : "used in columns"
```

## 5. Geographic Regions

```mermaid
erDiagram
    RegionSet ||--o{ Region : "contains regions"
    RegionSet ||--o{ RegionSetShape : "has shapes"
    
    Region ||--o{ RegionRelation : "source region"
    Region ||--o{ RegionRelation : "target region"
    
    RegionSet ||--o{ Col : "used in columns"
```

## 6. Genetic Analysis and Phylogenetics

```mermaid
erDiagram
    GeneticDistanceProtocol ||--o{ Col : "used in columns"
    
    TreeAlgorithmClass ||--o{ TreeAlgorithm : "has algorithms"
    TreeAlgorithm
```

## 7. Access Control Policies (ABAC)

```mermaid
erDiagram
    %% Top Level - Security Principals
    Organization ||--o{ OrganizationAccessCasePolicy : "has access policies"
    Organization ||--o{ OrganizationShareCasePolicy : "has share policies"
    
    User ||--o{ UserAccessCasePolicy : "has access policies"
    User ||--o{ UserShareCasePolicy : "has share policies"
    
    %% Second Level - Protected Resources
    DataCollection ||--o{ OrganizationAccessCasePolicy : "target collection"
    DataCollection ||--o{ UserAccessCasePolicy : "target collection"
    DataCollection }o--|| OrganizationShareCasePolicy : "source collection"
    DataCollection }o--|| UserShareCasePolicy : "source collection"
    
    CaseTypeSet }o--|| OrganizationAccessCasePolicy : "applies to case types"
    CaseTypeSet }o--|| OrganizationShareCasePolicy : "applies to case types"
    CaseTypeSet }o--|| UserAccessCasePolicy : "applies to case types"
    CaseTypeSet }o--|| UserShareCasePolicy : "applies to case types"
    
    CaseTypeColSet }o--|| OrganizationAccessCasePolicy : "read column set"
    CaseTypeColSet }o--|| OrganizationAccessCasePolicy : "write column set"
    CaseTypeColSet }o--|| UserAccessCasePolicy : "read column set"
    CaseTypeColSet }o--|| UserAccessCasePolicy : "write column set"
```

## Key Model Groups

### 📋 **Core Epidemiological Data**
- **Case** - Individual epidemiological cases with flexible content structure
- **Subject** - People or entities associated with cases
- **CaseType** - Templates defining case structure and validation rules

### 👥 **Case Management**
- **CaseSet** - Collections of related cases for analysis
- **CaseSetMember** - Case membership with classification status
- **CaseSetCategory/Status** - Case set organization and workflow

### 🏗️ **Case Structure Definition** 
- **Dim** - Dimensions for organizing case data fields
- **Col** - Columns defining specific data fields in cases
- **CaseTypeDim/CaseTypeColSet** - Linking case types to their structure

### 🦠 **Disease and Causation**
- **Disease** - Disease definitions with ICD codes
- **EtiologicalAgent** - Causative agents (pathogens, toxins, etc.)
- **Etiology** - Disease-agent relationships

### 📚 **Knowledge Management**
- **ConceptSet** - Controlled vocabularies and value sets
- **Concept** - Individual concepts with codes and descriptions
- **ConceptRelation** - Hierarchical and associative relationships

### 🗺️ **Geographic Data**
- **RegionSet** - Geographic hierarchies (countries, states, etc.)
- **Region** - Individual geographic areas with coordinates
- **RegionRelation** - Geographic containment relationships
- **RegionSetShape** - GeoJSON shape data for mapping

### 🧬 **Genetic Analysis**
- **GeneticDistanceProtocol** - Methods for calculating genetic distances
- **TreeAlgorithm/TreeAlgorithmClass** - Phylogenetic tree algorithms

### 🔐 **Security and Access Control (ABAC)**
- **OrganizationAccessCasePolicy** - Organization-level case access permissions
- **OrganizationShareCasePolicy** - Organization-level case sharing permissions
- **UserAccessCasePolicy** - Individual user case access permissions  
- **UserShareCasePolicy** - Individual user case sharing permissions

#### ABAC Policy Features:
- **Granular Permissions**: add_case, remove_case, add_case_set, remove_case_set
- **Field-Level Access**: read_case_type_col_set_id, write_case_type_col_set_id
- **Data Collection Scoping**: Policies apply to specific data collections
- **Case Type Filtering**: Policies target specific case type sets
- **Privacy Controls**: is_private flag for sensitive data
- **Data Sharing**: Cross-collection data sharing with from_data_collection_id

### 🔗 **Integration Points**
- **SubjectIdentifier** - External system identifiers for subjects
- **CaseDataCollectionLink** - Links cases to data collection events
- **CaseSetDataCollectionLink** - Links case sets to data collections

The CaseDB models support flexible, structured epidemiological case management with rich metadata, geographic integration, and genetic analysis capabilities for comprehensive outbreak investigation and surveillance.