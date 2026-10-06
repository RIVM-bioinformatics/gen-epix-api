"""Verify command dispatch and exception forwarding for sequence API adapters."""

from test.util.mock_compat import Mock

import pytest

from gen_epix.seqdb.api.seq import (
    UpdateSeqDistancesRequestBody,
    _handle_seq_command,
)


def test_handle_seq_command_returns_app_result() -> None:
    """Return the dispatched command result unchanged."""
    app = Mock()
    app.handle.return_value = ["result"]
    handle_exception = Mock()

    result = _handle_seq_command(app, handle_exception, "error", None, "command")

    assert result == ["result"]
    handle_exception.assert_not_called()


@pytest.mark.parametrize(
    ("values", "expected_limit"),
    [
        ({"max_new_profiles": 10}, 10),
        ({"max_new_profiles": 10, "limit": 3}, 3),
    ],
)
def test_update_distances_request_normalizes_deprecated_limit(
    values: dict[str, int], expected_limit: int
) -> None:
    """Use the deprecated value only when the current limit is absent."""
    request = UpdateSeqDistancesRequestBody(
        protocol_id="00000000-0000-0000-0000-000000000001",
        **values,
    )

    assert request.limit == expected_limit


@pytest.mark.parametrize("request_ids", [None, ["request-id"]])
def test_handle_seq_command_forwards_failures(
    request_ids: list[str] | None,
) -> None:
    """Forward dispatch exceptions, including request IDs when provided."""
    app = Mock()
    dispatch_error = RuntimeError("dispatch failed")
    app.handle.side_effect = dispatch_error
    handle_exception = Mock(side_effect=LookupError("handled"))

    with pytest.raises(LookupError, match="handled"):
        _handle_seq_command(
            app,
            handle_exception,
            "error-code",
            "user",
            "command",
            request_ids=request_ids,
        )

    expected_kwargs = {"request_ids": request_ids} if request_ids is not None else {}
    handle_exception.assert_called_once_with(
        "error-code", "user", dispatch_error, **expected_kwargs
    )
