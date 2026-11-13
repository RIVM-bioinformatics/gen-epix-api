from test.util.mock_compat import Mock, call
from types import SimpleNamespace

import pytest

from gen_epix.casedb.domain import exc
from gen_epix.casedb.domain.policy.abac import BaseCaseAbacPolicy
from gen_epix.fastapp.model import Policy


@pytest.fixture
def abac_service() -> Mock:
    return Mock()


@pytest.fixture
def abac_policy(abac_service: Mock) -> BaseCaseAbacPolicy:
    return BaseCaseAbacPolicy(abac_service)


@pytest.fixture
def make_cmd():
    def _make(*policies: object) -> SimpleNamespace:
        return SimpleNamespace(_policies=list(policies))

    return _make


def test_init_stores_service_and_props(abac_service: Mock) -> None:
    policy = BaseCaseAbacPolicy(abac_service, a=1, b="x")

    assert policy.abac_service is abac_service
    assert policy.props == {"a": 1, "b": "x"}


def test_init_without_kwargs_has_empty_props(abac_service: Mock) -> None:
    assert not BaseCaseAbacPolicy(abac_service).props


def test_get_ref_data_access_delegates_to_service(
    abac_policy: BaseCaseAbacPolicy, abac_service: Mock, make_cmd
) -> None:
    cmd = make_cmd()

    result = abac_policy.get_ref_data_access(cmd)  # type: ignore[arg-type]

    assert result is abac_service.get_ref_data_access.return_value
    assert abac_service.get_ref_data_access.call_args_list == [call(cmd)]


def test_get_case_abac_from_command_no_policies(make_cmd) -> None:
    assert BaseCaseAbacPolicy.get_case_abac_from_command(make_cmd()) is None  # type: ignore[arg-type]


def test_get_case_abac_from_command_ignores_other_policies(make_cmd) -> None:
    cmd = make_cmd(Mock(spec=Policy), object())

    assert BaseCaseAbacPolicy.get_case_abac_from_command(cmd) is None  # type: ignore[arg-type]


def test_get_case_abac_from_command_single_policy(
    abac_policy: BaseCaseAbacPolicy, abac_service: Mock, make_cmd
) -> None:
    cmd = make_cmd(Mock(spec=Policy), abac_policy)

    result = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)  # type: ignore[arg-type]

    assert result is abac_service.get_case_abac.return_value
    assert abac_service.get_case_abac.call_args_list == [call(cmd)]


def test_get_case_abac_from_command_subclass_policy(
    abac_service: Mock, make_cmd
) -> None:
    class _SubPolicy(BaseCaseAbacPolicy):
        pass

    cmd = make_cmd(_SubPolicy(abac_service))

    result = BaseCaseAbacPolicy.get_case_abac_from_command(cmd)  # type: ignore[arg-type]

    assert result is abac_service.get_case_abac.return_value


def test_get_case_abac_from_command_multiple_policies_raise(
    abac_service: Mock, make_cmd
) -> None:
    cmd = make_cmd(BaseCaseAbacPolicy(abac_service), BaseCaseAbacPolicy(abac_service))

    with pytest.raises(exc.InitializationServiceError):
        BaseCaseAbacPolicy.get_case_abac_from_command(cmd)  # type: ignore[arg-type]


def test_get_ref_data_access_from_command_no_policies(make_cmd) -> None:
    assert BaseCaseAbacPolicy.get_ref_data_access_from_command(make_cmd()) is None  # type: ignore[arg-type]


def test_get_ref_data_access_from_command_ignores_other_policies(make_cmd) -> None:
    cmd = make_cmd(Mock(spec=Policy), object())

    assert BaseCaseAbacPolicy.get_ref_data_access_from_command(cmd) is None  # type: ignore[arg-type]


def test_get_ref_data_access_from_command_single_policy(
    abac_policy: BaseCaseAbacPolicy, abac_service: Mock, make_cmd
) -> None:
    cmd = make_cmd(abac_policy)

    result = BaseCaseAbacPolicy.get_ref_data_access_from_command(cmd)  # type: ignore[arg-type]

    assert result is abac_service.get_ref_data_access.return_value
    assert abac_service.get_ref_data_access.call_args_list == [call(cmd)]


def test_get_ref_data_access_from_command_multiple_policies_raise(
    abac_service: Mock, make_cmd
) -> None:
    cmd = make_cmd(BaseCaseAbacPolicy(abac_service), BaseCaseAbacPolicy(abac_service))

    with pytest.raises(exc.InitializationServiceError):
        BaseCaseAbacPolicy.get_ref_data_access_from_command(cmd)  # type: ignore[arg-type]
