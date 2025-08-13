from __future__ import annotations

import abc
import uuid
from typing import Any, ClassVar, Hashable, Iterable, Self, Type

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
    NAME: ClassVar[str | None] = None
    ENTITY: ClassVar[Entity | None] = None


class User(Model):
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

    # @field_serializer("id")
    # def _serialize_id(self, value: Hashable, _info: Any) -> str:
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

    @computed_field
    def name(self) -> str:
        return f"{self.command_name}{Permission._NAME_DELIMITER}{self.permission_type.value}"

    @computed_field
    def sort_key(self) -> tuple[str, int]:
        permission_type_map = {
            PermissionType.EXECUTE: 0,
            PermissionType.CREATE: 1,
            PermissionType.READ: 2,
            PermissionType.UPDATE: 3,
            PermissionType.DELETE: 4,
        }
        return self.command_name, permission_type_map[self.permission_type]

    def __eq__(self, permission: object) -> bool:
        # TODO: Investigate why two objs of this class with the same values are
        # not equal without overriding __eq__
        if not isinstance(permission, Permission):
            return False
        return (
            self.name == permission.name
            and self.permission_type == permission.permission_type
        )

    def __repr__(self) -> str:
        return f"({self.command_name},{self.permission_type.value})"

    @field_serializer("permission_type")
    def _serialize_permission_type(self, value: PermissionType, _info: Any) -> str:
        return value.value


class Policy(abc.ABC):
    def get_is_denied_exception(self) -> Type[Exception]:
        return exc.UnauthorizedAuthError

    # Not an abstract method since it is not always needed
    def is_allowed(self, cmd: Command) -> bool:
        raise NotImplementedError

    # Not an abstract method since it is not always needed
    def get_content(self, cmd: Command) -> Any:
        raise NotImplementedError

    # Not an abstract method since it is not always needed
    def get_content_return_type(self, cmd: Command) -> Type:
        raise NotImplementedError

    # Not an abstract method since it is not always needed
    def filter(self, cmd: Command, retval: Any) -> Any:
        raise NotImplementedError


class Command(PydanticBaseModel):
    PERMISSION_TYPE_SET: ClassVar[PermissionTypeSet] = PermissionTypeSet.E
    NAME: ClassVar[str | None] = None

    _PERMISSIONS: ClassVar[frozenset[Permission] | None] = None

    id: Hashable = Field(
        default_factory=uuid.uuid4, description="The ID of the command obj"
    )
    user: User | None = None
    _policies: list[Policy] = PrivateAttr(default_factory=list)

    # @field_serializer("id")
    # def _serialize_id(self, value: Hashable, _info: Any) -> str | None:
    #     return serialize_id(value)


class CrudCommand(Command):
    PERMISSION_TYPE_SET: ClassVar[PermissionTypeSet] = PermissionTypeSet.CRUD
    MODEL_CLASS: ClassVar[Type[Model]] = Model

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
        default={},
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
        elif self.objs is not None:
            # Command has objs and cannot have obj_ids
            entity = self.MODEL_CLASS.ENTITY
            if entity is None:
                raise exc.InitializationServiceError(
                    f"Entity not set for model {self.MODEL_CLASS.__name__}"
                )
            id_field_name = entity.get_id_field_name()
            if isinstance(self.objs, list):
                if as_set:
                    retval = {getattr(obj, id_field_name) for obj in self.objs}
                    retval.discard(None)
                    return retval
                return [getattr(obj, id_field_name) for obj in self.objs]
            else:
                if as_set:
                    retval = {getattr(self.objs, id_field_name)}
                    retval.discard(None)
                    return retval
                return [getattr(self.objs, id_field_name)]
        # Command has neither obj_ids nor objs
        return None

    def get_objs(self) -> list[Model] | None:
        """
        Get the objects as a list, or None if no objects.
        """
        if self.objs is not None:
            return self.objs if isinstance(self.objs, list) else [self.objs]
        return None


class UpdateAssociationCommand(Command):
    ASSOCIATION_CLASS: ClassVar[Type[Model]] = Model
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
        default=[],
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
    name: str
    permissions: set[Permission]
