import datetime
import json
import logging
from collections.abc import Callable, Hashable
from enum import Enum
from typing import Annotated, Any, NoReturn

from fastapi import APIRouter, FastAPI, Form
from fastapi.responses import Response
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.commondb.api import exc
from gen_epix.commondb.app_impl_details import AppImplDetails
from gen_epix.commondb.domain import command, enum, model
from gen_epix.commondb.domain.model.system import PackageMetadata
from gen_epix.fastapp import App, LogLevel
from gen_epix.fastapp.api import CrudEndpointGenerator
from gen_epix.fastapp.services.auth.service import AuthService

external_logger_fmap = exc.get_logger_fmap(logging.getLogger("commondb.external"))


class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


class HealthReponseBody(PydanticBaseModel):
    status: HealthStatus


class FeatureFlagsResponseBody(PydanticBaseModel):
    feature_flags: dict[str, bool]


class LogItem(PydanticBaseModel):
    level: LogLevel
    command_id: str
    timestamp: str
    duration: float | None = None
    software_version: str
    topic: str
    detail: str | dict | None = None


class LogRequestBody(PydanticBaseModel):
    log_items: list[LogItem]


class LicensesResponseBody(PydanticBaseModel):
    packages: list[PackageMetadata]


def create_system_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    service_type: enum.ServiceType = enum.ServiceType.SYSTEM,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    **kwargs: Any,
) -> None:

    assert handle_exception
    app_impl: AppImplDetails = app.impl
    registered_user_dependency = app_impl.registered_user_dependency
    idp_user_dependency = app_impl.idp_user_dependency

    # Health endpoint
    @router.get(
        "/health",
        operation_id="health",
        name="Health",
    )
    async def get__health() -> HealthReponseBody:
        """
        Returns the health status of the service. If no response is received
        within the timeout period, the service is considered unhealthy.
        """
        return HealthReponseBody(
            status=HealthStatus.HEALTHY,
        )

    @router.get(
        "/retrieve/feature_flags",
        operation_id="retrieve__feature_flags",
        name="Feature Flags",
        description=command.RetrieveFeatureFlagsCommand.__doc__,
    )
    async def retrieve__feature_flags() -> FeatureFlagsResponseBody:
        """
        Returns the feature flags of the application.
        """
        try:
            cmd = command.RetrieveFeatureFlagsCommand(user=None)
            feature_flags: dict[Hashable, bool] = app.handle(cmd)
            retval = {
                str(x.value) if isinstance(x, Enum) else str(x): y
                for x, y in feature_flags.items()
            }
        except Exception as exception:
            handle_exception("f8e8c5e6", None, exception)
        return FeatureFlagsResponseBody(feature_flags=retval)

    # Licenses endpoint
    @router.post(
        "/retrieve/licenses",
        operation_id="retrieve__licenses",
        name="Licenses",
        description=command.RetrieveLicensesCommand.__doc__,
    )
    async def retrieve__licenses(
        idp_user: idp_user_dependency,  # type: ignore
    ) -> list[model.PackageMetadata]:
        try:
            cmd = command.RetrieveLicensesCommand(user=None)
            retval: list[model.PackageMetadata] = app.handle(cmd)
        except Exception as exception:
            handle_exception("6ba2c4ca", None, exception)
        return retval

    # Log
    @router.post("/log", operation_id="log")
    async def log(user: registered_user_dependency, request_body: LogRequestBody) -> None:  # type: ignore
        """
        Logs the provided log items.
        """
        try:
            user_id = str(user.id)  # type: ignore[attr-defined]
            for log_item in request_body.log_items:
                if isinstance(log_item.detail, str):
                    log_item.detail = json.loads(log_item.detail)
                content_str = app.create_log_message(
                    log_item.command_id,
                    None,
                    add_debug_info=False,
                    user_id=user_id,
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
        description=command.RetrieveOutagesCommand.__doc__,
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

    # Export database
    @router.post(
        "/export/database",
        operation_id="export__database",
        name="Export Database",
        description=command.ExportDatabaseCommand.__doc__,
        response_class=Response,
    )
    async def export__database(
        token: Annotated[str, Form()],
    ) -> Response:
        """
        Export all application data as a SQL script for re-creating the
        database locally in Azure Data Studio.
        """
        user: model.User | None = None
        try:
            auth_service_type = next(
                k for k in app_impl.services if k.name == "AUTH"
            )
            auth_service: AuthService = app_impl.services[
                auth_service_type
            ]  # type: ignore[assignment]
            user = await auth_service.get_existing_user_from_token(token=token)  # type: ignore[assignment]
            cmd = command.ExportDatabaseCommand(user=user)
            sql_content: bytes = app.handle(cmd)
        except Exception as exception:
            handle_exception("b4e2f901", user, exception)
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%d_%H%M%S"
        )
        filename = f"database_export_{timestamp}.sql"
        return Response(
            content=sql_content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    # CRUD
    crud_endpoint_sets = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
        app,
        service_type=service_type,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
