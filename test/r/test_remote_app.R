repo_root <- normalizePath(".")

source(file.path(repo_root, "gen_epix", "commondb", "services", "remote_app.R"))
source(file.path(repo_root, "gen_epix", "casedb", "services", "remote_app.R"))

record_request <- function(url, body, access_token, timeout_seconds) {
    list(
        url = url,
        body = body,
        access_token = access_token,
        timeout_seconds = timeout_seconds
    )
}

query_request <- retrieve_cases_by_query(
    base_url = "http://localhost:8000/",
    access_token = "test-token",
    post_json = record_request
)
stopifnot(
    identical(query_request$url, "http://localhost:8000/v1/retrieve/case_ids_by_query"),
    identical(query_request$body, list(case_type_id = SALM_CASE_TYPE_ID)),
    identical(query_request$access_token, "test-token")
)

case_ids <- c("case-1", "case-2")
cases_request <- retrieve_cases_by_id(
    base_url = "http://localhost:8000",
    access_token = "test-token",
    case_ids = case_ids,
    post_json = record_request
)
stopifnot(
    identical(cases_request$url, "http://localhost:8000/v1/retrieve/cases_by_ids"),
    identical(
        cases_request$body,
        list(case_type_id = SALM_CASE_TYPE_ID, case_ids = case_ids)
    )
)

tree_request <- retrieve_phylogenetic_tree_by_cases(
    base_url = "http://localhost:8000",
    access_token = "test-token",
    case_ids = case_ids,
    post_json = record_request
)
stopifnot(
    identical(tree_request$url, "http://localhost:8000/v1/calculate/phylogenetic_tree"),
    identical(tree_request$body$case_type_id, SALM_CASE_TYPE_ID),
    identical(tree_request$body$genetic_distance_col_id, SALM_CGMLST_DISTANCE_COL_ID),
    identical(tree_request$body$tree_algorithm_code, "SLINK"),
    identical(tree_request$body$case_ids, case_ids)
)

token_result <- list(result = list(value = "browser-token"))
stopifnot(identical(chromote_access_token_value(token_result), "browser-token"))

missing_token_result <- list(result = list(subtype = "null"))
stopifnot(is.null(chromote_access_token_value(missing_token_result)))

timed_out_runtime <- new.env()
timed_out_runtime$evaluate <- function(...) {
    stop("Chromote: timed out waiting for response to command Runtime.evaluate")
}
timed_out_session <- list(Runtime = timed_out_runtime)
stopifnot(is.null(read_chromote_access_token_during_login(timed_out_session)))

disconnected_runtime <- new.env()
disconnected_runtime$evaluate <- function(...) {
    stop("Chromote: websocket disconnected")
}
disconnected_session <- list(Runtime = disconnected_runtime)
capture_error_message <- function(error) conditionMessage(error)
disconnected_error <- tryCatch(
    read_chromote_access_token_during_login(disconnected_session),
    error = capture_error_message
)
stopifnot(identical(disconnected_error, "Chromote: websocket disconnected"))
