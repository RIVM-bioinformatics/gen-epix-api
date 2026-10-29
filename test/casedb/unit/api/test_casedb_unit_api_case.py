import asyncio
import base64
from collections.abc import Callable
from test.util.mock_compat import Mock
from typing import Any
from uuid import uuid4

import pytest
from fastapi import APIRouter
from fastapi.routing import APIRoute

from gen_epix.casedb.api import case as casedb_api_case
from gen_epix.casedb.domain import command
from gen_epix.seqdb.domain import enum as seqdb_enum


@pytest.fixture
def registered_case_endpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[APIRouter, Mock]:
    app = Mock()
    app.impl.registered_user_dependency = str
    monkeypatch.setattr(
        casedb_api_case.CrudEndpointGenerator,
        "create_crud_endpoint_set_for_domain",
        lambda *_args, **_kwargs: [],
    )
    monkeypatch.setattr(
        casedb_api_case.CrudEndpointGenerator,
        "generate_endpoints",
        lambda *_args, **_kwargs: None,
    )
    handle_command = Mock(return_value=[])
    monkeypatch.setattr(casedb_api_case, "handle_command", handle_command)
    router = APIRouter()

    casedb_api_case.create_case_endpoints(router, app, handle_exception=Mock())
    return router, handle_command


def _get_endpoint(router: APIRouter, path: str) -> Callable[..., Any]:
    return next(
        route.endpoint
        for route in router.routes
        if isinstance(route, APIRoute) and route.path == path
    )


def test_retrieve_case_cohort_links_forwards_include_missing(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    endpoint = _get_endpoint(router, "/retrieve/case_cohort_links_by_case_type")
    request_body = casedb_api_case.RetrieveCaseCohortLinksByCaseTypeRequestBody(
        case_type_id=uuid4(), include_missing=True
    )

    asyncio.run(endpoint(user=None, request_body=request_body))

    input_command = handle_command.call_args.kwargs["input_command"]
    assert isinstance(input_command, command.RetrieveCaseCohortLinksByCaseTypeCommand)
    assert input_command.include_missing is True


def test_create_file_for_read_set_forwards_format_and_compression(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    endpoint = _get_endpoint(router, "/create_file_for_read_set/{case_id}/{col_id}")
    case_id = uuid4()
    col_id = uuid4()
    file_content = b"reads"
    request_body = casedb_api_case.CreateFileForReadSetRequestBody(
        file_content=base64.b64encode(file_content).decode("ascii"),
        is_fwd=False,
        file_format=seqdb_enum.ReadsFileFormat.FASTQ,
        file_compression=seqdb_enum.FileCompression.GZIP,
    )

    asyncio.run(
        endpoint(
            user=None,
            case_id=case_id,
            col_id=col_id,
            request_body=request_body,
        )
    )

    input_command = handle_command.call_args.kwargs["input_command"]
    assert isinstance(input_command, command.CreateFileForReadSetCommand)
    assert input_command.file_content == file_content
    assert input_command.is_fwd is False
    assert input_command.file_format == request_body.file_format
    assert input_command.file_compression == request_body.file_compression


def test_create_file_for_seq_forwards_format_and_compression(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    endpoint = _get_endpoint(router, "/create_file_for_seq/{case_id}/{col_id}")
    case_id = uuid4()
    col_id = uuid4()
    file_content = b"sequence"
    request_body = casedb_api_case.CreateFileForSeqRequestBody(
        file_content=base64.b64encode(file_content).decode("ascii"),
        file_format=seqdb_enum.SeqFileFormat.FASTA,
        file_compression=seqdb_enum.FileCompression.GZIP,
    )

    asyncio.run(
        endpoint(
            user=None,
            case_id=case_id,
            col_id=col_id,
            request_body=request_body,
        )
    )

    input_command = handle_command.call_args.kwargs["input_command"]
    assert isinstance(input_command, command.CreateFileForSeqCommand)
    assert input_command.file_content == file_content
    assert input_command.file_format == request_body.file_format
    assert input_command.file_compression == request_body.file_compression
