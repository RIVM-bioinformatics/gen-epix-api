# SeqDB Base Mixins - Entity Relationship Diagram

This ERD shows the SQLAlchemy mixin classes defined in `gen_epix/seqdb/repositories/sa_model/base.py`.

```mermaid
erDiagram
    %% Mixin Classes (shown as entities for clarity)
    CodeMixin {
        string code "Standard code field"
    }
    
    QualityMixin {
        float qc_score "Quality control score"
        enum qc_result "Quality control result"
    }
    
    SeqMixin {
        string seq "Sequence data"
        enum seq_format "Sequence format"
        int length "Sequence length"
    }
    
    ProtocolMixin {
        string code "Protocol code"
        string name "Protocol name"
        string version "Protocol version"
        string description "Protocol description"
        dict props "Protocol properties"
    }
    
    AlignmentMixin {
        string aln "Alignment data"
        string aln_format "Alignment format"
        UUID aln_hash "Alignment hash"
    }
```

## Mixin Usage Overview

These mixins are used by various SeqDB models to provide common field sets:

### 🏷️ **CodeMixin**
Used by models that need a standard code field:
- Sample, ReadSet, Seq
- RefSeq, LocusSet
- SeqCategory, Taxon

### 🔬 **QualityMixin** 
Used by models with quality control data:
- ReadSet, Seq
- AlleleProfile, LocusProfile, SnpProfile
- KmerProfile, MlvaProfile
- AlleleAlignment

### 🧬 **SeqMixin**
Used by models that store sequence data:
- Allele, RefAllele, RefSeq
- Combined with RowMetadataMixin

### ⚙️ **ProtocolMixin**
Used by all protocol models:
- SequencingProtocol, AssemblyProtocol
- AlignmentProtocol, LocusDetectionProtocol
- SnpDetectionProtocol, KmerDetectionProtocol
- SeqClassificationProtocol, AstProtocol
- PcrProtocol, TaxonomyProtocol

### 🔗 **AlignmentMixin**
Used by alignment result models:
- AlleleAlignment, SeqAlignment

These mixins promote code reuse and ensure consistent field definitions across the SeqDB schema.