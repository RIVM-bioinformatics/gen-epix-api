"""Test outage-window authorization behavior."""

from datetime import datetime
from test.util.mock_compat import Mock

import pytest

from gen_epix.commondb.domain.model.system import Outage
from gen_epix.commondb.policies import has_system_outage_policy
from gen_epix.commondb.policies.has_system_outage_policy import (
    HasSystemOutagePolicy,
)

_NOW = 2_000_000_000


def _create_policy(monkeypatch, outages: list[Outage]) -> HasSystemOutagePolicy:
    HasSystemOutagePolicy._IS_ALLOWED_CACHE.clear()
    monkeypatch.setattr(has_system_outage_policy.time, "time", lambda: _NOW)
    system_service = Mock()
    system_service.crud.return_value = outages
    system_service.app.domain.get_permission.return_value = object()
    return HasSystemOutagePolicy(system_service)


@pytest.mark.parametrize(
    ("outage", "expected_allowed"),
    [
        (
            Outage(
                active_from=datetime.fromtimestamp(_NOW + 10),
                active_to=datetime.fromtimestamp(_NOW + 20),
            ),
            True,
        ),
        (
            Outage(
                active_from=datetime.fromtimestamp(_NOW - 10),
                active_to=datetime.fromtimestamp(_NOW + 10),
            ),
            False,
        ),
        (
            Outage(
                active_from=datetime.fromtimestamp(_NOW),
                active_to=datetime.fromtimestamp(_NOW + 10),
            ),
            False,
        ),
        (
            Outage(
                active_from=datetime.fromtimestamp(_NOW - 10),
                active_to=datetime.fromtimestamp(_NOW),
            ),
            True,
        ),
        (Outage(), True),
        (Outage(active_from=datetime.fromtimestamp(_NOW - 10)), False),
        (Outage(active_to=datetime.fromtimestamp(_NOW + 10)), False),
        (
            Outage(
                active_from=datetime.fromtimestamp(_NOW - 10),
                active_to=datetime.fromtimestamp(_NOW + 10),
                is_active=False,
            ),
            True,
        ),
        (
            Outage(
                active_from=datetime.fromtimestamp(_NOW + 10),
                active_to=datetime.fromtimestamp(_NOW + 20),
                is_active=True,
            ),
            False,
        ),
    ],
)
def test_is_allowed_respects_outage_window_and_override(
    monkeypatch, outage: Outage, expected_allowed: bool
) -> None:
    policy = _create_policy(monkeypatch, [outage])

    assert policy._is_allowed() is expected_allowed
