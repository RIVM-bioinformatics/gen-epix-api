import pytest

from gen_epix.fastapp.cache.enum import (
    CacheOperation,
    CircuitState,
    EvictionPolicyType,
    ExpiryMode,
    FailureMode,
    InvalidationMode,
    InvalidationScope,
    RemovalCause,
)


@pytest.mark.parametrize(
    ("enum_type", "expected_values"),
    [
        (
            CacheOperation,
            ("GET", "SET", "DELETE", "CLEAR", "LOAD", "REFRESH", "INVALIDATE"),
        ),
        (
            RemovalCause,
            ("EXPLICIT", "REPLACED", "EXPIRED", "SIZE", "INVALIDATED", "CLEARED"),
        ),
        (EvictionPolicyType, ("LRU", "LFU", "FIFO", "RANDOM", "TINY_LFU")),
        (ExpiryMode, ("AFTER_WRITE", "AFTER_ACCESS")),
        (InvalidationScope, ("KEY", "TAG", "NAMESPACE", "REGION", "ALL")),
        (InvalidationMode, ("HARD", "SOFT")),
        (FailureMode, ("FAIL_OPEN", "FAIL_CLOSED")),
        (CircuitState, ("CLOSED", "OPEN", "HALF_OPEN")),
    ],
    ids=(
        "cache-operation",
        "removal-cause",
        "eviction-policy",
        "expiry-mode",
        "invalidation-scope",
        "invalidation-mode",
        "failure-mode",
        "circuit-state",
    ),
)
def test_cache_enum_members_keep_their_names_and_values(enum_type, expected_values):
    assert tuple((member.name, member.value) for member in enum_type) == tuple(
        (value, value) for value in expected_values
    )


@pytest.mark.parametrize(
    ("cause", "expected"),
    [
        (RemovalCause.EXPLICIT, False),
        (RemovalCause.REPLACED, False),
        (RemovalCause.EXPIRED, True),
        (RemovalCause.SIZE, True),
        (RemovalCause.INVALIDATED, False),
        (RemovalCause.CLEARED, False),
    ],
    ids=("explicit", "replaced", "expired", "size", "invalidated", "cleared"),
)
def test_removal_cause_was_evicted(cause, expected):
    assert cause.was_evicted is expected
