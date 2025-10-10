import json
from functools import partial
from typing import Any, Callable, Type
from uuid import UUID

import httpx
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.fastapp import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import CrudOperation, EventTiming
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Policy, User


class RemoteApp(App):
    def __init__(
        self,
        domain: Domain,
        host: str,
        port: int,
        default_route_prefix: str,
        create_crud_handlers: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(domain, **kwargs)
        self._default_route_prefix = default_route_prefix
        self._host = host
        self._port = port
        self._user_jwts: dict[str, str] = {}
        self._routes: dict[type[Command], str] = {}

        # register handlers here
        if create_crud_handlers:
            for command_class in self.domain.crud_commands:
                handler = self.create_crud_handler(
                    command_class, self._default_route_prefix, {}
                )
                self.register_handler(command_class, handler)

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

    def register_user(self, user: User, jwt: str) -> None:
        """Register a user user with a jwt token, which will be used for requests."""
        self._user_jwts[user.get_key()] = jwt

    def register_route(
        self, command: Command, route: str, add_prefix: bool = True
    ) -> None:
        """Registers route to the db on the command."""
        route = self._default_route_prefix + route if add_prefix else route
        self._routes[command] = route

    def get_headers(self, cmd: Command) -> dict[str, str]:
        jwt = "DUMMY_JWT"
        return {"Authorization": f"Bearer {jwt}"} if jwt else {}

    def apply_handler(
        self,
        command: Command,
        handler: Callable[[Command], Any],
    ) -> Any:
        command_class = command.__class__
        route = self._routes.get(command_class, None)
        if not route:
            raise NotImplementedError(
                f"No route registered for command: {command.__class__.__name__}"
            )

        return handler(command)

    def create_crud_handler(
        self,
        command_class: Type[CrudCommand],
        route_prefix: str,
        headers: dict[str, str],
    ) -> Callable[[Command], Any]:
        model_class = command_class.MODEL_CLASS
        entity = model_class.ENTITY
        assert entity is not None
        route = f"https://{self._host}:{self._port}{route_prefix}{entity.snake_case_plural_name}"
        self.register_route(command_class, route, add_prefix=False)

        def handler(route: str, cmd: CrudCommand) -> Any:
            with httpx.Client() as client:
                if cmd.operation == CrudOperation.READ_ALL:
                    if cmd.query_filter:
                        response = client.post(
                            route + "/query",
                            json=json.loads(cmd.query_filter.model_dump_json()),
                            headers=headers,
                        )
                    else:
                        response = client.get(route, headers=headers)
                    retval = self._content_to_obj(response, model_class, is_list=True)
                elif cmd.operation == CrudOperation.READ_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    ids = json.dumps([str(x) for x in cmd.obj_ids])
                    response = client.get(
                        f"{route}/batch",
                        headers=headers,
                        params={"ids": ids},
                    )
                    retval = self._content_to_obj(response, model_class, is_list=True)
                elif cmd.operation == CrudOperation.READ_ONE:
                    response = client.get(
                        f"{route}/{cmd.obj_ids}",
                        headers=headers,
                    )
                    retval = self._content_to_obj(response, model_class)
                elif cmd.operation == CrudOperation.CREATE_ONE:
                    assert isinstance(cmd.objs, model.Model)
                    response = client.post(
                        f"{route}",
                        json=json.loads(cmd.objs.model_dump_json()),
                        headers=headers,
                    )
                    retval = self._content_to_obj(response, model_class)
                elif cmd.operation == CrudOperation.CREATE_SOME:
                    assert isinstance(cmd.objs, list)
                    response = client.post(
                        f"{route}/batch",
                        json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                        headers=headers,
                    )
                    retval = self._content_to_obj(response, model_class, is_list=True)
                elif cmd.operation == CrudOperation.UPDATE_ONE:
                    assert isinstance(cmd.objs, model.Model)
                    response = client.put(
                        f"{route}/{cmd.objs.id}",
                        json=json.loads(cmd.objs.model_dump_json()),
                        headers=headers,
                    )
                    retval = self._content_to_obj(response, model_class)
                elif cmd.operation == CrudOperation.UPDATE_SOME:
                    assert isinstance(cmd.objs, list)
                    response = client.put(
                        f"{route}",
                        json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                        headers=headers,
                    )
                    retval = self._content_to_obj(response, model_class, is_list=True)
                elif cmd.operation == CrudOperation.DELETE_ONE:
                    assert isinstance(cmd.obj_ids, UUID)
                    response = client.delete(f"{route}/{cmd.obj_ids}", headers=headers)
                    retval = self._content_to_obj(response, UUID)
                elif cmd.operation == CrudOperation.DELETE_SOME:
                    assert isinstance(cmd.obj_ids, list)
                    ids = json.dumps([str(x) for x in cmd.obj_ids])
                    response = client.delete(
                        f"{route}/batch",
                        headers=headers,
                        params={"ids": ids},
                    )
                    retval = self._content_to_obj(response, UUID, is_list=True)
                else:
                    raise NotImplementedError(f"Unsupported operation: {cmd.operation}")
            return retval, response

        return partial(handler, route)

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
