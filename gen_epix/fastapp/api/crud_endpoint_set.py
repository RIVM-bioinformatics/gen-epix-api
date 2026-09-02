"""Configuration for generated CRUD API endpoints."""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator

from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import CrudEndpointType
from gen_epix.fastapp.model import CrudCommand
from gen_epix.filter import Filter


class CrudEndpointSet(BaseModel):
    """Represents the routes and models used for a CRUD API resource.

    Model validation:
    Missing read and create API model classes are derived from `model_class`.
    Non-mapping initialization data is rejected.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())
    model_class: type
    create_api_model_class: type | None = None
    read_api_model_class: type | None = None
    endpoint_basename: str
    crud_command_class: type[CrudCommand]
    endpoint_types: set[CrudEndpointType]
    user_dependency: Callable | None = None
    app: App
    id_class: type
    operation_id_basename: str | None = None
    description: str | None = None
    post_returns_id: bool | None = False
    put_returns_id: bool | None = False
    delete_all_returns_id: bool | None = False
    response_model_exclude_none: bool | None = False
    query_filter_validator: Callable[[Filter], bool] | None = None

    @model_validator(mode="before")
    @classmethod
    def _validate_args(cls, data: Any) -> Any:
        """Normalize endpoint-set initialization data."""
        if isinstance(data, dict):
            if not data.get("read_api_model_class"):
                data["read_api_model_class"] = data["model_class"]
            if not data.get("create_api_model_class"):
                data["create_api_model_class"] = data["read_api_model_class"]
            if data.get("operation_id_basename"):
                data["operation_id_basename"] = data["endpoint_basename"]
        else:
            raise NotImplementedError("Not implemented for non-dict data")
        return data
