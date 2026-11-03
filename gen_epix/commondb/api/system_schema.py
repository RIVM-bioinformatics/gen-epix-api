"""Request and response models of the commondb system API.

These models are kept apart from the routes that use them, so that a remote
client can import them without importing the web framework.
"""

from enum import Enum

from pydantic import BaseModel as PydanticBaseModel

from gen_epix.commondb.domain.model.system import PackageMetadata
from gen_epix.fastapp import LogLevel


class HealthStatus(Enum):
    """Encapsulates the externally reported application health state."""

    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"


class HealthResponseBody(PydanticBaseModel):
    """Represents the current application health state."""

    status: HealthStatus


class FeatureFlagsResponseBody(PydanticBaseModel):
    """Represents configured feature flags keyed by their public names."""

    feature_flags: dict[str, bool]


class ExternalLogItem(PydanticBaseModel):
    """Represents one externally submitted structured application log item."""

    level: LogLevel
    command_id: str
    timestamp: str
    duration: float | None = None
    software_version: str
    topic: str
    detail: str | dict | None = None


class LogRequestBody(PydanticBaseModel):
    """Represents structured log items submitted to the commondb logging endpoint."""

    log_items: list[ExternalLogItem]


class LicensesResponseBody(PydanticBaseModel):
    """Represents metadata for application and dependency package licenses."""

    packages: list[PackageMetadata]
