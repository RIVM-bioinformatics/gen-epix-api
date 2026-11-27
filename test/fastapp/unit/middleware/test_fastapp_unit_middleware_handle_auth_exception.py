"""Verify authentication exceptions can be logged without a FastApp instance."""

import logging

from fastapi import FastAPI

from gen_epix.fastapp.middleware.handle_auth_exception import (
    HandleAuthExceptionMiddleware,
)


def test_logger_only_construction_logs_auth_exception(caplog) -> None:
    """Log the exception text when no FastApp log-message factory is supplied."""
    logger = logging.getLogger("auth-middleware-test")
    middleware = HandleAuthExceptionMiddleware(FastAPI(), logger=logger)

    with caplog.at_level(logging.WARNING, logger=logger.name):
        middleware._log_exception(ValueError("invalid token"))

    assert "invalid token" in caplog.text
