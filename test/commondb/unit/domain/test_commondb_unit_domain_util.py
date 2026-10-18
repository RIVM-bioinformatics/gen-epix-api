"""Tests for common domain configuration utilities."""

import os
from contextlib import nullcontext
from enum import Enum
from pathlib import Path
from test.util.mock_compat import Mock
from typing import ClassVar

import pytest

from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain import util
from gen_epix.commondb.domain.enum import (
    AppType,
    DevIdpConfig,
    DevRepositoryConfig,
)
from gen_epix.commondb.domain.util import (
    _get_identity_provider_settings_file,
    _get_repository_settings_files,
    _resolve_extra_settings_files,
    complete_stored_model_field_props,
    create_demo_data_from_repository,
    get_app_cfg_class,
    get_app_cfgs,
    load_demo_data,
    register_domain_entities,
    set_env_variables,
)
from gen_epix.fastapp import Command, Model, ModelFieldProps, exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation


class _TestServiceType(Enum):
    FIRST = "FIRST"
    SECOND = "SECOND"


class _TestRepositoryType(Enum):
    DICT = "DICT"


@pytest.mark.parametrize("settings_files", [None, []])
def test_resolve_extra_settings_files_returns_none_when_absent(
    settings_files: list[Path] | None,
) -> None:
    """Normalize absent and empty optional settings-file inputs to None."""
    assert _resolve_extra_settings_files(settings_files) is None


def test_resolve_extra_settings_files_accepts_single_path_and_file_list(
    tmp_path: Path,
) -> None:
    """Resolve a single path or list of existing files to absolute paths."""
    first = tmp_path / "first.toml"
    second = tmp_path / "second.toml"
    first.touch()
    second.touch()

    assert _resolve_extra_settings_files(first) == [first.resolve()]
    assert _resolve_extra_settings_files([str(first), second]) == [
        first.resolve(),
        second.resolve(),
    ]


@pytest.mark.parametrize("is_directory", [False, True])
def test_resolve_extra_settings_files_rejects_non_files(
    tmp_path: Path, is_directory: bool
) -> None:
    """Reject paths that do not identify an existing regular file."""
    path = tmp_path / "missing.toml"
    if is_directory:
        path.mkdir()

    with pytest.raises(ValueError, match="does not exist or is not a file"):
        _resolve_extra_settings_files(path)


def test_get_app_cfg_class_resolves_shared_and_app_specific_classes() -> None:
    """Use AppCfg for commondb and each app's own configuration subclass."""
    assert get_app_cfg_class(AppType.COMMONDB) is AppCfg
    assert get_app_cfg_class("CASEDB").__name__ == "CasedbAppCfg"


@pytest.mark.parametrize(
    ("config", "filename"),
    [
        (DevIdpConfig.IDPS, "identity_providers.toml"),
        (DevIdpConfig.MOCK, "mock_identity_provider.toml"),
        (DevIdpConfig.NONE, "no_identity_providers.toml"),
    ],
    ids=["idps", "mock", "none"],
)
def test_get_identity_provider_settings_file(config, filename, tmp_path: Path) -> None:
    """Select the settings file corresponding to each supported IDP mode."""
    assert _get_identity_provider_settings_file(config, tmp_path) == tmp_path / filename


def test_get_identity_provider_settings_file_rejects_unknown_config(
    tmp_path: Path,
) -> None:
    """Reject IDP values outside the supported enum."""
    with pytest.raises(ValueError, match="Unknown dev_idp_config"):
        _get_identity_provider_settings_file("unexpected", tmp_path)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("config", "filenames"),
    [
        (
            DevRepositoryConfig.DICT_DEMO,
            ["settings.repository.dict.toml", "settings.repository.dict.demo.toml"],
        ),
        (
            DevRepositoryConfig.DICT_EMPTY,
            ["settings.repository.dict.toml", "settings.repository.dict.empty.toml"],
        ),
        (
            DevRepositoryConfig.SA_SQLITE_DEMO,
            [
                "settings.repository.sa_sqlite.toml",
                "settings.repository.sa_sqlite.demo.toml",
            ],
        ),
        (
            DevRepositoryConfig.SA_SQLITE_EMPTY,
            [
                "settings.repository.sa_sqlite.toml",
                "settings.repository.sa_sqlite.empty.toml",
            ],
        ),
    ],
    ids=["dict-demo", "dict-empty", "sqlite-demo", "sqlite-empty"],
)
def test_get_repository_settings_files_for_file_backends(
    config: DevRepositoryConfig, filenames: list[str], tmp_path: Path
) -> None:
    """Return the backend settings followed by the selected data variant."""
    assert _get_repository_settings_files(config, tmp_path) == [
        tmp_path / filename for filename in filenames
    ]


