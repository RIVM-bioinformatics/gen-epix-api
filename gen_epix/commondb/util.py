import datetime
import gzip
import importlib
import logging
import os
import pickle
from collections.abc import Hashable, Iterable
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID

from gen_epix import fastapp
from gen_epix.commondb.config import AppCfg
from gen_epix.commondb.domain.enum import (
    AppType,
    AppTypeSet,
    DevIdpConfig,
    DevRepositoryConfig,
    DevRepositoryConfigSet,
)
from gen_epix.fastapp import Command, Domain, Model, ModelFieldProps, exc
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict import DictRepository
from gen_epix.fastapp.repositories.sa import SARepository
from gen_epix.util import get_package_root


def set_env_variables(
    app_type: AppType | str,
    dev_idp_config: DevIdpConfig | str,
    dev_repository_config: DevRepositoryConfig | str,
    extra_settings_files: list[Path] | None = None,
    general_cfg_path: Path | None = None,
    cfg_path: Path | None = None,
) -> None:
    # Parse input
    if isinstance(app_type, str):
        if app_type.upper() in AppType.__members__:
            app_type_enum = AppType[app_type.upper()]
            app_type_str = app_type_enum.value.lower()
        else:
            app_type_str = app_type.lower()
            app_type_enum = None
    else:
        app_type_str = app_type.value.lower()
        app_type_enum = app_type
    if isinstance(dev_idp_config, str):
        dev_idp_config_enum = DevIdpConfig[dev_idp_config.upper()]
    else:
        dev_idp_config_enum = dev_idp_config
    if isinstance(dev_repository_config, str):
        dev_repository_config_enum = DevRepositoryConfig[dev_repository_config.upper()]
    else:
        dev_repository_config_enum = dev_repository_config
    # Special case: set environment variables for all apps
    if app_type_enum == AppType.ALL:
        for app2 in AppTypeSet.ALL.value:
            set_env_variables(app2, dev_idp_config_enum, dev_repository_config_enum)
        return
    elif app_type_enum == AppType.CASEDB:
        set_env_variables(
            AppType.SEQDB, dev_idp_config_enum, dev_repository_config_enum
        )
    # Initialise some
    package_root = get_package_root()
    if general_cfg_path is None:
        general_cfg_path = package_root / "config"
    if cfg_path is None:
        cfg_path = package_root / "gen_epix" / app_type_str / "config"
    envvar_prefix = app_type_str.upper() + "_"
    settings_files: list[Path] = []
    # General settings
    settings_files.append(cfg_path / "settings.toml")
    # Service secrets
    settings_files.append(cfg_path / ".example.secrets.service.toml")
    # Identity provider settings
    if dev_idp_config_enum == DevIdpConfig.IDPS:
        settings_files.append(general_cfg_path / "identity_providers.toml")
    elif dev_idp_config_enum == DevIdpConfig.MOCK:
        settings_files.append(general_cfg_path / "mock_identity_provider.toml")
    elif dev_idp_config_enum == DevIdpConfig.NONE:
        settings_files.append(general_cfg_path / "no_identity_providers.toml")
    else:
        raise ValueError(f"Unknown dev_idp_config: {dev_idp_config_enum}")
    # Repository settings
    if dev_repository_config_enum in DevRepositoryConfigSet.DICT.value:
        settings_files.append(cfg_path / "settings.repository.dict.toml")
    elif dev_repository_config_enum in DevRepositoryConfigSet.SA.value:
        settings_files.append(cfg_path / "settings.repository.sa.toml")
    else:
        raise ValueError(f"Unknown dev_repository_config: {dev_repository_config_enum}")
    # Repository secrets
    if dev_repository_config_enum == DevRepositoryConfig.DICT_DEMO:
        settings_files.append(cfg_path / ".example.secrets.repository.dict.demo.toml")
    elif dev_repository_config_enum == DevRepositoryConfig.DICT_EMPTY:
        settings_files.append(cfg_path / ".example.secrets.repository.dict.empty.toml")
    elif dev_repository_config_enum == DevRepositoryConfig.SA_SQLITE_DEMO:
        settings_files.append(
            cfg_path / ".example.secrets.repository.sa_sqlite.demo.toml"
        )
    elif dev_repository_config_enum == DevRepositoryConfig.SA_SQLITE_EMPTY:
        settings_files.append(
            cfg_path / ".example.secrets.repository.sa_sqlite.empty.toml"
        )
    elif dev_repository_config_enum == DevRepositoryConfig.SA_SQL:
        settings_files.append(cfg_path / ".example.secrets.repository.sa_sql.toml")
    else:
        raise ValueError(f"Unknown dev_repository_config: {dev_repository_config_enum}")
    # Add any extra settings files at the end
    if extra_settings_files:
        settings_files.extend(extra_settings_files)
    # Set environment variables
    os.environ[envvar_prefix + "SETTINGS_FILES"] = ",".join(
        [str(x.resolve()) for x in settings_files]
    )
    os.environ[envvar_prefix + "LOG_CONFIG_FILE"] = str(
        (cfg_path / "logging.yaml").resolve()
    )


