from test.util.mock_compat import Mock

import pytest

from gen_epix.casedb.domain import command, model
from gen_epix.casedb.domain.policy import BaseCaseAbacPolicy
from gen_epix.casedb.policies.case_abac_policy import CaseAbacPolicy


@pytest.fixture
def abac_service() -> Mock:
    return Mock()


@pytest.fixture
def policy(abac_service: Mock) -> CaseAbacPolicy:
    return CaseAbacPolicy(abac_service)


def test_is_base_case_abac_policy(policy: CaseAbacPolicy) -> None:
    assert isinstance(policy, BaseCaseAbacPolicy)


def test_init_retains_service_and_props(abac_service: Mock) -> None:
    policy = CaseAbacPolicy(abac_service, key="value")

    assert policy.abac_service is abac_service
    assert policy.props == {"key": "value"}


def test_get_content_returns_service_case_abac(
    policy: CaseAbacPolicy, abac_service: Mock
) -> None:
    cmd = Mock(spec=command.Command)

    result = policy.get_content(cmd)

    assert result is abac_service.get_case_abac.return_value
    abac_service.get_case_abac.assert_called_once_with(cmd)


def test_get_content_propagates_service_error(
    policy: CaseAbacPolicy, abac_service: Mock
) -> None:
    abac_service.get_case_abac.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        policy.get_content(Mock(spec=command.Command))


def test_get_content_return_type_is_case_abac(policy: CaseAbacPolicy) -> None:
    cmd = Mock(spec=command.Command)

    assert policy.get_content_return_type(cmd) is model.CaseAbac
    assert policy.get_content_return_type(None) is model.CaseAbac  # type: ignore[arg-type]
