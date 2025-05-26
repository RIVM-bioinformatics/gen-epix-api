from typing import Any, Callable, Type

from pydantic import BaseModel, ConfigDict, model_validator

from gen_epix.fastapp import App, CrudCommand
from gen_epix.fastapp.enum import CrudEndpointType
from gen_epix.filter import Filter


class CrudEndpointSet(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())
    model_class: Type
    create_api_model_class: Type | None = None
    read_api_model_class: Type | None = None
    endpoint_basename: str
    crud_command_class: Type[CrudCommand]
    endpoint_types: set[CrudEndpointType]
    user_dependency: Callable | None = None
    app: App
    id_class: Type
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
