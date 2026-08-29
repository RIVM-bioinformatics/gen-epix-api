# Minimal CASEDB HTTP interface for the SALM analysis workflow.
#
# Local use:
# install.packages(c("chromote", "httr2"))
# source("gen_epix/commondb/services/remote_app.R")
# source("gen_epix/casedb/services/remote_app.R")
# token <- login_with_chromote("http://localhost:5173")
# result <- retrieve_cases_by_query("http://localhost:8000", token)

SALM_CASE_TYPE_ID <- "a2f25555-3444-43cc-914d-dbaa6703f21b"
SALM_CGMLST_DISTANCE_COL_ID <- "c7daf551-daa4-4ed2-b082-e4c41f4e58c3"

casedb_post <- function(
    base_url,
    path,
    body,
    access_token,
    timeout_seconds,
    post_json
) {
    url <- commondb_url(base_url, paste0("/v1", path))
    post_json(
        url = url,
        body = body,
        access_token = access_token,
        timeout_seconds = timeout_seconds
    )
}

retrieve_cases_by_query <- function(
    base_url,
    access_token,
    case_type_id = SALM_CASE_TYPE_ID,
    timeout_seconds = 45,
    post_json = commondb_post_json
) {
    body <- list(case_type_id = case_type_id)
    casedb_post(
        base_url,
        "/retrieve/case_ids_by_query",
        body,
        access_token,
        timeout_seconds,
        post_json
    )
}

retrieve_cases_by_id <- function(
    base_url,
    access_token,
    case_ids,
    case_type_id = SALM_CASE_TYPE_ID,
    timeout_seconds = 45,
    post_json = commondb_post_json
) {
    body <- list(case_type_id = case_type_id, case_ids = case_ids)
    casedb_post(
        base_url,
        "/retrieve/cases_by_ids",
        body,
        access_token,
        timeout_seconds,
        post_json
    )
}

retrieve_phylogenetic_tree_by_cases <- function(
    base_url,
    access_token,
    case_ids,
    genetic_distance_col_id = SALM_CGMLST_DISTANCE_COL_ID,
    tree_algorithm_code = "SLINK",
    case_type_id = SALM_CASE_TYPE_ID,
    timeout_seconds = 45,
    post_json = commondb_post_json
) {
    body <- list(
        case_type_id = case_type_id,
        genetic_distance_col_id = genetic_distance_col_id,
        tree_algorithm_code = tree_algorithm_code,
        case_ids = case_ids
    )
    casedb_post(
        base_url,
        "/calculate/phylogenetic_tree",
        body,
        access_token,
        timeout_seconds,
        post_json
    )
}