@pytest.mark.parametrize("exists", [False, True], ids=["absent", "present"])
def test_get_repository_settings_files_for_sql_secrets(
    exists: bool, tmp_path: Path
) -> None:
    """Load SQL secrets only when the optional file exists."""
    secrets_file = tmp_path / "secrets.repository.sa_sql.toml"
    if exists:
        secrets_file.touch()
    expected = [secrets_file] if exists else []

    assert (
        _get_repository_settings_files(DevRepositoryConfig.SA_SQL, tmp_path) == expected
    )


def test_get_repository_settings_files_rejects_unknown_config(tmp_path: Path) -> None:
    """Reject repository modes without a settings-file mapping."""
    with pytest.raises(ValueError, match="Unknown dev_repository_config"):
        _get_repository_settings_files("unexpected", tmp_path)  # type: ignore[arg-type]


def test_set_env_variables_resolves_names_and_preserves_settings_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Normalize string enums and append extra settings after built-in files."""
    general_path = tmp_path / "shared"
    config_path = tmp_path / "application"
    extra_file = tmp_path / "override.toml"
    extra_file.touch()
    monkeypatch.delenv("SEQDB_SETTINGS_FILES", raising=False)
    monkeypatch.delenv("SEQDB_LOG_CONFIG_FILE", raising=False)

    set_env_variables(
        "seqdb",
        "mock",
        "dict_empty",
        [extra_file],
        general_path,
        config_path,
    )

    assert os.environ["SEQDB_SETTINGS_FILES"].split(",") == [
        str((config_path / "settings.toml").resolve()),
        str((general_path / "mock_identity_provider.toml").resolve()),
        str((config_path / "settings.repository.dict.toml").resolve()),
        str((config_path / "settings.repository.dict.empty.toml").resolve()),
        str(extra_file.resolve()),
    ]
    assert os.environ["SEQDB_LOG_CONFIG_FILE"] == str(
        (config_path / "logging.yaml").resolve()
    )


def test_set_env_variables_sets_every_app_and_casedb_seqdb_pair(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Apply ALL to every app and CASEDB to both casedb and seqdb."""
    monkeypatch.setattr(util, "get_package_root", lambda: tmp_path)
    for app_type in AppType:
        if app_type is not AppType.ALL:
            monkeypatch.delenv(f"{app_type.value}_SETTINGS_FILES", raising=False)
            monkeypatch.delenv(f"{app_type.value}_LOG_CONFIG_FILE", raising=False)

    set_env_variables(AppType.ALL, DevIdpConfig.NONE, DevRepositoryConfig.DICT_EMPTY)
    for app_type in AppType:
        if app_type is not AppType.ALL:
            assert f"{app_type.value}_SETTINGS_FILES" in os.environ

    set_env_variables(AppType.CASEDB, DevIdpConfig.MOCK, DevRepositoryConfig.DICT_DEMO)
    assert "CASEDB_SETTINGS_FILES" in os.environ
    assert "SEQDB_SETTINGS_FILES" in os.environ


def test_resolve_extra_settings_files_rejects_invalid_list_item() -> None:
    """Reject list members that are neither strings nor paths."""
    with pytest.raises(ValueError, match="must be a list of str or Path"):
        _resolve_extra_settings_files([42])  # type: ignore[list-item]


def test_get_app_cfg_class_resolves_each_application() -> None:
    """Resolve all concrete application configuration subclasses."""
    for app_type in (AppType.CASEDB, AppType.SEQDB, AppType.OMOPDB):
        config_class = get_app_cfg_class(app_type)
        assert config_class.__name__ == f"{app_type.value.capitalize()}AppCfg"


