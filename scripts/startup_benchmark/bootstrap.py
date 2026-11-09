"""Install diagnostic-only phase wrappers before executing the existing launcher."""

import contextvars
import functools
import inspect
import itertools
import json
import os
import runpy
import sys
import time
from pathlib import Path

_PARENT = contextvars.ContextVar("startup_span_parent", default=None)
_IDS = itertools.count()


class Recorder:
    """Encapsulates flushed span events and signature-preserving wrappers."""

    def __init__(self, path: Path, application: str | None = None):
        """Open the event stream before preparation imports begin."""
        self.stream = path.open("w")
        self.application = application

    def emit(self, event: dict) -> None:
        """Persist an event immediately so crashes retain incomplete spans."""
        self.stream.write(json.dumps({**event, "pid": os.getpid()}) + "\n")
        self.stream.flush()

    def wrap(self, function, name: str):
        """Preserve sync or async call behavior, return values, and exceptions."""
        signature = inspect.signature(function)

        def begin(args, kwargs):
            identifier = next(_IDS)
            bound = signature.bind_partial(*args, **kwargs).arguments
            label = self.application
            if args:
                obj = args[0]
                cfg = getattr(obj, "_app_cfg", None)
                label = getattr(obj, "_app_name", label)
                if cfg is not None:
                    label = cfg.app_name
            selected = bound.get("app_name_or_enum", bound.get("app_type"))
            if selected is not None:
                label = getattr(selected, "value", selected)
            service = bound.get("service_type")
            self.emit(
                {
                    "event": "start",
                    "id": identifier,
                    "parent": _PARENT.get(),
                    "name": name,
                    "label": str(label).lower() if label else None,
                    "service": (
                        str(getattr(service, "value", service))
                        if service is not None
                        else None
                    ),
                    "time_ns": time.perf_counter_ns(),
                    "async": inspect.iscoroutinefunction(function),
                }
            )
            return identifier, _PARENT.set(identifier)

        def finish(identifier, token, state):
            self.emit(
                {
                    "event": "end",
                    "id": identifier,
                    "time_ns": time.perf_counter_ns(),
                    "state": state,
                }
            )
            _PARENT.reset(token)

        if inspect.iscoroutinefunction(function):

            @functools.wraps(function)
            async def asynchronous(*args, **kwargs):
                identifier, token = begin(args, kwargs)
                state = "error"
                try:
                    result = await function(*args, **kwargs)
                    state = "complete"
                    return result
                finally:
                    finish(identifier, token, state)

            return asynchronous

        @functools.wraps(function)
        def synchronous(*args, **kwargs):
            identifier, token = begin(args, kwargs)
            state = "error"
            try:
                result = function(*args, **kwargs)
                state = "complete"
                return result
            finally:
                finish(identifier, token, state)

        return synchronous

    def hook(self, owner, attribute: str, name: str) -> None:
        """Wrap a verified boundary while preserving descriptor behavior.

        Raises:
            RuntimeError: If an installed dependency no longer exposes the hook.
            TypeError: If the boundary no longer has a callable API.
        """
        raw = inspect.getattr_static(owner, attribute, None)
        if raw is None:
            raise RuntimeError(f"Diagnostic hook unavailable: {name}")
        descriptor = type(raw) if isinstance(raw, (classmethod, staticmethod)) else None
        function = raw.__func__ if descriptor else getattr(owner, attribute)
        if not callable(function):
            raise TypeError(f"Diagnostic hook is not callable: {name}")
        wrapped = self.wrap(function, name)
        setattr(owner, attribute, descriptor(wrapped) if descriptor else wrapped)


def main() -> None:
    """Prepare hooks in the diagnostic child and delegate to run.py."""
    recorder = Recorder(Path(sys.argv[1]), sys.argv[3])

    def install():
        import sqlalchemy
        import uvicorn
        from sqlalchemy.engine import Engine
        from uvicorn.lifespan.on import LifespanOn

        from gen_epix.commondb import app_setup
        from gen_epix.commondb.config.cfg import AppCfg
        from gen_epix.commondb.domain import util
        from gen_epix.commondb.env import AppComposer

        recorder.hook(util, "set_env_variables", "environment bootstrap")
        for attribute in (
            "__init__",
            "_init_configure_loggers",
            "_init_load_settings",
            "_init_validate_settings",
        ):
            recorder.hook(AppCfg, attribute, "AppCfg." + attribute)
        for attribute in ("compose_application", "_init_service", "_create_repository"):
            recorder.hook(AppComposer, attribute, "composition." + attribute)
        recorder.hook(app_setup, "create_fast_api", "FastAPI factory")
        recorder.hook(sqlalchemy, "create_engine", "SQLAlchemy engine creation")
        # Record factory cache lookups separately from actual engine creation.
        from gen_epix.fastapp.repositories.sa.engine_factory import EngineFactory

        recorder.hook(EngineFactory, "create_engine", "SQLAlchemy engine factory")
        recorder.hook(Engine, "connect", "SQLAlchemy connection acquisition")
        recorder.hook(uvicorn.Config, "load", "Uvicorn app loading and configuration")
        recorder.hook(LifespanOn, "startup", "Uvicorn lifespan startup")
        recorder.hook(uvicorn.Server, "startup", "Uvicorn server startup")

    try:
        recorder.wrap(install, "instrumentation preparation")()
        sys.argv = ["run.py", *sys.argv[2:]]
        runpy.run_path("run.py", run_name="__main__")
    finally:
        recorder.stream.close()


if __name__ == "__main__":
    main()
