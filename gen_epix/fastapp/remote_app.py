"""Client for dispatching commands to a remote application instance."""

import json
import ssl
from collections.abc import Callable, Generator
from decimal import Decimal
from functools import partial
from pathlib import Path
from typing import Any, cast
from uuid import UUID

import httpx
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.fastapp import exc, model
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import (
    CrudOperation,
    EventTiming,
    HttpMethod,
    HttpProtocol,
    StringCasing,
)
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Policy
from gen_epix.fastapp.util import create_ssl_context
from gen_epix.filter import (
    FilterType,
    TypedNumberSetFilter,
    TypedStringSetFilter,
    TypedUuidSetFilter,
)


class RemoteApp(App):
    """Encapsulates the base class for remote application clients that forward commands as HTTP requests."""

    DEFAULT_ROUTE_PREFIX = "/"

    DEFAULT_REQUEST_TIMEOUT = 5.0

    DEFAULT_REQUEST_HEADERS: dict[str, str] = {"Content-Type": "application/json"}

    def __init__(
        self,
        domain: Domain,
        host: str,
        port: int | None,
        protocol: HttpProtocol | str = HttpProtocol.HTTPS,
        default_route_prefix: str | None = None,
        default_headers: dict[str, str] | None = None,
        default_request_timeout: int | None = None,
        add_generated_crud_route_handlers: bool = True,
        ssl_cert_file: Path | str | None = None,
        disable_ssl_verification: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize connection parameters, SSL context, routes, and optional CRUD handlers."""
        super().__init__(domain, **kwargs)
        self._host = host
        self._port = port
        self._protocol = protocol
        self._default_request_timeout = (
            default_request_timeout or self.DEFAULT_REQUEST_TIMEOUT
        )
        self._default_route_prefix = default_route_prefix or self.DEFAULT_ROUTE_PREFIX
        self._default_headers = default_headers or self.DEFAULT_REQUEST_HEADERS
        self._routes: dict[type[Command], str] = {}
        self._timeouts: dict[type[Command], float] = {}

        # Initialise SSL context
        self._initialize_ssl_context(host, ssl_cert_file, disable_ssl_verification)

        # Create and register generated crud route handlers
        if add_generated_crud_route_handlers:
            for command_class in self.domain.crud_commands:
                base_route = self.register_generated_crud_route(command_class)
                handler = self.create_generated_crud_route_handler(
                    command_class,
                    base_route,
                )
                self.register_handler(command_class, handler)

    def _initialize_ssl_context(
        self,
        host: str,
        ssl_cert_file: Path | str | None,
        disable_ssl_verification: bool,
    ) -> None:
        """Configure the SSL context based on protocol and certificate settings."""
        if self.protocol == HttpProtocol.HTTPS:
            self._ssl_context = create_ssl_context(
                host, ssl_cert_file, disable_ssl_verification
            )
        else:
            self._ssl_context = False

    @property
    def host(self) -> str:
        """Remote host name."""
        return self._host

    @property
    def port(self) -> int | None:
        """Remote port, or None if not specified."""
        return self._port

    @property
    def protocol(self) -> HttpProtocol:
        """HTTP protocol (HTTP or HTTPS)."""
        if isinstance(self._protocol, HttpProtocol):
            return self._protocol
        return HttpProtocol[self._protocol.upper()]

    @property
    def host_url(self) -> str:
        """Full base URL including protocol, host, and port."""
        port_str = f":{self.port}" if self.port else ""
        return f"{self.protocol.value.lower()}://{self.host}{port_str}"

    @property
    def ssl_context(self) -> ssl.SSLContext | bool:
        """SSL context for HTTPS connections, or False to disable verification."""
        return self._ssl_context

    def register_policy(
        self,
        command_class: type[Command],
        policy: Policy,
        timing: EventTiming = EventTiming.BEFORE,
    ) -> None:
        """Raise ServiceException; policies are not supported on RemoteApp."""
        raise ServiceException("Policies cannot be registered on RemoteApp instances")

    def unregister_policy(
        self, command_class: type[Command], policy: Policy, timing: EventTiming
    ) -> None:
        """Raise ServiceException; policies are not supported on RemoteApp."""
        raise ServiceException("Policies cannot be unregistered on RemoteApp instances")

    def register_route(
        self,
        command_class: type[Command],
        route: str,
        add_host: bool = True,
        add_prefix: bool = True,
    ) -> str:
        """
        Registers the route that is able to handle the command after it is
        converted into a request by the handler.

        """
        if command_class in self._routes:
            raise ServiceException(
                f"Route already registered for command: {command_class.__name__}"
            )
        if add_prefix:
            route = f"{self._default_route_prefix.rstrip('/')}/{route.lstrip('/')}"
        elif not route.startswith("/"):
            route = "/" + route

        route = route if not add_host else f"{self.host_url}{route}"
        self._routes[command_class] = route
        return route

    def unregister_route(self, command_class: type[Command]) -> None:
        """Remove the registered route for the given command class."""
        if command_class not in self._routes:
            raise ServiceException(
                f"No route registered for command: {command_class.__name__}"
            )
        del self._routes[command_class]

    def get_route(self, cmd: Command) -> str:
        """Return the registered URL for the given command, raising if not found."""
        route = self._routes.get(cmd.__class__, None)
        if not route:
            raise NotImplementedError(
                f"No route registered for command: {cmd.__class__.__name__}"
            )
        return route

    def get_headers(self, cmd: Command) -> dict[str, str]:
        """Get headers for the command. Override to include e.g. authorization header."""
        return self._default_headers

    def apply_handler(
        self,
        cmd: Command,
        handler: Callable[[Command], Any],
    ) -> Any:
        """Invoke the handler, wrapping transport and HTTP errors in ServiceException."""
        command_class = cmd.__class__
        route = self._routes.get(command_class, None)
        if not route:
            raise NotImplementedError(
                f"No route registered for command: {cmd.__class__.NAME}"
            )
        try:
            retval = handler(cmd)
        except httpx.RequestError as e:
            raise exc.ServiceException(
                "869e34b6",
                f"HTTP request error when handling remote command {command_class.NAME}: {e}",
            ) from e
        except httpx.HTTPStatusError as e:
            # Handle HTTPStatusError with proper access to response attributes
            status_code = (
                getattr(e.response, "status_code", "unknown")
                if hasattr(e, "response") and e.response
                else "unknown"
            )
            raise exc.ServiceException(
                "b7b0a22c",
                f"HTTP status {status_code} error when handling remote command {command_class.NAME}: {e}",
            ) from e
        except Exception as e:
            raise exc.ServiceException(
                "3dd5acdb",
                f"Error when handling remote command {command_class.NAME}: {e}",
            ) from e
        return retval

    def get_timeout(self, command_class: type[Command]) -> float:
        """Get the timeout in seconds for a specific command class. Returns the custom timeout if set, otherwise returns the default timeout."""
        return self._timeouts.get(
            command_class,
            self._default_request_timeout,
        )

    def set_timeout(self, command_class: type[Command], timeout_seconds: float) -> None:
        """Set a custom timeout for a specific command class. This will be used instead of the default timeout when making requests for that command."""
        if timeout_seconds <= 0:
            raise exc.ServiceException("7f3a9c2e", "Timeout must be a positive integer")
        self._timeouts[command_class] = timeout_seconds

    def get_client(self, cmd: Command, timeout: float | None = None) -> httpx.Client:
        """Get an httpx.Client instance with the appropriate SSL context and timeout for the given command. This can be used in handlers to make requests to the remote service."""
        return httpx.Client(
            verify=self.ssl_context, timeout=timeout or self.get_timeout(type(cmd))
        )

    def request(
        self,
        cmd: Command,
        method: HttpMethod,
        *,
        route: str | None = None,
        model: PydanticBaseModel | None = None,
        json_body: Any = None,
        params: dict[str, Any] | None = None,
        exclude: set[str] | None = None,
    ) -> Any | None:
        """
        Execute an HTTP request for a command and method and return the parsed JSON
        response body, if any.

        The registered route for the command can be overridden by providing a custom
        route, typically when a parameterised route is needed based on the command
        contents.

        If a request body is needed, it must be provided via either the `model` or the
        `json_body` parameter. The Pydantic model will be converted to json via
        model_dump_json(exclude=exclude) so any non-standard serialization is handled
        properly and some fields can be excluded as necessary. If both model and
        json_body are None, no request body will be sent. Other types of request bodies
        are currently not supported by this method.
        """
        # Parse input
        if model is not None:
            if json_body is not None:
                raise ValueError(
                    "Cannot provide both a Pydantic model and a JSON body for the request"
                )
            json_body = json.loads(model.model_dump_json(exclude=exclude))
        # Get headers and route
        headers = self.get_headers(cmd)
        url = route if route is not None else self.get_route(cmd)
        # Execute request and parse response
        with self.get_client(cmd) as client:
            response = client.request(
                method.value, url, json=json_body, params=params, headers=headers
            )
            response.raise_for_status()
            if not response.content:
                return None
            return response.json()

    def stream(
        self,
        cmd: Command,
        method: HttpMethod,
        *,
        route: str | None = None,
        model: PydanticBaseModel | None = None,
        json_body: Any = None,
        form_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        exclude: set[str] | None = None,
    ) -> Generator[str, None, None]:
        """
        Execute a streaming HTTP request for a command and yield decoded chunks.

        Mirrors `request` but uses client.stream() and yields response bytes
        decoded as UTF-8 strings instead of returning parsed JSON.

        When `form_data` is provided, the request is sent as form-encoded data
        without the default headers (e.g. for endpoints that authenticate via a
        form field instead of an Authorization header).
        """
        if model is not None:
            if json_body is not None:
                raise ValueError(
                    "Cannot provide both a Pydantic model and a JSON body for the request"
                )
            json_body = json.loads(model.model_dump_json(exclude=exclude))
        url = route if route is not None else self.get_route(cmd)
        # Skip default headers when auth is embedded in form_data.
        headers = None if form_data is not None else self.get_headers(cmd)
        with self.get_client(cmd) as client:
            with client.stream(
                method.value,
                url,
                json=json_body,
                data=form_data,
                params=params,
                headers=headers,
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    yield chunk.decode()

    def register_generated_crud_route(
        self,
        command_class: type[CrudCommand],
        route_root: str | None = None,
        add_host: bool = True,
        add_prefix: bool = True,
        route_root_casing: StringCasing = StringCasing.SNAKE_CASE,
        route_root_plural: bool = True,
    ) -> str:
        """Derive the CRUD route from the model entity name and register it."""
        model_class = command_class.MODEL_CLASS
        entity = model_class.ENTITY
        assert entity is not None
        route_root = route_root or entity.get_name_by_casing(
            route_root_casing, is_plural=route_root_plural
        )
        assert route_root is not None
        return self.register_route(
            command_class, route_root, add_host=add_host, add_prefix=add_prefix
        )

    def create_generated_crud_route_handler(
        self,
        command_class: type[CrudCommand],
        base_route: str,
        batch_route_suffix: str | None = None,
        query_route_suffix: str | None = None,
        ids_route_suffix: str | None = None,
    ) -> Callable[[Command], Any]:
        """Return a partial handler that maps CRUD operations to HTTP requests."""
        batch_route_suffix = (
            batch_route_suffix or CrudEndpointGenerator.DEFAULT_BATCH_ROUTE_SUFFIX
        )
        query_route_suffix = (
            query_route_suffix or CrudEndpointGenerator.DEFAULT_QUERY_ROUTE_SUFFIX
        )
        ids_route_suffix = (
            ids_route_suffix or CrudEndpointGenerator.DEFAULT_IDS_ROUTE_SUFFIX
        )
        model_class = command_class.MODEL_CLASS
        entity = model_class.ENTITY
        assert entity is not None

        return cast(
            Callable[[Command], Any],
            partial(
                self._execute_crud_operation,
                base_route,
                batch_route_suffix,
                query_route_suffix,
                ids_route_suffix,
            ),
        )

    def _execute_crud_operation(
        self,
        base_route: str,
        batch_route_suffix: str,
        query_route_suffix: str,
        ids_route_suffix: str,
        cmd: CrudCommand,
    ) -> Any:
        """Execute a CRUD command by dispatching to the appropriate HTTP method."""
        headers = self.get_headers(cmd)
        model_class = cmd.MODEL_CLASS
        return_model_class: type = model_class
        is_list = False
        with self.get_client(cmd) as client:
            match cmd.operation:
                case CrudOperation.READ_ALL:
                    if cmd.query_filter:
                        if cmd.return_id:
                            query_suffix = query_route_suffix.rstrip("/")
                            ids_suffix = (
                                ids_route_suffix
                                if ids_route_suffix.startswith("/")
                                else ("/" + ids_route_suffix)
                            )
                            url = base_route + query_suffix + ids_suffix
                        else:
                            url = base_route + query_route_suffix
                        response = client.post(
                            url,
                            json=json.loads(cmd.query_filter.model_dump_json()),
                            headers=headers,
                        )
                    else:
                        response = client.get(base_route, headers=headers)
                    is_list = True
                case CrudOperation.READ_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    ids = json.dumps([str(x) for x in cmd.obj_ids])
                    response = client.get(
                        base_route + batch_route_suffix,
                        headers=headers,
                        params={"ids": ids},
                    )
                    is_list = True
                case CrudOperation.READ_ONE:
                    response = client.get(
                        f"{base_route}/{cmd.obj_ids}",
                        headers=headers,
                    )
                case CrudOperation.EXISTS_ONE:
                    assert cmd.obj_ids is not None
                    return self._exists_some_via_query_ids(
                        client=client,
                        headers=headers,
                        model_class=model_class,
                        base_route=base_route,
                        query_route_suffix=query_route_suffix,
                        ids_route_suffix=ids_route_suffix,
                        obj_ids=[cmd.obj_ids],
                    )[0]
                case CrudOperation.EXISTS_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    return self._exists_some_via_query_ids(
                        client=client,
                        headers=headers,
                        model_class=model_class,
                        base_route=base_route,
                        query_route_suffix=query_route_suffix,
                        ids_route_suffix=ids_route_suffix,
                        obj_ids=cmd.obj_ids,
                    )
                case CrudOperation.CREATE_ONE:
                    assert isinstance(cmd.objs, model.Model)
                    response = client.post(
                        f"{base_route}",
                        json=json.loads(cmd.objs.model_dump_json()),
                        headers=headers,
                    )
                case CrudOperation.CREATE_SOME:
                    assert isinstance(cmd.objs, list)
                    response = client.post(
                        base_route + batch_route_suffix,
                        json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                        headers=headers,
                    )
                    is_list = True
                case CrudOperation.UPDATE_ONE:
                    assert isinstance(cmd.objs, model.Model)
                    response = client.put(
                        f"{base_route}/{cmd.objs.id}",  # type: ignore[attr-defined]
                        json=json.loads(cmd.objs.model_dump_json()),
                        headers=headers,
                    )
                case CrudOperation.UPDATE_SOME:
                    assert isinstance(cmd.objs, list)
                    response = client.put(
                        base_route + batch_route_suffix,
                        json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                        headers=headers,
                    )
                    is_list = True
                case CrudOperation.DELETE_ONE:
                    assert isinstance(cmd.obj_ids, UUID)
                    response = client.delete(
                        f"{base_route}/{cmd.obj_ids}", headers=headers
                    )
                    return_model_class = UUID
                case CrudOperation.DELETE_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    ids = json.dumps([str(x) for x in cmd.obj_ids])
                    response = client.delete(
                        base_route + batch_route_suffix,
                        headers=headers,
                        params={"ids": ids},
                    )
                    return_model_class = UUID
                    is_list = True
                case _:
                    raise AssertionError(f"Unsupported operation: {cmd.operation}")
            response.raise_for_status()
        retval = self._content_to_obj(response, return_model_class, is_list=is_list)
        return retval

    def _exists_some_via_query_ids(
        self,
        base_route: str,
        query_route_suffix: str,
        ids_route_suffix: str,
        model_class: type[model.Model],
        obj_ids: list[Any],
        client: httpx.Client,
        headers: dict[str, str],
    ) -> list[bool]:
        """Check existence of multiple IDs using a query-by-IDs endpoint."""
        if not obj_ids:
            return []

        id_field_name = model_class.ENTITY.id_field_name
        if not isinstance(id_field_name, str):
            raise AssertionError(
                f"Model {model_class.__name__} does not define a string id_field_name."
            )
        query_suffix = query_route_suffix.rstrip("/")
        ids_suffix = (
            ids_route_suffix
            if ids_route_suffix.startswith("/")
            else ("/" + ids_route_suffix)
        )
        query_ids_url = base_route + query_suffix + ids_suffix

        id_type = self._classify_exists_id_type(obj_ids)
        number_id_types = {"int", "float", "decimal"}
        query_filter: TypedUuidSetFilter | TypedStringSetFilter | TypedNumberSetFilter

        if id_type == "uuid":
            query_filter = TypedUuidSetFilter(
                type=FilterType.UUID_SET.value,
                key=id_field_name,
                members=frozenset(obj_ids),
            )
        elif id_type == "string":
            query_filter = TypedStringSetFilter(
                type=FilterType.STRING_SET.value,
                key=id_field_name,
                members=frozenset(obj_ids),
                case_sensitive=True,
            )
        elif id_type in number_id_types:
            query_filter = TypedNumberSetFilter(
                type=FilterType.NUMBER_SET.value,
                key=id_field_name,
                members=frozenset(obj_ids),
            )
        else:
            return self._exists_some_via_get(
                base_route=base_route,
                obj_ids=obj_ids,
                client=client,
                headers=headers,
            )

        response = client.post(
            query_ids_url,
            json=json.loads(query_filter.model_dump_json()),
            headers=headers,
        )
        response.raise_for_status()
        found_ids = json.loads(response.content.decode(response.encoding or "utf-8"))
        if id_type == "uuid":
            found_set = {UUID(x) for x in found_ids}
        else:
            found_set = set(found_ids)
        return [obj_id in found_set for obj_id in obj_ids]

    @staticmethod
    def _classify_exists_id_type(obj_ids: list[Any]) -> str:
        """Return the id kind ('uuid', 'string', 'int', 'float', 'decimal', or 'mixed')."""
        if not obj_ids:
            return "mixed"

        first_type = type(obj_ids[0])
        if not all(type(obj_id) is first_type for obj_id in obj_ids[1:]):
            return "mixed"

        type_to_id_kind: dict[type, str] = {
            UUID: "uuid",
            str: "string",
            int: "int",
            float: "float",
            Decimal: "decimal",
        }
        return type_to_id_kind.get(first_type, "mixed")

    @staticmethod
    def _exists_some_via_get(
        base_route: str,
        obj_ids: list[Any],
        client: httpx.Client,
        headers: dict[str, str],
    ) -> list[bool]:
        """Check existence of each ID via individual GET requests."""
        is_existing: list[bool] = []
        for obj_id in obj_ids:
            response = client.get(
                f"{base_route}/{obj_id}",
                headers=headers,
            )
            if response.status_code == 404:
                is_existing.append(False)
                continue
            response.raise_for_status()
            is_existing.append(True)
        return is_existing

    @staticmethod
    def _content_to_obj(
        response: httpx.Response, retval_class: type, is_list: bool = False
    ) -> Any:
        """Deserialize an HTTP response body into the expected model or UUID type."""
        if response.status_code not in (200, 201):
            return None
        decoded_obj = json.loads(response.content.decode(response.encoding or "utf-8"))
        if issubclass(retval_class, PydanticBaseModel):
            if is_list:
                return [retval_class(**x) for x in decoded_obj]
            else:
                return retval_class(**decoded_obj)
        elif issubclass(retval_class, UUID):
            if is_list:
                return [UUID(x) for x in decoded_obj]
            else:
                return UUID(decoded_obj)
        raise NotImplementedError(f"Unsupported return type: {retval_class}")
