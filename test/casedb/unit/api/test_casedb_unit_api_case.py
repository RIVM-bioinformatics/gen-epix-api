import asyncio
from test.util.mock_compat import Mock
from uuid import uuid4

from fastapi import APIRouter

from gen_epix.casedb.api import case as casedb_api_case
from gen_epix.casedb.domain import command


def test_retrieve_case_cohort_links_forwards_include_missing(monkeypatch) -> None:
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
    endpoint = next(
        route.endpoint
        for route in router.routes
        if getattr(route, "path", None) == "/retrieve/case_cohort_links_by_case_type"
    )
    request_body = casedb_api_case.RetrieveCaseCohortLinksByCaseTypeRequestBody(
        case_type_id=uuid4(), include_missing=True
    )

    asyncio.run(endpoint(user=None, request_body=request_body))

    input_command = handle_command.call_args.kwargs["input_command"]
    assert isinstance(input_command, command.RetrieveCaseCohortLinksByCaseTypeCommand)
    assert input_command.include_missing is True
