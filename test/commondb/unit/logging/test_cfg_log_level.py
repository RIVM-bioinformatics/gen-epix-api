import json
import logging

from gen_epix.commondb.config.cfg import AppCfg


class _DummyHandler:
    def __init__(self, level: int = logging.INFO) -> None:
        self.level = level

    def setLevel(self, level: int | str) -> None:
        self.level = level


class _DummyLogger:
    def __init__(self, name: str, handlers: list[_DummyHandler] | None = None) -> None:
        self.name = name
        self.level: int | str | None = None
        self.handlers: list[_DummyHandler] = handlers or [_DummyHandler()]
        self.messages: list[tuple[str, str]] = []

    def setLevel(self, level: int | str) -> None:
        self.level = level

    def debug(self, msg: str) -> None:
        self.messages.append(("DEBUG", msg))

    def info(self, msg: str) -> None:
        self.messages.append(("INFO", msg))


def _build_test_fixture(
    *, shared_handler: bool, log_setup: bool
) -> tuple[AppCfg, dict[str, _DummyLogger], _DummyHandler]:
    app_cfg = AppCfg.__new__(AppCfg)
    app_cfg._envvar_prefix = "CASEDB_"
    app_cfg._logger_prefix = "casedb"
    app_cfg._log_level_envvar = "LOG_LEVEL"
    app_cfg._log_setup = log_setup
    app_cfg._cfg = {"log": {"level": "INFO"}}
    app_cfg._logging_config_yaml = {
        "loggers": {
            "casedb.setup": {"level": "INFO"},
            "casedb.service": {"level": "INFO"},
            "casedb.app": {"level": "INFO"},
            "casedb.api": {"level": "INFO"},
            "casedb.external": {"level": "INFO"},
            "sqlalchemy.engine": {"level": "WARNING"},
            "sqlalchemy.pool": {"level": "WARNING"},
            "httpx": {"level": "INFO"},
            "asyncio": {"level": "WARNING"},
            "uvicorn.error": {"level": "INFO"},
        }
    }
    handler = _DummyHandler()
    logger_map: dict[str, _DummyLogger] = {}
    for logger_name in app_cfg._logging_config_yaml["loggers"]:
        handlers = [handler] if shared_handler else [_DummyHandler()]
        logger_map[logger_name] = _DummyLogger(logger_name, handlers=handlers)

    app_cfg._setup_logger = logger_map["casedb.setup"]
    app_cfg._service_logger = logger_map["casedb.service"]
    app_cfg._app_logger = logger_map["casedb.app"]
    app_cfg._api_logger = logger_map["casedb.api"]

    return app_cfg, logger_map, handler


def _patch_logging_get_logger(monkeypatch, logger_map: dict[str, _DummyLogger]) -> None:
    original_get_logger = logging.getLogger

    def _get_logger(name: str | None = None):  # type: ignore[no-untyped-def]
        if name is None:
            return original_get_logger()
        return logger_map[name]

    monkeypatch.setattr(logging, "getLogger", _get_logger)


def _patch_runtime_logger_dict(monkeypatch, names: list[str] | None = None) -> None:
    logger_names = names or []
    monkeypatch.setattr(
        logging.root.manager,
        "loggerDict",
        {name: object() for name in logger_names},
    )


def _extract_diagnostic_payload(logger: _DummyLogger) -> dict:
    for level, msg in reversed(logger.messages):
        if level != "INFO":
            continue
        payload = json.loads(msg)
        if payload.get("msg") == "APPLIED_LOG_LEVEL":
            return payload
    raise AssertionError("Missing APPLIED_LOG_LEVEL diagnostic payload")


def test_set_log_level_preserves_pinned_third_party_loggers_without_handler_overwrite(
    monkeypatch,
) -> None:
    app_cfg, logger_map, shared_handler = _build_test_fixture(
        shared_handler=True, log_setup=False
    )
    logger_map["sqlalchemy.engine.Engine"] = _DummyLogger("sqlalchemy.engine.Engine")
    logger_map["sqlalchemy.pool.impl.QueuePool"] = _DummyLogger(
        "sqlalchemy.pool.impl.QueuePool"
    )
    _patch_logging_get_logger(monkeypatch, logger_map)
    monkeypatch.setattr(
        logging.root.manager,
        "loggerDict",
        {
            "sqlalchemy.engine.Engine": object(),
            "sqlalchemy.pool.impl.QueuePool": object(),
        },
    )

    app_cfg.set_log_level("DEBUG")

    assert app_cfg._cfg["log"]["level"] == "DEBUG"
    assert shared_handler.level == logging.NOTSET
    assert logger_map["casedb.setup"].level == "INFO"
    assert logger_map["casedb.service"].level == "INFO"
    assert logger_map["casedb.app"].level == "INFO"
    assert logger_map["casedb.api"].level == "INFO"
    assert logger_map["casedb.external"].level == "INFO"
    assert logger_map["sqlalchemy.engine"].level == "WARNING"
    assert logger_map["sqlalchemy.pool"].level == "WARNING"
    assert logger_map["sqlalchemy.engine.Engine"].level == "WARNING"
    assert logger_map["sqlalchemy.pool.impl.QueuePool"].level == "WARNING"
    assert logger_map["httpx"].level == "INFO"
    assert logger_map["asyncio"].level == "WARNING"
    assert logger_map["uvicorn.error"].level == "DEBUG"


def test_set_log_level_diagnostic_precedence_arg_over_env_and_settings(
    monkeypatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.setenv("CASEDB_LOG_LEVEL", "WARNING")

    app_cfg.set_log_level("ERROR")

    diagnostic = _extract_diagnostic_payload(logger_map["casedb.setup"])
    assert app_cfg._cfg["log"]["level"] == "ERROR"
    assert diagnostic["resolved_level"] == "ERROR"
    assert diagnostic["source"] == "arg"
    assert diagnostic["env_var_name"] == "CASEDB_LOG_LEVEL"
    assert diagnostic["env_var_value"] == "WARNING"
    assert diagnostic["settings_value"] == "INFO"


def test_set_log_level_diagnostic_precedence_env_over_settings(
    monkeypatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.setenv("CASEDB_LOG_LEVEL", "WARNING")

    app_cfg.set_log_level()

    diagnostic = _extract_diagnostic_payload(logger_map["casedb.setup"])
    assert app_cfg._cfg["log"]["level"] == "WARNING"
    assert diagnostic["resolved_level"] == "WARNING"
    assert diagnostic["source"] == "env"
    assert diagnostic["env_var_name"] == "CASEDB_LOG_LEVEL"
    assert diagnostic["env_var_value"] == "WARNING"
    assert diagnostic["settings_value"] == "INFO"


def test_set_log_level_diagnostic_precedence_settings_when_env_absent(
    monkeypatch,
) -> None:
    app_cfg, logger_map, _ = _build_test_fixture(shared_handler=False, log_setup=True)
    _patch_logging_get_logger(monkeypatch, logger_map)
    _patch_runtime_logger_dict(monkeypatch)
    monkeypatch.delenv("CASEDB_LOG_LEVEL", raising=False)

    app_cfg.set_log_level()

    diagnostic = _extract_diagnostic_payload(logger_map["casedb.setup"])
    assert app_cfg._cfg["log"]["level"] == "INFO"
    assert diagnostic["resolved_level"] == "INFO"
    assert diagnostic["source"] == "settings"
    assert diagnostic["env_var_name"] == "CASEDB_LOG_LEVEL"
    assert diagnostic["env_var_value"] is None
    assert diagnostic["settings_value"] == "INFO"
