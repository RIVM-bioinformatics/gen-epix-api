import asyncio
from test.util.mock_compat import Mock, patch
from typing import NoReturn
from uuid import UUID, uuid4

import pytest
from fastapi import APIRouter
from pydantic import ValidationError

from gen_epix.casedb.api import ontology as ontology_module
from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.domain.literal import MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH

ENDPOINT_PATH = "/diseases/{disease_id}/etiological_agents"


@pytest.fixture(name="app")
def app_fixture() -> Mock:
    app = Mock()
    app.impl.registered_user_dependency = str
    return app


@pytest.fixture(name="handle_exception")
def handle_exception_fixture() -> Mock:
    def _raise(_code: str, _user: object, exception: Exception) -> NoReturn:
        raise exception

    # Real handlers never return (NoReturn), so surface the original error.
    return Mock(side_effect=_raise)


@pytest.fixture(name="generator_cls")
def generator_cls_fixture():
    with patch(f"{ontology_module.__name__}.CrudEndpointGenerator") as generator_cls:
        yield generator_cls


@pytest.fixture(name="router")
def router_fixture() -> APIRouter:
    return APIRouter()


@pytest.fixture(name="user")
def user_fixture() -> model.User:
    return model.User(
        id=uuid4(),
        key="user@example.org",
        email="user@example.org",
        roles={enum.Role.APP_ADMIN},
        organization_id=uuid4(),
        is_active=True,
    )


def _make_etiology(disease_id: UUID | None = None) -> model.Etiology:
    return model.Etiology(
        disease_id=disease_id or uuid4(), etiological_agent_id=uuid4()
    )


def _get_route(router: APIRouter):
    return next(r for r in router.routes if getattr(r, "path", None) == ENDPOINT_PATH)


def test_request_body_accepts_etiologies() -> None:
    etiologies = [_make_etiology(), _make_etiology()]

    body = ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
        etiologies=etiologies
    )

    assert body.etiologies == etiologies


def test_request_body_accepts_empty_list() -> None:
    body = ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
        etiologies=[]
    )

    assert body.etiologies == []


def test_request_body_requires_etiologies() -> None:
    with pytest.raises(ValidationError):
        ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody()


def test_request_body_rejects_malformed_item() -> None:
    with pytest.raises(ValidationError):
        ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
            etiologies=[{"disease_id": "not-a-uuid"}]
        )


@pytest.mark.parametrize(
    "size, valid",
    [
        (MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH, True),
        (MAX_REQUEST_BODY_ITERABLE_FIELD_LENGTH + 1, False),
    ],
    ids=["at-limit", "above-limit"],
)
def test_request_body_enforces_max_length(size: int, valid: bool) -> None:
    etiology = _make_etiology()
    etiologies = [etiology] * size

    if valid:
        body = ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
            etiologies=etiologies
        )
        assert len(body.etiologies) == size
    else:
        with pytest.raises(ValidationError):
            ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
                etiologies=etiologies
            )


def test_create_ontology_endpoints_requires_exception_handler(
    app: Mock, router: APIRouter, generator_cls: Mock
) -> None:
    with pytest.raises(AssertionError):
        ontology_module.create_ontology_endpoints(router, app, None)

    assert not router.routes
    generator_cls.generate_endpoints.assert_not_called()


@pytest.mark.usefixtures("generator_cls")
def test_create_ontology_endpoints_registers_put_route(
    app: Mock, router: APIRouter, handle_exception: Mock
) -> None:
    ontology_module.create_ontology_endpoints(router, app, handle_exception)

    route = _get_route(router)
    assert route.methods == {"PUT"}
    assert route.operation_id == "diseases__put__etiological_agents"
    assert route.name == "Disease_EtiologicalAgent"
    # FastAPI cleans the docstring when building the description.
    expected = command.DiseaseEtiologicalAgentUpdateAssociationCommand.__doc__
    assert route.description == expected.strip()


def test_create_ontology_endpoints_generates_ontology_crud_endpoints(
    app: Mock, router: APIRouter, handle_exception: Mock, generator_cls: Mock
) -> None:
    endpoint_sets = Mock()
    generator_cls.create_crud_endpoint_set_for_domain.return_value = endpoint_sets

    ontology_module.create_ontology_endpoints(
        router, app, handle_exception, unused_option=True
    )

    generator_cls.create_crud_endpoint_set_for_domain.assert_called_once_with(
        app,
        service_type=enum.ServiceType.ONTOLOGY,
        user_dependency=str,
    )
    generator_cls.generate_endpoints.assert_called_once_with(
        router, endpoint_sets, handle_exception
    )


@pytest.mark.usefixtures("generator_cls")
def test_put_endpoint_handles_command_and_returns_result(
    app: Mock, router: APIRouter, handle_exception: Mock, user: model.User
) -> None:
    disease_id: UUID = uuid4()
    etiologies = [_make_etiology(disease_id), _make_etiology(disease_id)]
    app.handle.return_value = etiologies
    ontology_module.create_ontology_endpoints(router, app, handle_exception)
    endpoint = _get_route(router).endpoint
    request_body = ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
        etiologies=etiologies
    )

    result = asyncio.run(
        endpoint(user=user, disease_id=disease_id, request_body=request_body)
    )

    assert result == etiologies
    cmd = app.handle.call_args.args[0]
    assert isinstance(cmd, command.DiseaseEtiologicalAgentUpdateAssociationCommand)
    assert cmd.user is user
    assert cmd.obj_id1 == disease_id
    assert cmd.association_objs == etiologies
    handle_exception.assert_not_called()


@pytest.mark.usefixtures("generator_cls")
def test_put_endpoint_delegates_exceptions_to_handler(
    app: Mock, router: APIRouter, user: model.User
) -> None:
    error = RuntimeError("boom")
    app.handle.side_effect = error

    class Handled(Exception):
        """Marker raised by the mocked exception handler."""

    handle_exception = Mock(side_effect=Handled)
    ontology_module.create_ontology_endpoints(router, app, handle_exception)
    endpoint = _get_route(router).endpoint
    request_body = ontology_module.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
        etiologies=[]
    )

    with pytest.raises(Handled):
        asyncio.run(endpoint(user=user, disease_id=uuid4(), request_body=request_body))

    handle_exception.assert_called_once_with("d5459ee4", user, error)
