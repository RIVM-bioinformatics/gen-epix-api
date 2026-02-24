# SeqDB SQLAlchemy Models - Simplified Entity Relationship Diagrams

This document contains multiple simplified ERDs showing different functional areas of the SeqDB SQLAlchemy models, with core entities duplicated across diagrams for clarity.

## 1. Core Sample and Sequence Workflow

```mermaid
erDiagram
    Sample ||--o{ ReadSet : "has read sets"
    Sample ||--o{ Seq : "has sequences"
    Sample ||--o{ SampleIdentifier : "has identifiers"
    Sample ||--o{ SampleDataCollectionLink : "linked to collections"
    
    ReadSet ||--o{ Seq : "used in assembly"
    ReadSet }o--|| SequencingProtocol : "sequenced with"
    Seq }o--|| AssemblyProtocol : "assembled with"
    Seq ||--o{ SeqAlignment : "aligned"
    SeqAlignment }o--|| AlignmentProtocol : "alignment method"
```

## 2. Genomic Profile Analysis

```mermaid
erDiagram
    Sample ||--o{ AlleleProfile : "has allele profiles"
    Sample ||--o{ LocusProfile : "has locus profiles"
    Sample ||--o{ SnpProfile : "has SNP profiles"
    Sample ||--o{ KmerProfile : "has kmer profiles"
    Sample ||--o{ MlvaProfile : "has MLVA profiles"
    
    Seq ||--o{ AlleleProfile : "analyzed for alleles"
    Seq ||--o{ LocusProfile : "analyzed for loci"
    Seq ||--o{ SnpProfile : "analyzed for SNPs"
    Seq ||--o{ KmerProfile : "analyzed for kmers"
    Seq ||--o{ MlvaProfile : "analyzed for MLVA"
    
    LocusSet ||--o{ AlleleProfile : "defines allele profile"
    LocusSet ||--o{ LocusProfile : "defines locus profile"
    
    RefSeq ||--o{ SnpProfile : "reference for SNP profile"
    
    AlleleProfile }o--|| LocusDetectionProtocol : "detection method"
    LocusProfile }o--|| LocusDetectionProtocol : "detection method"
    SnpProfile }o--|| SnpDetectionProtocol : "detection method"
    KmerProfile }o--|| KmerDetectionProtocol : "detection method"
    MlvaProfile }o--|| MlvaDetectionProtocol : "detection method"
```

## 3. Reference Data and Genetic Elements

```mermaid
erDiagram
    Locus ||--o{ Allele : "has alleles"
    Locus ||--o{ RefAllele : "has reference alleles"
    
    RefSeq ||--o{ RefSnp : "contains SNPs"
    RefSeq }o--|| Taxon : "belongs to taxon"
    
    RefSnpSet ||--o{ RefSnpSetMember : "has members"
    RefSnp ||--o{ RefSnpSetMember : "member of sets"
    
    RefAllele ||--o{ AlleleAlignment : "reference for alignment"
    Allele ||--o{ AlleleAlignment : "aligned against reference"
    AlleleAlignment }o--|| AlignmentProtocol : "alignment method"
    
    LocusSet ||--o{ LocusProfile : "defines profile"
    LocusCodeMap
```

## 4. Classification and Taxonomy

```mermaid
erDiagram
    Sample ||--o{ SeqClassification : "has classifications"
    Sample ||--o{ SeqTaxonomy : "has taxonomy"
    
    Seq ||--o{ SeqClassification : "classified"
    Seq ||--o{ SeqTaxonomy : "taxonomically analyzed"
    
    SeqClassification }o--|| SeqClassificationProtocol : "classification method"
    SeqClassification }o--|| SeqCategory : "primary category"
    
    SeqTaxonomy }o--|| TaxonomyProtocol : "taxonomy method"
    SeqTaxonomy }o--|| Taxon : "primary taxon"
    
    SeqCategory }o--|| SeqCategorySet : "belongs to set"
    
    TaxonSet ||--o{ TaxonSetMember : "has members"
    Taxon ||--o{ TaxonSetMember : "member of sets"
```

