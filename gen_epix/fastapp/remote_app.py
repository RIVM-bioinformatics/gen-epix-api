import json
import ssl
from functools import partial
from pathlib import Path
from typing import Any, Callable, Type
from uuid import UUID

import httpx
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.fastapp import exc, model
from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import CrudOperation, EventTiming, HttpProtocol, StringCasing
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Policy


class RemoteApp(App):

    DEFAULT_ROUTE_PREFIX = "/"

    DEFAULT_REQUEST_HEADERS: dict[str, str] = {"Content-Type": "application/json"}

    LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}

    def __init__(
        self,
        domain: Domain,
        host: str,
        port: int | None,
        http_protocol: HttpProtocol = HttpProtocol.HTTPS,
        default_route_prefix: str | None = None,
        default_headers: dict[str, str] | None = None,
        add_generated_crud_route_handlers: bool = True,
        ssl_cert_file: Path | str | None = None,
        disable_ssl_verification: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(domain, **kwargs)
        self._host = host
        self._port = port
        self._http_protocol = http_protocol
        self._default_route_prefix = default_route_prefix or self.DEFAULT_ROUTE_PREFIX
        self._default_headers = default_headers or self.DEFAULT_REQUEST_HEADERS
        self._routes: dict[type[Command], str] = {}

        # Initialise SSL context
        self._ssl_context = RemoteApp.create_ssl_context(
            host, ssl_cert_file, disable_ssl_verification
        )

        # Create and register generated crud route handlers
        if add_generated_crud_route_handlers:
            for command_class in self.domain.crud_commands:
                base_route = self.register_generated_crud_route(command_class)
                handler = self.create_generated_crud_route_handler(
                    command_class,
                    base_route,
                )
                self.register_handler(command_class, handler)

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int | None:
        return self._port

    @property
    def http_protocol(self) -> HttpProtocol:
        return self._http_protocol

    @property
    def host_url(self) -> str:
        port_str = f":{self._port}" if self._port else ""
        return f"{self.http_protocol.value.lower()}://{self._host}{port_str}"

    @property
    def ssl_context(self) -> ssl.SSLContext | bool:
        return self._ssl_context

    def register_policy(
        self,
        command_class: type[Command],
        policy: Policy,
        timing: EventTiming = EventTiming.BEFORE,
    ) -> None:
        raise ServiceException("Policies cannot be registered on RemoteApp instances")

    def unregister_policy(
        self, command_class: type[Command], policy: Policy, timing: EventTiming
    ) -> None:
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
        route = self._default_route_prefix + route if add_prefix else route
        route = route if not add_host else f"{self.host_url}{route}"
        self._routes[command_class] = route
        return route

    def unregister_route(self, command_class: type[Command]) -> None:
        if command_class not in self._routes:
            raise ServiceException(
                f"No route registered for command: {command_class.__name__}"
            )
        del self._routes[command_class]

    def get_route(self, cmd: Command) -> str:
        route = self._routes.get(cmd.__class__, None)
        if not route:
            raise NotImplementedError(
                f"No route registered for command: {cmd.__class__.__name__}"
            )
        return route

    def get_headers(self, cmd: Command) -> dict[str, str]:
        """
        Get headers for the command. Override to include e.g. authorization header.
        """
        return self._default_headers

    def apply_handler(
        self,
        cmd: Command,
        handler: Callable[[Command], Any],
    ) -> Any:
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
                f"HTTP request error when handling remote command {command_class.NAME}: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            # Handle HTTPStatusError with proper access to response attributes
            status_code = getattr(e.response, 'status_code', 'unknown') if hasattr(e, 'response') and e.response else 'unknown'
            raise exc.ServiceException(
                f"HTTP status {status_code} error when handling remote command {command_class.NAME}: {e}"
            ) from e
        except Exception as e:
            raise exc.ServiceException(
                f"Error when handling remote command {command_class.NAME}: {e}"
            ) from e
        return retval

    def register_generated_crud_route(
        self,
        command_class: Type[CrudCommand],
        route_root: str | None = None,
        add_host: bool = True,
        add_prefix: bool = True,
        route_root_casing: StringCasing = StringCasing.SNAKE_CASE,
        route_root_plural: bool = True,
    ) -> str:
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
        command_class: Type[CrudCommand],
        base_route: str,
        batch_route_suffix: str | None = None,
        query_route_suffix: str | None = None,
        ids_route_suffix: str | None = None,
    ) -> Callable[[Command], Any]:
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

        def handler(
            base_route: str,
            batch_route_suffix: str,
            query_route_suffix: str,
            ids_route_suffix: str,
            cmd: CrudCommand,
        ) -> Any:

            headers = self.get_headers(cmd)
            model_class = cmd.MODEL_CLASS
            return_model_class: type = model_class
            is_list = False
            with httpx.Client(verify=self.ssl_context) as client:
                if cmd.operation == CrudOperation.READ_ALL:
                    if cmd.query_filter:
                        response = client.post(
                            base_route
                            + query_route_suffix
                            + (
                                "/" + ids_route_suffix
                                if cmd.props.get("return_id", False)
                                else ""
                            ),
                            json=json.loads(cmd.query_filter.model_dump_json()),
                            headers=headers,
                        )
                    else:
                        response = client.get(base_route, headers=headers)
                    is_list = True
                elif cmd.operation == CrudOperation.READ_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    ids = json.dumps([str(x) for x in cmd.obj_ids])
                    response = client.get(
                        base_route + batch_route_suffix,
                        headers=headers,
                        params={"ids": ids},
                    )
                    is_list = True
                elif cmd.operation == CrudOperation.READ_ONE:
                    response = client.get(
                        f"{base_route}/{cmd.obj_ids}",
                        headers=headers,
                    )
                elif cmd.operation == CrudOperation.CREATE_ONE:
                    assert isinstance(cmd.objs, model.Model)
                    response = client.post(
                        f"{base_route}",
                        json=json.loads(cmd.objs.model_dump_json()),
                        headers=headers,
                    )
                elif cmd.operation == CrudOperation.CREATE_SOME:
                    assert isinstance(cmd.objs, list)
                    response = client.post(
                        base_route + batch_route_suffix,
                        json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                        headers=headers,
                    )
                    is_list = True
                elif cmd.operation == CrudOperation.UPDATE_ONE:
                    assert isinstance(cmd.objs, model.Model)
                    response = client.put(
                        f"{base_route}/{cmd.objs.id}",  # type: ignore[attr-defined]
                        json=json.loads(cmd.objs.model_dump_json()),
                        headers=headers,
                    )
                elif cmd.operation == CrudOperation.UPDATE_SOME:
                    assert isinstance(cmd.objs, list)
                    response = client.put(
                        f"{base_route}",
                        json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                        headers=headers,
                    )
                    is_list = True
                elif cmd.operation == CrudOperation.DELETE_ONE:
                    assert isinstance(cmd.obj_ids, UUID)
                    response = client.delete(
                        f"{base_route}/{cmd.obj_ids}", headers=headers
                    )
                    return_model_class = UUID
                elif cmd.operation == CrudOperation.DELETE_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    ids = json.dumps([str(x) for x in cmd.obj_ids])
                    response = client.delete(
                        base_route + batch_route_suffix,
                        headers=headers,
                        params={"ids": ids},
                    )
                    return_model_class = UUID
                    is_list = True
                else:
                    raise NotImplementedError(f"Unsupported operation: {cmd.operation}")
                response.raise_for_status()
            retval = self._content_to_obj(response, return_model_class, is_list=is_list)
            return retval

        return partial(
            handler,
            base_route,
            batch_route_suffix,
            query_route_suffix,
            ids_route_suffix,
        )

    @staticmethod
    def create_ssl_context(
        host: str, ssl_cert_file: Path | str | None, disable_ssl_verification: bool
    ) -> ssl.SSLContext | bool:
        """Get SSL verification setting using similar logic to OidcClient."""
        if disable_ssl_verification:
            return False

        # For local development hosts, disable verification
        if host in RemoteApp.LOCAL_HOSTS:
            return False

        # If a cert file is given, use that for verification
        if ssl_cert_file is not None:
            if isinstance(ssl_cert_file, str):
                ssl_cert_file = Path(ssl_cert_file)
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(ssl_cert_file.absolute().as_posix())
            return ssl_context

        # Use default verification
        return True

    @staticmethod
    def _content_to_obj(
        response: httpx.Response, retval_class: Type, is_list: bool = False
    ) -> Any:
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
