import asyncio
import base64
from collections.abc import Callable
from test.util.mock_compat import Mock
from typing import Any
from unittest.mock import AsyncMock
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
    app_impl = Mock()
    app_impl.registered_user_dependency = str
    app_impl.services = {}
    app.impl = app_impl
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
    handle_exception = Mock()
    handle_command.handle_exception = handle_exception
    handle_command.app = app
    app.handle_exception = handle_exception
    monkeypatch.setattr(casedb_api_case, "handle_command", handle_command)
    router = APIRouter()

    casedb_api_case.create_case_endpoints(
        router, app, handle_exception=handle_exception
    )
    return router, handle_command


def _get_endpoint(router: APIRouter, path: str) -> Callable[..., Any]:
    return next(
        route.endpoint
        for route in router.routes
        if isinstance(route, APIRoute) and route.path == path
    )


def _get_input_command(handle_command: Mock) -> Any:
    return handle_command.call_args.kwargs["input_command"]


def test_retrieve_case_cohort_links_forwards_include_missing(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    endpoint = _get_endpoint(router, "/retrieve/case_cohort_links_by_case_type")
    request_body = casedb_api_case.RetrieveCaseCohortLinksByCaseTypeRequestBody(
        case_type_id=uuid4(), include_missing=True
    )

    asyncio.run(endpoint(user=None, request_body=request_body))

    input_command = _get_input_command(handle_command)
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

    input_command = _get_input_command(handle_command)
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

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.CreateFileForSeqCommand)
    assert input_command.file_content == file_content
    assert input_command.file_format == request_body.file_format
    assert input_command.file_compression == request_body.file_compression


