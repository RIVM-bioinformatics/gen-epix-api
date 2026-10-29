from __future__ import annotations

import json
from test.util.mock_compat import Mock, patch
from typing import Any, Callable, ClassVar, cast
from uuid import UUID, uuid4

import httpx
import pytest
from pydantic import Field

from gen_epix.fastapp.client import Client, RetryPolicy
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import (
    CrudOperation,
    EventTiming,
    HttpMethod,
    HttpProtocol,
    StringCasing,
)
from gen_epix.fastapp.exc import AuthException, ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Model, Policy

# Helpers and dummies for testing


class DummyEntity:
    @staticmethod
    def get_name_by_casing(casing: StringCasing, is_plural: bool) -> str:
        return "dummy_models" if is_plural else "dummy_model"


class DummyModel(Model):
    id: UUID | None = None
    name: str | None = None

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="dummy_models",
        table_name="dummy_model",
        persistable=True,
        keys=create_keys({1: "id"}),
    )


class DummyQueryFilter(Model):
    q: str


class DummyCrud(CrudCommand):
    NAME = "DummyCrud"
    MODEL_CLASS = DummyModel

    # Pydantic fields
    operation: CrudOperation
    objs: DummyModel | list[DummyModel] | None = None  # type: ignore[assignment]
    obj_ids: UUID | list[UUID] | None = None  # type: ignore[assignment]
    query_filter: DummyQueryFilter | None = None  # type: ignore[assignment]
    props: dict[str, Any] = Field(default_factory=dict)


class DummyCmd(Command):
    NAME = "DummyCmd"

    def __init__(self) -> None:
        # minimal structure
        pass


class UnsupportedModel:
    # Not a Pydantic model, but needs ENTITY for route generation
    ENTITY: ClassVar[DummyEntity] = DummyEntity()


class UnsupportedCrud(CrudCommand):
    NAME = "UnsupportedCrud"
    MODEL_CLASS = UnsupportedModel  # type: ignore[assignment]

    # Pydantic fields
    operation: CrudOperation
    objs: Any | None = None
    obj_ids: UUID | list[UUID] | None = None  # type: ignore[assignment]
    query_filter: Any | None = None
    props: dict[str, Any] = Field(default_factory=dict)


class FakeResponse:
    def __init__(self, status_code: int = 200, payload: Any = None) -> None:
        self.status_code = status_code
        self._payload = payload
        self.encoding = "utf-8"

    @property
    def content(self) -> bytes:
        return json.dumps(self._payload).encode(self.encoding)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=Mock(),
                response=Mock(status_code=self.status_code),
            )


