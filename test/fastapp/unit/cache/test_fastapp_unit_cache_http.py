"""Tests for HTTP cache validators and policy headers."""

from gen_epix.fastapp.cache.http import (
    SURROGATE_KEY_HEADER,
    HttpCachePolicy,
    compute_etag,
    matches_etag,
)


def test_an_entity_tag_changes_with_the_body() -> None:
    """Different response bytes produce distinct validators."""
    assert compute_etag(b"a") != compute_etag(b"b")
    assert compute_etag(b"a", weak=True).startswith('W/"')


def test_a_weak_validator_matches_its_strong_counterpart() -> None:
    """Weak comparison also supports wildcard and absent headers."""
    etag = compute_etag(b"body")

    assert matches_etag(etag, etag)
    assert matches_etag(f"W/{etag}", etag)
    assert matches_etag("*", etag)
    assert not matches_etag(None, etag)
    assert not matches_etag('"other"', etag)


def test_cache_control_reflects_the_policy() -> None:
    """Response headers contain configured client and shared directives."""
    policy = HttpCachePolicy(
        max_age=60,
        shared_max_age=300,
        stale_while_revalidate=30,
        stale_if_error=600,
        vary=("Accept", "Authorization"),
    )

    headers = policy.response_headers(etag='"abc"', surrogate_keys=["case:1"])

    assert "max-age=60" in headers["Cache-Control"]
    assert "s-maxage=300" in headers["Cache-Control"]
    assert "stale-while-revalidate=30" in headers["Cache-Control"]
    assert "stale-if-error=600" in headers["Cache-Control"]
    assert headers["Vary"] == "Accept, Authorization"
    assert headers[SURROGATE_KEY_HEADER] == "case:1"


def test_a_private_response_is_never_shared() -> None:
    """Private responses do not emit a shared-cache lifetime."""
    policy = HttpCachePolicy(max_age=60, shared_max_age=300, private=True)

    directives = policy.cache_control()

    assert "private" in directives
    assert "s-maxage" not in directives


def test_no_store_suppresses_every_other_directive() -> None:
    """No-store policy takes precedence over other cache directives."""
    policy = HttpCachePolicy(max_age=60, no_store=True)

    assert policy.cache_control() == "no-store"
    assert policy.is_not_modified({"If-None-Match": '"abc"'}, '"abc"') is False


def test_a_matching_validator_allows_a_not_modified_response() -> None:
    """Only a matching conditional request is eligible for a 304 response."""
    policy = HttpCachePolicy(max_age=60)

    assert policy.is_not_modified({"if-none-match": '"abc"'}, '"abc"') is True
    assert policy.is_not_modified({"If-None-Match": '"other"'}, '"abc"') is False
    assert policy.is_not_modified({}, '"abc"') is False