def test_get_app_cfgs_builds_each_repository_config_and_links_seqdb(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Build all named configs and attach each supplied seqdb config to casedb."""
    env_calls = []

    class FakeAppCfg:
        def __init__(self, app_type, _service_type, _repository_type, **kwargs):
            self.app_type = app_type
            self.name = kwargs["name"]
            self.cfg = {"service": {"seqdb": {"props": {"local_client": {}}}}}
            self.log_level = None

        def set_log_level(self, level):
            self.log_level = level

    monkeypatch.setattr(util, "get_app_cfg_class", lambda _app: FakeAppCfg)
    monkeypatch.setattr(
        util, "set_env_variables", lambda *args, **kwargs: env_calls.append(args)
    )

    test_type = _TestServiceType.FIRST
    seqdb_cfgs = {
        f"{test_type.value}__{config.value}": object() for config in DevRepositoryConfig
    }
    cfgs = get_app_cfgs(
        AppType.CASEDB,
        _TestServiceType,
        _TestRepositoryType,
        test_type,
        extra_settings_files=None,
        seqdb_app_cfgs=seqdb_cfgs,
        log_level="DEBUG",
    )

    assert list(cfgs) == list(seqdb_cfgs)
    assert len(env_calls) == len(DevRepositoryConfig)
    assert all(cfg.log_level == "DEBUG" for cfg in cfgs.values())
    for name, cfg in cfgs.items():
        assert cfg.cfg["service"]["seqdb"]["props"]["local_client"]["app_cfg"] is (
            seqdb_cfgs[name]
        )


def test_get_app_cfgs_accepts_string_test_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Use string test names directly when creating configuration keys."""

    class FakeAppCfg:
        def __init__(self, *args, **kwargs):
            self.name = kwargs["name"]

        def set_log_level(self, _level):
            pass

    monkeypatch.setattr(util, "get_app_cfg_class", lambda _app: FakeAppCfg)
    monkeypatch.setattr(util, "set_env_variables", lambda *args, **kwargs: None)

    cfgs = get_app_cfgs(
        AppType.COMMONDB,
        _TestServiceType,
        _TestRepositoryType,
        "manual",
        extra_settings_files=None,
    )

    assert all(name.startswith("manual__") for name in cfgs)


def test_create_demo_data_from_repository_deletes_then_copies_in_order() -> None:
    """Delete in reverse entity order, then copy dict records to the SA repo."""

    class FirstModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True)
        id: int = 0
        value: int = 1

    class SecondModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True)
        id: int = 0
        value: int = 2

    FirstModel.ENTITY.set_model_class(FirstModel)
    SecondModel.ENTITY.set_model_class(SecondModel)
    events = []

    class FakeRepository:
        def uow(self):
            return nullcontext(object())

        def crud(self, _uow, _user_id, model_class, operation, **kwargs):
            events.append((self, model_class, operation, kwargs))
            if operation is CrudOperation.READ_ALL:
                return [{"model": model_class.__name__}]

    dict_repository = FakeRepository()
    sa_repository = FakeRepository()
    create_demo_data_from_repository(
        None,
        [FirstModel.ENTITY, SecondModel.ENTITY],
        dict_repository,
        sa_repository,
        "unused",
    )

    assert [(event[1], event[2]) for event in events] == [
        (SecondModel, CrudOperation.DELETE_ALL),
        (FirstModel, CrudOperation.DELETE_ALL),
        (FirstModel, CrudOperation.READ_ALL),
        (FirstModel, CrudOperation.CREATE_SOME),
        (SecondModel, CrudOperation.READ_ALL),
        (SecondModel, CrudOperation.CREATE_SOME),
    ]
    assert events[2][3]["return_copy"] is False
    assert events[3][3]["objs"] == [{"model": "FirstModel"}]


