"""Represent validated implementation metadata used to compose a commondb app."""

from collections.abc import Callable
from enum import Enum
from functools import cached_property
from typing import Any, TypeVar, overload

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
    """Represents validated service, repository, dependency, and authorization metadata.

    Model validation:
    Role maps must have unique values, service types must be unique, and mapped
    implementation classes must derive from their mapped base classes.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    sorted_service_types: list[Enum] = Field(
        description="List of unique service types in DAG initialization order; tuples are normalized to lists."
    )
    services: dict[Enum, fastapp.BaseService[Any]] = Field(
        default_factory=dict, description="Dictionary of services keyed by service type"
    )
    repositories: dict[Enum, fastapp.BaseRepository] = Field(
        default_factory=dict,
        description="Dictionary of repositories keyed by service type",
    )
    registered_user_dependency_or_none: Callable[..., model.User] | None = Field(
        default=None,
        description="Dependency that provides the currently registered user",
    )
    new_user_dependency_or_none: Callable[..., model.User] | None = Field(
        default=None, description="Dependency that provides a new user"
    )
    idp_user_dependency_or_none: Callable[..., Any] | None = Field(
        default=None,
        description="Dependency that provides a user known by the identity provider but not registered in the application",
    )
    model_class_map: dict[type[fastapp.Model], type[fastapp.Model]] = Field(
        default_factory=dict,
        description="Mapping of commondb model classes to any derived implementing model classes",
    )
    command_class_map: dict[type[fastapp.Command], type[fastapp.Command]] = Field(
        default_factory=dict,
        description="Mapping of commondb command classes to any derived implementing command classes",
    )
    policy_class_map: dict[type[fastapp.Policy], type[fastapp.Policy]] = Field(
        default_factory=dict,
        description="Mapping of commondb policy classes to any derived implementing policy classes",
    )
    rbac_service_class: type[BaseRbacService] = Field(
        description="Class used for RBAC service"
    )
    user_manager_class: type[BaseUserManager] = Field(
        description="Class used for user management"
    )
    role_map: dict[enum.Role | Enum, str] = Field(
        description="Mapping of roles to unique string representations; an enum class is expanded to this mapping.",
    )
    role_set_map: dict[enum.RoleSet | Enum, frozenset[str]] = Field(
        description="Mapping of role sets to role strings; an enum class is expanded to this mapping.",
    )
    role_permissions_map: dict[
        str, set[tuple[type[fastapp.Command], fastapp.PermissionType]]
    ] = Field(
        description="Mapping of roles as strings to (command, permission type) tuples",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="Reverse mapping of role strings to their corresponding roles."
    )
    @cached_property
    def rev_role_map(self) -> dict[str, enum.Role | Enum]:
        """Return a reverse lookup map from role string to role enum value."""
        return {x: y for y, x in self.role_map.items()}

    @computed_field(  # type: ignore[prop-decorator]
        description="Dependency that provides the currently registered user."
    )
    @cached_property
    def registered_user_dependency(self) -> Callable[..., model.User]:
        """Return the registered-user dependency.

        Returns:
            Dependency that resolves a registered user.

        Raises:
            ValueError: If no registered-user dependency was configured.
        """
        if self.registered_user_dependency_or_none is None:
            raise ValueError("registered_user_dependency is not set")
        return self.registered_user_dependency_or_none

    @computed_field(  # type: ignore[prop-decorator]
        description="Dependency that provides a new user."
    )
    @cached_property
    def new_user_dependency(self) -> Callable[..., model.User]:
        """Return the new-user dependency.

        Returns:
            Dependency that resolves a newly registering user.

        Raises:
            ValueError: If no new-user dependency was configured.
        """
        if self.new_user_dependency_or_none is None:
            raise ValueError("new_user_dependency is not set")
        return self.new_user_dependency_or_none

    @computed_field(  # type: ignore[prop-decorator]
        description="Dependency that provides a user known by the identity provider but not registered in the application."
    )
    @cached_property
    def idp_user_dependency(self) -> Callable[..., Any]:
        """Return the identity-provider user dependency.

        Returns:
            Dependency that resolves an identity-provider user.

        Raises:
            ValueError: If no identity-provider user dependency was configured.
        """
        if self.idp_user_dependency_or_none is None:
            raise ValueError("idp_user_dependency is not set")
        return self.idp_user_dependency_or_none

    @field_validator("role_map", mode="before")
    @classmethod
    def _validate_role_map(
        cls, value: dict[enum.Role | Enum, str] | type[Enum]
    ) -> dict[enum.Role | Enum, str]:
        """Normalize role enum input and reject duplicate mapped values."""
        role_map: dict[enum.Role | Enum, str]
        if not isinstance(value, dict):
            role_map = {e: str(e.value) for e in value}
        else:
            role_map = value
        if len(set(role_map.values())) != len(role_map):
            raise ValueError("role_map must not contain duplicate values")

        return role_map

    @field_validator("role_set_map", mode="before")
    @classmethod
    def _validate_role_set_map(
        cls, value: dict[enum.RoleSet | Enum, str] | type[Enum]
    ) -> dict[enum.RoleSet | Enum, str]:
        """Normalize a role-set enum class to its value mapping."""
        if not isinstance(value, dict):
            # Allow passing Enum type directly for convenience
            value = {e: e.value for e in value}
        return value

    @field_validator("sorted_service_types", mode="before")
    @classmethod
    def _validate_sorted_service_types(
        cls, value: tuple[Enum, ...] | list[Enum]
    ) -> list[Enum]:
        """Normalize service types to a unique list in dependency order."""
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
        """Validate implementation classes against their mapped base classes."""
        for x, y in value.items():
            if not issubclass(y, x):
                raise ValueError(f"Class {y} is not a subclass of {x}")
        return value

    @overload
    def get_mapped_class(self, base_class: type[ModelType]) -> type[ModelType]: ...

    @overload
    def get_mapped_class(self, base_class: type[CommandType]) -> type[CommandType]: ...

    @overload
    def get_mapped_class(self, base_class: type[PolicyType]) -> type[PolicyType]: ...

    def get_mapped_class(
        self,
        base_class: type[fastapp.Model] | type[fastapp.Command] | type[fastapp.Policy],
    ) -> type[fastapp.Model] | type[fastapp.Command] | type[fastapp.Policy]:
        """Return a mapped implementation class or the supplied supported base class.

        Args:
            base_class: commondb model, command, or policy base class.

        Returns:
            Registered implementation class, or ``base_class`` when it has no mapping.

        Raises:
            ValueError: If ``base_class`` is not a supported FastApp base class.
        """
        if issubclass(base_class, fastapp.Model):
            return self.model_class_map.get(base_class, base_class)
        if issubclass(base_class, fastapp.Command):
            return self.command_class_map.get(base_class, base_class)
        if issubclass(base_class, fastapp.Policy):
            return self.policy_class_map.get(base_class, base_class)
        raise ValueError(f"Unsupported base class type: {base_class}")
