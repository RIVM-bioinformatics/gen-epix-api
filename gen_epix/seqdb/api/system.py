import json
import logging
from enum import Enum
from typing import Callable

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.common.api import exc
from gen_epix.fastapp import App, LogLevel
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.seqdb.api.base import EXCLUDED_PERMISSIONS
from gen_epix.seqdb.domain import command, enum, model

external_logger_fmap = exc.get_logger_fmap(logging.getLogger("seqdb.external"))


class LogItem(PydanticBaseModel):
    level: LogLevel
    command_id: str
    timestamp: str
    duration: float | None = None
    software_version: str
    topic: str
    detail: str | dict | None = None


class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


class HealthReponseBody(PydanticBaseModel):
    status: HealthStatus


class LogRequestBody(PydanticBaseModel):
    log_items: list[LogItem]


def create_system_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable | None = None,
    **kwargs: dict,
) -> None:

    assert handle_exception

    # Health endpoint
    @router.get(
        "/health",
        operation_id="health",
        name="Health",
    )
    async def health() -> HealthReponseBody:
        return HealthReponseBody(
            status=HealthStatus.HEALTHY,
        )

    # Log
    @router.post("/log", operation_id="log")
    async def log(user: registered_user_dependency, request_body: LogRequestBody) -> None:  # type: ignore
        try:
            user_id = str(user.id)  # type: ignore[attr-defined]
            for log_item in request_body.log_items:
                if isinstance(log_item.detail, str):
                    log_item.detail = json.loads(log_item.detail)
                content_str = app.create_log_message(
                    log_item.command_id,
                    None,
                    add_debug_info=False,
                    user_id=user_id,  # type: ignore[arg-type]
                    **log_item.model_dump(
                        exclude_none=True, exclude={"level", "command_id"}
                    ),
                )
                external_logger_fmap[log_item.level](content_str)
        except Exception as exception:
            handle_exception("09c8e2cd", user, exception)

    # Outage
    @router.get(
        "/retrieve/outages",
        operation_id="retrieve__outages",
        name="Outages",
    )
    async def retrieve__outages(
        idp_user: idp_user_dependency,  # type: ignore
    ) -> list[model.Outage]:
        try:
            cmd = command.RetrieveOutagesCommand(user=None)
            retval: list[model.Outage] = app.handle(cmd)
        except Exception as exception:
            handle_exception("6b47b8b6", None, exception)
        return retval

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=enum.ServiceType.SYSTEM,
        user_dependency=registered_user_dependency,
        excluded_permissions=EXCLUDED_PERMISSIONS,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
