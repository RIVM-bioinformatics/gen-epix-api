from typing import Any

from gen_epix.commondb.services import CommondbRemoteApp as CommondbRemoteApp
from gen_epix.fastapp.enum import HttpMethod
from gen_epix.fastapp.model import Command
from gen_epix.omopdb import api
from gen_epix.omopdb.domain import DOMAIN, command, model


class OmopdbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.UploadPersonsCommand: "/upload/persons",
        command.RetrievePersonsByQueryCommand: "/retrieve/person_ids_by_query",
        command.RetrievePersonsByIdCommand: "/retrieve/persons_by_ids",
        command.RetrieveSpecimenIdsByCohortIdsCommand: (
            "/retrieve/specimen_ids_by_cohort_ids"
        ),
    }

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        command.UploadPersonsCommand: 45.0,
        command.RetrievePersonsByIdCommand: 45.0,
        command.RetrievePersonsByQueryCommand: 45.0,
        command.RetrieveSpecimenIdsByCohortIdsCommand: 45.0,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)

        # Register routes
        for cmd_class, route in self.ROUTE_MAP.items():
            self.register_route(cmd_class, route)
        # Register handlers
        self.register_handler(
            command.UploadPersonsCommand,
            self.upload_persons,
        )
        self.register_handler(
            command.RetrievePersonsByQueryCommand,
            self.retrieve_persons_by_query,
        )
        self.register_handler(
            command.RetrievePersonsByIdCommand,
            self.retrieve_persons_by_id,
        )
        self.register_handler(
            command.RetrieveSpecimenIdsByCohortIdsCommand,
            self.retrieve_specimen_ids_by_cohort_ids,
        )

    def upload_persons(
        self,
        cmd: command.UploadPersonsCommand,
    ) -> model.PersonBatchUploadResult:
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=cmd,
            exclude={"user"},
        )
        return model.PersonBatchUploadResult(**response_body)

    def retrieve_persons_by_query(
        self,
        cmd: command.RetrievePersonsByQueryCommand,
    ) -> model.PersonQueryResult:
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=cmd.person_query,
        )
        return model.PersonQueryResult(**response_body)

    def retrieve_persons_by_id(
        self,
        cmd: command.RetrievePersonsByIdCommand,
    ) -> list[model.FullPerson]:
        request_body = api.RetrievePersonsByIdsRequestBody(
            person_ids=cmd.person_ids,
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return [model.FullPerson(**person) for person in response_body]

    def retrieve_specimen_ids_by_cohort_ids(
        self,
        cmd: command.RetrieveSpecimenIdsByCohortIdsCommand,
    ) -> model.SpecimenIdsByCohortResult:
        request_body = api.RetrieveSpecimenIdsByCohortIdsRequestBody(
            cohort_definition_id=cmd.cohort_definition_id,
            cohort_ids=cmd.cohort_ids,
        )
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return model.SpecimenIdsByCohortResult(**response_body)
