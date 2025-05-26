import importlib
import json
import os
import uuid
from enum import Enum
from typing import Any, Hashable, Iterable, Type

import ulid

from gen_epix.fastapp import Domain


def generate_ulid() -> uuid.UUID:
    return ulid.api.new().uuid


def map_paired_elements(
    data: Iterable[tuple[Hashable, Any]], as_set: bool = False, frozen: bool = False
) -> (
    dict[Hashable, list[Any]]
    | dict[Hashable, set[Any]]
    | dict[Hashable, frozenset[Any]]
):
    """
    Convert an iterable of paired elements to a dictionary of lists or sets, where
    the keys are the unique first elements and the values the list or set of second
    elements matching that key in the input. If frozen=True, the sets are converted
    to frozensets.
    """
    retval: (
        dict[Hashable, list[Any]]
        | dict[Hashable, set[Any]]
        | dict[Hashable, frozenset[Any]]
    ) = {}
    if as_set:
        for k, v in data:
            if k not in retval:
                retval[k] = set()  # type: ignore[assignment]
            retval[k].add(v)  # type: ignore[union-attr]
        if frozen:
            for k in retval:
                retval[k] = frozenset(retval[k])  # type: ignore[assignment]
    else:
        for k, v in data:
            if k not in retval:
                retval[k] = []  # type: ignore[assignment]
            retval[k].append(v)  # type: ignore[union-attr]
    return retval


def update_cfg_from_file(
    cfg: dict,
    file_or_dir: str,
    cfg_key_map: None | dict[str, str] = None,
    file_key_delimiter: str = "-",
) -> None:
    """
    Import values from files as a nested dict where the nested keys are the file
    name split by "-". The value of the innermost key is the content of the file,
    which can in turn again be a dict.
    """
    cfg_key_map = cfg_key_map or {}

    def _add_value_recursion(cfg: dict, new_cfg: dict, parent_path: str) -> None:
        # Recursively add/replace values to/in cfg
        for key, value in new_cfg.items():
            path = f"{parent_path}.{key}" if len(parent_path) else key
            key = cfg_key_map.get(key, key)
            if isinstance(value, dict):
                if key not in cfg:
                    cfg[key] = {}
                _add_value_recursion(cfg[key], value, path)
            else:
                cfg[key] = value

    # Get list of files
    if os.path.isfile(file_or_dir):
        files = [file_or_dir]
    elif os.path.isdir(file_or_dir):
        files = [os.path.join(file_or_dir, x) for x in os.listdir(file_or_dir)]
    else:
        raise ValueError(f"Invalid file_or_dir: {file_or_dir}")

    # Read files into new_cfg
    new_cfg: dict[str, Any] = {}
    for file in files:
        name = os.path.basename(file)
        keys = [cfg_key_map.get(x, x) for x in name.split(file_key_delimiter)]
        curr_cfg = new_cfg
        for key in keys[0:-1]:
            if key not in curr_cfg:
                curr_cfg[key] = {}
            curr_cfg = curr_cfg[key]
        with open(os.path.join(file), "r") as handle:
            try:
                value = json.load(handle)
            except json.JSONDecodeError as e:
                print(f"Error reading {file}: {e}\nSkipping file")
                continue
        curr_cfg[keys[-1]] = value

    # Recursively add/replace values in cfg
    _add_value_recursion(cfg, new_cfg, "")


def set_entity_repository_model_classes(
    domain: Domain,
    service_type_enum: Type[Enum],
    row_metadata_mixin_class: Type,
    service_modules_path: str,
    field_name_map: dict[Type, dict[str, str]] | None = None,
) -> None:
    if field_name_map is None:
        field_name_map = {}
    sa_metadata_field_names = set(
        row_metadata_mixin_class.__dict__["__annotations__"].keys()
    ) - {"id"}
    sa_model_name_class_map = {}
    for service_type in service_type_enum:
        try:
            sa_module = importlib.import_module(
                f"{service_modules_path}.{service_type.value.lower()}"
            )
        except ModuleNotFoundError:
            continue
        for variable_content in sa_module.__dict__.values():
            if not hasattr(variable_content, "__tablename__"):
                # Not an SA model class
                continue
            sa_model_name_class_map[variable_content.__name__] = variable_content
    for entity in domain.get_dag_sorted_entities():
        if not entity.persistable:
            continue
        model_class = entity.model_class
        sa_model_class = sa_model_name_class_map.get(model_class.__name__)
        if not sa_model_class:
            raise ValueError(
                f"Model {model_class.__name__} does not have a corresponding SA model"
            )
        entity.set_db_model_class(sa_model_class)
        # Verify that the SA model has exactly the same fields as the model
        field_names = set(entity.get_field_names())
        curr_field_name_map = field_name_map.get(model_class)
        if curr_field_name_map:
            field_names = {curr_field_name_map.get(x, x) for x in field_names}
        sa_field_names = (
            set(sa_model_class.__table__.columns.keys()) - sa_metadata_field_names
        )
        extra_field_names = field_names - sa_field_names
        extra_field_names = {
            x for x in extra_field_names if f"{x}_id" not in field_names
        }
        if extra_field_names:
            print(
                f"TEMPORARY PRINT STATEMENT: Model {model_class.__name__} has fields {extra_field_names} that are not in SA model {sa_model_class.__name__}"
            )
            # raise ValueError(
            #     f"Model {model_class.__name__} has fields {extra_field_names} that are not in SA model {sa_model_class.__name__}"
            # )
        extra_sa_field_names = sa_field_names - field_names
        if extra_sa_field_names:
            print(
                f"TEMPORARY PRINT STATEMENT: Model {model_class.__name__} has fields {extra_field_names} that are not in SA model {sa_model_class.__name__}"
            )
            # raise ValueError(
            #     f"SA model {sa_model_class.__name__} has fields {extra_sa_field_names} that are not in model {model_class.__name__}"
            # )
