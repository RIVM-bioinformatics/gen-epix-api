"""Verify file API command dispatch and exception forwarding."""

import asyncio
from test.util.mock_compat import Mock
from typing import Annotated, Any

import pytest
from fastapi import APIRouter, Depends
from fastapi.routing import APIRoute

from gen_epix.seqdb.api import file as file_api
from gen_epix.seqdb.api.file_schema import CreateFileRequestBody
from gen_epix.seqdb.domain import enum


def test_create_file_forwards_dispatch_failure_to_exception_handler(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Forward app failures without requiring unrelated request identifiers."""
    monkeypatch.setattr(
        file_api.CrudEndpointGenerator,
        "create_crud_endpoint_set_for_domain",
        lambda *args, **kwargs: (),
    )
    monkeypatch.setattr(
        file_api.CrudEndpointGenerator,
        "generate_endpoints",
        lambda *args, **kwargs: None,
    )
    app = Mock()
    app.impl.registered_user_dependency = Annotated[Any, Depends(lambda: None)]
    dispatch_error = RuntimeError("dispatch failed")
    app.handle.side_effect = dispatch_error
    handle_exception = Mock(side_effect=LookupError("handled"))
    router = APIRouter()

    file_api.create_file_endpoints(router, app, handle_exception)
    route = next(
        route
        for route in router.routes
        if isinstance(route, APIRoute) and route.name == "CreateFile"
    )
    request = CreateFileRequestBody(content="", format=enum.FileFormat.FASTA)

    with pytest.raises(LookupError, match="handled"):
        asyncio.run(route.endpoint(None, request))

    handle_exception.assert_called_once_with("a8f9d24e", None, dispatch_error)
