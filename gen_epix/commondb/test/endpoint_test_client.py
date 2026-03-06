import json
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt

# import libraries
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.commondb.api import UpdateUserRequestBody, UserInvitationRequestBody
from gen_epix.commondb.domain import command, model
from gen_epix.fastapp import App, Command, CrudCommand, CrudOperation


class EndpointTestClient:

    SECRET_KEY = str(uuid.uuid4())
    ENCRYPTION_ALGORITHM = "HS256"

    def __init__(
        self,
        app: App,
        fast_api: FastAPI,
        app_last_handled_exception: dict,
        user_class: type[model.User] = model.User,
        user_invitation_class: type[model.UserInvitation] = model.UserInvitation,
        user_invitation_constraints_class: type[
            model.UserInvitationConstraints
        ] = model.UserInvitationConstraints,
        organization_admin_policy_class: type[
            model.OrganizationAdminPolicy
        ] = model.OrganizationAdminPolicy,
        user_crud_command_class: type[
            command.UserCrudCommand
        ] = command.UserCrudCommand,
        user_invitation_crud_command_class: type[
            command.UserInvitationCrudCommand
        ] = command.UserInvitationCrudCommand,
        organization_admin_policy_crud_command_class: type[
            command.OrganizationAdminPolicyCrudCommand
        ] = command.OrganizationAdminPolicyCrudCommand,
        retrieve_invite_user_constraints_command_class: type[
            command.RetrieveInviteUserConstraintsCommand
        ] = command.RetrieveInviteUserConstraintsCommand,
        invite_user_command_class: type[
            command.InviteUserCommand
        ] = command.InviteUserCommand,
        register_invited_user_command_class: type[
            command.RegisterInvitedUserCommand
        ] = command.RegisterInvitedUserCommand,
        retrieve_organization_admin_name_emails_command_class: type[
            command.RetrieveOrganizationAdminNameEmailsCommand
        ] = command.RetrieveOrganizationAdminNameEmailsCommand,
        update_user_command_class: type[
            command.UpdateUserCommand
        ] = command.UpdateUserCommand,
        user_invitation_request_body: type[
            PydanticBaseModel
        ] = UserInvitationRequestBody,
        update_user_request_body: type[PydanticBaseModel] = UpdateUserRequestBody,
        register_crud_commands: bool = True,
        route_prefix: str | None = None,
    ):
        self.app = app
        self.fast_api = fast_api
        self.test_client = TestClient(fast_api, raise_server_exceptions=False)
        self.user_class = user_class
        self.user_invitation_class = user_invitation_class
        self.user_invitation_constraints_class = user_invitation_constraints_class
        self.organization_admin_policy_class = organization_admin_policy_class
        self.user_crud_command_class = user_crud_command_class
        self.user_invitation_crud_command_class = user_invitation_crud_command_class
        self.organization_admin_policy_crud_command_class = (
            organization_admin_policy_crud_command_class
        )
        self.retrieve_invite_user_constraints_command_class = (
            retrieve_invite_user_constraints_command_class
        )
        self.invite_user_command_class = invite_user_command_class
        self.register_invited_user_command_class = register_invited_user_command_class
        self.retrieve_organization_admin_name_emails_command_class = (
            retrieve_organization_admin_name_emails_command_class
        )
        self.update_user_command_class = update_user_command_class
        self.user_invitation_request_body = user_invitation_request_body
        self.update_user_request_body = update_user_request_body
        self.route_prefix = route_prefix or ""
        self._handlers: dict[
            type[Command],
            Callable[[Command, str, dict[str, str] | None], tuple[Any, Response]],
        ] = {}
        if register_crud_commands:
            for crud_command_class in app.domain.crud_commands:
                self.register_handler(crud_command_class, self.handle_crud_command)  # type: ignore[arg-type]
        self.register_handler(
            command.GetIdentityProvidersCommand, self.handle_get_identity_providers
        )
        self.register_handler(self.invite_user_command_class, self.handle_invite_user)
        self.register_handler(
            self.retrieve_invite_user_constraints_command_class,
            self.handle_retrieve_invite_user_constraints,
        )
        self.register_handler(
            self.register_invited_user_command_class, self.handle_register_invited_user
        )
        self.register_handler(self.update_user_command_class, self.handle_update_user)

    def register_handler(
        self,
        command_class: type[Command],
        handler: Callable[[Command, str, dict[str, str] | None], tuple[Any, Response]],
    ) -> None:
        self._handlers[command_class] = handler

    def handle(
        self,
        cmd: Command,
        return_response: bool = False,
        route_prefix: str | None = None,
        **kwargs: Any,
    ) -> Any:
        route_prefix = route_prefix or self.route_prefix
        if cmd.user:
            headers = self.get_headers(cmd)
        else:
            headers = None
        handler = self._handlers.get(cmd.__class__)
        if not handler:
            raise NotImplementedError(f"Unsupported command: {cmd.__class__.__name__}")
        retval, response = handler(cmd, route_prefix, headers)
        if return_response:
            return retval, response
        return retval

    def handle_get_identity_providers(
        self,
        cmd: command.GetIdentityProvidersCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.get(route_prefix + "/identity_providers")
        retval = self._content_to_obj(response, model.IdentityProvider, is_list=True)
        return retval, response

    def handle_invite_user(
        self,
        cmd: command.InviteUserCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        request_body = self.user_invitation_request_body(
            key=cmd.key,
            email=cmd.email,
            name=cmd.name,
            roles=cmd.roles,
            organization_id=cmd.organization_id,
        )
        response = self.test_client.post(
            route_prefix + "/invite_user",
            json=json.loads(request_body.model_dump_json()),
            headers=headers,
        )
        retval = self._content_to_obj(response, self.user_invitation_class)
        return retval, response

    def handle_retrieve_invite_user_constraints(
        self,
        cmd: command.RetrieveInviteUserConstraintsCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.get(
            route_prefix + "/invite_user/constraints",
            headers=headers,
        )
        retval = self._content_to_obj(response, self.user_invitation_constraints_class)
        return retval, response

    def handle_register_invited_user(
        self,
        cmd: command.RegisterInvitedUserCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.post(
            route_prefix + f"/user_registrations/{cmd.token}",
            headers=headers,
        )
        retval = self._content_to_obj(response, self.user_class)
        return retval, response

    def handle_update_user(
        self,
        cmd: command.UpdateUserCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        request_body = self.update_user_request_body(
            is_active=cmd.is_active,
            roles=cmd.roles,
            organization_id=cmd.organization_id,
        )
        cmd_dict = json.loads(cmd.model_dump_json())
        tgt_user_id = cmd_dict["tgt_user_id"]
        response = self.test_client.put(
            route_prefix + f"/update_user/{tgt_user_id}",
            headers=headers,
            json=json.loads(request_body.model_dump_json()),
        )
        retval = self._content_to_obj(response, self.user_class)
        return retval, response

    def get_headers(self, cmd: Command, **kwargs: Any) -> dict[str, str] | None:
        if cmd.user:
            assert cmd.user is not None
            key_or_email = cmd.user.get_key() or cmd.user.email  # type: ignore[attr-defined]
            if not key_or_email:
                raise ValueError(
                    "Unable to build authorization header: user has neither key nor email"
                )
            headers = self.get_dummy_jwt_header(key_or_email)
        else:
            headers = None
        return headers

    def get_dummy_jwt(
        self,
        email: str,
        iss: str | None = None,
        sub: str | None = None,
        aud: str | None = None,
        exp: int | None = None,
        expire_default_minutes: int = 15,
    ) -> str:
        claims = {
            "__key__": email,
            "email": email,
            "iss": iss or f"https://{uuid.uuid4()}.org",
            "sub": sub or str(uuid.uuid4()),
            "aud": aud or str(uuid.uuid4()),
            "exp": exp
            or datetime.now(timezone.utc) + timedelta(minutes=expire_default_minutes),
        }
        encoded_jwt = jwt.encode(
            claims, self.SECRET_KEY, algorithm=self.ENCRYPTION_ALGORITHM
        )
        return encoded_jwt

    def get_dummy_jwt_header(
        self,
        email: str,
        iss: str | None = None,
        sub: str | None = None,
        aud: str | None = None,
        exp: int | None = None,
        expire_default_minutes: int = 15,
    ) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.get_dummy_jwt(email, iss, sub, aud, exp, expire_default_minutes)}"
        }

    def handle_crud_command(
        self, cmd: CrudCommand, route_prefix: str, headers: dict[str, str] | None
    ) -> tuple[Any, Response]:
        model_class = cmd.MODEL_CLASS
        entity = model_class.ENTITY
        assert entity is not None
        route = f"{route_prefix}/{entity.snake_case_plural_name}"
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

    @staticmethod
    def _content_to_obj(
        response: Response, retval_class: type, is_list: bool = False
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
