import logging

from gen_epix.commondb.config.cfg import AppCfg


class _DummyHandler:
    def __init__(self, level: int = logging.INFO) -> None:
        self.level = level

    def setLevel(self, level: int | str) -> None:
        self.level = level


class _DummyLogger:
    def __init__(self) -> None:
        self.level: int | str | None = None
        self.handlers: list[_DummyHandler] = [_DummyHandler()]

    def setLevel(self, level: int | str) -> None:
        self.level = level


def test_set_log_level_preserves_pinned_third_party_loggers(
    monkeypatch,
) -> None:
    app_cfg = AppCfg.__new__(AppCfg)
    app_cfg._envvar_prefix = "CASEDB_"
    app_cfg._logger_prefix = "casedb"
    app_cfg._log_level_envvar = "LOG_LEVEL"
    app_cfg._log_setup = False
    app_cfg._cfg = {"log": {"level": "INFO"}}
    app_cfg._setup_logger = _DummyLogger()
    app_cfg._logging_config_yaml = {
        "loggers": {
            "casedb.setup": {"level": "INFO"},
            "casedb.service": {"level": "INFO"},
            "casedb.app": {"level": "INFO"},
            "sqlalchemy.engine": {"level": "WARNING"},
            "sqlalchemy.pool": {"level": "WARNING"},
            "httpx": {"level": "INFO"},
            "asyncio": {"level": "WARNING"},
        }
    }

    logger_map = {
        name: _DummyLogger() for name in app_cfg._logging_config_yaml["loggers"]
    }
    logger_map["sqlalchemy.engine.Engine"] = _DummyLogger()
    logger_map["sqlalchemy.pool.impl.QueuePool"] = _DummyLogger()

    original_get_logger = logging.getLogger

    def _get_logger(name: str | None = None):  # type: ignore[no-untyped-def]
        if name is None:
            return original_get_logger()
        return logger_map[name]

    monkeypatch.setattr(logging, "getLogger", _get_logger)
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
    assert logger_map["casedb.setup"].level == "INFO"
    assert logger_map["casedb.service"].level == "INFO"
    assert logger_map["casedb.app"].level == "INFO"
    assert logger_map["sqlalchemy.engine"].level == "WARNING"
    assert logger_map["sqlalchemy.pool"].level == "WARNING"
    assert logger_map["sqlalchemy.engine.Engine"].level == "WARNING"
    assert logger_map["sqlalchemy.pool.impl.QueuePool"].level == "WARNING"
    assert logger_map["httpx"].level == "INFO"
    assert logger_map["asyncio"].level == "WARNING"