def create_demo_data_from_repository(
    user_id: str,
    entities: list,
    dict_repository: DictRepository,
    sa_repository: SARepository,
    module_root: str,
) -> None:
    model = importlib.import_module(f"{module_root}.domain.model")
    # Delete all first in reverse order
    for entity in entities[::-1]:
        model_class = entity.model_class
        with sa_repository.uow() as sa_uow:
            sa_repository.crud(
                sa_uow,
                user_id,
                model_class,
                None,
                None,
                CrudOperation.DELETE_ALL,
            )
    for entity in entities:
        model_class = entity.model_class
        with (
            dict_repository.uow() as dict_uow,
            sa_repository.uow() as sa_uow,
        ):
            objs: list[model.Model] = dict_repository.crud(  # type: ignore[assignment]
                dict_uow,
                user_id,
                model_class,
                None,
                None,
                CrudOperation.READ_ALL,
                return_copy=False,
            )
            sa_repository.crud(
                sa_uow,
                user_id,
                model_class,
                objs,
                None,
                CrudOperation.CREATE_SOME,
            )


def load_demo_data(
    app_type: AppType,
    module_root: str,
    connect_timeout: float = 1,
    verbose: bool = True,
) -> None:
    domain: Domain = importlib.import_module(f"{module_root}.domain").DOMAIN
    # Import the sa_model module to register the models
    importlib.import_module(f"{module_root}.repositories.sa_model")
    # Get classes and config for the app type

    enum = importlib.import_module(f"{module_root}.domain.enum")

    set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.DICT_DEMO)
    dict_app_cfg = AppCfg(
        app_type.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.SA_SQLITE_DEMO)
    sa_sqlite_app_cfg = AppCfg(
        app_type.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    set_env_variables(app_type, DevIdpConfig.MOCK, DevRepositoryConfig.SA_SQL)
    sa_sql_app_cfg = AppCfg(
        app_type.value, enum.ServiceType, enum.RepositoryType, log_setup=False
    )
    # user_id = dict_app_cfg.cfg["service"]["auth"]["props"]["root"]["user"]["id"]
    user_id = UUID("00000000-0000-0000-0000-000000000000")
    for service_type in enum.ServiceType:
        # # TODO: TEMPORARY for debugging, remove later
        # if service_type.value != "CASE":
        #     continue
        dict_repository_cfg = dict_app_cfg.cfg["repository"].get(service_type.value)
        if not dict_repository_cfg:
            continue
        entities = domain.get_dag_sorted_entities(
            service_type=service_type, persistable=True
        )
        # Create dict repository, which is assumed to always be available
        dict_repository_class: type[DictRepository] = dict_repository_cfg["class"]
        demo_dict_file = Path(dict_repository_cfg["props"]["file"]).resolve()
        empty_dict_file = Path(
            str(demo_dict_file).replace(".full.", ".empty.")
        ).resolve()
        zip_file: str = str(demo_dict_file).replace(".pkl.gz", ".zip")
        start_time = datetime.datetime.now()
        dict_repository: DictRepository = (
            dict_repository_class.create_repository(  # type:ignore[assignment]
                entities=entities, file=zip_file
            )
        )
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: demo data parsed in {end_time - start_time}s"
            )
        # Write empty and demo dict repository to file
        start_time = datetime.datetime.now()
        with gzip.open(empty_dict_file, "wb") as handle:
            pickle.dump({x: {} for x in dict_repository.db}, handle)
        with gzip.open(demo_dict_file, "wb") as handle:
            pickle.dump(dict_repository.db, handle)
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: dict repository written to file in {end_time - start_time}s"
            )
        # Create empty and demo SA_SQLITE repositories
        sa_sqlite_repository_cfg = sa_sqlite_app_cfg.cfg["repository"][
            service_type.value
        ]
        sa_repository_class: type[SARepository] = sa_sqlite_repository_cfg["class"]
        demo_sa_sqlite_file = Path(sa_sqlite_repository_cfg["props"]["file"]).resolve()
        empty_sa_sqlite_file = Path(
            str(demo_sa_sqlite_file).replace(".full", ".empty")
        ).resolve()
        start_time = datetime.datetime.now()
        # Empty repository
        sa_repository_class.create_repository(
            entities=entities,
            file=empty_sa_sqlite_file,
            name=service_type.value,
            recreate_sqlite_file=True,
        )
        # Full repository
        sa_sqlite_repository: SARepository = (
            sa_repository_class.create_repository(  # type:ignore[assignment]
                entities=entities,
                file=demo_sa_sqlite_file,
                name=service_type.value,
                recreate_sqlite_file=True,
            )
        )
        create_demo_data_from_repository(
            user_id, entities, dict_repository, sa_sqlite_repository, module_root
        )
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sqlite repository written to file in {end_time - start_time}s"
            )
        # Create empty SA_SQL repository or loaded with demo data
        sa_sql_repository_cfg = sa_sql_app_cfg.cfg["repository"][service_type.value]
        connection_string = sa_sql_repository_cfg["props"]["connection_string"]
        if "mssql" in connection_string:
            connect_args = {
                "timeout": connect_timeout,
                "login_timeout": connect_timeout,
            }
        elif "pyodcb" in connection_string:
            connect_args = {
                "connect_timeout": connect_timeout,
                "timeout": connect_timeout,
            }
        else:
            connect_args = {}
        # Skip load if no connection can be made
        if exception := sa_repository_class.test_connection(
            connection_string, **connect_args
        ):
            if verbose:
                print(
                    # f"App {app_type.value}, service {service_type.value}: sa_sql connection failed: {exception}"
                    f"App {app_type.value}, service {service_type.value}: sa_sql connection failed"
                )
            continue
        start_time = datetime.datetime.now()
        sa_repository_class.clear_repository_content(
            entities=entities, connection_string=connection_string
        )
        sa_sql_repository: SARepository = (
            sa_repository_class.create_repository(  # type:ignore[assignment]
                entities=entities,
                connection_string=connection_string,
                name=service_type.value,
            )
        )
        create_demo_data_from_repository(
            user_id, entities, dict_repository, sa_sql_repository, module_root
        )
        end_time = datetime.datetime.now()
        if verbose:
            print(
                f"App {app_type.value}, service {service_type.value}: sa_sql repository loaded in {end_time - start_time}s"
            )