def test_load_demo_data_imports_modules_and_dispatches_each_service(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Load app metadata and dispatch one demo-data operation per service."""

    class ServiceType(Enum):
        FIRST = "FIRST"
        SECOND = "SECOND"

    imported = {
        "demo.domain": type("DomainModule", (), {"DOMAIN": object()}),
        "demo.repositories.sa_model": object(),
        "demo.domain.enum": type(
            "EnumModule",
            (),
            {"ServiceType": ServiceType, "RepositoryType": _TestRepositoryType},
        ),
    }
    config_calls = []

    class FakeAppCfg:
        def __init__(self, *args, **kwargs):
            config_calls.append((args, kwargs))
            self.cfg = {"repository": {}}

    dispatched = []
    monkeypatch.setattr(
        util,
        "importlib",
        Mock(import_module=lambda name: imported[name]),
    )
    monkeypatch.setattr(util, "get_app_cfg_class", lambda _app: FakeAppCfg)
    monkeypatch.setattr(util, "set_env_variables", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        util,
        "_load_demo_data_for_service",
        lambda *args: dispatched.append(args),
    )

    load_demo_data(AppType.CASEDB, "demo", connect_timeout=4, verbose=False)

    assert [args[1] for args in dispatched] == list(ServiceType)
    assert all(args[0] is AppType.CASEDB for args in dispatched)
    assert all(args[8:] == (4, False) for args in dispatched)
    assert len(config_calls) == 3


@pytest.mark.parametrize(
    ("connection_string", "expected_connect_args"),
    [
        (
            "mssql+pyodbc://host/database",
            {"timeout": 3, "login_timeout": 3},
        ),
        ("other+pyodbc://host/database", {"connect_timeout": 3, "timeout": 3}),
        ("sqlite:///database.db", {}),
    ],
    ids=["mssql-pyodbc", "generic-pyodbc", "other-driver"],
)
def test_load_demo_data_for_service_routes_connection_timeout_args(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    connection_string: str,
    expected_connect_args: dict[str, int],
) -> None:
    """Pass the backend-specific timeout keyword arguments to connection checks."""

    class FakeDictRepository:
        db = {"model": {"id": 1}}

        @classmethod
        def create_repository(cls, **kwargs):
            return cls()

    class FakeSARepository:
        checked = []

        @classmethod
        def create_repository(cls, **kwargs):
            return cls()

        @classmethod
        def test_connection(cls, connection, **kwargs):
            cls.checked.append((connection, kwargs))
            return None

        @classmethod
        def clear_repository_content(cls, **kwargs):
            pass

    dict_file = tmp_path / "demo.full.pkl.gz"
    sqlite_file = tmp_path / "demo_sa.full.sqlite"
    entities = [object()]
    domain = Mock()
    domain.get_dag_sorted_entities.return_value = entities
    repository_configs = {
        "repository": {
            "FIRST": {"class": FakeDictRepository, "props": {"file": str(dict_file)}}
        }
    }
    sqlite_configs = {
        "repository": {
            "FIRST": {"class": FakeSARepository, "props": {"file": str(sqlite_file)}}
        }
    }
    sql_configs = {
        "repository": {
            "FIRST": {
                "class": FakeSARepository,
                "props": {"connection_string": connection_string},
            }
        }
    }
    monkeypatch.setattr(util, "create_demo_data_from_repository", lambda *args: None)

    util._load_demo_data_for_service(
        AppType.CASEDB,
        _TestServiceType.FIRST,
        "demo",
        domain,
        repository_configs,
        sqlite_configs,
        sql_configs,
        None,
        3,
        False,
    )

    assert FakeSARepository.checked == [(connection_string, expected_connect_args)]


def test_load_demo_data_for_service_returns_when_dict_config_missing() -> None:
    """Skip service processing when its dict repository configuration is absent."""
    domain = Mock()

    util._load_demo_data_for_service(
        AppType.CASEDB,
        _TestServiceType.SECOND,
        "demo",
        domain,
        {"repository": {}},
        {},
        {},
        None,
        1,
        False,
    )

    domain.get_dag_sorted_entities.assert_not_called()


def test_load_demo_data_for_service_skips_sql_copy_when_connection_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Stop before clearing SQL data when the connection test returns an error."""

    class FakeDictRepository:
        db = {}

        @classmethod
        def create_repository(cls, **kwargs):
            return cls()

    class FakeSARepository:
        cleared = False

        @classmethod
        def create_repository(cls, **kwargs):
            return cls()

        @classmethod
        def test_connection(cls, *_args, **_kwargs):
            return RuntimeError("unavailable")

        @classmethod
        def clear_repository_content(cls, **kwargs):
            cls.cleared = True

    domain = Mock()
    domain.get_dag_sorted_entities.return_value = []
    dict_cfg = {
        "repository": {
            "FIRST": {
                "class": FakeDictRepository,
                "props": {"file": str(tmp_path / "empty.full.pkl.gz")},
            }
        }
    }
    sqlite_cfg = {
        "repository": {
            "FIRST": {
                "class": FakeSARepository,
                "props": {"file": str(tmp_path / "empty.full.sqlite")},
            }
        }
    }
    sql_cfg = {
        "repository": {
            "FIRST": {
                "class": FakeSARepository,
                "props": {"connection_string": "sqlite:///test.db"},
            }
        }
    }
    monkeypatch.setattr(util, "create_demo_data_from_repository", lambda *args: None)

    util._load_demo_data_for_service(
        AppType.CASEDB,
        _TestServiceType.FIRST,
        "demo",
        domain,
        dict_cfg,
        sqlite_cfg,
        sql_cfg,
        None,
        1,
        False,
    )

    assert FakeSARepository.cleared is False


def test_complete_stored_model_field_props_adds_missing_defaults() -> None:
    """Create defaults for missing persisted models and fields, but not transient ones."""

    class PersistedModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True)
        id: int = 0
        value: str | None = None

    class TransientModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=False)
        value: str | None = None

    stored = {PersistedModel: {"value": ModelFieldProps(is_mutable_always=True)}}
    complete_stored_model_field_props(
        stored, {"service": [PersistedModel, TransientModel]}
    )

    assert stored[PersistedModel]["value"].is_mutable_always is True
    assert stored[PersistedModel]["id"].is_mutable_always is False
    assert TransientModel not in stored


