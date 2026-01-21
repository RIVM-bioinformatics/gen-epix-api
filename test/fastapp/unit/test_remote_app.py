from __future__ import annotations

import json
from typing import Any, Callable, ClassVar, cast
from unittest import TestCase
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

import httpx
from pydantic import Field

from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import CrudOperation, EventTiming, HttpProtocol, StringCasing
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Model, Policy
from gen_epix.fastapp.remote_app import RemoteApp

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

    def __init__(self, verify: Any) -> None:
        type(self).last_verify = verify

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


class BaseRemoteAppTestCase(TestCase):
    def setUp(self) -> None:
        # Patch App.__init__ to avoid side-effects and set required attributes
        def _fake_app_init(self: Any, domain: Domain, **kwargs: Any) -> None:
            setattr(self, "_domain", domain)
            setattr(self, "_logger", None)  # ensure __del__ can safely access

        self._app_init_patcher = patch(
            "gen_epix.fastapp.remote_app.App.__init__", _fake_app_init
        )
        self._app_init_patcher.start()
        self.addCleanup(self._app_init_patcher.stop)

        # Patch create_ssl_context to predictable value
        self._ssl_patcher = patch(
            "gen_epix.fastapp.remote_app.create_ssl_context", return_value="SSLCTX"
        )
        self._ssl_patcher.start()
        self.addCleanup(self._ssl_patcher.stop)

        # Domain stub
        self.domain: Domain = cast(Domain, Mock(spec=Domain))
        self.domain.crud_commands = []  # type: ignore[assignment,misc]

        # Instance under test
        self.app = RemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            protocol=HttpProtocol.HTTP,
            default_route_prefix="/",
            default_headers={"Content-Type": "application/json", "X-Test": "1"},
            add_generated_crud_route_handlers=False,
        )

    # Utilities
    def register_route_for(
        self, cmd_class: type[Command], route: str = "endpoint"
    ) -> str:
        return self.app.register_route(cmd_class, route, add_host=True, add_prefix=True)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestInitAndProperties(BaseRemoteAppTestCase):

    def test_protocol_property_accepts_enum_and_string(self) -> None:
        # Protocol as enum
        app_enum = RemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            protocol=HttpProtocol.HTTPS,
            add_generated_crud_route_handlers=False,
        )
        self.assertEqual(app_enum.protocol, HttpProtocol.HTTPS)

        # Protocol as string (lowercase)
        app_str = RemoteApp(
            domain=self.domain,
            host="example.org",
            port=8000,
            protocol="https",
            add_generated_crud_route_handlers=False,
        )
        self.assertEqual(app_str.protocol, HttpProtocol.HTTPS)

    def test_properties_and_host_url(self) -> None:
        # Create input
        # ... already created in setUp ...

        # Set up mocks: none

        # Execute
        host: str = self.app.host
        port: int | None = self.app.port
        protocol: HttpProtocol | str = self.app._protocol
        host_url: str = self.app.host_url
        ssl_context: Any = self.app.ssl_context

        # Verify
        self.assertEqual(host, "example.org")
        self.assertEqual(port, 8000)
        self.assertEqual(protocol, HttpProtocol.HTTP)
        self.assertEqual(host_url, "http://example.org:8000")
        self.assertEqual(ssl_context, False)

        # With no port
        other = RemoteApp(
            self.domain,
            "example.org",
            None,
            protocol=HttpProtocol.HTTPS,
            add_generated_crud_route_handlers=False,
        )
        self.assertEqual(other.host_url, "https://example.org")

    def test_register_policy_and_unregister_policy_raise(self) -> None:
        # Create input
        policy: Policy = cast(Policy, Mock(spec=Policy))

        # Set up mocks: none

        # Execute/Verify
        with self.assertRaises(ServiceException):
            self.app.register_policy(DummyCmd, policy, timing=EventTiming.BEFORE)
        with self.assertRaises(ServiceException):
            self.app.unregister_policy(DummyCmd, policy, timing=EventTiming.BEFORE)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestRouteRegistration(BaseRemoteAppTestCase):
    def test_register_route_and_get_route(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute
        route: str = self.register_route_for(DummyCmd, "endpoint")

        # Verify
        self.assertEqual(route, "http://example.org:8000/endpoint")
        got = self.app.get_route(cmd)
        self.assertEqual(got, route)

    def test_register_route_without_host_or_prefix(self) -> None:
        # Create input
        # Set up mocks: none

        # Execute
        route: str = self.app.register_route(
            DummyCmd, "endpoint", add_host=False, add_prefix=False
        )

        # Verify
        self.assertEqual(route, "endpoint")
        self.assertEqual(self.app.get_route(DummyCmd()), "endpoint")

    def test_register_route_duplicate_raises(self) -> None:
        # Create input
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks: none

        # Execute/Verify
        with self.assertRaises(ServiceException):
            self.register_route_for(DummyCmd, "endpoint2")

    def test_unregister_route_and_missing(self) -> None:
        # Create input
        # Set up mocks: none

        # Execute/Verify missing
        with self.assertRaises(ServiceException):
            self.app.unregister_route(DummyCmd)

        # Execute present
        self.register_route_for(DummyCmd, "endpoint")
        self.app.unregister_route(DummyCmd)

        # Verify removed
        with self.assertRaises(NotImplementedError):
            self.app.get_route(DummyCmd())

    def test_get_route_not_registered_raises(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute/Verify
        with self.assertRaises(NotImplementedError):
            self.app.get_route(cmd)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestHeadersAndApplyHandler(BaseRemoteAppTestCase):
    def test_get_headers_returns_defaults(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute
        headers = self.app.get_headers(cmd)

        # Verify
        self.assertEqual(headers, {"Content-Type": "application/json", "X-Test": "1"})

    def test_apply_handler_no_route_raises(self) -> None:
        # Create input
        cmd = DummyCmd()

        # Set up mocks: none

        # Execute/Verify
        with self.assertRaises(NotImplementedError):
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
        self.assertEqual(retval, "ok")

    def test_apply_handler_wraps_request_error(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        def _raise(_: Command) -> None:
            raise httpx.RequestError("boom", request=Mock())

        # Execute/Verify
        with self.assertRaises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        self.assertIn(
            "HTTP request error when handling remote command DummyCmd", str(e.exception)
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
        with self.assertRaises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        self.assertIn(
            "HTTP status 418 error when handling remote command DummyCmd",
            str(e.exception),
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
        with self.assertRaises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        self.assertIn(
            "HTTP status unknown error when handling remote command DummyCmd",
            str(e.exception),
        )

    def test_apply_handler_wraps_generic_exception(self) -> None:
        # Create input
        cmd = DummyCmd()
        self.register_route_for(DummyCmd, "endpoint")

        # Set up mocks
        def _raise(_: Command) -> None:
            raise RuntimeError("oops")

        # Execute/Verify
        with self.assertRaises(ServiceException) as e:
            self.app.apply_handler(cmd, _raise)
        self.assertIn("Error when handling remote command DummyCmd", str(e.exception))


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestGeneratedCrudRoutes(BaseRemoteAppTestCase):
    def test_register_generated_crud_route_builds_path(self) -> None:
        # Create input
        # Set up mocks: none

        # Execute
        route = self.app.register_generated_crud_route(DummyCrud)

        # Verify
        self.assertEqual(route, "http://example.org:8000/dummy_models")

    def test_create_generated_crud_handler_all_operations(self) -> None:
        # Create input
        base_route = "http://example.org:8000/dummy_models"
        handler = self.app.create_generated_crud_route_handler(DummyCrud, base_route)

        # Set up mocks: patch httpx.Client with FakeClient
        with patch("gen_epix.fastapp.remote_app.httpx.Client", FakeClient):
            # Ensure ssl verify is passed
            set_fake_response(payload=[], status_code=200)
            cmd = DummyCrud(operation=CrudOperation.READ_ALL)
            retval = handler(cmd)
            self.assertIsInstance(retval, list)
            self.assertEqual(
                FakeClient.last_request,
                {
                    "method": "GET",
                    "url": base_route,
                    "headers": self.app.get_headers(cmd),
                    "params": None,
                },
            )
            self.assertEqual(FakeClient.last_verify, self.app.ssl_context)

            # READ_ALL with query filter (without ids)
            qf = DummyQueryFilter(q="x")
            payload = [{"id": str(uuid4()), "name": "a"}]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(
                operation=CrudOperation.READ_ALL,
                query_filter=qf,
                props={"return_id": False},
            )
            retval = handler(cmd)
            self.assertEqual([DummyModel(**payload[0])], retval)  # type: ignore[arg-type]
            self.assertEqual(FakeClient.last_request["method"], "POST")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith("/query"))  # type: ignore[index]
            self.assertEqual(
                FakeClient.last_request["headers"], self.app.get_headers(cmd)  # type: ignore[index]
            )

            # READ_ALL with query filter and ids suffix (still returns models for test purposes)
            payload = [{"id": str(uuid4()), "name": "b"}]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(
                operation=CrudOperation.READ_ALL,
                query_filter=qf,
                props={"return_id": True},
            )
            retval = handler(cmd)
            self.assertEqual([DummyModel(**payload[0])], retval)  # type: ignore[arg-type]
            self.assertTrue(FakeClient.last_request["url"].endswith("/query/ids"))  # type: ignore[index]

            # READ_SOME
            ids = [uuid4(), uuid4()]
            payload = [
                {"id": str(ids[0]), "name": "x"},
                {"id": str(ids[1]), "name": "y"},
            ]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(operation=CrudOperation.READ_SOME, obj_ids=ids)
            retval = handler(cmd)
            self.assertEqual(
                [DummyModel(**payload[0]), DummyModel(**payload[1])], retval  # type: ignore[arg-type]
            )
            self.assertEqual(FakeClient.last_request["method"], "GET")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith("/batch"))  # type: ignore[index]
            self.assertIn("ids", FakeClient.last_request["params"])  # type: ignore[index]
            self.assertEqual(
                json.loads(FakeClient.last_request["params"]["ids"]),  # type: ignore[index]
                [str(x) for x in ids],
            )

            # READ_ONE
            one_id = uuid4()
            payload = {"id": str(one_id), "name": "z"}  # type: ignore[assignment]
            set_fake_response(payload=payload, status_code=200)
            cmd = DummyCrud(operation=CrudOperation.READ_ONE, obj_ids=one_id)
            retval = handler(cmd)
            self.assertEqual(DummyModel(**payload), retval)  # type: ignore[arg-type]
            self.assertEqual(FakeClient.last_request["method"], "GET")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith(f"/{one_id}"))  # type: ignore[index]

            # CREATE_ONE
            new_obj = DummyModel(id=uuid4(), name="n1")
            set_fake_response(
                payload=json.loads(new_obj.model_dump_json()), status_code=201
            )
            cmd = DummyCrud(operation=CrudOperation.CREATE_ONE, objs=new_obj)
            retval = handler(cmd)
            self.assertEqual(new_obj, retval)
            self.assertEqual(FakeClient.last_request["method"], "POST")  # type: ignore[index]
            self.assertEqual(FakeClient.last_request["url"], base_route)  # type: ignore[index]
            self.assertEqual(
                FakeClient.last_request["json"], json.loads(new_obj.model_dump_json())  # type: ignore[index]
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
            self.assertEqual(new_objs, retval)
            self.assertEqual(FakeClient.last_request["method"], "POST")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith("/batch"))  # type: ignore[index]

            # UPDATE_ONE
            upd = DummyModel(id=uuid4(), name="u1")
            set_fake_response(
                payload=json.loads(upd.model_dump_json()), status_code=200
            )
            cmd = DummyCrud(operation=CrudOperation.UPDATE_ONE, objs=upd)
            retval = handler(cmd)
            self.assertEqual(upd, retval)
            self.assertEqual(FakeClient.last_request["method"], "PUT")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith(f"/{upd.id}"))  # type: ignore[index]

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
            self.assertEqual(upds, retval)
            self.assertEqual(FakeClient.last_request["method"], "PUT")  # type: ignore[index]
            self.assertEqual(FakeClient.last_request["url"], base_route)  # type: ignore[index]

            # DELETE_ONE
            del_id = uuid4()
            set_fake_response(payload=str(del_id), status_code=200)
            cmd = DummyCrud(operation=CrudOperation.DELETE_ONE, obj_ids=del_id)
            retval = handler(cmd)
            self.assertEqual(del_id, retval)
            self.assertEqual(FakeClient.last_request["method"], "DELETE")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith(f"/{del_id}"))  # type: ignore[index]

            # DELETE_SOME
            del_ids = [uuid4(), uuid4()]
            set_fake_response(payload=[str(x) for x in del_ids], status_code=200)
            cmd = DummyCrud(operation=CrudOperation.DELETE_SOME, obj_ids=del_ids)
            retval = handler(cmd)
            self.assertEqual(del_ids, retval)
            self.assertEqual(FakeClient.last_request["method"], "DELETE")  # type: ignore[index]
            self.assertTrue(FakeClient.last_request["url"].endswith("/batch"))  # type: ignore[index]
            self.assertIn("ids", FakeClient.last_request["params"])  # type: ignore[index]
            self.assertEqual(
                json.loads(FakeClient.last_request["params"]["ids"]),  # type: ignore[index]
                [str(x) for x in del_ids],
            )

            # Non-200/201 status returns None
            set_fake_response(payload={"ignored": True}, status_code=204)
            cmd = DummyCrud(operation=CrudOperation.READ_ONE, obj_ids=uuid4())
            retval = handler(cmd)
            self.assertIsNone(retval)

    def test_generated_handler_unsupported_return_type_raises(self) -> None:
        # Create input
        base_route = "http://example.org:8000/dummy_models"
        handler = self.app.create_generated_crud_route_handler(
            UnsupportedCrud, base_route
        )

        # Set up mocks
        with patch("gen_epix.fastapp.remote_app.httpx.Client", FakeClient):
            set_fake_response(payload={"something": "x"}, status_code=200)
            cmd = UnsupportedCrud(operation=CrudOperation.READ_ONE, obj_ids=uuid4())

            # Execute/Verify
            with self.assertRaises(NotImplementedError):
                handler(cmd)


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestAutoRegistration(BaseRemoteAppTestCase):
    def test_init_auto_registers_handlers_for_domain_crud_commands(self) -> None:
        # Create input
        domain: Domain = cast(Domain, Mock(spec=Domain))
        domain.crud_commands = [DummyCrud]  # type: ignore[misc,assignment]

        # Set up mocks
        with (
            patch.object(
                RemoteApp, "register_generated_crud_route", return_value="/dummy_models"
            ) as reg_route,
            patch.object(
                RemoteApp, "register_handler", return_value=None
            ) as reg_handler,
        ):
            app = RemoteApp(
                domain=domain,
                host="example.org",
                port=8000,
                protocol=HttpProtocol.HTTP,
                add_generated_crud_route_handlers=True,
            )

        # Execute: none

        # Verify
        reg_route.assert_called_once_with(DummyCrud)
        self.assertEqual(reg_handler.call_count, 1)
        args, kwargs = reg_handler.call_args
        self.assertIs(args[0], DummyCrud)
        self.assertTrue(callable(args[1]))
        # Also verify host_url constructed
        self.assertEqual(app.host_url, "http://example.org:8000")
