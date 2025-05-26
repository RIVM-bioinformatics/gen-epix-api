import json
from enum import Enum
from test.test_client.endpoint_test_client import EndpointTestClient
from typing import Any

# import libraries
from fastapi import FastAPI, Response

from gen_epix.casedb.domain import command, model
from gen_epix.fastapp.app import App


class EndpointVersion(Enum):
    V1 = "v1"


class CasedbEndpointTestClient(EndpointTestClient):

    def __init__(
        self,
        app: App,
        fast_api: FastAPI,
        app_last_handled_exception: dict,
        **kwargs: dict,
    ):
        super().__init__(app, fast_api, app_last_handled_exception, **kwargs)
        self.register_handler(
            command.GetIdentityProvidersCommand, self.handle_get_identity_providers
        )
        self.register_handler(command.InviteUserCommand, self.handle_invite_user)
        self.register_handler(
            command.RegisterInvitedUserCommand, self.handle_register_invited_user
        )
        self.register_handler(command.UpdateUserCommand, self.handle_update_user)
        self.register_handler(
            command.UpdateUserOwnOrganizationCommand,
            self.handle_update_user_own_organization,
        )
        self.register_handler(
            command.RetrieveCasesByIdCommand, self.handle_retrieve_cases_by_id
        )
        self.register_handler(command.CasesCreateCommand, self.handle_cases_create)
        self.register_handler(command.CaseSetCreateCommand, self.handle_case_set_create)

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
        # Import the request body model here so that the APP_ENV is not created
        # before the cfg is updated, since the APP_ENV is imported in the routers
        from gen_epix.casedb.api.auth import UserInvitationRequestBody

        request_body = UserInvitationRequestBody(
            email=cmd.email,
            roles=cmd.roles,
            organization_id=cmd.organization_id,
        )
        response = self.test_client.post(
            route_prefix + "/user_invitations",
            json=json.loads(request_body.model_dump_json()),
            headers=headers,
        )
        retval = self._content_to_obj(response, model.UserInvitation)
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
        retval = self._content_to_obj(response, model.User)
        return retval, response

    def handle_update_user(
        self,
        cmd: command.UpdateUserCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        # Import the request body model here so that the APP_ENV is not created
        # before the cfg is updated, since the APP_ENV is imported in the routers
        from gen_epix.casedb.api.organization import UpdateUserRequestBody

        request_body = UpdateUserRequestBody(
            is_active=cmd.is_active,
            roles=cmd.roles,
            organization_id=cmd.organization_id,
        )
        cmd_dict = json.loads(cmd.model_dump_json())
        tgt_user_id = cmd_dict["tgt_user_id"]
        response = self.test_client.put(
            route_prefix + f"/users/{tgt_user_id}",
            headers=headers,
            json=json.loads(request_body.model_dump_json()),
        )
        retval = self._content_to_obj(response, model.User)
        return retval, response

    def handle_update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        # Import the request body model here so that the APP_ENV is not created
        # before the cfg is updated, since the APP_ENV is imported in the routers
        from gen_epix.casedb.api.organization import (
            UpdateUserOwnOrganizationRequestBody,
        )

        request_body = UpdateUserOwnOrganizationRequestBody(
            organization_id=cmd.organization_id,
        )
        response = self.test_client.put(
            route_prefix + f"/update_user_own_organization",
            headers=headers,
            json=json.loads(request_body.model_dump_json()),
        )
        retval = self._content_to_obj(response, model.User)
        return retval, response

    def handle_retrieve_cases_by_id(
        self,
        cmd: command.RetrieveCasesByIdCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.post(
            route_prefix + f"/retrieve/cases_by_ids",
            json=json.loads(cmd.model_dump_json())["case_ids"],
            headers=headers,
        )
        retval = self._content_to_obj(response, model.Case, is_list=True)
        return retval, response

    def handle_cases_create(
        self,
        cmd: command.CasesCreateCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        # Import the request body model here so that the APP_ENV is not created
        # before the cfg is updated, since the APP_ENV is imported in the routers
        from gen_epix.casedb.api.case import CreateCasesRequestBody

        request_body = CreateCasesRequestBody(
            cases=cmd.cases,
            data_collection_ids=cmd.data_collection_ids,
        )
        response = self.test_client.post(
            route_prefix + "/create/cases",
            headers=headers,
            json=json.loads(request_body.model_dump_json()),
        )
        retval = self._content_to_obj(response, model.Case, is_list=True)
        return retval, response

    def handle_case_set_create(
        self,
        cmd: command.CaseSetCreateCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        # Import the request body model here so that the APP_ENV is not created
        # before the cfg is updated, since the APP_ENV is imported in the routers
        from gen_epix.casedb.api.case import CreateCaseSetRequestBody

        request_body = CreateCaseSetRequestBody(
            case_set=cmd.case_set,
            data_collection_ids=cmd.data_collection_ids,
            case_ids=cmd.case_ids,
        )
        response = self.test_client.post(
            route_prefix + "/create/case_set",
            headers=headers,
            json=json.loads(request_body.model_dump_json()),
        )
        retval = self._content_to_obj(response, model.CaseSet)
        return retval, response
