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
        self.register_handler(
            command.RetrieveSamplesByIdCommand, self.handle_retrieve_samples_by_id
        )
        self.register_handler(
            command.RetrieveSampleIdentifiersByIdCommand,
            self.handle_retrieve_sample_identifiers_by_id,
        )
        self.register_handler(
            command.RetrieveSamplesByQueryCommand,
            self.handle_retrieve_sample_ids_by_query,
        )

    def handle_update_user_own_organization(
        self,
        cmd: command.UpdateUserOwnOrganizationCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        # Import the request body model here so that the APP_COMPOSER is not created
        # before the cfg is updated, since the APP_COMPOSER is imported in the routers
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

    def handle_retrieve_samples_by_id(
        self,
        cmd: command.RetrieveSamplesByIdCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.post(
            route_prefix + "/retrieve/samples_by_id",
            headers=headers,
            json=json.loads(cmd.model_dump_json(exclude={"user"})),
        )
        retval = self._content_to_obj(response, model.FullSample, is_list=True)
        return retval, response

    def handle_retrieve_sample_identifiers_by_id(
        self,
        cmd: command.RetrieveSampleIdentifiersByIdCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.post(
            route_prefix + "/retrieve/sample_identifiers_by_ids",
            headers=headers,
            json=json.loads(cmd.model_dump_json(exclude={"user"})),
        )
        retval = self._content_to_obj(response, model.SampleIdentifier, is_list=True)
        return retval, response

    def handle_retrieve_sample_ids_by_query(
        self,
        cmd: command.RetrieveSamplesByQueryCommand,
        route_prefix: str,
        headers: dict[str, str] | None,
    ) -> tuple[Any, Response]:
        response = self.test_client.post(
            route_prefix + "/retrieve/sample_ids_by_query",
            headers=headers,
            json=json.loads(cmd.model_dump_json(exclude={"user"})),
        )
        retval = self._content_to_obj(response, model.SampleQueryResult)
        return retval, response