## 5. Distance Analysis and Phylogenetics

```mermaid
erDiagram
    Sample ||--o{ SeqDistance : "has distance calculations"
    Seq ||--o{ SeqDistance : "distance calculated"
    
    SeqDistance }o--|| SeqDistanceProtocol : "distance calculation method"
    SeqDistance }o--|| AlleleProfile : "based on allele profile"
    SeqDistance }o--|| SnpProfile : "based on SNP profile"
    SeqDistance }o--|| KmerProfile : "based on kmer profile"
    
    SeqDistanceProtocol }o--|| LocusSet : "uses locus set"
    SeqDistanceProtocol }o--|| RefSeq : "uses reference"
    
    TreeAlgorithmClass ||--o{ TreeAlgorithm : "has algorithms"
```

## 6. Laboratory Measurements

```mermaid
erDiagram
    Sample ||--o{ AstMeasurement : "has AST measurements"
    Sample ||--o{ AstPrediction : "has AST predictions"
    Sample ||--o{ PcrMeasurement : "has PCR measurements"
    
    Seq ||--o{ AstPrediction : "AST predicted"
    
    AstMeasurement }o--|| AstProtocol : "measurement protocol"
    AstPrediction }o--|| AstProtocol : "prediction protocol"
    PcrMeasurement }o--|| PcrProtocol : "PCR protocol"
```

## Entity Groups Overview

### 🧬 Core Data Entities
- **Sample** - Biological samples
- **Seq** - Assembled genomic sequences  
- **ReadSet** - Raw sequencing data
- **Allele** - Genetic variants
- **Locus** - Gene locations

### 📊 Analysis Profiles
- **AlleleProfile** - MLST results
- **SnpProfile** - SNP analysis
- **LocusProfile** - Gene detection
- **KmerProfile** - K-mer analysis
- **MlvaProfile** - VNTR analysis

### 🔬 Analysis Results
- **SeqClassification** - Sequence classification
- **SeqTaxonomy** - Taxonomic assignment
- **SeqDistance** - Phylogenetic distances
- **SeqAlignment** - Sequence alignments

### 🧪 Laboratory Results
- **AstMeasurement/AstPrediction** - Antimicrobial susceptibility
- **PcrMeasurement** - PCR results

### 📋 Reference Data
- **RefSeq** - Reference genomes
- **RefAllele** - Reference alleles
- **RefSnp** - Reference SNPs
- **Taxon** - Taxonomic data
- **LocusSet** - Locus collections

### ⚙️ Analysis Protocols
- **SequencingProtocol** - Sequencing methods
- **AssemblyProtocol** - Assembly methods
- **AlignmentProtocol** - Alignment methods
- **LocusDetectionProtocol** - Locus detection
- **SnpDetectionProtocol** - SNP detection
- **KmerDetectionProtocol** - K-mer detection
- **MlvaDetectionProtocol** - MLVA detection
- **SeqClassificationProtocol** - Classification methods
- **SeqDistanceProtocol** - Distance calculation
- **AstProtocol** - AST methods
- **PcrProtocol** - PCR methods
- **TaxonomyProtocol** - Taxonomy methods

### 🔗 Supporting Entities
- **SampleIdentifier** - Sample IDs from external systems
- **SampleDataCollectionLink** - Sample collection associations
- **AlleleAlignment** - Allele alignment results
- **RefSnpSet/RefSnpSetMember** - SNP collections
- **SeqCategory/SeqCategorySet** - Classification categories
- **TaxonSet/TaxonSetMember** - Taxonomic collections
- **TreeAlgorithm/TreeAlgorithmClass** - Phylogenetic methods
- **LocusCodeMap** - Locus code mappings

This simplified view shows the high-level data flow: **Sample** → **ReadSet** → **Seq** → **Analysis Results** (Profiles, Classifications, etc.), with **Reference Data** and **Protocols** supporting the analysis pipeline.