import re
import uuid
from enum import Enum
from functools import partial
from typing import Any, Callable, ClassVar, Hashable, Mapping, Self, Type
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from gen_epix.fastapp.domain.key import Key
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.enum import FieldType, StringCasing
from gen_epix.fastapp.exc import DomainException


class Entity(BaseModel):
    CAMEL_TO_SNAKE_CASE_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])"
    )
    NO_MODEL_ERROR_MSG: ClassVar[str] = "Entity does not have a model set"
    NOT_PERSISTABLE_ERROR_MSG: ClassVar[str] = "Entity is not persistable"
    NO_ERM_ERROR_MSG: ClassVar[str] = (
        "Entity is not linked to an entity-relationship model"
    )
    DEFAULT_ID_FIELD_NAME: ClassVar[str] = "id"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid.uuid4)
    persistable: bool = Field(default=False, frozen=True)
    snake_case_singular_name: str | None = None
    snake_case_plural_name: str | None = None
    camel_case_singular_name: str | None = None
    camel_case_plural_name: str | None = None
    pascal_case_singular_name: str | None = None
    pascal_case_plural_name: str | None = None
    kebab_case_singular_name: str | None = None
    kebab_case_plural_name: str | None = None
    url_name: str | None = None
    database_name: str | None = None
    schema_name: str | None = None
    table_name: str | None = None
    id_field_name: str | None = None
    keys: dict[int, Key] = {}
    links: dict[int, Link] = {}

    _model_class: Type[BaseModel] | None = None
    _db_model_class: Type | None = None
    _crud_command_class: Type | None = None
    _create_api_model_class: Type | None = None
    _read_api_model_class: Type | None = None
    _fields: dict[str, dict[str, Any]] | None = None
    _links_by_field_name: dict[str, tuple[int, Link]] = {}
    _get_link_id_by_model_class: dict[Type, Callable[[Any], Hashable]] = {}
    _keys_generator: Callable | None = None
    _has_model: bool = False

    @field_validator(
        "snake_case_plural_name",
        "snake_case_singular_name",
        "camel_case_plural_name",
        "camel_case_singular_name",
        "pascal_case_plural_name",
        "pascal_case_singular_name",
        "kebab_case_plural_name",
        "kebab_case_singular_name",
        "url_name",
        "database_name",
        "schema_name",
        "table_name",
        "id_field_name",
        mode="before",
    )
    @classmethod
    def _validate_names(cls, value: str | Enum | None) -> str | None:
        return str(value.value) if isinstance(value, Enum) else value

    @model_validator(mode="before")
    @classmethod
    def _validate_model(cls, data: Any) -> Any:
        if (
            "id_field_name" not in data
            and "persistable" in data
            and data["persistable"]
        ):
            data["id_field_name"] = cls.DEFAULT_ID_FIELD_NAME
        return data

    @field_validator("keys", mode="before")
    @classmethod
    def _validate_keys(cls, value: dict[int, Any]) -> dict[int, Key]:
        """
        Validate and convert keys to Key objs.
        """
        return {x: y if isinstance(y, Key) else Key(y) for x, y in value.items()}

    @field_validator("links", mode="before")
    @classmethod
    def _validate_links(cls, value: dict[int, Any]) -> dict[int, Link]:
        """
        Validate and convert links to Link objs.
        """
        return {
            x: (
                y
                if isinstance(y, Link)
                else (
                    Link(
                        link_field_name=y[0],
                        link_model_class=y[1],
                        relationship_field_name=y[2],
                    )
                    if isinstance(y, tuple)
                    else Link(**y)
                )
            )
            for x, y in value.items()
        }

    @property
    def name(self) -> str:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        return self._model_class.NAME  # type: ignore

    @property
    def model_class(self) -> Type[BaseModel]:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        return self._model_class  # type: ignore

    @property
    def crud_command_class(self) -> Type[BaseModel] | None:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        if not self.persistable:
            raise ValueError(Entity.NOT_PERSISTABLE_ERROR_MSG)
        return self._crud_command_class  # type: ignore

    @property
    def db_model_class(self) -> Type | None:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        if not self.persistable:
            raise ValueError(Entity.NOT_PERSISTABLE_ERROR_MSG)
        return self._db_model_class  # type: ignore

    @property
    def create_api_model_class(self) -> Type | None:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        return self._create_api_model_class  # type: ignore

    @property
    def read_api_model_class(self) -> Type | None:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        return self._read_api_model_class  # type: ignore

    @property
    def get_obj_id(self) -> Callable[[Any], Hashable]:
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        assert self.id_field_name
        return lambda x: getattr(x, self.id_field_name)

    def set_model_class(
        self, model_class: Type[BaseModel], on_existing: str = "raise"
    ) -> Self:
        """
        Set the model class for the entity.

        Parameters
        ----------
        model_class : Type[BaseModel]
            The model class to set for the entity.

        Returns
        -------
        Self
            The updated entity obj.

        Raises
        ------
        ValueError
            If the entity already has a model set or if the id_field_name is invalid.
        """
        if self.has_model():
            if self._model_class is model_class:
                return self
            if on_existing == "raise":
                raise ValueError("Instance already has a model set")
            elif on_existing == "replace":
                pass
            else:
                raise ValueError(f"Unknown on_existing value: {on_existing}")
        field_names = Entity._get_model_field_names(model_class)

        # Set fields and derive their FieldType
        self._fields = {
            x[0]: {
                "name": x[0],
                "alias": x[0] if not x[1] else x[1],
                "type": FieldType.VALUE,
            }
            for x in field_names
        }

        # Set ID field
        if self.id_field_name:
            if self.id_field_name not in self._fields:
                raise ValueError(
                    f"id_field_name property for model {model_class} does "
                    f"not contain a valid field name: {self.id_field_name}"
                )
            self._fields[self.id_field_name]["type"] = FieldType.ID

        # Set LINK and RELATIONSHIP fields
        for link in self.links.values():
            self._fields[link.link_field_name]["type"] = FieldType.LINK
            if link.relationship_field_name:
                self._fields[link.relationship_field_name][
                    "type"
                ] = FieldType.RELATIONSHIP

        # Set COMPUTED fields
        for field_name in model_class.model_computed_fields:
            self._fields[field_name]["type"] = FieldType.COMPUTED

        # Verify and parse links
        self._verify_and_parse_model_links(model_class)

        # Set properties and create keys generator
        self._model_class = model_class
        self._has_model = True
        self._create_keys_generator()
        return self

    def has_model(self) -> bool:
        """
        Check if the entity has a model set.

        Returns
        -------
        bool
            True if the entity has a model set, False otherwise.
        """
        return self._model_class is not None

    def set_db_model_class(self, db_model_class: Type) -> Self:
        """
        Set the repository model class for the entity, which is intended as the class
        that is stored or retrieved from the repository.
        """
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        if not self.persistable:
            raise ValueError(Entity.NOT_PERSISTABLE_ERROR_MSG)
        self._db_model_class = db_model_class
        return self

    def set_create_api_model_class(self, create_api_model_class: Type) -> Self:
        """
        Set the API model class for the entity, which is intended as the request model
        that is posted to an endpoint to create a resource.
        """
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        self._create_api_model_class = create_api_model_class
        return self

    def set_read_api_model_class(self, read_api_model_class: Type) -> Self:
        """
        Set the API model class for the entity, which is intended as the model
        that returned in a response by an endpoint.
        """
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        self._read_api_model_class = read_api_model_class
        return self

    def set_crud_command_class(self, crud_command_class: Type[BaseModel]) -> Self:
        """
        Set the CRUD command class for the entity, which is intended as the class
        that is stored or retrieved from the repository.
        """
        if not self.has_model():
            raise DomainException(Entity.NO_MODEL_ERROR_MSG)
        if not self.persistable:
            raise ValueError(Entity.NOT_PERSISTABLE_ERROR_MSG)
        self._crud_command_class = crud_command_class
        return self

    def get_field_names(
        self, by_alias: bool = True, field_type: FieldType | None = None
    ) -> list[str]:
        """
        Get the field names of the entity.

        Parameters
        ----------
        by_alias : bool, optional
            If True, return the field names by alias. Defaults to True.
        field_type : FieldType or None, optional
            The type of model fields to filter by. Defaults to None.

        Returns
        -------
        list[str]
            A list of field names of the entity.

        Raises
        ------
        ValueError
            If the entity does not have fields set.
        """
        if self._fields is None:
            raise ValueError("Entity does not have fields set")
        key = "alias" if by_alias else "name"
        return [
            x[key]
            for x in self._fields.values()
            if not field_type or x["type"] == field_type
        ]

    def get_id_field_name(self, by_alias: bool = True) -> str | None:
        """
        Get the ID field name of the entity.

        Parameters
        ----------
        by_alias : bool, optional
            If True, return the ID field name by alias. Defaults to True.

        Returns
        -------
        str
            The ID field name of the entity.

        """
        field_names = self.get_field_names(by_alias=by_alias, field_type=FieldType.ID)
        if not field_names:
            raise ValueError("Entity does not have an ID field")
        return field_names[0]

    def get_keys_field_names(self, by_alias: bool = True) -> list[tuple[str, ...]]:
        if by_alias:
            return [
                tuple(self._fields[y]["alias"] for y in x.field_names)
                for x in self.keys.values()
            ]
        return [x.field_names for x in self.keys.values()]

    def get_link_field_names(self, by_alias: bool = True) -> list[str]:
        """
        Get the link field names of the entity.

        Parameters
        ----------
        by_alias : bool, optional
            If True, return the link field names by alias. Defaults to True.

        Returns
        -------
        list[str]
            A list of link field names of the entity.
        """

        return self.get_field_names(by_alias=by_alias, field_type=FieldType.LINK)

    def get_relationship_field_names(self, by_alias: bool = True) -> list[str]:
        """
        Get the relationship field names of the entity.

        Parameters
        ----------
        by_alias : bool, optional
            If True, return the back-populate field names by alias. Defaults to True.

        Returns
        -------
        list[str]
            A list of back-populate field names of the entity.
        """
        return self.get_field_names(
            by_alias=by_alias, field_type=FieldType.RELATIONSHIP
        )

    def get_value_field_names(self, by_alias: bool = True) -> list[str]:
        """
        Get the value field names of the entity.

        Parameters
        ----------
        by_alias : bool, optional
            If True, return the value field names by alias. Defaults to True.

        Returns
        -------
        list[str]
            A list of value field names of the entity.
        """

        return self.get_field_names(by_alias=by_alias, field_type=FieldType.VALUE)

    def get_keys_generator(self) -> Callable | None:
        """
        Get the keys generator for the entity.

        Returns
        -------
        Callable or None
            The keys generator for the entity, or None if no keys generator is set.

        Raises
        ------
        ValueError
            If the entity does not have a model set.
        """
        if not self.has_model():
            raise ValueError("Entity does not have a model set")
        return self._keys_generator

    def get_link_id(self, link_model_class: Type) -> Callable[[Any], Hashable]:
        fun = self._get_link_id_by_model_class.get(link_model_class)
        if fun is None:
            raise ValueError(
                f"No link or several links to {link_model_class.__name__} exist for entity {self.name}"
            )
        return fun

    def get_link_entity(self, link_field_name: str) -> Any | None:
        """
        Get the linked entity, if any.

        Parameters
        ----------
        link_field_name : str
            The field name of the link.

        Returns
        -------
        Entity | None
            The linked entity or None if no linked entity.

        Raises
        ------
        ValueError
            If the entity is not linked to an entity-relationship model.
        """
        _, link = self._links_by_field_name.get(link_field_name, (None, None))
        return link.link_model_class.ENTITY if link else None  # type: ignore

    def get_link_properties_by_field_name(
        self, link_field_name: str
    ) -> tuple[int, Type[BaseModel], str | None]:
        """
        Get the properties of a link by its field name.

        Parameters
        ----------
        link_field_name : str
            The field name of the link.

        Returns
        -------
        tuple[int, Type[BaseModel], str or None]
            A tuple containing the link type ID, link model class, and back-populate
            field name.

        Raises
        ------
        ValueError
            If the entity is not linked to an entity-relationship model or if the
            entity does not have links set.
        """
        link_type_id, link = self._links_by_field_name.get(
            link_field_name, (None, None)
        )
        if not link_type_id or not link:
            raise ValueError(f"Field {link_field_name} is not a link field")
        return (link_type_id, link.link_model_class, link.relationship_field_name)

    def has_links(self) -> bool:
        """
        Check if the entity has links.

        Returns
        -------
        bool
            True if the entity has links, False otherwise.
        """
        return len(self.links) > 0

    def has_keys(self) -> bool:
        """
        Check if the entity has keys.

        Returns
        -------
        bool
            True if the entity has keys, False otherwise.
        """
        return len(self.keys) > 0

    def get_name_by_casing(
        self,
        string_casing: StringCasing = StringCasing.SNAKE_CASE,
        is_plural: bool = False,
    ) -> str | None:
        if string_casing == StringCasing.SNAKE_CASE:
            name = (
                self.snake_case_plural_name
                if is_plural
                else self.snake_case_singular_name
            )
        elif string_casing == StringCasing.PASCAL_CASE:
            name = (
                self.pascal_case_plural_name
                if is_plural
                else self.pascal_case_singular_name
            )
        elif string_casing == StringCasing.CAMEL_CASE:
            name = (
                self.camel_case_plural_name
                if is_plural
                else self.camel_case_singular_name
            )
        else:
            raise NotImplementedError(f"String casing {string_casing} not implemented")
        return name

    def copy(self, update: Mapping[str, Any]) -> "Entity":
        """
        Create a copy of the entity with the given keyword arguments replacing
        any of the existing values.

        Parameters
        ----------
        **kwargs : Any
            Keyword arguments to update the entity.

        Returns
        -------
        Self
            A copy of the entity with updated attributes.
        """
        props = self.model_dump(exclude_unset=True, exclude_defaults=True)
        props.update(update)
        return Entity(**props)

    def _verify_and_parse_model_links(self, model_class: Type[BaseModel]) -> Self:
        """
        Check if the link field names and back populate field names are valid given
        the model class. If they are valid, set the type of the field to LINK and
        add a map from link field name to link type id and link object to the entity.

        Parameters
        ----------
        model_class : Type[BaseModel]
            The model class to verify and parse links for.

        Returns
        -------
        Self
            The updated entity obj.

        Raises
        ------
        ValueError
            If any link field names or back populate field names are invalid.
        """
        link_field_names: set[str] = set()
        relationship_field_names: set[str] = set()
        to_remove_get_link_id = []
        assert isinstance(self._fields, dict)
        assert isinstance(self._links_by_field_name, dict)
        assert isinstance(self._get_link_id_by_model_class, dict)
        for link_type_id, link in self.links.items():
            self._verify_link_field_name(model_class, link_field_names, link)
            self._fields[link.link_field_name]["type"] = FieldType.LINK
            self._links_by_field_name[link.link_field_name] = (link_type_id, link)
            if link.link_model_class in self._get_link_id_by_model_class:
                to_remove_get_link_id.append(link.link_model_class)
            else:
                self._get_link_id_by_model_class[link.link_model_class] = partial(
                    lambda x, y: getattr(y, x), link.link_field_name
                )
            self._verify_relationship_fields(
                model_class, relationship_field_names, link
            )
        for link_model_class in to_remove_get_link_id:
            self._get_link_id_by_model_class.pop(link_model_class)
        self._check_identical_field_names(link_field_names, relationship_field_names)
        return self

    def _verify_link_field_name(
        self, model_class: Type[BaseModel], link_field_names: set, link: Link
    ) -> None:
        """
        Verify the link field name.

        Parameters
        ----------
        model_class : Type[BaseModel]
            The model class to verify the link field name for.
        link_field_names : set
            The set of link field names.
        link : Link
            The link to verify.

        Raises
        ------
        ValueError
            If the link field name is invalid or not unique.
        """
        assert self._fields
        if link.link_field_name not in self._fields:
            raise ValueError(
                f"Link field name {link.link_field_name} to {link.link_model_class} "
                f"for model {model_class.__name__} is not a valid field name"
            )
        if link.link_field_name == self.id_field_name:
            raise ValueError(
                f"Link field name is identical to id field name: {link.link_field_name}"
            )
        if link.link_field_name in link_field_names:
            raise ValueError(
                f"Link field name {link.link_field_name}"
                f" for model {model_class.__name__} is not unique"
            )
        link_field_names.add(link.link_field_name)

    def _verify_relationship_fields(
        self, model_class: Type[BaseModel], relationship_field_names: set, link: Link
    ) -> None:
        """
        Verify the back populate field names.

        Parameters
        ----------
        model_class : Type[BaseModel]
            The model class to verify the back populate field names for.
        relationship_field_names : set
            The set of back populate field names.
        link : Link
            The link to verify.

        Raises
        ------
        ValueError
            If the back populate field name is invalid or not unique.
        """
        if link.relationship_field_name:
            assert self._fields
            if link.relationship_field_name not in self._fields:
                raise ValueError(
                    f"Back populate field name {link.relationship_field_name} "
                    f"to {link.link_field_name} for model {model_class.__name__} "
                    "is not a valid field name"
                )
            if link.relationship_field_name == self.id_field_name:
                raise ValueError(
                    "Back populate field name is identical to id "
                    f"field name: {link.relationship_field_name}"
                )
            if link.relationship_field_name in relationship_field_names:
                raise ValueError(
                    f"Back populate field name {link.relationship_field_name}"
                    f" for model {model_class.__name__} is not unique"
                )
            relationship_field_names.add(link.relationship_field_name)
            self._fields[link.relationship_field_name]["type"] = FieldType.RELATIONSHIP

    def _check_identical_field_names(
        self, link_field_names: set, relationship_field_names: set
    ) -> None:
        identical_field_names = link_field_names & relationship_field_names
        if identical_field_names:
            identical_field_names_str = ", ".join(identical_field_names)
            raise ValueError(
                "Some back populate field names "
                f"are identical to link field names: {identical_field_names_str}"
            )

    def _create_keys_generator(self) -> None:
        """Create a function that will calculate all the keys for a given obj"""
        # Special case: no keys
        if not self.keys:
            self._keys_generator = lambda x: {}
            return

        def keys_generator(keys: dict[int, Key], obj: BaseModel) -> dict[int, Any]:
            return {x: y(obj) for x, y in keys.items()}

        self._keys_generator = partial(keys_generator, self.keys)

    @classmethod
    def camel_to_snake_case(cls, value: str) -> str:
        return cls.CAMEL_TO_SNAKE_CASE_PATTERN.sub("_", value).lower()

    @staticmethod
    def _get_model_field_names(
        model_class: Type[BaseModel],
    ) -> list[tuple[str, str | None]]:
        """
        Returns a list of (field_name, alias) tuples.
        """
        field_names = []
        for field_name, field in (
            model_class.model_fields | model_class.model_computed_fields
        ).items():
            field_names.append((field_name, field.alias))
        return field_names

    def __hash__(self) -> int:
        return self.name.__hash__()
