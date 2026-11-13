from enum import Enum

from gen_epix.omopdb.config import cfg as omopdb_cfg
from gen_epix.omopdb.domain import enum as omopdb_enum


def test_omopdb_defaults_layer_over_shared_defaults(monkeypatch):
    monkeypatch.setenv("OMOPDB_SETTINGS_FILES", "config/no_identity_providers.toml")
    monkeypatch.setenv("OMOPDB_REPOSITORY__DEFAULTS__PROPS__UID", "test-user")
    monkeypatch.setenv("OMOPDB_REPOSITORY__DEFAULTS__PROPS__PWD", "test-password")

    cfg = omopdb_cfg.OmopdbAppCfg(log_any=False, log_setup=False)

    assert cfg.app_name == "OMOPDB"
    assert cfg.service_type_enum is omopdb_enum.ServiceType
    assert cfg.repository_type_enum is omopdb_enum.RepositoryType
    assert cfg.cfg["app"]["port"] == 8002
    assert cfg.cfg["app"]["host"] == "0.0.0.0"
    assert cfg.cfg["service"]["auth"]["props"]["auto_created_user"]["roles"] == [
        "OMOPDB_ORG_USER"
    ]
    assert cfg.cfg["service"]["omop"]["module"] == "gen_epix.omopdb.services"
    assert cfg.cfg["service"]["omop"]["class_name"] == "OmopService"
    assert cfg.cfg["repository"]["defaults"]["props"]["database"] == "omopdb"
    assert cfg.cfg["repository"]["omop"]["class_name"] == "OmopSARepository"


def test_constructor_forwards_arguments_to_app_cfg(monkeypatch):
    class CustomServiceType(Enum):
        """Represent test service types."""

        SERVICE = "SERVICE"

    class CustomRepositoryType(Enum):
        """Represent test repository types."""

        REPOSITORY = "REPOSITORY"

    received = {}

    def capture_init(
        self, app_name_or_enum, service_type_enum, repository_type_enum, **kwargs
    ):
        received["args"] = (app_name_or_enum, service_type_enum, repository_type_enum)
        received["kwargs"] = kwargs

    monkeypatch.setattr(omopdb_cfg.AppCfg, "__init__", capture_init)

    omopdb_cfg.OmopdbAppCfg(
        "CUSTOM",
        CustomServiceType,
        CustomRepositoryType,
        settings_files=["custom.toml"],
    )

    assert received == {
        "args": ("CUSTOM", CustomServiceType, CustomRepositoryType),
        "kwargs": {"settings_files": ["custom.toml"]},
    }
