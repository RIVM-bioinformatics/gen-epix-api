from __future__ import annotations

import abc
import uuid
from collections.abc import Hashable, Iterable
from functools import cached_property
from typing import Any, ClassVar, Literal, Self, overload

from pydantic import BaseModel
from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    Field,
    PrivateAttr,
    computed_field,
    field_serializer,
    model_validator,
)

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import (
    CrudOperation,
    CrudOperationSet,
    PermissionType,
    PermissionTypeSet,
)
from gen_epix.filter.base import Filter


class Model(PydanticBaseModel):
    """
    Base class for all models in an application. Models are used to represent the
    state of the application and are typically persisted in a database. Models can also
    be used to represent the state of the application in memory, e.g. for caching or
    for passing data between services. Models can be immutable or mutable, depending on
    the use case.

    Each model must have an associated Entity, which defines the metadata for the
    model. See the Entity class for more details. The Entity must be set in the
    subclass of Model. Analogously, a unique name for the model can be set in the
    subclass, which can be used for identification and logging purposes.

    The model_entity and model_name class methods can be used to retrieve the Entity
    and name of the model, respectively. These methods have the same "model_" prefix as
    generic Pydantic models to avoid name conflicts with other.
    """

    NAME: ClassVar[str] = None  # type: ignore[assignment]
    ENTITY: ClassVar[Entity] = None  # type: ignore[assignment]

    @classmethod
    def model_entity(cls) -> Entity:
        """Get the Entity associated with this model."""
        if cls.ENTITY is None:
            raise exc.InitializationServiceError(
                f"Entity not set for model {cls.__name__}"
            )
        return cls.ENTITY

    @classmethod
    def model_name(cls) -> str:
        """Get the name of the model."""
        if cls.NAME is None:
            raise exc.InitializationServiceError(
                f"Name not set for model {cls.__name__}"
            )
        return cls.NAME

    @overload
    def get_id(self, raise_on_missing: Literal[True]) -> Hashable: ...

    @overload
    def get_id(self, raise_on_missing: Literal[False] = ...) -> Hashable | None: ...

    def get_id(self, raise_on_missing: bool = False) -> Hashable | None:
        """
        Get the ID of the model instance. If the ID is not set and
        raise_on_missing is True, an InitializationServiceError is raised.
        Otherwise, None is returned if the ID is not set. If the Model has no ID field, an error is raised.

        This method retrieves the ID using the field name defined in the
        associated Entity, so that it can be used generically for any model
        without needing to know the specific field name of the ID. The ID is
        typically used for persistence and for identifying the model instance
        across systems.

        This method should be overridden where relevant for performance reasons.
        """
        id_: Hashable | None = getattr(self, self.ENTITY.get_id_field_name())
        if id_ is None and raise_on_missing:
            raise exc.InvalidIdsError(
                f"ID not set for model instance {self.__class__.__name__}"
            )
        return id_


class User(PydanticBaseModel):
    """
    A user of the application. This can represent an actual user, or a service
    account, or any other type of principal that can be authenticated and authorized to
    perform actions in the application. The key of the user is used to identify the
    user across systems, e.g. as a claim a in security token.
    """

    id: Hashable | None = Field(
        default_factory=uuid.uuid4,
        description="The ID of the user. This can be the key of the user (see get_key method), or a separate ID.",
    )

    def get_key(self) -> str:
        """
        Get the key of the user. The key is used to identify the user across systems,
        e.g. as a claim a in security token. This can be the email or any other unique
        identifier. Override this method to use retrieve the key in question, if
        different from the ID of the user.
        """
        return str(self.id)

    # @field_serializer("id", mode="plain")
    # def _serialize_id(self, value: Hashable) -> str:
    #     return str(value)


