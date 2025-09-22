import json
from functools import partial
from typing import Any, Callable, Type

import httpx

from gen_epix.fastapp import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import CrudOperation, EventTiming
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Policy, User


class RemoteApp(App):
    def __init__(self, domain: Domain, default_route_prefix: str, default_jwt: str, **kwargs: Any) -> None:
        super().__init__(domain, **kwargs)
        self._default_route_prefix = default_route_prefix
        self._default_jwt = default_jwt
        self._user_jwts: dict[str, str] = {}
        self._routes: dict[type[Command], str] = {}

    def register_policy(
        self,
        command_class: type[Command],
        policy: Policy,
        timing: EventTiming = EventTiming.BEFORE,
    ) -> None:
        raise ServiceException("Policies cannot be registered on RemoteApp instances")

    def unregister_policy(self, command_class: type[Command], policy: Policy, timing: EventTiming) -> None:
        raise ServiceException("Policies cannot be unregistered on RemoteApp instances")

    def register_user(self, user: User, jwt: str) -> None:
        """Register a user user with a jwt token, which will be used for requests."""
        self._user_jwts[user.get_key()] = jwt

    def register_route(self, command: Command, route: str, add_prefix: bool = True) -> None:
        """Registers route to the db on the command."""
        route = self._default_route_prefix + route if add_prefix else route
        self._routes[command] = route

    def get_headers(self, cmd: Command) -> dict[str, str]:
        jwt = self._user_jwts.get(cmd.user.get_key(), self._default_jwt) if cmd.user else self._default_jwt
        return {"Authorization": f"Bearer {jwt}"} if jwt else {}

    def apply_handler(
        self,
        command: Command,
        handler: Callable[[Command], Any],
    ) -> Any:
        command_class = command.__class__
        if command_class not in self._routes:
            if isinstance(command, CrudCommand):
                route = f"{self._default_route_prefix}/{command.MODEL_CLASS.ENTITY.snake_case_plural_name}"
            else:
                # non CRUD commands dont always have a MODEL_CLASS
                route = f"{self._default_route_prefix}/{command_class.__name__.lower().replace('command', '')}"
        else:
            route = self._routes.get(command_class, None)
        if not route:
            raise NotImplementedError(f"No route registered for command: {command.__class__.__name__}")

        headers = self.get_headers(command)
        if isinstance(command, CrudCommand):
            handler = self.create_crud_handler(command, route, headers)
        else:
            handler = self.create_non_crud_handler(command, route, headers, handler)
        return handler(command)

    def create_crud_handler(self, cmd: CrudCommand, route_prefix: str, headers: dict[str, str]) -> Callable[[Command], Any]:
        model_class = cmd.MODEL_CLASS
        entity = model_class.ENTITY
        assert entity is not None
        route = f"{route_prefix}/{entity.snake_case_plural_name}"
        self.register_route(cmd.__class__, route, add_prefix=False)

        def handler(cmd: CrudCommand, route: str) -> Any:

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
    def _content_to_obj(response: httpx.Response, retval_class: Type, is_list: bool = False) -> Any:
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