def test_case_type_set_case_type_association_forwards_members(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_set_id = uuid4()
    members: list[casedb_api_case.model.CaseTypeSetMember] = []
    request_body = casedb_api_case.CaseTypeSetCaseTypeUpdateAssociationRequestBody(
        case_type_set_members=members
    )

    asyncio.run(
        _get_endpoint(router, "/case_type_sets/{case_type_set_id}/case_types")(
            user=None,
            case_type_set_id=case_type_set_id,
            request_body=request_body,
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(
        input_command, command.CaseTypeSetCaseTypeUpdateAssociationCommand
    )
    assert input_command.obj_id1 == case_type_set_id
    assert input_command.association_objs == members


def test_col_set_col_association_forwards_members(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    col_set_id = uuid4()
    members: list[casedb_api_case.model.ColSetMember] = []
    request_body = casedb_api_case.ColSetColUpdateAssociationRequestBody(
        col_set_members=members
    )

    asyncio.run(
        _get_endpoint(router, "/col_sets/{col_set_id}/cols")(
            user=None, col_set_id=col_set_id, request_body=request_body
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.ColSetColUpdateAssociationCommand)
    assert input_command.obj_id1 == col_set_id
    assert input_command.association_objs == members


def test_complete_case_type_forwards_case_type_id(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_id = uuid4()

    asyncio.run(
        _get_endpoint(router, "/complete_case_types")(
            user=None, case_type_id=case_type_id
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveCompleteCaseTypeCommand)
    assert input_command.case_type_id == case_type_id


def test_update_case_created_in_data_collection_forwards_fields(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_ids = [uuid4()]
    target_id = uuid4()
    request_body = casedb_api_case.UpdateCaseCreatedInDataCollectionRequestBody(
        case_ids=case_ids,
        target_created_in_data_collection_id=target_id,
    )

    asyncio.run(
        _get_endpoint(router, "/update_case_created_in_data_collection")(
            user=None, request_body=request_body
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.UpdateCaseCreatedInDataCollectionCommand)
    assert input_command.case_ids == case_ids
    assert input_command.target_created_in_data_collection_id == target_id


def test_upload_cases_sets_authenticated_user_on_command(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    user = object()
    upload_command = command.UploadCasesCommand.model_construct()

    asyncio.run(_get_endpoint(router, "/upload/cases")(user=user, cmd=upload_command))

    assert upload_command.user is user
    assert _get_input_command(handle_command) is upload_command


def test_create_case_set_forwards_request_fields(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_set = casedb_api_case.model.CaseSet.model_construct(
        created_in_data_collection_id=uuid4()
    )
    data_collection_ids = {uuid4()}
    case_ids = {uuid4()}
    request_body = casedb_api_case.CreateCaseSetRequestBody.model_construct(
        case_set=case_set,
        data_collection_ids=data_collection_ids,
        case_ids=case_ids,
    )

    asyncio.run(
        _get_endpoint(router, "/create/case_set")(user=None, request_body=request_body)
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.CreateCaseSetCommand)
    assert input_command.case_set is case_set
    assert input_command.data_collection_ids == data_collection_ids
    assert input_command.case_ids == case_ids


@pytest.mark.parametrize(
    ("path", "request_body", "command_type", "ids_field"),
    [
        (
            "/retrieve/case_type_stats",
            casedb_api_case.RetrieveCaseTypeStatsRequestBody.model_construct(
                case_type_ids={uuid4()}, datetime_range_filter=None
            ),
            command.RetrieveCaseTypeStatsCommand,
            "case_type_ids",
        ),
        (
            "/retrieve/case_set_stats",
            casedb_api_case.RetrieveCaseSetStatsRequestBody.model_construct(
                case_set_ids={uuid4()}, datetime_range_filter=None
            ),
            command.RetrieveCaseSetStatsCommand,
            "case_set_ids",
        ),
    ],
)
def test_retrieve_stats_forwards_request_fields(
    registered_case_endpoints: tuple[APIRouter, Mock],
    path: str,
    request_body: Any,
    command_type: type,
    ids_field: str,
) -> None:
    router, handle_command = registered_case_endpoints

    asyncio.run(_get_endpoint(router, path)(user=None, request_body=request_body))

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command_type)
    assert getattr(input_command, ids_field) == getattr(request_body, ids_field)
    assert getattr(input_command, "datetime_range_filter") is None


def test_retrieve_cases_by_query_forwards_query(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_query = casedb_api_case.model.CaseQuery.model_construct()

    asyncio.run(
        _get_endpoint(router, "/retrieve/case_ids_by_query")(
            user=None, request_body=case_query
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveCasesByQueryCommand)
    assert input_command.case_query is case_query


@pytest.mark.parametrize(
    ("path", "command_type"),
    [
        ("/retrieve/cases_by_ids", command.RetrieveCasesByIdCommand),
        ("/retrieve/case_rights", command.RetrieveCaseRightsCommand),
    ],
)
def test_retrieve_cases_or_rights_forwards_ids(
    registered_case_endpoints: tuple[APIRouter, Mock],
    path: str,
    command_type: type,
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_id = uuid4()
    case_ids = [uuid4()]
    request_body = casedb_api_case.RetrieveCasesByIdRequestBody(
        case_type_id=case_type_id, case_ids=case_ids
    )

    asyncio.run(_get_endpoint(router, path)(user=None, request_body=request_body))

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command_type)
    assert getattr(input_command, "case_type_id") == case_type_id
    assert getattr(input_command, "case_ids") == case_ids


def test_retrieve_case_set_rights_forwards_ids(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_set_ids = [uuid4()]

    asyncio.run(
        _get_endpoint(router, "/retrieve/case_set_rights")(
            user=None, request_body=case_set_ids
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveCaseSetRightsCommand)
    assert input_command.case_set_ids == case_set_ids


def test_retrieve_phylogenetic_tree_forwards_parameters(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_id = uuid4()
    distance_col_id = uuid4()
    case_ids = [uuid4()]
    algorithm = next(iter(casedb_api_case.enum.TreeAlgorithmType))
    request_body = casedb_api_case.RetrievePhylogeneticTreeRequestBody(
        case_type_id=case_type_id,
        genetic_distance_col_id=distance_col_id,
        tree_algorithm_code=algorithm,
        case_ids=case_ids,
    )

    asyncio.run(
        _get_endpoint(router, "/calculate/phylogenetic_tree")(
            user=None, request_body=request_body
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrievePhylogeneticTreeByCasesCommand)
    assert input_command.case_type_id == case_type_id
    assert input_command.genetic_distance_col_id == distance_col_id
    assert input_command.tree_algorithm == algorithm
    assert input_command.case_ids == case_ids


def test_retrieve_sequence_distances_forwards_parameters(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_id = uuid4()
    distance_col_id = uuid4()
    case_ids = [uuid4()]
    request_body = casedb_api_case.RetrieveSeqDistancesByCasesRequestBody(
        case_type_id=case_type_id,
        genetic_distance_col_id=distance_col_id,
        case_ids=case_ids,
        filter_other_cases=False,
    )

    asyncio.run(
        _get_endpoint(router, "/retrieve/seq_distances_by_cases")(
            user=None, request_body=request_body
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveSeqDistancesByCasesCommand)
    assert input_command.case_type_id == case_type_id
    assert input_command.genetic_distance_col_id == distance_col_id
    assert input_command.case_ids == case_ids
    assert input_command.filter_other_cases is False


def test_retrieve_similar_cases_forwards_parameters(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_id = uuid4()
    distance_col_id = uuid4()
    case_ids = [uuid4()]
    request_body = casedb_api_case.RetrieveSimilarCasesRequestBody(
        case_type_id=case_type_id,
        genetic_distance_col_id=distance_col_id,
        case_ids=case_ids,
        max_distance=2.5,
    )

    asyncio.run(
        _get_endpoint(router, "/retrieve/similar_cases")(
            user=None, request_body=request_body
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveSimilarCasesCommand)
    assert input_command.case_type_id == case_type_id
    assert input_command.genetic_distance_col_id == distance_col_id
    assert input_command.case_ids == case_ids
    assert input_command.max_distance == 2.5


def test_retrieve_genetic_sequence_fasta_streams_authenticated_result(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    app = handle_command.app
    user = casedb_api_case.model.User.model_construct()
    auth_service = Mock()
    auth_service.get_existing_user_from_token = AsyncMock(return_value=user)
    app.impl.services = {casedb_api_case.enum.ServiceType.AUTH: auth_service}
    app.handle = Mock(return_value=iter([">sample", "ACGT"]))
    app.handle_exception.side_effect = lambda *args: pytest.fail(repr(args[2]))
    case_type_id = uuid4()
    sequence_col_id = uuid4()
    case_ids = [uuid4()]

    response = asyncio.run(
        _get_endpoint(router, "/retrieve/genetic_sequence/fasta")(
            token="token",
            case_type_id=case_type_id,
            genetic_sequence_col_id=sequence_col_id,
            case_ids=case_ids,
            file_name="sequences.fasta",
        )
    )

    input_command = app.handle.call_args.args[0]
    assert isinstance(input_command, command.RetrieveGeneticSequenceFastaByCaseCommand)
    assert input_command.user is user
    assert input_command.case_type_id == case_type_id
    assert input_command.genetic_sequence_col_id == sequence_col_id
    assert input_command.case_ids == case_ids
    assert response.media_type == "application/x-fasta"
    assert response.headers["content-disposition"] == (
        'attachment; filename="sequences.fasta"'
    )


def test_retrieve_genetic_sequence_fasta_delegates_errors(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    app = handle_command.app
    auth_service = Mock()
    auth_service.get_existing_user_from_token = AsyncMock(
        side_effect=ValueError("invalid token")
    )
    app.impl.services = {casedb_api_case.enum.ServiceType.AUTH: auth_service}
    handle_exception = registered_case_endpoints[1].handle_exception
    handle_exception.side_effect = RuntimeError("handled")
    endpoint = _get_endpoint(router, "/retrieve/genetic_sequence/fasta")

    with pytest.raises(RuntimeError, match="handled"):
        asyncio.run(
            endpoint(
                token="token",
                case_type_id=uuid4(),
                genetic_sequence_col_id=uuid4(),
                case_ids=[uuid4()],
                file_name="sequences.fasta",
            )
        )

    handle_exception.assert_called_once()
    assert handle_exception.call_args.args[0] == "d4c2e1b1"
    assert handle_exception.call_args.args[1] is None


@pytest.mark.parametrize(
    ("path", "expected_protocol_type"),
    [
        ("/retrieve/sequencing_protocols", seqdb_enum.ProtocolType.SEQUENCING),
        ("/retrieve/assembly_protocols", seqdb_enum.ProtocolType.ASSEMBLY),
    ],
)
def test_retrieve_protocols_forwards_protocol_type(
    registered_case_endpoints: tuple[APIRouter, Mock],
    path: str,
    expected_protocol_type: seqdb_enum.ProtocolType,
) -> None:
    router, handle_command = registered_case_endpoints

    asyncio.run(_get_endpoint(router, path)(user=None))

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveProtocolsCommand)
    assert input_command.protocol_type is expected_protocol_type


def test_retrieve_is_own_cases_forwards_ids(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, handle_command = registered_case_endpoints
    case_type_id = uuid4()
    case_ids = [uuid4()]
    request_body = casedb_api_case.RetrieveCasesByIdRequestBody(
        case_type_id=case_type_id, case_ids=case_ids
    )

    asyncio.run(
        _get_endpoint(router, "/retrieve/is_own_cases")(
            user=None, request_body=request_body
        )
    )

    input_command = _get_input_command(handle_command)
    assert isinstance(input_command, command.RetrieveIsOwnCasesCommand)
    assert input_command.case_type_id == case_type_id
    assert input_command.case_ids == case_ids


def test_ref_col_validation_rules_returns_schema(
    registered_case_endpoints: tuple[APIRouter, Mock],
) -> None:
    router, _ = registered_case_endpoints

    response = asyncio.run(
        _get_endpoint(router, "/ref_cols/validation_rules")(user=None)
    )

    assert isinstance(response, casedb_api_case.RefColValidationRulesResponseBody)
    assert response.valid_col_types_by_dim_type


def test_ref_col_validation_rules_delegates_construction_error(
    registered_case_endpoints: tuple[APIRouter, Mock], monkeypatch: pytest.MonkeyPatch
) -> None:
    router, handle_command = registered_case_endpoints
    handle_exception = handle_command.handle_exception
    handle_exception.side_effect = RuntimeError("handled")
    monkeypatch.setattr(
        casedb_api_case,
        "RefColValidationRulesResponseBody",
        Mock(side_effect=ValueError("invalid schema")),
    )

    with pytest.raises(RuntimeError, match="handled"):
        asyncio.run(_get_endpoint(router, "/ref_cols/validation_rules")(user=None))

    handle_exception.assert_called_once()
    assert handle_exception.call_args.args[0] == "f2a4b8c6"
