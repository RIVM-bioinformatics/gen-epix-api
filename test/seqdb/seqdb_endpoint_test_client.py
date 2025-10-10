import json
from typing import Any

from fastapi import FastAPI, Response

from gen_epix.commondb.test.endpoint_test_client import EndpointTestClient
from gen_epix.fastapp.app import App
from gen_epix.seqdb.domain import command, model


class SeqdbEndpointTestClient(EndpointTestClient):

    def __init__(
        self,
        app: App,
        fast_api: FastAPI,
        app_last_handled_exception: dict,
        **kwargs: Any,
    ):
        super().__init__(app, fast_api, app_last_handled_exception, **kwargs)
        self.register_handler(
            command.UpdateUserOwnOrganizationCommand,
            self.handle_update_user_own_organization,
        )
        # self.register_handler(
        #     command.RetrieveCasesByIdCommand, self.handle_retrieve_cases_by_id
        # )
        # self.register_handler(command.CreateCasesCommand, self.handle_cases_create)
        # self.register_handler(command.CreateCaseSetCommand, self.handle_case_set_create)

    def handle_update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        # Import the request body model here so that the APP_ENV is not created
        # before the cfg is updated, since the APP_ENV is imported in the routers
        from gen_epix.casedb.api import UpdateUserOwnOrganizationRequestBody

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

    # def handle_retrieve_cases_by_id(
    #     self,
    #     cmd: command.RetrieveCasesByIdCommand,
    #     route_prefix: str,
    #     headers: dict[str, str] | None,
    # ) -> tuple[Any, Response]:
    #     response = self.test_client.post(
    #         route_prefix + f"/retrieve/cases_by_ids",
    #         json=json.loads(cmd.model_dump_json())["case_ids"],
    #         headers=headers,
    #     )
    #     retval = self._content_to_obj(response, model.Case, is_list=True)
    #     return retval, response
