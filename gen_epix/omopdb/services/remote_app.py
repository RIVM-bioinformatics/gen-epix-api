import json
from typing import Any

from gen_epix.commondb.services import CommondbRemoteApp as CommondbRemoteApp
from gen_epix.fastapp.model import Command
from gen_epix.omopdb.domain import DOMAIN, command, model


class OmopdbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.UploadPersonsCommand: "/upload/persons",
    }

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        command.UploadPersonsCommand: 45.0,
        command.RetrievePersonsByIdCommand: 45.0,
        command.RetrievePersonsByQueryCommand: 45.0,
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

    def upload_persons(
        self,
        cmd: command.UploadPersonsCommand,
    ) -> model.PersonBatchUploadResult:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = cmd

        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return model.PersonBatchUploadResult(**data)
