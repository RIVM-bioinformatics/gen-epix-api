from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.commondb.policies.pdp import PolicyDecisionPoint


def test_is_exempted_without_user() -> None:
    pdp = PolicyDecisionPoint(Mock())

    assert pdp.is_exempted(Mock(user=None)) is True


def test_is_exempted_without_configured_role_set() -> None:
    abac_service = Mock(ABAC_EXEMPTED_ROLE_SET_MAP={})
    pdp = PolicyDecisionPoint(abac_service)
    cmd = Mock(user=Mock(id=uuid4()))

    assert pdp.is_exempted(cmd) is False


def test_is_exempted_when_user_has_configured_role() -> None:
    role_set_id = uuid4()
    role_id = uuid4()
    cmd = Mock(user=Mock(id=uuid4(), roles={role_id}))
    abac_service = Mock(
        ABAC_EXEMPTED_ROLE_SET_MAP={type(cmd): role_set_id},
        app=Mock(impl=Mock(role_set_map={role_set_id: {role_id}})),
    )
    pdp = PolicyDecisionPoint(abac_service)

    assert pdp.is_exempted(cmd) is True


def test_is_not_exempted_when_user_has_no_configured_role() -> None:
    role_set_id = uuid4()
    cmd = Mock(user=Mock(id=uuid4(), roles={uuid4()}))
    abac_service = Mock(
        ABAC_EXEMPTED_ROLE_SET_MAP={type(cmd): role_set_id},
        app=Mock(impl=Mock(role_set_map={role_set_id: {uuid4()}})),
    )
    pdp = PolicyDecisionPoint(abac_service)

    assert pdp.is_exempted(cmd) is False


def test_is_allowed_is_not_implemented() -> None:
    pdp = PolicyDecisionPoint(Mock())

    with pytest.raises(NotImplementedError):
        pdp.is_allowed(Mock())