class Permission(PydanticBaseModel, frozen=True):
    """
    Implements a permission as a combination of (command_name, permission_type).
    The command_name is a string rather than the class of the command, to avoid
    issues with serialization such as for persistence and for API requests/responses.
    """

    _NAME_DELIMITER: ClassVar[str] = "_"

    command_name: str
    permission_type: PermissionType

    @computed_field(  # type: ignore[prop-decorator]
        description="The name of the permission, combining command name and permission type."
    )
    @cached_property
    def name(self) -> str:
        """"""
        return f"{self.command_name}{Permission._NAME_DELIMITER}{self.permission_type.value}"

    @computed_field(  # type: ignore[prop-decorator]
        description="A sort key for ordering permissions."
    )
    @cached_property
    def sort_key(self) -> tuple[str, int]:
        """"""
        permission_type_map = {
            PermissionType.EXECUTE: 0,
            PermissionType.CREATE: 1,
            PermissionType.READ: 2,
            PermissionType.UPDATE: 3,
            PermissionType.DELETE: 4,
        }
        return self.command_name, permission_type_map[self.permission_type]

    def __eq__(self, permission: object) -> bool:
        """"""
        # TODO: Investigate why two objs of this class with the same values are
        # not equal without overriding __eq__
        if not isinstance(permission, Permission):
            return False
        return (
            self.name == permission.name
            and self.permission_type == permission.permission_type
        )

    def __repr__(self) -> str:
        """"""
        return f"({self.command_name},{self.permission_type.value})"

    @field_serializer("permission_type", mode="plain")
    def _serialize_permission_type(self, value: PermissionType) -> str:
        """"""
        return value.value


class Policy(abc.ABC):
    """
    A policy defines logic for a command to be executed before, during or after the
    execution of the command. It can be used to implement e.g. authorization and other
    cross-cutting concerns.
    """

    def get_is_denied_exception(self) -> type[Exception]:
        return exc.UnauthorizedAuthError

    # Not an abstract method since it is not always needed
    def is_allowed(self, cmd: Command) -> bool:
        raise NotImplementedError

    # Not an abstract method since it is not always needed
    def get_content(self, cmd: Command) -> Any:
        raise NotImplementedError

    # Not an abstract method since it is not always needed
    def get_content_return_type(self, cmd: Command) -> type:
        raise NotImplementedError

    # Not an abstract method since it is not always needed
    def filter(self, cmd: Command, retval: Any) -> Any:
        raise NotImplementedError


class Command(PydanticBaseModel):
    """
    A command represents an action to be performed in the application. The logic for
    executing commands is typically implemented by services in the application, which
    register the relevant handler function or method with the app.
    """

    PERMISSION_TYPE_SET: ClassVar[PermissionTypeSet] = PermissionTypeSet.E
    NAME: ClassVar[str | None] = None

    _PERMISSIONS: ClassVar[frozenset[Permission] | None] = None

    id: Hashable = Field(
        default_factory=uuid.uuid4, description="The ID of the command obj"
    )
    user: User | None = None
    _policies: list[Policy] = PrivateAttr(default_factory=list)

    # @field_serializer("id", mode="plain")
    # def _serialize_id(self, value: Hashable) -> str | None:
    #     return serialize_id(value)


