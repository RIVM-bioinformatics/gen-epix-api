from enum import Enum
from typing import Type, TypeVar, overload

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from gen_epix import fastapp
from gen_epix.commondb.domain import command, enum, model
from gen_epix.fastapp import BaseUserManager
from gen_epix.fastapp.services.rbac import BaseRbacService

# TypeVars for get_mapped_class method to express subclass relationships
ModelType = TypeVar("ModelType", bound=model.Model)
CommandType = TypeVar("CommandType", bound=command.Command)
PolicyType = TypeVar("PolicyType", bound=fastapp.Policy)


class AppImplDetails(BaseModel):
    """
    Implementation details for the App.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    sorted_service_types: list[Enum] = Field(
        description="List of service types in DAG sorted order for initialization"
    )
    services: dict[Enum, fastapp.BaseService] = Field(
        default_factory=dict, description="Dictionary of services keyed by service type"
    )
    repositories: dict[Enum, fastapp.BaseRepository] = Field(
        default_factory=dict,
        description="Dictionary of repositories keyed by service type",
    )
    registered_user_dependency_or_none: model.User | None = Field(
        default=None,
        description="Dependency that provides the currently registered user",
    )
    new_user_dependency_or_none: model.User | None = Field(
        default=None, description="Dependency that provides a new user"
    )
    idp_user_dependency_or_none: model.User | None = Field(
        default=None,
        description="Dependency that provides a user known by the identity provider but not registered in the application",
    )
    model_class_map: dict[Type[model.Model], Type[model.Model]] = Field(
        default_factory=dict,
        description="Mapping of commondb model classes to any derived implementing model classes",
    )
    command_class_map: dict[Type[command.Command], Type[command.Command]] = Field(
        default_factory=dict,
        description="Mapping of commondb command classes to any derived implementing command classes",
    )
    policy_class_map: dict[Type[fastapp.Policy], Type[fastapp.Policy]] = Field(
        default_factory=dict,
        description="Mapping of commondb policy classes to any derived implementing policy classes",
    )
    rbac_service_class: Type[BaseRbacService] = Field(
        description="Class used for RBAC service"
    )
    user_manager_class: Type[BaseUserManager] = Field(
        description="Class used for user management"
    )
    role_map: dict[enum.Role | Enum, str] = Field(
        description="Mapping of roles to their string representations. Where possible, the key is the commondb role enum.",
    )
    role_set_map: dict[enum.RoleSet | Enum, frozenset[str]] = Field(
        description="Mapping of role sets to their corresponding sets of role strings. Where possible, the key is the commondb role set enum.",
    )
    role_permissions_map: dict[
        str, set[tuple[Type[fastapp.Command], fastapp.PermissionType]]
    ] = Field(
        description="Mapping of roles as strings to (command, permission type) tuples",
    )

    @computed_field
    def rev_role_map(self) -> dict[str, enum.Role | Enum]:
        return {x: y for y, x in self.role_map.items()}

    @computed_field
    def registered_user_dependency(self) -> model.User:
        if self.registered_user_dependency_or_none is None:
            raise ValueError("registered_user_dependency is not set")
        return self.registered_user_dependency_or_none

    @computed_field
    def new_user_dependency(self) -> model.User:
        if self.new_user_dependency_or_none is None:
            raise ValueError("new_user_dependency is not set")
        return self.new_user_dependency_or_none

    @computed_field
    def idp_user_dependency(self) -> model.User:
        if self.idp_user_dependency_or_none is None:
            raise ValueError("idp_user_dependency is not set")
        return self.idp_user_dependency_or_none

    @field_validator("role_map", mode="before")
    @classmethod
    def _validate_role_map(
        cls, value: dict[enum.Role | Enum, str] | Type[Enum]
    ) -> dict[enum.Role | Enum, str]:
        if not isinstance(value, dict):
            value = {e: str(e.value) for e in value}
            if len(set(value.values())) != len(value):
                raise ValueError("role_map must not contain duplicate values")
        return value

    @field_validator("role_set_map", mode="before")
    @classmethod
    def _validate_role_set_map(
        cls, value: dict[enum.RoleSet | Enum, str] | Type[Enum]
    ) -> dict[enum.RoleSet | Enum, str]:
        if not isinstance(value, dict):
            # Allow passing Enum type directly for convenience
            value = {e: e.value for e in value}
        return value

    @field_validator("sorted_service_types", mode="before")
    @classmethod
    def _validate_sorted_service_types(
        cls, value: tuple[Enum, ...] | list[Enum]
    ) -> list[Enum]:
        if isinstance(value, tuple):
            return list(value)
        if len(set(value)) != len(value):
            raise ValueError("sorted_service_types must not contain duplicates")
        return value

    @field_validator(
        "model_class_map", "command_class_map", "policy_class_map", mode="after"
    )
    @classmethod
    def _validate_model_class_map(cls, value: dict[type, type]) -> dict[type, type]:
        for x, y in value.items():
            if not issubclass(y, x):
                raise ValueError(f"Class {y} is not a subclass of {x}")
        return value

    @overload
    def get_mapped_class(self, base_class: Type[ModelType]) -> Type[ModelType]: ...

    @overload
    def get_mapped_class(self, base_class: Type[CommandType]) -> Type[CommandType]: ...

    @overload
    def get_mapped_class(self, base_class: Type[PolicyType]) -> Type[PolicyType]: ...

    def get_mapped_class(
        self,
        base_class: Type[model.Model] | Type[command.Command] | Type[fastapp.Policy],
    ) -> Type[model.Model] | Type[command.Command] | Type[fastapp.Policy]:
        """
        Get the mapped class for a given base class, or return the base class if no mapping exists.
        """
        if issubclass(base_class, model.Model):
            return self.model_class_map.get(base_class, base_class)
        if issubclass(base_class, command.Command):
            return self.command_class_map.get(base_class, base_class)
        if issubclass(base_class, fastapp.Policy):
            return self.policy_class_map.get(base_class, base_class)
        raise ValueError(f"Unsupported base class type: {base_class}")