def get_app_cfgs(
    app_type: AppType,
    service_type_enum: type[Enum],
    repository_type_enum: type[Enum],
    test_type: Enum | str,
    dev_idp_config: DevIdpConfig = DevIdpConfig.NONE,
    general_cfg_path: Path | None = None,
    cfg_path: Path | None = None,
    extra_settings_files: (
        list[Path | str] | Path | str | None
    ) = "./test/test_client/settings.toml",
    seqdb_app_cfgs: dict[str, AppCfg] | None = None,
    log_setup: bool = False,
    log_level: str | int = logging.ERROR,
) -> dict[str, AppCfg]:
    """
    Create all casedb and seqdb app cfgs with a name for the given test type and
    dev repository config so that they can be reused in tests
    """
    if isinstance(test_type, Enum):
        test_type = test_type.value
    if extra_settings_files:
        if not isinstance(extra_settings_files, list):
            extra_settings_files = [extra_settings_files]
        for i, file in enumerate(extra_settings_files):
            if not isinstance(file, (str, Path)):
                raise ValueError("extra_settings_files must be a list of str or Path")
            if isinstance(file, str):
                file = Path(file)
            if not file.is_file():
                raise ValueError(
                    f"extra_settings_file {file} does not exist or is not a file"
                )
            extra_settings_files[i] = file.resolve()
    app_cfgs: dict[str, AppCfg] = {}
    for dev_repository_config in DevRepositoryConfig:
        name = f"{test_type}__{dev_repository_config.value}"
        set_env_variables(
            app_type,
            dev_idp_config,
            dev_repository_config,
            general_cfg_path=general_cfg_path,
            cfg_path=cfg_path,
            extra_settings_files=extra_settings_files,
        )
        app_cfgs[name] = AppCfg(
            app_type,
            service_type_enum,
            repository_type_enum,
            name=name,
            log_setup=log_setup,
        )
        # Set log level
        app_cfgs[name].set_log_level(log_level)
        # Add seqdb app_cfg to casedb app_cfg for seqdb service local app so that when the latter is instantiated, it can directly use this app_cfg without risk of having seqdb env variables being altered in the meantime
        if app_type == AppType.CASEDB and seqdb_app_cfgs is not None:
            app_cfgs[name].cfg["service"]["seqdb"]["props"]["seqdb_local_app"][
                "app_cfg"
            ] = seqdb_app_cfgs[name]
    return app_cfgs


