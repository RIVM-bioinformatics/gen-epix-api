"""Provide an in-process client that dispatches commondb commands to API endpoints."""

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

from gen_epix.commondb.api import InviteUserRequestBody, UpdateUserRequestBody
from gen_epix.commondb.domain import command, model
from gen_epix.fastapp import App, Command, CrudCommand, CrudOperation


class EndpointTestClient:
    """Encapsulates translation of supported commondb commands into FastAPI test-client requests."""

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
        user_invitation_request_body: type[PydanticBaseModel] = InviteUserRequestBody,
        update_user_request_body: type[PydanticBaseModel] = UpdateUserRequestBody,
        register_crud_commands: bool = True,
        route_prefix: str | None = None,
    ):
        """Initialize endpoint handlers and model classes used by the test client.

        Args:
            app: Composed application whose commands determine registered handlers.
            fast_api: FastAPI application receiving in-process HTTP requests.
            app_last_handled_exception: Shared exception diagnostic state.
            user_class: Model class used to deserialize user responses.
            user_invitation_class: Model class used to deserialize invitations.
            user_invitation_constraints_class: Model class for invitation constraints.
            organization_admin_policy_class: Model class for administrator policies.
            user_crud_command_class: Command class used for user CRUD.
            user_invitation_crud_command_class: Command class for invitation CRUD.
            organization_admin_policy_crud_command_class: Command class for policy CRUD.
            retrieve_invite_user_constraints_command_class: Constraints command class.
            invite_user_command_class: Invitation command class.
            register_invited_user_command_class: Registration command class.
            retrieve_organization_admin_name_emails_command_class: Admin lookup command.
            update_user_command_class: User update command class.
            user_invitation_request_body: Request schema for invitations.
            update_user_request_body: Request schema for user updates.
            register_crud_commands: Whether to register generic CRUD handlers.
            route_prefix: Optional prefix prepended to generated API routes.
        """
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
        """Register a command class with its endpoint-dispatch handler.

        Args:
            command_class: Command class accepted by the handler.
            handler: Function that turns the command into an HTTP request.
        """
        self._handlers[command_class] = handler

    def handle(
        self,
        cmd: Command,
        return_response: bool = False,
        route_prefix: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Dispatch a supported command to its corresponding API endpoint.

        Args:
            cmd: Command to translate into an HTTP request.
            return_response: Whether to return the raw HTTP response with the result.
            route_prefix: Optional prefix overriding the configured route prefix.
            **kwargs: Reserved options for specialized test clients.

        Returns:
            Deserialized endpoint result, optionally paired with its HTTP response.

        Raises:
            NotImplementedError: If no handler is registered for the command class.
        """
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
        """Request identity providers and deserialize the returned list.

        Args:
            cmd: Identity-provider command being dispatched.
            route_prefix: Prefix prepended to the identity-provider route.
            headers: Optional request headers.

        Returns:
            Deserialized identity providers and the HTTP response.
        """
        response = self.test_client.get(route_prefix + "/identity_providers")
        retval = self._content_to_obj(response, model.IdentityProvider, is_list=True)
        return retval, response

    def handle_invite_user(
        self,
        cmd: command.InviteUserCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        """Submit an invitation command to the invitation endpoint.

        Args:
            cmd: Invitation command supplying the request body.
            route_prefix: Prefix prepended to the invitation route.
            headers: Optional authorization headers.

        Returns:
            Deserialized invitation and the HTTP response.
        """
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
        """Request invitation constraints from the API.

        Args:
            cmd: Invitation-constraints command being dispatched.
            route_prefix: Prefix prepended to the constraints route.
            headers: Optional authorization headers.

        Returns:
            Deserialized constraints and the HTTP response.
        """
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
        """Register an invited user through the registration endpoint.

        Args:
            cmd: Registration command supplying the invitation token.
            route_prefix: Prefix prepended to the registration route.
            headers: Optional authorization headers.

        Returns:
            Deserialized registered user and the HTTP response.
        """
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
        """Submit a user-update command to the update endpoint.

        Args:
            cmd: User-update command supplying target and changed properties.
            route_prefix: Prefix prepended to the update route.
            headers: Optional authorization headers.

        Returns:
            Deserialized updated user and the HTTP response.
        """
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
        """Create test authorization headers for a command user when available.

        Args:
            cmd: Command whose user supplies the synthetic JWT identity.
            **kwargs: Reserved options for specialized test clients.

        Returns:
            Bearer-token headers, or None for commands without a user.

        Raises:
            ValueError: If the command user has neither a key nor email address.
        """
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
        """Create a signed test JWT with configurable standard claims.

        Args:
            email: Email and synthetic application key claim.
            iss: Optional issuer claim.
            sub: Optional subject claim.
            aud: Optional audience claim.
            exp: Optional expiration claim.
            expire_default_minutes: Expiry duration when ``exp`` is omitted.

        Returns:
            Encoded JWT signed with the test client's secret key.
        """
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
        """Create bearer authorization headers containing a synthetic JWT.

        Args:
            email: Email and synthetic application key claim.
            iss: Optional issuer claim.
            sub: Optional subject claim.
            aud: Optional audience claim.
            exp: Optional expiration claim.
            expire_default_minutes: Expiry duration when ``exp`` is omitted.

        Returns:
            Authorization header containing the encoded JWT.
        """
        return {
            "Authorization": f"Bearer {self.get_dummy_jwt(email, iss, sub, aud, exp, expire_default_minutes)}"
        }

    def handle_crud_command(
        self, cmd: CrudCommand, route_prefix: str, headers: dict[str, str] | None
    ) -> tuple[Any, Response]:
        """Dispatch a generic CRUD command to its model's REST endpoint.

        Args:
            cmd: CRUD command to translate into an HTTP request.
            route_prefix: Prefix prepended to the model route.
            headers: Optional authorization headers.

        Returns:
            Deserialized CRUD result and the HTTP response.

        Raises:
            NotImplementedError: If the CRUD operation is unsupported.
        """
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
        """Deserialize a successful HTTP response to the requested model type.

        Args:
            response: HTTP response returned by the test client.
            retval_class: Pydantic model or UUID class used for deserialization.
            is_list: Whether the response body contains a list of values.

        Returns:
            Deserialized response body, or None for an unsuccessful response.

        Raises:
            NotImplementedError: If the requested return type is unsupported.
        """
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
