# casedb / CASE — Simplified ERD

Auto-generated.  Service type **CASE** — 35 entities, relationships only.

```mermaid
erDiagram
    %% casedb / CASE (simplified)

    %% Relationships
<<<<<<< HEAD
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseDataCollectionLink }o--|| Case : "case_id"
    RefCol }o--|| RefDim : "ref_dim_id"
    RefCol }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    CaseIdentifier }o--|| Case : "internal_id"
    Col }o--|| CaseType : "case_type_id"
    Col }o--|| Dim : "dim_id"
    Col }o--|| RefCol : "ref_col_id"
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    Dim }o--|| CaseType : "case_type_id"
    Dim }o--|| RefDim : "ref_dim_id"
    Case }o--|| CaseType : "case_type_id"
    ColSetMember }o--|| ColSet : "col_set_id"
    ColSetMember }o--|| Col : "col_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"

    CaseBatchForUpload {
    }
=======
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    ColSetMember }o--|| ColSet : "col_set_id"
    ColSetMember }o--|| Col : "col_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    Dim }o--|| CaseType : "case_type_id"
    Dim }o--|| RefDim : "ref_dim_id"
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseDataCollectionLink }o--|| Case : "case_id"
    Case }o--|| CaseType : "case_type_id"
    CaseIdentifier }o--|| Case : "internal_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"
    Col }o--|| CaseType : "case_type_id"
    Col }o--|| Dim : "dim_id"
    Col }o--|| RefCol : "ref_col_id"
    RefCol }o--|| RefDim : "ref_dim_id"
    RefCol }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0

    RefDataAccess {
    }

<<<<<<< HEAD
    CaseSetRights {
=======
    CaseBatchForUpload {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    ReadSetForUpload {
    }

    CaseUploadResult {
    }

    CaseQueryResult {
    }

<<<<<<< HEAD
    CaseQuery {
    }

    CaseQueryResult {
    }

    CaseBatchUploadResult {
=======
    CaseRights {
    }

    CaseQuery {
    }

    SeqForUpload {
    }

    CompleteCaseType {
    }

    CaseForUpload {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    CaseBatchUploadResult {
    }

<<<<<<< HEAD
    CaseForUpload {
    }

    CaseStats {
=======
    CaseSetQuery {
    }

    CaseSetRights {
>>>>>>> 308323364935921da85b7fa99e87c3af4ae7f9f0
    }

    CaseStats {
    }

    CaseUploadResult {
    }

```
