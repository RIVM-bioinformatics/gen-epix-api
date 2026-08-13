# Shared helpers for calling a Gen-EpiX app from R.

CHROMOTE_ACCESS_TOKEN_SCRIPT <- paste0(
    "(() => {",
    "const key = Object.keys(sessionStorage)",
    ".find((key) => key.startsWith('oidc.user:'));",
    "if (!key) return null;",
    "const user = JSON.parse(sessionStorage.getItem(key));",
    "return user.access_token || null;",
    "})()"
)

chromote_access_token_value <- function(evaluation_result) {
    access_token <- evaluation_result$result$value
    if (!is.character(access_token) || length(access_token) != 1L) {
        return(NULL)
    }
    if (!nzchar(access_token)) {
        return(NULL)
    }
    access_token
}

read_chromote_access_token <- function(chromote_session) {
    evaluation_result <- chromote_session$Runtime$evaluate(
        CHROMOTE_ACCESS_TOKEN_SCRIPT,
        returnByValue = TRUE
    )
    chromote_access_token_value(evaluation_result)
}

login_with_chromote <- function(
    login_url,
    timeout_seconds = 300,
    poll_interval_seconds = 1
) {
    if (!requireNamespace("chromote", quietly = TRUE)) {
        stop("Package 'chromote' is required for browser login.", call. = FALSE)
    }

    chromote_session <- chromote::ChromoteSession$new()
    on.exit(chromote_session$close(), add = TRUE)
    chromote_session$go_to(login_url)
    chromote_session$view()
    message("Complete the login in the Chromote viewer.")

    deadline <- Sys.time() + timeout_seconds
    while (Sys.time() < deadline) {
        access_token <- read_chromote_access_token(chromote_session)
        if (!is.null(access_token)) {
            return(access_token)
        }
        Sys.sleep(poll_interval_seconds)
    }

    stop("Timed out waiting for the browser login to complete.", call. = FALSE)
}

commondb_url <- function(base_url, path) {
    normalized_base_url <- sub("/+$", "", base_url)
    normalized_path <- sub("^/*", "/", path)
    paste0(normalized_base_url, normalized_path)
}

commondb_post_json <- function(
    url,
    body,
    access_token,
    timeout_seconds = 45
) {
    if (!requireNamespace("httr2", quietly = TRUE)) {
        stop("Package 'httr2' is required for HTTP requests.", call. = FALSE)
    }
    is_valid_access_token <- is.character(access_token) &&
        length(access_token) == 1L &&
        nzchar(access_token)
    if (!is_valid_access_token) {
        stop("A non-empty access token is required.", call. = FALSE)
    }

    request <- httr2::request(url)
    request <- httr2::req_headers(
        request,
        Authorization = paste("Bearer", access_token)
    )
    request <- httr2::req_body_json(request, body, auto_unbox = TRUE)
    request <- httr2::req_timeout(request, timeout_seconds)

    response <- httr2::req_perform(request)
    httr2::resp_body_json(response, simplifyVector = FALSE)
}
