"""Pydantic schema for settings validation."""

from pydantic import BaseModel, ConfigDict, Field


class HttpHeaderConfig(BaseModel):
    """HTTP header configuration."""

    CacheControl: str = Field(default="no-cache, no-store")
    ContentSecurityPolicy: str = Field(
        default="default-src 'none'; frame-ancestors 'none'; sandbox",
        alias="Content-Security-Policy",
    )
    CrossOriginOpenerPolicy: str = Field(
        default="same-origin", alias="Cross-Origin-Opener-Policy"
    )
    Expires: str = Field(default="0")
    Pragma: str = Field(default="no-cache")
    ReferrerPolicy: str = Field(
        default="strict-origin-when-cross-origin", alias="Referrer-Policy"
    )
    StrictTransportSecurity: str = Field(
        default="max-age=63072000; includeSubDomains", alias="Strict-Transport-Security"
    )
    XContentTypeOptions: str = Field(default="nosniff", alias="X-Content-Type-Options")
    XFrameOptions: str = Field(default="DENY", alias="X-Frame-Options")
    XXSSProtection: str = Field(default="1; mode=block", alias="X-XSS-Protection")


class HttpHeadersConfig(BaseModel):
    """HTTP headers configuration for different contexts."""

    general: HttpHeaderConfig = Field(default_factory=HttpHeaderConfig)
    openapi: HttpHeaderConfig = Field(default_factory=HttpHeaderConfig)
    auth: HttpHeaderConfig = Field(default_factory=HttpHeaderConfig)


class ApiRouteConfig(BaseModel):
    """API route configuration."""

    v1: str = Field(default="/v1")


class ApiConfig(BaseModel):
    """API configuration."""

    default_route: str = Field(default="/openapi.json")
    gzip_response_minimum_size: int = Field(default=1024)
    http_header: HttpHeadersConfig = Field(default_factory=HttpHeadersConfig)
    route: ApiRouteConfig = Field(default_factory=ApiRouteConfig)


class AppConfig(BaseModel):
    """Application configuration."""

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    debug: bool = Field(default=False)


class LogConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="DEBUG")


class ServiceDefaultsConfig(BaseModel):
    """Service defaults configuration."""

    id_factory: str = Field(default="ULID")
    timestamp_factory: str = Field(default="DATETIME_NOW")


class ServiceRbacConfig(BaseModel):
    """Service RBAC configuration."""

    user_invitation_time_to_live: int = Field(default=604800)  # One week in seconds


class ServiceConfig(BaseModel):
    """Service configuration."""

    defaults: ServiceDefaultsConfig = Field(default_factory=ServiceDefaultsConfig)
    rbac: ServiceRbacConfig = Field(default_factory=ServiceRbacConfig)


class SettingsSchema(BaseModel):
    """Main settings schema."""

    model_config = ConfigDict(
        extra="allow"
    )  # Allow additional fields for extensibility

    app: AppConfig = Field(default_factory=AppConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    log: LogConfig = Field(default_factory=LogConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
