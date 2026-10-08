from inspect import isabstract
from test.util.mock_compat import Mock
from uuid import uuid4

import pytest

from gen_epix.commondb.domain import command, exc
from gen_epix.commondb.domain.policy.pdp import BasePolicyDecisionPoint


class _ConcretePolicyDecisionPoint(BasePolicyDecisionPoint):
    def is_exempted(self, cmd: command.Command) -> bool:
        return False

    def is_allowed(self, cmd: command.Command) -> bool:
        return False


def test_base_policy_decision_point_remains_abstract() -> None:
    assert isabstract(BasePolicyDecisionPoint)


def test_constructor_stores_abac_service() -> None:
    abac_service = Mock()

    pdp = _ConcretePolicyDecisionPoint(abac_service)

    assert pdp.abac_service is abac_service


def test_get_command_user_returns_none_when_command_has_no_user() -> None:
    pdp = _ConcretePolicyDecisionPoint(Mock())
    cmd = Mock(user=None)

    assert pdp.get_command_user(cmd) is None


def test_get_command_user_returns_user_with_id() -> None:
    pdp = _ConcretePolicyDecisionPoint(Mock())
    user = Mock(id=uuid4())
    cmd = Mock(user=user)

    assert pdp.get_command_user(cmd) is user


def test_get_command_user_raises_when_user_id_is_missing() -> None:
    pdp = _ConcretePolicyDecisionPoint(Mock())
    cmd = Mock(user=Mock(id=None))

    with pytest.raises(exc.ServiceException) as error:
        pdp.get_command_user(cmd)
    assert error.value.message == "Command user must have an ID."


def test_get_command_user_id_returns_none_when_command_has_no_user() -> None:
    pdp = _ConcretePolicyDecisionPoint(Mock())
    cmd = Mock(user=None)

    assert pdp.get_command_user_id(cmd) is None


def test_get_command_user_id_returns_user_id() -> None:
    pdp = _ConcretePolicyDecisionPoint(Mock())
    user_id = uuid4()
    cmd = Mock(user=Mock(id=user_id))

    assert pdp.get_command_user_id(cmd) == user_id


def test_get_command_user_id_raises_when_user_id_is_missing() -> None:
    pdp = _ConcretePolicyDecisionPoint(Mock())
    cmd = Mock(user=Mock(id=None))

    with pytest.raises(exc.ServiceException) as error:
        pdp.get_command_user_id(cmd)
    assert error.value.message == "Command user must have an ID."