class FakeClient:
    # Class-level state to be controlled from tests
    next_response: FakeResponse = FakeResponse()
    last_request: dict[str, Any] | None = None
    last_verify: Any | None = None
    last_timeout: Any | None = None

    def __init__(self, verify: Any, timeout: Any) -> None:
        type(self).last_verify = verify
        type(self).last_timeout = timeout

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        return None

    def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> FakeResponse:
        type(self).last_request = {
            "method": "GET",
            "url": url,
            "headers": headers,
            "params": params,
        }
        return type(self).next_response

    def post(
        self, url: str, json: Any = None, headers: dict[str, str] | None = None
    ) -> FakeResponse:
        type(self).last_request = {
            "method": "POST",
            "url": url,
            "headers": headers,
            "json": json,
        }
        return type(self).next_response

    def put(
        self, url: str, json: Any = None, headers: dict[str, str] | None = None
    ) -> FakeResponse:
        type(self).last_request = {
            "method": "PUT",
            "url": url,
            "headers": headers,
            "json": json,
        }
        return type(self).next_response

    def delete(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> FakeResponse:
        type(self).last_request = {
            "method": "DELETE",
            "url": url,
            "headers": headers,
            "params": params,
        }
        return type(self).next_response


def set_fake_response(payload: Any, status_code: int = 200) -> None:
    FakeClient.next_response = FakeResponse(status_code=status_code, payload=payload)
    FakeClient.last_request = None


class BaseClientTestCase:
    def setup_method(self) -> None:
        # Patch App.__init__ to avoid side-effects and set required attributes
        def _fake_app_init(self: Any, domain: Domain, **kwargs: Any) -> None:
            setattr(self, "_domain", domain)
            setattr(self, "_logger", None)  # ensure __del__ can safely access

        self._app_init_patcher = patch(
            "gen_epix.fastapp.client.App.__init__", _fake_app_init
        )
        self._app_init_patcher.start()

        # Patch create_ssl_context to predictable value
        self._ssl_patcher = patch(
            "gen_epix.fastapp.client.create_ssl_context", return_value="SSLCTX"
        )
        self._ssl_patcher.start()

        # Domain stub
        self.domain: Domain = cast(Domain, Mock(spec=Domain))
        self.domain.crud_commands = []  # type: ignore[assignment,misc]

        # Instance under test
        self.app = Client(
            domain=self.domain,
            host="example.org",
            port=8000,
            protocol=HttpProtocol.HTTP,
            default_route_prefix="/",
            default_headers={"Content-Type": "application/json", "X-Test": "1"},
            add_generated_crud_route_handlers=False,
        )

    def teardown_method(self) -> None:
        self._app_init_patcher.stop()
        self._ssl_patcher.stop()

    # Utilities
    def register_route_for(
        self, cmd_class: type[Command], route: str = "endpoint"
    ) -> str:
        return self.app.register_route(cmd_class, route, add_host=True, add_prefix=True)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestInitAndProperties(BaseClientTestCase):

    def test_protocol_property_accepts_enum_and_string(self) -> None:
        # Protocol as enum
        app_enum = Client(
            domain=self.domain,
            host="example.org",
            port=8000,
            protocol=HttpProtocol.HTTPS,
            add_generated_crud_route_handlers=False,
        )
        assert app_enum.protocol == HttpProtocol.HTTPS

        # Protocol as string (lowercase)
        app_str = Client(
            domain=self.domain,
            host="example.org",
            port=8000,
            protocol="https",
            add_generated_crud_route_handlers=False,
        )
        assert app_str.protocol == HttpProtocol.HTTPS

    def test_properties_and_host_url(self) -> None:
        # Create input
        # ... already created in setup_method ...

        # Set up mocks: none

        # Execute
        host: str = self.app.host
        port: int | None = self.app.port
        protocol: HttpProtocol | str = self.app._protocol
        host_url: str = self.app.host_url
        ssl_context: Any = self.app.ssl_context

        # Verify
        assert host == "example.org"
        assert port == 8000
        assert protocol == HttpProtocol.HTTP
        assert host_url == "http://example.org:8000"
        assert ssl_context == False

        # With no port
        other = Client(
            self.domain,
            "example.org",
            None,
            protocol=HttpProtocol.HTTPS,
            add_generated_crud_route_handlers=False,
        )
        assert other.host_url == "https://example.org"

    def test_register_policy_and_unregister_policy_raise(self) -> None:
        # Create input
        policy: Policy = cast(Policy, Mock(spec=Policy))

        # Set up mocks: none

        # Execute/Verify
        with pytest.raises(ServiceException):
            self.app.register_policy(DummyCmd, policy, timing=EventTiming.BEFORE)
        with pytest.raises(ServiceException):
            self.app.unregister_policy(DummyCmd, policy, timing=EventTiming.BEFORE)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestRouteRegistration(BaseClientTestCase):
    def test_register_route_and_get_route(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute
        route: str = self.register_route_for(DummyCmd, "endpoint")

        # Verify
        assert route == "http://example.org:8000/endpoint"
        got = self.app.get_route(cmd)
        assert got == route

    def test_register_route_without_host_or_prefix(self) -> None:
        # Create input
        # Set up mocks: none

        # Execute
        route: str = self.app.register_route(
            DummyCmd, "endpoint", add_host=False, add_prefix=False
        )

        # Verify
        assert route == "/endpoint"
        assert self.app.get_route(DummyCmd()) == "/endpoint"

    def test_register_route_preserves_an_existing_leading_slash(self) -> None:
        route = self.app.register_route(
            DummyCmd, "/endpoint", add_host=False, add_prefix=False
        )

        assert route == "/endpoint"

    def test_register_route_duplicate_raises(self) -> None:
        # Create input
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks: none

        # Execute/Verify
        with pytest.raises(ServiceException):
            self.register_route_for(DummyCmd, "endpoint2")

    def test_unregister_route_and_missing(self) -> None:
        # Create input
        # Set up mocks: none

        # Execute/Verify missing
        with pytest.raises(ServiceException):
            self.app.unregister_route(DummyCmd)

        # Execute present
        self.register_route_for(DummyCmd, "endpoint")
        self.app.unregister_route(DummyCmd)

        # Verify removed
        with pytest.raises(NotImplementedError):
            self.app.get_route(DummyCmd())

    def test_get_route_not_registered_raises(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute/Verify
        with pytest.raises(NotImplementedError):
            self.app.get_route(cmd)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestHeadersAndApplyHandler(BaseClientTestCase):
    def test_get_headers_returns_defaults(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute
        headers = self.app.get_headers(cmd)

        # Verify
        assert headers == {"Content-Type": "application/json", "X-Test": "1"}

    def test_apply_handler_no_route_raises(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute/Verify
        with pytest.raises(NotImplementedError):
            self.app.apply_handler(cmd, lambda c: None)

    def test_apply_handler_success(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        handler: Callable[[Command], Any] = lambda c: "ok"

        # Execute
        retval = self.app.apply_handler(cmd, handler)

        # Verify
        assert retval == "ok"

    def test_apply_handler_wraps_request_error(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        def _raise(_: Command) -> None:
            raise httpx.RequestError("boom", request=Mock())

        # Execute/Verify
        with pytest.raises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        assert "HTTP request error when handling remote command DummyCmd" in str(
            e.value
        )

    def test_apply_handler_wraps_http_status_error_with_status(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        def _raise(_: Command) -> None:
            raise httpx.HTTPStatusError(
                "boom", request=Mock(), response=Mock(status_code=418)
            )

        # Execute/Verify
        with pytest.raises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        assert "HTTP status 418 error when handling remote command DummyCmd" in str(
            e.value
        )

    def test_apply_handler_wraps_http_status_error_without_response(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        def _raise(_: Command) -> None:
            err = httpx.HTTPStatusError(
                "boom", request=Mock(), response=Mock(status_code=500)
            )
            err.response = None  # type: ignore[assignment]
            raise err

        # Execute/Verify
        with pytest.raises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        assert "HTTP status unknown error when handling remote command DummyCmd" in str(
            e.value
        )

    def test_apply_handler_wraps_generic_exception(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        def _raise(_: Command) -> None:
            raise RuntimeError("oops")

        # Execute/Verify
        with pytest.raises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        assert "Error when handling remote command DummyCmd" in str(e.value)


class TestRequestAndStream(BaseClientTestCase):
    def test_request_serializes_models_and_handles_empty_responses(
        self,
    ) -> None:
        cmd = DummyCmd()
        self.register_route_for(DummyCmd)
        requests: list[httpx.Request] = []
        model_id = uuid4()

        def respond(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.url.path.endswith("/empty"):
                return httpx.Response(204, request=request)
            return httpx.Response(200, json={"accepted": True}, request=request)

        transport = httpx.MockTransport(respond)

        def make_client(command: Command, timeout: float | None = None) -> httpx.Client:
            return httpx.Client(transport=transport)

        with patch.object(self.app, "get_client", side_effect=make_client):
            result = self.app.request(
                cmd,
                HttpMethod.POST,
                model=DummyModel(id=model_id, name="ignored"),
                exclude={"name"},
            )
            empty = self.app.request(
                cmd, HttpMethod.GET, route="http://example.org/empty"
            )

        assert result == {"accepted": True}
        assert empty is None
        assert requests[0].url.path == "/endpoint"
        assert json.loads(requests[0].content) == {"id": str(model_id)}
        assert requests[0].headers["X-Test"] == "1"
        assert requests[1].url.path == "/empty"

    def test_set_timeout_validates_and_overrides_the_default(self) -> None:
        assert self.app.get_timeout(DummyCmd) == self.app.DEFAULT_REQUEST_TIMEOUT
        self.app.set_timeout(DummyCmd, 2.5)
        assert self.app.get_timeout(DummyCmd) == 2.5

        for timeout in (0, -1):
            with pytest.raises(ServiceException, match="Timeout must be a positive"):
                self.app.set_timeout(DummyCmd, timeout)

    def test_request_rejects_two_body_sources(self) -> None:
        with pytest.raises(ValueError, match="both a Pydantic model and a JSON body"):
            self.app.request(
                DummyCmd(),
                HttpMethod.POST,
                model=DummyModel(name="model"),
                json_body={"name": "json"},
            )

    def test_stream_sends_form_data_without_default_headers(self) -> None:
        cmd = DummyCmd()
        self.register_route_for(DummyCmd)
        requests: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, content=b"hello world", request=request)

        transport = httpx.MockTransport(respond)

        def make_client(command: Command, timeout: float | None = None) -> httpx.Client:
            return httpx.Client(transport=transport)

        with patch.object(self.app, "get_client", side_effect=make_client):
            chunks = list(
                self.app.stream(
                    cmd,
                    HttpMethod.POST,
                    form_data={"code": "abc"},
                    params={"page": 1},
                )
            )

        assert "".join(chunks) == "hello world"
        assert requests[0].content == b"code=abc"
        assert "X-Test" not in requests[0].headers

    def test_stream_uses_default_headers_without_form_data(self) -> None:
        cmd = DummyCmd()
        self.register_route_for(DummyCmd)
        requests: list[httpx.Request] = []

        def respond(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, content=b"stream", request=request)

        transport = httpx.MockTransport(respond)

        def make_client(command: Command, timeout: float | None = None) -> httpx.Client:
            return httpx.Client(transport=transport)

        with patch.object(self.app, "get_client", side_effect=make_client):
            chunks = list(
                self.app.stream(
                    cmd, HttpMethod.POST, model=DummyModel(name="stream-body")
                )
            )

        assert "".join(chunks) == "stream"
        assert requests[0].headers["X-Test"] == "1"
        assert json.loads(requests[0].content) == {
            "id": None,
            "name": "stream-body",
        }

    def test_stream_rejects_two_body_sources(self) -> None:
        with pytest.raises(ValueError, match="both a Pydantic model and a JSON body"):
            list(
                self.app.stream(
                    DummyCmd(),
                    HttpMethod.POST,
                    model=DummyModel(name="model"),
                    json_body={"name": "json"},
                )
            )


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestGeneratedCrudRoutes(BaseClientTestCase):
    def test_register_generated_crud_route_builds_path(self) -> None:
        # Create input
        # Set up mocks: none

        # Execute
        route = self.app.register_generated_crud_route(DummyCrud)

        # Verify
        assert route == "http://example.org:8000/dummy_models"

    def test_create_generated_crud_handler_all_operations(self) -> None:
        # Create input
        base_route = "http://example.org:8000/dummy_models"
        handler = self.app.create_generated_crud_route_handler(DummyCrud, base_route)

        # Set up mocks: patch httpx.Client with FakeClient
        with patch("gen_epix.fastapp.client.httpx.Client", FakeClient):
            # Ensure ssl verify is passed
            set_fake_response(payload=[], status_code=200)
            cmd = DummyCrud(operation=CrudOperation.READ_ALL)
            retval = handler(cmd)
            assert isinstance(retval, list)
            assert FakeClient.last_request == {
                "method": "GET",
                "url": base_route,
                "headers": self.app.get_headers(cmd),
                "params": None,
            }
            assert FakeClient.last_verify == self.app.ssl_context

            # READ_ALL with query filter (without ids)
            qf = DummyQueryFilter(q="x")
            payload = [{"id": str(uuid4()), "name": "a"}]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(
                operation=CrudOperation.READ_ALL,
                query_filter=qf,
                return_id=False,
            )
            retval = handler(cmd)
            assert [DummyModel(**payload[0])] == retval  # type: ignore[arg-type]
            assert FakeClient.last_request["method"] == "POST"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith("/query")  # type: ignore[index]
            assert FakeClient.last_request["headers"] == self.app.get_headers(cmd)

            # READ_ALL with query filter and ids suffix
            expected_ids = [uuid4()]
            set_fake_response(payload=[str(expected_ids[0])], status_code=200)
            cmd = DummyCrud(
                operation=CrudOperation.READ_ALL,
                query_filter=qf,
                return_id=True,
            )
            retval = handler(cmd)
            assert retval == expected_ids
            assert FakeClient.last_request["url"].endswith("/query/ids")  # type: ignore[index]

            # READ_SOME
            ids = [uuid4(), uuid4()]
            payload = [
                {"id": str(ids[0]), "name": "x"},
                {"id": str(ids[1]), "name": "y"},
            ]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(operation=CrudOperation.READ_SOME, obj_ids=ids)
            retval = handler(cmd)
            assert [DummyModel(**payload[0]), DummyModel(**payload[1])] == retval
            assert FakeClient.last_request["method"] == "GET"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith("/batch")  # type: ignore[index]
            assert "ids" in FakeClient.last_request["params"]  # type: ignore[index]
            assert json.loads(FakeClient.last_request["params"]["ids"]) == [
                str(x) for x in ids
            ]  # type: ignore[index]

            # READ_ONE
            one_id = uuid4()
            payload = {"id": str(one_id), "name": "z"}  # type: ignore[assignment]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(operation=CrudOperation.READ_ONE, obj_ids=one_id)
            retval = handler(cmd)
            assert DummyModel(**payload) == retval  # type: ignore[arg-type]
            assert FakeClient.last_request["method"] == "GET"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith(f"/{one_id}")  # type: ignore[index]

            # CREATE_ONE
            new_obj = DummyModel(id=uuid4(), name="n1")
            set_fake_response(
                payload=json.loads(new_obj.model_dump_json()), status_code=201
            )
            cmd = DummyCrud(operation=CrudOperation.CREATE_ONE, objs=new_obj)
            retval = handler(cmd)
            assert new_obj == retval
            assert FakeClient.last_request["method"] == "POST"  # type: ignore[index]
            assert FakeClient.last_request["url"] == base_route  # type: ignore[index]
            assert FakeClient.last_request["json"] == json.loads(
                new_obj.model_dump_json()
            )

            # CREATE_SOME
            new_objs = [
                DummyModel(id=uuid4(), name="n2"),
                DummyModel(id=uuid4(), name="n3"),
            ]
            set_fake_response(
                payload=[json.loads(o.model_dump_json()) for o in new_objs],
                status_code=201,
            )
            cmd = DummyCrud(operation=CrudOperation.CREATE_SOME, objs=new_objs)
            retval = handler(cmd)
            assert new_objs == retval
            assert FakeClient.last_request["method"] == "POST"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith("/batch")  # type: ignore[index]

            # UPDATE_ONE
            upd = DummyModel(id=uuid4(), name="u1")
            set_fake_response(
                payload=json.loads(upd.model_dump_json()), status_code=200
            )
            cmd = DummyCrud(operation=CrudOperation.UPDATE_ONE, objs=upd)
            retval = handler(cmd)
            assert upd == retval
            assert FakeClient.last_request["method"] == "PUT"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith(f"/{upd.id}")  # type: ignore[index]

            # UPDATE_SOME
            upds = [
                DummyModel(id=uuid4(), name="u2"),
                DummyModel(id=uuid4(), name="u3"),
            ]
            set_fake_response(
                payload=[json.loads(o.model_dump_json()) for o in upds], status_code=200
            )
            cmd = DummyCrud(operation=CrudOperation.UPDATE_SOME, objs=upds)
            retval = handler(cmd)
            assert upds == retval
            assert FakeClient.last_request["method"] == "PUT"  # type: ignore[index]
            assert FakeClient.last_request["url"] == f"{base_route}/batch"  # type: ignore[index]

            # DELETE_ONE
            del_id = uuid4()
            set_fake_response(payload=str(del_id), status_code=200)
            cmd = DummyCrud(operation=CrudOperation.DELETE_ONE, obj_ids=del_id)
            retval = handler(cmd)
            assert del_id == retval
            assert FakeClient.last_request["method"] == "DELETE"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith(f"/{del_id}")  # type: ignore[index]

            # DELETE_SOME
            del_ids = [uuid4(), uuid4()]
            set_fake_response(payload=[str(x) for x in del_ids], status_code=200)
            cmd = DummyCrud(operation=CrudOperation.DELETE_SOME, obj_ids=del_ids)
            retval = handler(cmd)
            assert del_ids == retval
            assert FakeClient.last_request["method"] == "DELETE"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith("/batch")  # type: ignore[index]
            assert "ids" in FakeClient.last_request["params"]  # type: ignore[index]
            assert json.loads(FakeClient.last_request["params"]["ids"]) == [
                str(x) for x in del_ids
            ]  # type: ignore[index]

            # Non-200/201 status returns None
            set_fake_response(payload={"ignored": True}, status_code=204)
            cmd = DummyCrud(operation=CrudOperation.READ_ONE, obj_ids=uuid4())
            retval = handler(cmd)
            assert retval is None

    def test_create_generated_crud_handler_exists_operations(self) -> None:
        # Create input
        base_route = "http://example.org:8000/dummy_models"
        handler = self.app.create_generated_crud_route_handler(DummyCrud, base_route)
        obj_ids = [uuid4(), uuid4(), uuid4()]

        # Set up mocks
        with patch("gen_epix.fastapp.client.httpx.Client", FakeClient):
            # EXISTS_SOME
            set_fake_response(payload=[True, False, True], status_code=200)
            cmd = DummyCrud(operation=CrudOperation.EXISTS_SOME, obj_ids=obj_ids)
            retval = handler(cmd)

            # Verify
            assert retval == [True, False, True]
            assert FakeClient.last_request["method"] == "GET"  # type: ignore[index]
            assert FakeClient.last_request["url"].endswith("/exists")  # type: ignore[index]
            assert json.loads(FakeClient.last_request["params"]["ids"]) == [  # type: ignore[index]
                str(obj_id) for obj_id in obj_ids
            ]

            # EXISTS_ONE
            set_fake_response(payload=True, status_code=200)
            cmd = DummyCrud(operation=CrudOperation.EXISTS_ONE, obj_ids=obj_ids[1])
            retval = handler(cmd)
            assert retval

    def test_exists_some_sends_mixed_id_types_to_exists_route(self) -> None:
        # Create input
        base_route = "http://example.org:8000/dummy_models"
        handler = self.app.create_generated_crud_route_handler(DummyCrud, base_route)
        uuid_id = uuid4()
        legacy_id = "legacy-id"
        cmd = DummyCrud.model_construct(
            operation=CrudOperation.EXISTS_SOME,
            obj_ids=[uuid_id, legacy_id],
            objs=None,
            query_filter=None,
            props={},
        )

        # Set up mocks
        with patch("gen_epix.fastapp.client.httpx.Client", FakeClient):
            set_fake_response(payload=[True, False], status_code=200)
            retval = handler(cmd)

        # Verify
        assert retval == [True, False]
        assert FakeClient.last_request["method"] == "GET"  # type: ignore[index]
        assert FakeClient.last_request["url"].endswith("/exists")  # type: ignore[index]
        assert json.loads(FakeClient.last_request["params"]["ids"]) == [  # type: ignore[index]
            str(uuid_id),
            legacy_id,
        ]

    def test_generated_handler_unsupported_return_type_raises(self) -> None:
        # Create input
        base_route = "http://example.org:8000/dummy_models"
        handler = self.app.create_generated_crud_route_handler(
            UnsupportedCrud, base_route
        )

        # Set up mocks
        with patch("gen_epix.fastapp.client.httpx.Client", FakeClient):
            set_fake_response(payload={"something": "x"}, status_code=200)
            cmd = UnsupportedCrud(operation=CrudOperation.READ_ONE, obj_ids=uuid4())

            # Execute/Verify
            with pytest.raises(NotImplementedError):
                handler(cmd)

    def test_generated_handler_rejects_unknown_operation(self) -> None:
        handler = self.app.create_generated_crud_route_handler(
            DummyCrud, "http://example.org:8000/dummy_models"
        )
        cmd = DummyCrud.model_construct(
            operation="unsupported",
            objs=None,
            obj_ids=None,
            query_filter=None,
            props={},
            return_id=False,
        )

        with patch("gen_epix.fastapp.client.httpx.Client", FakeClient):
            with pytest.raises(AssertionError, match="Unsupported operation"):
                handler(cmd)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestAutoRegistration(BaseClientTestCase):
    def test_init_auto_registers_handlers_for_domain_crud_commands(self) -> None:
        # Create input
        domain: Domain = cast(Domain, Mock(spec=Domain))
        domain.crud_commands = [DummyCrud]  # type: ignore[misc,assignment]

        # Set up mocks
        with (
            patch.object(
                Client, "register_generated_crud_route", return_value="/dummy_models"
            ) as reg_route,
            patch.object(Client, "register_handler", return_value=None) as reg_handler,
        ):
            app = Client(
                domain=domain,
                host="example.org",
                port=8000,
                protocol=HttpProtocol.HTTP,
                add_generated_crud_route_handlers=True,
            )

        # Execute: none

        # Verify
        reg_route.assert_called_once_with(DummyCrud)
        assert reg_handler.call_count == 1
        args, kwargs = reg_handler.call_args
        assert args[0] is DummyCrud
        assert callable(args[1])
        # Also verify host_url constructed
        assert app.host_url == "http://example.org:8000"


class RetryCommand(Command):
    NAME = "RetryCommand"


RETRY_POLICY = RetryPolicy(
    retryable_status_codes=frozenset({404, 429, 500, 502, 503, 504}),
    wait_schedule=(1, 2, 3),
)


def _status_error(status: int) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "http://example.org/x")
    response = httpx.Response(status, request=request)
    return httpx.HTTPStatusError("boom", request=request, response=response)


def _make_retry_client(
    handler: Callable[[Command], Any], retry_policy: RetryPolicy | None
) -> Client:
    client = Client(
        Domain("retry-test"),
        "example.org",
        8000,
        protocol=HttpProtocol.HTTP,
        retry_policy=retry_policy,
        add_generated_crud_route_handlers=False,
    )
    client.register_route(RetryCommand, "/retry")
    client.register_handler(RetryCommand, handler)
    return client


class Flaky:
    """Handler raising configured errors in order before succeeding."""

    def __init__(self, *errors: BaseException) -> None:
        self.errors = list(errors)
        self.calls = 0

    def __call__(self, cmd: Command) -> str:
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return "ok"


@pytest.fixture
def retry_sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record retry delays without sleeping."""
    recorded: list[float] = []
    monkeypatch.setattr("tenacity.nap.time.sleep", recorded.append)
    return recorded


class TestRetryPolicy:
    @pytest.mark.parametrize("status", [401, 403])
    def test_rejects_auth_status_codes(self, status: int) -> None:
        with pytest.raises(ValueError):
            RetryPolicy(frozenset({500, status}), (1,))

    def test_classifies_network_and_listed_status(self) -> None:
        assert RETRY_POLICY.is_retryable(httpx.ConnectError("x"))
        assert RETRY_POLICY.is_retryable(httpx.ReadTimeout("x"))
        assert RETRY_POLICY.is_retryable(_status_error(503))
        assert not RETRY_POLICY.is_retryable(ValueError("x"))

    def test_status_from_message_and_cause(self) -> None:
        error = ServiceException("11111111", "HTTP status 502 error")
        assert RetryPolicy.get_remote_http_status(error) == 502

        error = ServiceException("11111111", "no status here")
        error.__cause__ = _status_error(503)
        assert RetryPolicy.get_remote_http_status(error) == 503

    def test_status_fallback_and_non_http(self) -> None:
        assert (
            RetryPolicy.get_remote_http_status(ServiceException("11111111", "x")) == 500
        )
        assert RetryPolicy.get_remote_http_status(_status_error(404)) == 404
        assert RetryPolicy.get_remote_http_status(ValueError("x")) is None

        cause = _status_error(503)
        cause.response = None  # type: ignore[assignment]
        wrapped = ServiceException("11111111", "no status")
        wrapped.__cause__ = cause
        assert RetryPolicy.get_remote_http_status(wrapped) == 500

    def test_network_error_traverses_nested_causes(self) -> None:
        inner = ServiceException("11111111", "inner")
        inner.__cause__ = httpx.ConnectError("network")
        outer = ServiceException("11111111", "outer")
        outer.__cause__ = inner

        assert RetryPolicy(frozenset(), (1,)).is_retryable(outer)

    def test_auth_failures_are_never_retryable(self) -> None:
        error = ServiceException("11111111", "HTTP status 401 error")
        assert not RetryPolicy.is_retryable_status(error, frozenset({401, 500}))
        assert not RetryPolicy.is_retryable_status(
            AuthException("11111111", "x"), {500}
        )


class TestClientRetry:
    def test_retry_policy_property_returns_configured_policy(self) -> None:
        client = _make_retry_client(lambda cmd: "ok", RETRY_POLICY)

        assert client.retry_policy is RETRY_POLICY

    def test_no_policy_means_no_retry(self, retry_sleeps: list[float]) -> None:
        handler = Flaky(_status_error(503), _status_error(503))
        client = _make_retry_client(handler, None)

        with pytest.raises(ServiceException):
            client.handle(RetryCommand())

        assert handler.calls == 1
        assert retry_sleeps == []

    def test_retries_listed_status_then_succeeds(
        self, retry_sleeps: list[float]
    ) -> None:
        handler = Flaky(_status_error(503), _status_error(404))
        client = _make_retry_client(handler, RETRY_POLICY)

        assert client.handle(RetryCommand()) == "ok"

        assert handler.calls == 3
        assert retry_sleeps == [1, 2]

    def test_exhausted_attempts_reraise_last_error(
        self, retry_sleeps: list[float]
    ) -> None:
        handler = Flaky(*[_status_error(502) for _ in range(10)])
        client = _make_retry_client(handler, RETRY_POLICY)

        with pytest.raises(ServiceException, match="HTTP status 502"):
            client.handle(RetryCommand())

        assert handler.calls == len(RETRY_POLICY.wait_schedule) + 1
        assert retry_sleeps == [1, 2, 3]

    def test_unlisted_status_is_not_retried(self, retry_sleeps: list[float]) -> None:
        handler = Flaky(_status_error(400))
        client = _make_retry_client(handler, RETRY_POLICY)

        with pytest.raises(ServiceException):
            client.handle(RetryCommand())

        assert handler.calls == 1
        assert retry_sleeps == []

    def test_network_errors_are_retried(self, retry_sleeps: list[float]) -> None:
        handler = Flaky(httpx.ReadTimeout("t"), httpx.ConnectError("c"))
        client = _make_retry_client(handler, RetryPolicy(frozenset(), (5, 5)))

        assert client.handle(RetryCommand()) == "ok"

        assert handler.calls == 3
        assert retry_sleeps == [5, 5]

    @pytest.mark.parametrize("status", [401, 403])
    def test_auth_status_is_not_retried(
        self, status: int, retry_sleeps: list[float]
    ) -> None:
        handler = Flaky(_status_error(status))
        client = _make_retry_client(handler, RETRY_POLICY)

        with pytest.raises(ServiceException):
            client.handle(RetryCommand())

        assert handler.calls == 1
        assert retry_sleeps == []
