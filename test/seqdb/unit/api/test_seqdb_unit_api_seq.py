"""Verify command dispatch and exception forwarding for sequence API adapters."""

import asyncio
import threading
from test.util.mock_compat import Mock
from typing import Annotated, Any
from uuid import UUID, uuid4

import pytest
from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute
from pydantic import ValidationError

from gen_epix.seqdb.api.seq import (
    RetrieveSeqDistancesBySeqProfilesRequestBody,
    RetrieveSeqFastaRequestBody,
    UpdateSeqDistancesRequestBody,
    _handle_seq_command,
    create_seq_endpoints,
)
from gen_epix.seqdb.domain import command


@pytest.fixture
def seq_routes() -> tuple[dict[str, APIRoute], Mock]:
    """Register the real route functions with a mock dispatcher."""
    router = APIRouter()
    app = Mock()
    app.impl.registered_user_dependency = Annotated[Any, Depends(lambda: None)]
    app.domain.get_dag_sorted_entities.return_value = []
    create_seq_endpoints(router, app, Mock())
    return {
        route.path: route for route in router.routes if isinstance(route, APIRoute)
    }, app


def test_handle_seq_command_returns_app_result() -> None:
    """Return the dispatched command result unchanged."""
    app = Mock()
    app.handle.return_value = ["result"]
    handle_exception = Mock()

    result = _handle_seq_command(app, handle_exception, "error", None, "command")

    assert result == ["result"]
    handle_exception.assert_not_called()


@pytest.mark.parametrize(
    ("max_new_profiles", "limit", "expected_limit"),
    [
        (10, None, 10),
        (10, 3, 3),
    ],
)
def test_update_distances_request_normalizes_deprecated_limit(
    max_new_profiles: int, limit: int | None, expected_limit: int
) -> None:
    """Use the deprecated value only when the current limit is absent."""
    request = UpdateSeqDistancesRequestBody(
        protocol_id=UUID("00000000-0000-0000-0000-000000000001"),
        max_new_profiles=max_new_profiles,
        limit=limit,
    )

    assert request.limit == expected_limit


def test_retrieve_seq_fasta_request_defaults_wrap() -> None:
    """Use the sequence command's default wrapping width for API requests."""
    request = RetrieveSeqFastaRequestBody(
        seq_ids=[uuid4()], file_name="sequences.fasta"
    )

    assert request.wrap == 80


def test_retrieve_seq_fasta_route_forwards_wrap(
    seq_routes: tuple[dict[str, APIRoute], Mock],
) -> None:
    """Forward the request's wrapping width in the dispatched command."""

    routes, app = seq_routes
    app.handle.return_value = iter([">sequence\nacgt\n"])
    route = routes["/retrieve/seq_fasta"]
    request = RetrieveSeqFastaRequestBody(
        seq_ids=[uuid4()], wrap=0, file_name="sequences.fasta"
    )

    asyncio.run(route.endpoint(None, request))

    assert app.handle.call_args.args[0].wrap == 0


@pytest.mark.parametrize(
    ("path", "request_class", "command_class", "extra_fields"),
    [
        (
            "/retrieve/seq_distances_by_seq_profiles",
            RetrieveSeqDistancesBySeqProfilesRequestBody,
            command.RetrieveSeqDistancesBySeqProfilesCommand,
            {"seq_profile_ids": [uuid4()]},
        ),
        (
            "/update/seq_distances",
            UpdateSeqDistancesRequestBody,
            command.UpdateSeqDistancesCommand,
            {"limit": 4, "existing_chunk_size": 20},
        ),
    ],
)
def test_distance_routes_dispatch_on_worker(
    seq_routes: tuple[dict[str, APIRoute], Mock],
    path: str,
    request_class: type,
    command_class: type,
    extra_fields: dict[str, Any],
) -> None:
    """Forward the distance command and its fields from a worker thread."""
    routes, app = seq_routes
    request_fields = {"protocol_id": uuid4(), **extra_fields}
    request = request_class(**request_fields)
    event_loop_thread = threading.get_ident()

    def dispatch(cmd: Any) -> list[Any]:
        assert threading.get_ident() != event_loop_thread
        assert isinstance(cmd, command_class)
        for field, value in request_fields.items():
            assert getattr(cmd, field) == value
        return []

    app.handle.side_effect = dispatch
    assert asyncio.run(routes[path].endpoint(None, request)) == []


def test_retrieve_seq_fasta_request_rejects_negative_wrap() -> None:
    """Reject negative wrapping widths in FASTA request bodies."""
    with pytest.raises(ValidationError):
        RetrieveSeqFastaRequestBody(
            seq_ids=[uuid4()], wrap=-1, file_name="sequences.fasta"
        )


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
