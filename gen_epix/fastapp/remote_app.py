import json
from functools import partial
from typing import Any, Callable

from gen_epix.fastapp import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.enum import CrudOperation, EventTiming
from gen_epix.fastapp.exc import ServiceException
from gen_epix.fastapp.model import Command, CrudCommand, Policy, User


class RemoteApp(App):
    def __init__(
        self, domain: Domain, default_route_prefix: str, default_jwt: str, **kwargs: Any
    ) -> None:
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
        jwt = (
            self._user_jwts.get(cmd.user.get_key(), self._default_jwt)
            if cmd.user
            else self._default_jwt
        )
        return {"Authorization": f"Bearer {jwt}"} if jwt else {}

    def apply_handler(
        self,
        command: Command,
        handler: Callable[[Command], Any],
    ) -> Any:
        route = self._routes.get(command)
        if not route:
            raise NotImplementedError(
                f"No route registered for command: {command.__class__.__name__}"
            )

        headers = self.get_headers(command)
        handler = self.create_crud_handler(command, route, headers)
        return handler(command)

    def create_crud_handler(
        self, cmd: CrudCommand, route_prefix: str, headers: dict[str, str]
    ) -> Callable[[Command], Any]:
        model_class = cmd.MODEL_CLASS
        entity = model_class.ENTITY
        assert entity is not None
        route = f"{route_prefix}/{entity.snake_case_plural_name}"

        def handler(cmd: CrudCommand, route: str) -> Any:

            if cmd.operation == CrudOperation.READ_ALL:
                if cmd.query_filter:
                    response = self.test_client.post(
                        route + "/query",
                        json=json.loads(cmd.query_filter.model_dump_json()),
                        headers=headers,
                    )
                else:
                    response = self.test_client.get(route, headers=headers)
                retval = self._content_to_obj(response, model_class, is_list=True)
            elif cmd.operation == CrudOperation.READ_SOME:
                assert isinstance(cmd.obj_ids, list)
                ids = json.dumps([str(x) for x in cmd.obj_ids])
                response = self.test_client.get(
                    f"{route}/batch",
                    headers=headers,
                    params={"ids": ids},
                )
                retval = self._content_to_obj(response, model_class, is_list=True)
            elif cmd.operation == CrudOperation.READ_ONE:
                response = self.test_client.get(
                    f"{route}/{cmd.obj_ids}",
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class)
            elif cmd.operation == CrudOperation.CREATE_ONE:
                assert isinstance(cmd.objs, model.Model)
                response = self.test_client.post(
                    f"{route}",
                    json=json.loads(cmd.objs.model_dump_json()),
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class)
            elif cmd.operation == CrudOperation.CREATE_SOME:
                assert isinstance(cmd.objs, list)
                response = self.test_client.post(
                    f"{route}/batch",
                    json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class, is_list=True)
            elif cmd.operation == CrudOperation.UPDATE_ONE:
                assert isinstance(cmd.objs, model.Model)
                response = self.test_client.put(
                    f"{route}/{cmd.objs.id}",
                    json=json.loads(cmd.objs.model_dump_json()),
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class)
            elif cmd.operation == CrudOperation.UPDATE_SOME:
                assert isinstance(cmd.objs, list)
                response = self.test_client.put(
                    f"{route}",
                    json=[json.loads(x.model_dump_json()) for x in cmd.objs],
                    headers=headers,
                )
                retval = self._content_to_obj(response, model_class, is_list=True)
            elif cmd.operation == CrudOperation.DELETE_ONE:
                assert isinstance(cmd.obj_ids, UUID)
                response = self.test_client.delete(
                    f"{route}/{cmd.obj_ids}", headers=headers
                )
                retval = self._content_to_obj(response, UUID)
            elif cmd.operation == CrudOperation.DELETE_SOME:
                assert isinstance(cmd.obj_ids, list)
                ids = json.dumps([str(x) for x in cmd.obj_ids])
                response = self.test_client.delete(
                    f"{route}/batch",
                    headers=headers,
                    params={"ids": ids},
                )
                retval = self._content_to_obj(response, UUID, is_list=True)
            else:
                raise NotImplementedError(f"Unsupported operation: {cmd.operation}")
            return retval, response

        return partial(handler, route)