class CrudCommand(Command):
    """
    A command base class for performing a CRUD operation on a model. The command
    includes the CRUD operation to perform, the identifier(s) of the object(s) to
    operate on and/or the object(s) to operate on, and optional filters for read or
    delete all operations and for access control. The command also includes
    validation logic to ensure that the combination of operation, identifiers,
    objects and filters is valid.
    """

    PERMISSION_TYPE_SET: ClassVar[PermissionTypeSet] = PermissionTypeSet.CRUD
    MODEL_CLASS: ClassVar[type[Model]] = Model

    operation: CrudOperation = Field(description="The CRUD operation to perform.")
    obj_ids: Hashable | list[Hashable] | None = Field(
        default=None,
        description="The identifier(s) of the object(s) to operate on. Must be set to a single identifier for read, delete or exists one operations, and to a list of identifiers for read, delete or exists some operations. Otherwise must be None.",
    )
    objs: Model | list[Model] | None = Field(
        default=None,
        description="The object(s) to operate on. Must be set to a single object for create or update one operations, and to a list of objects for create or update some operations. Otherwise must be None.",
    )
    query_filter: Filter | None = Field(
        default=None,
        description="Optional filter to apply to the results of a read or delete all operation, thereby effectively applying a query instead of reading or deleting all. Must be None for all other operations.",
    )
    access_filter: Filter | None = Field(
        default=None,
        description="Optional filter to apply object-level access control. For a read or delete all operation, it filters the results just as the query_filter does and when both are provided only object that match both filters will be returned or deleted. For any other operation, an unauthorized exception is raised if the provided objects do not match the filter.",
    )
    props: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional properties to pass to the command and which can be used by custom implementations.",
    )

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        operation = self.operation
        obj_ids = self.obj_ids
        objs = self.objs
        if obj_ids is None:
            if (
                operation not in CrudOperationSet.ANY_ALL.value
                and operation not in CrudOperationSet.WRITE.value
            ):
                raise ValueError(
                    f"Invalid operation for obj_ids=None: {operation.value}"
                )
        elif isinstance(obj_ids, Iterable) and not isinstance(obj_ids, Model):
            if operation not in CrudOperationSet.NON_CREATE_SOME.value:
                raise ValueError(
                    f"Invalid operation for obj_ids=list: {operation.value}"
                )
        else:
            if operation not in CrudOperationSet.NON_CREATE_ONE.value:
                raise ValueError(
                    f"Invalid operation for obj_ids=obj_id: {operation.value}"
                )
        if objs is None:
            if operation in CrudOperationSet.WRITE.value:
                raise ValueError(
                    f"Invalid operation for objects=None: {operation.value}"
                )
        elif isinstance(objs, Iterable) and not isinstance(objs, Model):
            if operation not in CrudOperationSet.WRITE_SOME.value:
                raise ValueError(f"Invalid operation for objs=list: {operation.value}")
        else:
            if operation not in CrudOperationSet.WRITE_ONE.value or not isinstance(
                objs, Model
            ):
                raise ValueError(
                    f"Invalid operation for objs=object: {operation.value}"
                )
        if self.query_filter is not None:
            if operation not in CrudOperationSet.ANY_ALL.value:
                raise ValueError(
                    f"Invalid operation for query_filter not None: {operation.value}"
                )
        return self

    def get_obj_ids(
        self, as_set: bool = False
    ) -> list[Hashable | None] | set[Hashable] | None:
        """
        Get the object IDs, either from the obj_ids field or from the objs field. In
        the latter case, the IDs are extracted from the objects using the entity's ID
        field name. In case the command has obj_ids=None, None is returned. If
        as_set=True, a set of IDs and excluding None is returned where otherwise a list
        would be returned.
        """
        if self.obj_ids is not None:
            # Command has obj_ids and cannot have objs
            if as_set:
                return (
                    set(self.obj_ids)
                    if isinstance(self.obj_ids, list)
                    else {self.obj_ids}
                )
            return self.obj_ids if isinstance(self.obj_ids, list) else [self.obj_ids]
        objs = self.objs
        if objs is None:
            # No obj_ids and no objs
            return None
        if isinstance(objs, list):
            # List of objects
            if as_set:
                retval = {x.get_id() for x in objs}
                retval.discard(None)
                return retval
            return [x.get_id() for x in objs]
        # Single object
        if as_set:
            retval = {objs.get_id()}
            retval.discard(None)
            return retval
        return [objs.get_id()]

    def get_objs(self) -> list[Model] | None:
        """
        Get the objects as a list, or None if no objects.
        """
        if self.objs is not None:
            return self.objs if isinstance(self.objs, list) else [self.objs]
        return None

    def is_create(self) -> bool:
        """Whether the command is a create operation."""
        return self.operation in CrudOperationSet.CREATE.value

    def is_read(self, exclude_exists: bool = False) -> bool:
        """
        Whether the command is a read or exists operation. Exists also requires read
        operation and is included by default. If exclude_exists is True, only read
        operations are included.
        """
        if exclude_exists:
            return self.operation in CrudOperationSet.READ.value
        return self.operation in CrudOperationSet.READ_OR_EXISTS.value

    def is_read_all(self) -> bool:
        """Whether the command is a read all operation."""
        return self.operation == CrudOperation.READ_ALL

    def is_read_one(self) -> bool:
        """Whether the command is a read one operation."""
        return self.operation == CrudOperation.READ_ONE

    def is_update(self) -> bool:
        """Whether the command is an update operation."""
        return self.operation in CrudOperationSet.UPDATE.value

    def is_delete(self) -> bool:
        """Whether the command is a delete operation."""
        return self.operation in CrudOperationSet.DELETE.value

    def is_delete_all(self) -> bool:
        """Whether the command is a delete all operation."""
        return self.operation == CrudOperation.DELETE_ALL

    def is_exists(self) -> bool:
        """Whether the command is an exists operation."""
        return self.operation in CrudOperationSet.EXISTS.value

    def is_write(self) -> bool:
        """
        Whether the command is a write operation, i.e. a create, update or upsert
        operation.
        """
        return self.operation in CrudOperationSet.WRITE.value

    def is_crud_one(self) -> bool:
        """
        Whether the command is any one operation, i.e. a create one, read one, update
        one, delete one or exists one operation.
        """
        return self.operation in CrudOperationSet.ANY_ONE.value

    def is_crud_all(self) -> bool:
        """
        Whether the command is any all operation, i.e. a read all or delete all
        operation.
        """
        return self.operation in CrudOperationSet.ANY_ALL.value


