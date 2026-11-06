"""Define launcher descriptors, validated options, and versioned run records."""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, TypedDict

SCHEMA_VERSION = 1
HEADER = "X-Startup-Benchmark-Instance"
IDP_MODES = ("IDPS", "MOCK", "NONE")
REPOSITORY_MODES = (
    "DICT_DEMO",
    "DICT_EMPTY",
    "SA_SQLITE_DEMO",
    "SA_SQLITE_EMPTY",
    "SA_SQL",
)
ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Application:
    """Encapsulates the fixed listener and configuration prefix for an app."""

    name: str
    port: int
    prefix: str

    @property
    def target(self) -> str:
        """Return the existing ASGI import target."""
        return f"gen_epix.{self.name}.app:FAST_API"


APPLICATIONS = {
    name: Application(name, port, name.upper())
    for name, port in (("casedb", 8000), ("seqdb", 8001), ("omopdb", 8002))
}


@dataclass(frozen=True)
class Options:
    """Encapsulates validated settings shared by measurements and diagnostics."""

    application: Application
    idp_mode: str
    repository_mode: str
    runs: int = 30
    warmups: int = 0
    readiness_timeout: float = 60
    poll_interval: float = 0.05
    request_timeout: float = 0.25
    settle_seconds: float = 1
    ca_file: str | None = None
    insecure: bool = False

    def validate(self) -> None:
        """Reject unsupported modes and nonfinite or invalid numeric settings.

        Raises:
            ValueError: If settings cannot define a bounded measurement.
        """
        if (
            self.idp_mode not in IDP_MODES
            or self.repository_mode not in REPOSITORY_MODES
        ):
            raise ValueError("Unsupported IDP or repository mode")
        if self.runs < 1 or self.warmups < 0:
            raise ValueError("runs must be positive and warmups nonnegative")
        for name in (
            "readiness_timeout",
            "poll_interval",
            "request_timeout",
            "settle_seconds",
        ):
            value = getattr(self, name)
            if (
                not math.isfinite(value)
                or value < 0
                or (name != "settle_seconds" and value == 0)
            ):
                raise ValueError(f"Invalid {name}")
        if self.ca_file and self.insecure:
            raise ValueError("Choose either --ca-file or --insecure")


@dataclass
class RunRecord:
    """Encapsulates one attempt, including failure and process cleanup evidence."""

    index: int
    kind: str
    status: str = "not_attempted"
    seconds: float | None = None
    started_ns: int | None = None
    ready_ns: int | None = None
    pid: int | None = None
    exit_code: int | None = None
    cleanup: str = "not_needed"
    error: str | None = None
    stdout: str | None = None
    stderr: str | None = None
    phases: str | None = None


class Metadata(TypedDict):
    """Represent redacted source, interpreter, environment, and host evidence."""

    commit: str | None
    dirty: bool
    interpreter: str
    python: str
    os: str
    cpu_count: int | None
    cpu_available: list[int]
    resource_limits: dict[str, tuple[int, int]]
    dependencies: dict[str, str]
    environment: dict[str, Any]
    files: dict[str, str]
    worker_count: int
    tls: str
    tls_insecure: bool
    experiment: str


class Artifact(TypedDict, total=False):
    """Represent the version-one JSON contract for saved benchmark evidence."""

    schema_version: int
    application: str
    command: Literal["benchmark", "diagnose"]
    options: dict[str, Any]
    metadata: Metadata
    records: list[dict[str, Any]]
    diagnostics: list[dict[str, Any]]
    commands: dict[str, list[str]]
    configuration: dict[str, Any]
    configuration_valid: bool
    configuration_fingerprint: str | None
    configuration_changes: list[dict[str, Any]]
    configuration_error: str
    series_completed: bool
    series_exit_code: int
    statistics: dict[str, Any]
