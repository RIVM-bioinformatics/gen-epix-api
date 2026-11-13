"""Tests for seqdb application configuration behavior."""

from enum import Enum

from gen_epix.seqdb.config import cfg as seqdb_cfg
from gen_epix.seqdb.domain import enum as seqdb_enum


def test_seqdb_defaults_layer_over_shared_defaults(monkeypatch):
    """Use seqdb defaults while retaining inherited application settings."""
    monkeypatch.setenv("SEQDB_SETTINGS_FILES", "config/no_identity_providers.toml")
    monkeypatch.setenv("SEQDB_REPOSITORY__DEFAULTS__PROPS__UID", "test-user")
    monkeypatch.setenv("SEQDB_REPOSITORY__DEFAULTS__PROPS__PWD", "test-password")

    app_cfg = seqdb_cfg.SeqdbAppCfg(
        log_any=False,
        log_setup=False,
    )

    assert app_cfg.app_name == "SEQDB"
    assert app_cfg.service_type_enum is seqdb_enum.ServiceType
    assert app_cfg.repository_type_enum is seqdb_enum.RepositoryType
    assert app_cfg.cfg["app"]["port"] == 8001
    assert app_cfg.cfg["app"]["host"] == "0.0.0.0"
    assert app_cfg.cfg["service"]["auth"]["props"]["auto_created_user"]["roles"] == [
        "SEQDB_ORG_USER"
    ]
    assert app_cfg.cfg["service"]["seq"]["module"] == "gen_epix.seqdb.services"
    assert app_cfg.cfg["service"]["seq"]["class_name"] == "SeqService"
    assert app_cfg.cfg["service"]["file"]["class_name"] == "FileService"
    assert app_cfg.cfg["repository"]["defaults"]["props"]["database"] == "seqdb"
    assert app_cfg.cfg["repository"]["seq"]["class_name"] == "SeqSARepository"
    assert app_cfg.cfg["repository"]["file"]["class_name"] == "FileSARepository"


def test_constructor_forwards_arguments_to_app_cfg(monkeypatch):
    """Pass explicit application identity and keyword options to AppCfg."""

    class CustomServiceType(Enum):
        """Represent test service types."""

        SERVICE = "SERVICE"

    class CustomRepositoryType(Enum):
        """Represent test repository types."""

        REPOSITORY = "REPOSITORY"

    received = {}

    def capture_init(
        _self, app_name_or_enum, service_type_enum, repository_type_enum, **kwargs
    ):
        received["args"] = (app_name_or_enum, service_type_enum, repository_type_enum)
        received["kwargs"] = kwargs

    monkeypatch.setattr(seqdb_cfg.AppCfg, "__init__", capture_init)

    seqdb_cfg.SeqdbAppCfg(
        "CUSTOM",
        CustomServiceType,
        CustomRepositoryType,
        settings_files=["custom.toml"],
    )

    assert received == {
        "args": ("CUSTOM", CustomServiceType, CustomRepositoryType),
        "kwargs": {"settings_files": ["custom.toml"]},
    }
