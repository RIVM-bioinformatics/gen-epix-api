"""Capture redacted host metadata and configuration without composing an app."""

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import resource
import subprocess
import sys
from pathlib import Path

from .models import ROOT, Metadata, Options

_SENSITIVE = re.compile(
    r"password|passwd|pwd|secret|token|credential|authorization|cookie|uid|username|dsn|connection_string",
    re.IGNORECASE,
)


def redact(value, key: str = ""):
    """Remove credentials recursively, including opaque environment values."""
    if _SENSITIVE.search(key):
        return "<redacted>"
    if isinstance(value, dict):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v, key) for v in value]
    if isinstance(value, str) and re.search(
        r"(pwd|password|secret|token|uid)[\"\']?\s*[=:]|://[^/\s]*@",
        value,
        re.IGNORECASE,
    ):
        return "<redacted>"
    return (
        re.sub(r" at 0x[0-9a-fA-F]+(?=>)", "", value)
        if isinstance(value, str)
        else value
    )


def fingerprint(value) -> str:
    """Hash a stable non-secret representation for report compatibility."""
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, default=str).encode()
    ).hexdigest()


def file_fingerprints() -> dict[str, str]:
    """Fingerprint launcher configuration and certificates without their contents."""
    files = list((ROOT / "gen_epix").glob("*/config/*.toml"))
    files += (
        list((ROOT / "config").rglob("*.toml")) if (ROOT / "config").exists() else []
    )
    files += list((ROOT / "cert").glob("*.pem"))
    files += list((ROOT / "gen_epix").glob("*/config/*.yaml"))
    files += list((ROOT / "config").rglob("*.yaml"))
    return {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
    }


def capture(options: Options, env: dict[str, str]) -> Metadata:
    """Capture source, runtime, resource limits, and relevant redacted overrides."""

    def git(*args):
        result = subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
        )
        return result.stdout.strip() if result.returncode == 0 else None

    relevant = {
        k: v
        for k, v in env.items()
        if k.startswith(
            (
                "CASEDB_",
                "SEQDB_",
                "OMOPDB_",
                "COMMONDB_",
                "PYTHON",
                "COVERAGE",
                "UVICORN",
                "WEB_CONCURRENCY",
            )
        )
    }
    return {
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain")),
        "interpreter": sys.executable,
        "python": sys.version,
        "os": platform.platform(),
        "cpu_count": os.cpu_count(),
        "cpu_available": sorted(os.sched_getaffinity(0)),
        "resource_limits": {
            name: resource.getrlimit(getattr(resource, name))
            for name in ("RLIMIT_AS", "RLIMIT_CPU", "RLIMIT_NOFILE")
        },
        "dependencies": {
            d.metadata["Name"]: d.version
            for d in importlib.metadata.distributions()
            if d.metadata["Name"]
        },
        "environment": redact(relevant),
        "files": file_fingerprints(),
        "worker_count": 1,
        "tls": "https" if (ROOT / "cert/cert.pem").exists() else "http",
        "tls_insecure": options.insecure,
        "experiment": "fresh-process startup with ordinary system caches",
    }


def configuration_snapshot(options: Options, env: dict[str, str], output: Path) -> dict:
    """Run a metadata-only child and read its redacted configuration snapshot.

    Raises:
        ValueError: If configuration cannot be loaded without composition.
    """
    with (output.parent / (output.stem + ".log")).open("wb") as log:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.startup_benchmark.metadata",
                str(output),
                options.application.name,
                options.idp_mode,
                options.repository_mode,
            ],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=log,
            timeout=60,
            check=False,
        )
    if result.returncode != 0:
        raise ValueError(f"Configuration snapshot failed; see {output.stem}.log")
    return json.loads(output.read_text())


def snapshot_main() -> None:
    """Load existing configuration utilities in an isolated metadata process."""
    from gen_epix.commondb.domain.enum import AppType, DevIdpConfig, DevRepositoryConfig
    from gen_epix.commondb.domain.util import get_app_cfg_class, set_env_variables

    output, app, idp, repository = sys.argv[1:]
    selected = AppType[app.upper()]
    set_env_variables(selected, DevIdpConfig[idp], DevRepositoryConfig[repository])
    cfg = get_app_cfg_class(selected)()
    result = {
        "application": redact(cfg.to_dict(resolved=True, redact=True)),
        "debug": cfg.cfg["app"]["debug"],
    }
    if app == "casedb":
        result["seqdb_client_mode"] = cfg.cfg["service"]["seqdb"]["props"][
            "seqdb_client_type"
        ]
    if app == "casedb" and result["seqdb_client_mode"] == "LOCAL":
        result["seqdb"] = redact(
            get_app_cfg_class(AppType.SEQDB)().to_dict(resolved=True, redact=True)
        )
    result["settings_files"] = {
        k: v
        for k, v in os.environ.items()
        if k.endswith(("SETTINGS_FILES", "LOG_CONFIG_FILE"))
        and k.startswith((app.upper(), "SEQDB"))
    }
    Path(output).write_text(json.dumps(result, indent=2, default=str) + "\n")


if __name__ == "__main__":
    snapshot_main()
