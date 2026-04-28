import json
from typing import Any

from gen_epix.casedb.domain import DOMAIN, command, model
from gen_epix.commondb.services import CommondbRemoteApp as CommondbRemoteApp
from gen_epix.fastapp.model import Command


class CasedbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.UploadCasesCommand: "/upload/cases",
    }

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        command.UploadCasesCommand: 45.0,
        command.RetrieveCasesByIdCommand: 45.0,
        command.RetrieveCasesByQueryCommand: 45.0,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)

        # Register routes
        for cmd_class, route in self.ROUTE_MAP.items():
            self.register_route(cmd_class, route)
        # Register handlers
        self.register_handler(
            command.UploadCasesCommand,
            self.upload_cases,
        )

    def upload_cases(
        self,
        cmd: command.UploadCasesCommand,
    ) -> model.CaseBatchUploadResult:
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
        return model.CaseBatchUploadResult(**data)