def complete_stored_model_field_props(
    stored_model_field_props: dict[type[fastapp.Model], dict[str, ModelFieldProps]],
    sorted_models_by_service_type: dict[Any, list[type[fastapp.Model]]],
) -> None:
    """
    Complete the stored_model_field_props with default props for all other models/fields
    """
    # Complete the stored model field props with default props for all other models/fields
    for model_classes in sorted_models_by_service_type.values():
        for model_class in model_classes:
            entity = model_class.ENTITY
            if entity is None:
                raise ValueError(
                    f"Model class {model_class.__name__} does not have an ENTITY defined."
                )
            if not entity.persistable:
                if model_class in stored_model_field_props:
                    raise ValueError(
                        f"Model class {model_class.__name__} is not persistable but has stored field props defined."
                    )
                continue
            if model_class not in stored_model_field_props:
                # Add default props for all fields
                stored_model_field_props[model_class] = {
                    x: ModelFieldProps() for x in model_class.model_fields
                }  # Default props
                continue
            for field_name in model_class.model_fields:
                # Add default props for any missing fields
                if field_name not in stored_model_field_props[model_class]:
                    stored_model_field_props[model_class][
                        field_name
                    ] = ModelFieldProps()  # Default props


def register_domain_entities(
    domain: Domain,
    sorted_service_types: Iterable[Hashable],
    sorted_models_by_service_type: dict[Hashable, list[type[Model]]],
    commands_by_service_type: dict[Hashable, set[type[Command]]],
    common_model_map: dict[type[Model], type[Model]] | None = None,
    common_command_map: dict[type[Command], type[Command]] | None = None,
    set_schema_to_service_type: bool = False,
) -> None:
    """
    Register service types, models and commands with a domain. In case some
    models or commands are subclassed from another domain and the provides
    models and commands contain their parent classes, they can be substituted
    in the input and subsequently be registered as the actual classes, by
    providing a mapping.

    If `set_schema_to_service_type` is enabled, the schema name of the model
    will be set to the lower case service name for persistable entities, unless
    the schema name is already set.
    """
    if not common_model_map:
        common_model_map = {}
    for service_type in sorted_service_types:
        # Register the service type
        domain.register_service_type(service_type)
        schema_name = (
            str(service_type.value).lower()
            if isinstance(service_type, Enum)
            else str(service_type)
        )
        # Register the models
        for i, model_class in enumerate(
            sorted_models_by_service_type.get(service_type, [])
        ):
            if model_class in common_model_map:
                # Substitute the model class with its commondb implementation,
                # also in the input
                model_class = common_model_map[model_class]
                sorted_models_by_service_type[service_type][i] = model_class
            if model_class.ENTITY is None:
                raise exc.InitializationServiceError(
                    f"Entity for model class {model_class} is not initialized."
                )
            if (
                set_schema_to_service_type
                and model_class.ENTITY.persistable
                and model_class.ENTITY.schema_name is None
            ):
                model_class.ENTITY.schema_name = schema_name
            domain.register_entity(
                model_class.ENTITY, model_class=model_class, service_type=service_type
            )
        # Register the commands
        for command_class in commands_by_service_type.get(service_type, []):
            if common_command_map and command_class in common_command_map:
                # Substitute the command class with its commondb implementation,
                # also in the input
                commands_by_service_type[service_type].remove(command_class)
                command_class = common_command_map[command_class]
                commands_by_service_type[service_type].add(command_class)
            domain.register_command(command_class, service_type=service_type)
