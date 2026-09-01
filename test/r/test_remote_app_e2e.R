# Interactive end-to-end test for the CASEDB R remote app.
#
# Prerequisites:
# - CASEDB API at https://127.0.0.1:8000 using SA_SQLITE_DEMO
# - CASEDB UI at https://localhost:5010
# - Mock OIDC server at https://localhost:5443
#
# Run from the gen-epix-api repository root:
# Rscript test/r/test_remote_app_e2e.R

repo_root <- normalizePath(".")
certificate_path <- normalizePath(file.path(repo_root, "cert", "cert.pem"))

Sys.setenv(CURL_CA_BUNDLE = certificate_path)

source(file.path(repo_root, "gen_epix", "commondb", "services", "remote_app.R"))
source(file.path(repo_root, "gen_epix", "casedb", "services", "remote_app.R"))

CASEDB_URL <- "https://127.0.0.1:8000"
CASEDB_LOGIN_URL <- "https://localhost:5010"
DEMO_SALM_CASE_TYPE_ID <- "6e5b6a81-ccca-408f-8591-649dce8ccbeb"
DEMO_SALM_CGMLST_COL_ID <- "35174fb1-055c-46a9-98b5-1ef016e0d895"
N_CASES_FOR_TREE <- 3L

message("Click LOGIN for the Dum My CASEDB_ROOT user in the Chromote viewer.")
access_token <- login_with_chromote(CASEDB_LOGIN_URL)

query_result <- retrieve_cases_by_query(
    CASEDB_URL,
    access_token,
    case_type_id = DEMO_SALM_CASE_TYPE_ID
)
case_ids <- unlist(query_result$case_ids, use.names = FALSE)

if (length(case_ids) < N_CASES_FOR_TREE) {
    stop("CASEDB returned fewer than three demo cases.", call. = FALSE)
}

selected_case_ids <- head(case_ids, N_CASES_FOR_TREE)
cases <- retrieve_cases_by_id(
    CASEDB_URL,
    access_token,
    case_ids = selected_case_ids,
    case_type_id = DEMO_SALM_CASE_TYPE_ID
)
returned_case_ids <- vapply(cases, `[[`, character(1), "id")

if (!setequal(returned_case_ids, selected_case_ids)) {
    stop("CASEDB did not return all requested cases.", call. = FALSE)
}

tree <- retrieve_phylogenetic_tree_by_cases(
    CASEDB_URL,
    access_token,
    case_ids = selected_case_ids,
    genetic_distance_col_id = DEMO_SALM_CGMLST_COL_ID,
    case_type_id = DEMO_SALM_CASE_TYPE_ID
)

if (!identical(tree$tree_algorithm_code, "SLINK") || !nzchar(tree$newick_repr)) {
    stop("CASEDB did not return a valid SLINK tree.", call. = FALSE)
}

cat("\nCASEDB R end-to-end test succeeded.\n")
cat("Cases matched:", length(case_ids), "\n")
cat("Cases retrieved:", length(cases), "\n")
cat("Retrieved case IDs:\n", paste(returned_case_ids, collapse = "\n"), "\n")
cat("Tree algorithm:", tree$tree_algorithm_code, "\n")
cat("Newick tree:\n", tree$newick_repr, "\n")