def test_complete_stored_model_field_props_adds_all_defaults_for_new_model() -> None:
    """Create default field properties when a persisted model has no entry."""

    class PersistedModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True)
        value: int = 1

    stored = {}
    complete_stored_model_field_props(stored, {"service": [PersistedModel]})

    assert set(stored[PersistedModel]) == set(PersistedModel.model_fields)
    assert all(
        isinstance(props, ModelFieldProps) for props in stored[PersistedModel].values()
    )


@pytest.mark.parametrize(
    ("entity", "stored", "message"),
    [
        (None, {}, "does not have an ENTITY"),
        (Entity(persistable=False), {"field": ModelFieldProps()}, "not persistable"),
    ],
    ids=["missing-entity", "nonpersistable-with-props"],
)
def test_complete_stored_model_field_props_rejects_invalid_models(
    entity, stored: dict, message: str
) -> None:
    """Reject missing entity metadata and properties on transient models."""

    class InvalidModel(Model):
        ENTITY: ClassVar[Entity | None] = entity

    initial = {InvalidModel: stored} if stored else {}
    with pytest.raises(ValueError, match=message):
        complete_stored_model_field_props(initial, {"service": [InvalidModel]})


def test_register_domain_entities_substitutes_models_and_commands() -> None:
    """Substitute common implementations and infer an unset persisted schema."""

    class BaseModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True)
        NAME: ClassVar[str] = "UtilBaseModel"

    class CommonModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True)
        NAME: ClassVar[str] = "UtilCommonModel"

    class BaseCommand(Command):
        NAME: ClassVar[str] = "UtilBaseCommand"

    class CommonCommand(Command):
        NAME: ClassVar[str] = "UtilCommonCommand"

    models = [BaseModel]
    commands = {BaseCommand}
    domain = Mock()

    register_domain_entities(
        domain,
        [_TestServiceType.FIRST],
        {_TestServiceType.FIRST: models},
        {_TestServiceType.FIRST: commands},
        {BaseModel: CommonModel},
        {BaseCommand: CommonCommand},
        set_schema_to_service_type=True,
    )

    assert models == [CommonModel]
    assert commands == {CommonCommand}
    assert CommonModel.ENTITY.schema_name == "first"
    domain.register_entity.assert_called_once_with(
        CommonModel.ENTITY,
        model_class=CommonModel,
        service_type=_TestServiceType.FIRST,
    )
    domain.register_command.assert_called_once_with(
        CommonCommand, service_type=_TestServiceType.FIRST
    )


def test_register_domain_entities_preserves_explicit_schema_and_allows_no_models() -> (
    None
):
    """Keep explicit schemas and safely register service types without models."""

    class ExplicitSchemaModel(Model):
        ENTITY: ClassVar[Entity] = Entity(persistable=True, schema_name="custom")
        NAME: ClassVar[str] = "UtilExplicitSchemaModel"

    domain = Mock()
    models = [ExplicitSchemaModel]
    register_domain_entities(
        domain,
        ["plain-service", "empty-service"],
        {"plain-service": models},
        {},
        set_schema_to_service_type=True,
    )

    assert ExplicitSchemaModel.ENTITY.schema_name == "custom"
    assert domain.register_service_type.call_count == 2
    assert domain.register_entity.call_count == 1


def test_register_domain_entities_rejects_model_without_entity() -> None:
    """Raise the framework initialization error when a registered model lacks metadata."""

    class MissingEntityModel(Model):
        ENTITY: ClassVar[Entity | None] = None

    with pytest.raises(exc.InitializationServiceError, match="Entity for model class"):
        register_domain_entities(
            Mock(),
            ["service"],
            {"service": [MissingEntityModel]},
            {},
        )
