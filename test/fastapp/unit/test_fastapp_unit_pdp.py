"""Exercise policy registration and application across command lifecycle phases."""

from typing import Any

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import EventTiming
from gen_epix.fastapp.model import Command, Policy
from gen_epix.fastapp.pdp import PolicyDecisionPoint


class _Command(Command):
    """Provide a command type for policy decision point tests."""


class _RecordingPolicy(Policy):
    """Record authorization and result-filtering calls for PDP tests."""

    def __init__(self, *, allowed: bool = True, result_suffix: str = "") -> None:
        self.allowed = allowed
        self.result_suffix = result_suffix
        self.authorization_calls = 0
        self.filter_calls = 0

    def is_allowed(self, cmd: Command) -> bool:
        """Return the configured authorization decision."""
        self.authorization_calls += 1
        return self.allowed

    def get_content(self, cmd: Command) -> Any:
        """Leave content retrieval unsupported for this test policy."""
        raise NotImplementedError

    def get_content_return_type(self, cmd: Command) -> type:
        """Leave content type retrieval unsupported for this test policy."""
        raise NotImplementedError

    def filter(self, cmd: Command, retval: object) -> object:
        """Append this policy's suffix to the result."""
        self.filter_calls += 1
        return f"{retval}{self.result_suffix}"


def test_register_policy_preserves_order_and_returns_a_copy() -> None:
    """Keep registration order private from mutations to retrieved lists."""
    pdp = PolicyDecisionPoint()
    first_policy = _RecordingPolicy()
    second_policy = _RecordingPolicy()

    pdp.register_policy(_Command, first_policy)
    pdp.register_policy(_Command, second_policy)
    retrieved = pdp.get_policies(_Command, EventTiming.BEFORE)
    retrieved.clear()

    assert pdp.get_policies(_Command, EventTiming.BEFORE) == [
        first_policy,
        second_policy,
    ]


def test_register_policy_rejects_duplicate_registration() -> None:
    """Reject registering the same policy twice for one command and phase."""
    pdp = PolicyDecisionPoint()
    policy = _RecordingPolicy()
    pdp.register_policy(_Command, policy)

    with pytest.raises(exc.InitializationServiceError):
        pdp.register_policy(_Command, policy)


def test_unregister_policy_removes_only_the_requested_timing() -> None:
    """Leave registrations at other timings untouched."""
    pdp = PolicyDecisionPoint()
    policy = _RecordingPolicy()
    pdp.register_policy(_Command, policy, EventTiming.BEFORE)
    pdp.register_policy(_Command, policy, EventTiming.AFTER)

    pdp.unregister_policy(_Command, policy, EventTiming.BEFORE)

    assert not pdp.get_policies(_Command, EventTiming.BEFORE)
    assert pdp.get_policies(_Command, EventTiming.AFTER) == [policy]


def test_unregister_policy_without_timing_removes_all_matching_phases() -> None:
    """Remove one policy from every phase while preserving other policies."""
    pdp = PolicyDecisionPoint()
    policy = _RecordingPolicy()
    other_policy = _RecordingPolicy()
    pdp.register_policy(_Command, policy, EventTiming.BEFORE)
    pdp.register_policy(_Command, other_policy, EventTiming.BEFORE)
    pdp.register_policy(_Command, policy, EventTiming.DURING)
    pdp.register_policy(_Command, policy, EventTiming.AFTER)

    pdp.unregister_policy(_Command, policy)

    assert pdp.get_policies(_Command, EventTiming.BEFORE) == [other_policy]
    assert not pdp.get_policies(_Command, EventTiming.DURING)
    assert not pdp.get_policies(_Command, EventTiming.AFTER)


def test_unregister_policy_rejects_missing_registrations() -> None:
    """Raise for unknown commands, phases, and policy registrations."""
    pdp = PolicyDecisionPoint()
    policy = _RecordingPolicy()
    other_policy = _RecordingPolicy()

    with pytest.raises(exc.InitializationServiceError):
        pdp.unregister_policy(_Command, policy)

    pdp.register_policy(_Command, other_policy, EventTiming.BEFORE)
    with pytest.raises(exc.InitializationServiceError):
        pdp.unregister_policy(_Command, policy, EventTiming.AFTER)
    with pytest.raises(exc.InitializationServiceError):
        pdp.unregister_policy(_Command, policy, EventTiming.BEFORE)
    with pytest.raises(exc.InitializationServiceError):
        pdp.unregister_policy(_Command, policy)


def test_apply_before_checks_policies_in_registration_order() -> None:
    """Authorize with every BEFORE policy and return no handler result."""
    pdp = PolicyDecisionPoint()
    policies = [_RecordingPolicy(), _RecordingPolicy()]
    for policy in policies:
        pdp.register_policy(_Command, policy, EventTiming.BEFORE)

    result = pdp.apply(_Command(), EventTiming.BEFORE, retval="ignored")

    assert result is None
    assert [policy.authorization_calls for policy in policies] == [1, 1]


def test_apply_before_raises_when_a_policy_denies() -> None:
    """Stop authorization and raise the denying policy's exception."""
    pdp = PolicyDecisionPoint()
    allowed_policy = _RecordingPolicy()
    denied_policy = _RecordingPolicy(allowed=False)
    later_policy = _RecordingPolicy()
    for policy in (allowed_policy, denied_policy, later_policy):
        pdp.register_policy(_Command, policy, EventTiming.BEFORE)

    with pytest.raises(exc.UnauthorizedAuthError):
        pdp.apply(_Command(), EventTiming.BEFORE)

    assert allowed_policy.authorization_calls == 1
    assert denied_policy.authorization_calls == 1
    assert later_policy.authorization_calls == 0


def test_apply_during_attaches_policies_in_registration_order() -> None:
    """Attach DURING policies to the command without returning a result."""
    pdp = PolicyDecisionPoint()
    command = _Command()
    policies = [_RecordingPolicy(), _RecordingPolicy()]
    for policy in policies:
        pdp.register_policy(_Command, policy, EventTiming.DURING)

    result = pdp.apply(command, EventTiming.DURING, retval="ignored")

    assert result is None
    assert getattr(command, "_policies") == policies


def test_apply_after_filters_result_in_registration_order() -> None:
    """Pass the result through each AFTER policy in registration order."""
    pdp = PolicyDecisionPoint()
    policies = [
        _RecordingPolicy(result_suffix=" first"),
        _RecordingPolicy(result_suffix=" second"),
    ]
    for policy in policies:
        pdp.register_policy(_Command, policy, EventTiming.AFTER)

    result = pdp.apply(_Command(), EventTiming.AFTER, retval="result")

    assert result == "result first second"
    assert [policy.filter_calls for policy in policies] == [1, 1]


@pytest.mark.parametrize(
    ("timing", "retval", "expected"),
    [
        (EventTiming.BEFORE, "result", None),
        (EventTiming.DURING, "result", None),
        (EventTiming.AFTER, "result", "result"),
        (EventTiming.AFTER, None, None),
    ],
    ids=["empty-before", "empty-during", "empty-after", "after-none"],
)
def test_apply_without_policies_returns_phase_default(
    timing: EventTiming, retval: object, expected: object
) -> None:
    """Return the phase-specific default when no policy is registered."""
    result = PolicyDecisionPoint().apply(_Command(), timing, retval)

    assert result == expected
