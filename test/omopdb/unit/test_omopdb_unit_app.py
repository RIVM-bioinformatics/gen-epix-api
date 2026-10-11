"""Exercise OMOPDB app bootstrap under local, empty-repository settings."""

import importlib
import os

import pytest
from fastapi import FastAPI

from gen_epix.commondb.domain.enum import (
    AppType,
    DevIdpConfig,
    DevRepositoryConfig,
)
from gen_epix.commondb.domain.util import set_env_variables


def test_fast_api_exposes_openapi_and_legacy_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build the app and retain its configured OpenAPI metadata and alias."""
    monkeypatch.setenv(
        "OMOPDB_SETTINGS_FILES", os.environ.get("OMOPDB_SETTINGS_FILES", "")
    )
    monkeypatch.setenv(
        "OMOPDB_LOG_CONFIG_FILE", os.environ.get("OMOPDB_LOG_CONFIG_FILE", "")
    )
    set_env_variables(
        AppType.OMOPDB,
        DevIdpConfig.NONE,
        DevRepositoryConfig.DICT_EMPTY,
    )

    omopdb_app = importlib.import_module("gen_epix.omopdb.app")

    assert isinstance(omopdb_app.FAST_API, FastAPI)
    assert omopdb_app.app is omopdb_app.FAST_API
    assert (
        omopdb_app.FAST_API.openapi()["info"]["title"]
        == omopdb_app.SCHEMA_KWARGS["title"]
    )
