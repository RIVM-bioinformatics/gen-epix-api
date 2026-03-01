# casedb / CASE — Simplified ERD

Auto-generated.  Service type **CASE** — 33 entities, relationships only.

```mermaid
erDiagram
    %% casedb / CASE (simplified)

    %% Relationships
    CaseSetDataCollectionLink }o--|| CaseSet : "case_set_id"
    CaseDataCollectionLink }o--|| Case : "case_id"
    CaseTypeSetMember }o--|| CaseTypeSet : "case_type_set_id"
    CaseTypeSetMember }o--|| CaseType : "case_type_id"
    CaseTypeCol }o--|| CaseType : "case_type_id"
    CaseTypeCol }o--|| CaseTypeDim : "case_type_dim_id"
    CaseTypeCol }o--|| Col : "col_id"
    TreeAlgorithm }o--|| TreeAlgorithmClass : "tree_algorithm_class_id"
    Col }o--|| Dim : "dim_id"
    Col }o--|| GeneticDistanceProtocol : "genetic_distance_protocol_id"
    CaseSet }o--|| CaseType : "case_type_id"
    CaseSet }o--|| CaseSetCategory : "case_set_category_id"
    CaseSet }o--|| CaseSetStatus : "case_set_status_id"
    CaseSetMember }o--|| CaseSet : "case_set_id"
    CaseSetMember }o--|| Case : "case_id"
    CaseTypeColSetMember }o--|| CaseTypeColSet : "case_type_col_set_id"
    CaseTypeColSetMember }o--|| CaseTypeCol : "case_type_col_id"
    CaseTypeSet }o--|| CaseTypeSetCategory : "case_type_set_category_id"
    Case }o--|| CaseType : "case_type_id"
    CaseTypeDim }o--|| CaseType : "case_type_id"
    CaseTypeDim }o--|| Dim : "dim_id"

    CaseRights {
    }

    CaseSetQuery {
    }

    CompleteCaseType {
    }

    CaseQuery {
    }

    CaseBatchForUpload {
    }

    ReadSetForUpload {
    }

    CaseSetRights {
    }

    CaseBatchUploadResult {
    }

    CaseStats {
    }

    CaseQueryResult {
    }

    SeqForUpload {
    }

    CaseForUpload {
    }

    CaseUploadResult {
    }

```