class UpdateAssociationCommand(Command):
    """
    A command base class for updating a many-to-many association between two entities.
    The command includes the identifiers of the two objects to associate, or the
    association objects themselves, and validation logic to ensure that the combination
    of identifiers and association objects is valid. The command also includes an
    optional props field for additional properties to pass to the command and which can
    be used by custom implementations.
    """

    ASSOCIATION_CLASS: ClassVar[type[Model]] = Model
    LINK_FIELD_NAME1: ClassVar[str] = ""
    LINK_FIELD_NAME2: ClassVar[str] = ""

    obj_id1: Hashable | None = Field(
        default=None,
        description="The ID of the instance of the first entity in the many-to-many association.",
    )
    obj_id2: Hashable | None = Field(
        default=None,
        description="The ID of the instance of the second entity in the many-to-many association.",
    )
    association_objs: list[Model] = Field(
        default_factory=list,
        description="The association objects, linking the first (field LINK_FIELD_NAME1) to the second (field LINK_FIELD_NAME2) instance.",
    )
    props: dict[str, Any] = {}

    @model_validator(mode="after")
    def _validate_state(self) -> Self:
        obj_id1 = self.obj_id1
        obj_id2 = self.obj_id2
        association_objs = self.association_objs
        if obj_id1 and obj_id2:
            raise exc.DomainException(
                f"Invalid state: obj_id1 and obj_id2 are both present"
            )
        if association_objs:
            if obj_id1 and not all(
                getattr(obj, self.LINK_FIELD_NAME1) == obj_id1
                for obj in association_objs
            ):
                raise exc.DomainException(
                    f"Invalid state: obj_id1 and association_objs not matching"
                )
            if obj_id2 and not all(
                getattr(obj, self.LINK_FIELD_NAME2) == obj_id2
                for obj in association_objs
            ):
                raise exc.DomainException(
                    f"Invalid state: obj_id2 and association_objs not matching"
                )
        else:
            if not obj_id1 and not obj_id2:
                raise exc.DomainException(
                    f"Invalid state: association_objs, obj_id1 and obj_id2 all empty"
                )
        return self


class Role(PydanticBaseModel):
    """
    A role represents a set of permissions that can be assigned to users e.g. for
    implementing role-based access control (RBAC).
    """

    name: str
    permissions: set[Permission]


class ModelFieldProps(BaseModel):
    """
    Additional properties of a model field. The application of these properties needs
    to be implemented in the services using the model. Subclass as needed for specific
    additional properties.

    Additional validation:
    - is_mutable_always cannot be True if is_mutable_if_empty is False.
    """

    is_mutable_if_empty: bool = Field(
        default=True,
        description="Whether the field is mutable after creation if its initial value was empty (None, empty dict, empty list). If the field is always mutable, set to True as well.",
    )
    is_mutable_always: bool = Field(
        default=False,
        description="Whether the field is always mutable after creation. Cannot be True if is_mutable_if_empty is False. The default is conservatively set to False, so that immutability is assumed unless explicitly specified.",
    )
    is_sub_field_dict: bool = Field(
        default=False,
        description="Whether the field content is a dict with sub fields (key/value pairs) rather than a single value.",
    )

    @model_validator(mode="after")
    def _validate_model(self) -> Self:
        if not self.is_mutable_if_empty and self.is_mutable_always:
            raise ValueError(
                "is_mutable_always cannot be True if is_mutable_if_empty is False."
            )
        return self

    def is_mutable_value(self, stored_value: Any | None) -> bool:
        """
        Determine if a stored value for this field is mutable.
        """
        if self.is_mutable_always:
            return True
        if self.is_mutable_if_empty:
            if self.is_sub_field_dict:
                return stored_value is None or len(stored_value) == 0
            if stored_value is None:
                return True
        return False
