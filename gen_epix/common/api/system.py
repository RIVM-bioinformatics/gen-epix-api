import importlib.metadata
import json
import logging
import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable, NoReturn

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel as PydanticBaseModel

from gen_epix.common.api import exc
from gen_epix.common.domain import command, enum, model
from gen_epix.fastapp import App, LogLevel
from gen_epix.fastapp.api import CrudEndpointGenerator

external_logger_fmap = exc.get_logger_fmap(logging.getLogger("casedb.external"))


class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


class HealthReponseBody(PydanticBaseModel):
    status: HealthStatus


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


class PackageMetadata(PydanticBaseModel):
    name: str
    version: str
    license: str | None = None
    homepage: str | None = None


class LicensesResponseBody(PydanticBaseModel):
    packages: list[PackageMetadata]


def _parse_requirements_file() -> list[str]:
    """Parse requirements.txt and extract package names."""
    requirements_path = Path(__file__).parent.parent.parent.parent / "requirements.txt"
    package_names = []

    if not requirements_path.exists():
        return package_names

    with open(requirements_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Extract package name (everything before version specifiers)
            match = re.match(r"^([a-zA-Z0-9_-]+)", line)
            if match:
                package_names.append(match.group(1))

    return package_names


def _get_package_metadata(package_name: str) -> PackageMetadata | None:
    """Get metadata for a specific package using importlib.metadata."""
    try:
        metadata = importlib.metadata.metadata(package_name)
        return PackageMetadata(
            name=metadata.get("Name", package_name),
            version=metadata.get("Version", "Unknown"),
            license=metadata.get("License"),
            homepage=metadata.get("Home-page"),
        )
    except importlib.metadata.PackageNotFoundError:
        # Package not installed or name doesn't match
        return None


def create_system_endpoints(
    router: APIRouter | FastAPI,
    app: App,
    registered_user_dependency: Callable | None = None,
    new_user_dependency: Callable | None = None,
    idp_user_dependency: Callable | None = None,
    handle_exception: Callable[[str, Any, Exception], NoReturn] | None = None,
    service_type: enum.ServiceType = enum.ServiceType.SYSTEM,
    **kwargs: Any,
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

    # Licenses endpoint
    @router.get(
        "/licenses",
        operation_id="licenses",
        name="Licenses",
    )
    async def licenses(
        idp_user: idp_user_dependency,  # type: ignore
    ) -> LicensesResponseBody:
        try:
            package_names = _parse_requirements_file()
            packages = []

            for package_name in package_names:
                metadata = _get_package_metadata(package_name)
                if metadata:
                    packages.append(metadata)

            return LicensesResponseBody(packages=packages)
        except Exception as exception:
            handle_exception("8f3a2b1c", None, exception)

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
        service_type=service_type,
        user_dependency=registered_user_dependency,
    )
    CrudEndpointGenerator.generate_endpoints(
        router, crud_endpoint_sets, handle_exception
    )
