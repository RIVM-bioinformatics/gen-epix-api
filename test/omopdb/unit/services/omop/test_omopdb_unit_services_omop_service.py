"""Verify the OMOP service forwards commands to its workflow functions."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.omopdb.services.omop import service as service_module


@pytest.mark.parametrize(
    ("method_name", "delegate_name"),
    [
        ("upload_persons", "omop_service_upload_persons"),
        ("retrieve_persons_by_id", "omop_service_retrieve_persons_by_id"),
        ("retrieve_persons_by_query", "omop_service_retrieve_persons_by_query"),
    ],
)
def test_service_method_forwards_command_and_returns_delegate_result(
    method_name: str,
    delegate_name: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Forward the command and preserve the delegated result."""
    service = Mock(spec=service_module.OmopService)
    command = Mock()
    expected_result = Mock()
    delegate = Mock(return_value=expected_result)
    monkeypatch.setattr(service_module, delegate_name, delegate)

    result = getattr(service_module.OmopService, method_name)(service, command)

    delegate.assert_called_once_with(service, command)
    assert result is expected_result
