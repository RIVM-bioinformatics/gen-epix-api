from collections.abc import Hashable
from enum import Enum
from typing import Literal

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.enum import (
    CrudOperation,
    OnException,
    PermissionType,
    PermissionTypeSet,
)
from gen_epix.fastapp.model import Command, CrudCommand, Model, Permission


class Domain:
    CRUD_PERMISSION_TYPE_MAP: dict[CrudOperation, PermissionType] = {
        CrudOperation.CREATE_ONE: PermissionType.CREATE,
        CrudOperation.CREATE_SOME: PermissionType.CREATE,
        CrudOperation.READ_ALL: PermissionType.READ,
        CrudOperation.READ_SOME: PermissionType.READ,
        CrudOperation.READ_ONE: PermissionType.READ,
        CrudOperation.UPDATE_ONE: PermissionType.UPDATE,
        CrudOperation.UPDATE_SOME: PermissionType.UPDATE,
        CrudOperation.DELETE_ONE: PermissionType.DELETE,
        CrudOperation.DELETE_SOME: PermissionType.DELETE,
        CrudOperation.EXISTS_ONE: PermissionType.READ,
        CrudOperation.EXISTS_SOME: PermissionType.READ,
    }
    PERMISSION_TYPE_CRUD_MAP: dict[PermissionType, frozenset[CrudOperation]] = {
        PermissionType.CREATE: frozenset(
            {CrudOperation.CREATE_ONE, CrudOperation.CREATE_SOME}
        ),
        PermissionType.READ: frozenset(
            {
                CrudOperation.READ_ALL,
                CrudOperation.READ_SOME,
                CrudOperation.READ_ONE,
                CrudOperation.EXISTS_ONE,
                CrudOperation.EXISTS_SOME,
            }
        ),
        PermissionType.UPDATE: frozenset(
            {CrudOperation.UPDATE_ONE, CrudOperation.UPDATE_SOME}
        ),
        PermissionType.DELETE: frozenset(
            {
                CrudOperation.DELETE_ALL,
                CrudOperation.DELETE_SOME,
                CrudOperation.DELETE_ONE,
            }
        ),
    }

    @staticmethod
    def get_service_name(service_type: Hashable | None) -> str:
        if service_type is None:
            raise exc.DomainException("811a1bac", "Service type is not given")
        if isinstance(service_type, str):
            return service_type
        if isinstance(service_type, Enum):
            return str(service_type.value)
        return str(service_type)

    @staticmethod
    def get_command_name(command_class: type[Command]) -> str:
        if command_class.NAME is None:
            command_class.NAME = command_class.__name__
        return command_class.NAME

    @staticmethod
    def get_command_permissions(command_class: type[Command]) -> frozenset[Permission]:
        if command_class._PERMISSIONS is None:
            if command_class.NAME is None:
                raise exc.InitializationServiceError(
                    "d67d090a", f"Command {command_class} has no NAME set"
                )
            command_class._PERMISSIONS = frozenset(
                {
                    Permission(command_name=command_class.NAME, permission_type=x)
                    for x in command_class.PERMISSION_TYPE_SET.value
                }
            )
        return command_class._PERMISSIONS

    @staticmethod
    def get_model_name(model_class: type[Model]) -> str:
        if model_class.NAME is None:
            model_class.NAME = model_class.__name__  # type: ignore
        return model_class.NAME

    def __init__(self, name: str, description: str | None = None):
        self._name = name
        self._description = description

        # Initialize sets
        self._service_types: set[Hashable] = set()
        self._entities: set[Entity] = set()
        self._models: set[type[Model]] = set()
        self._crud_commands: set[type[CrudCommand]] = set()
        self._commands: set[type[Command]] = set()
        self._permissions: set[Permission] = set()
        self._entity_dag: dict[Entity, list[Entity]] = {}
        self._dag_sorted_entities: list[Entity] = []

        # Initialize mappings between classes and their names
        self._service_type_for_name: dict[str, Hashable] = {}
        self._name_for_service_type: dict[Hashable, str] = {}
        self._command_for_name: dict[str, type[Command]] = {}
        self._name_for_command: dict[type[Command], str] = {}
        self._model_for_name: dict[str, type[Model]] = {}
        self._name_for_model: dict[type[Model], str] = {}
        self._permission_for_tuple: dict[
            tuple[str | type[Command], PermissionType], Permission
        ] = {}

        # Initialize mappings between types of classes (service_type, Entity, Model,
        # Command, Permission)
        # These are pre-computed upon registration for efficiency
        # service_type and Entity
        self._service_type_for_entity: dict[Entity, Hashable] = {}
        self._entities_for_service_type: dict[Hashable, set[Entity]] = {}
        # service type and Model
        self._service_type_for_model: dict[type[Model] | str, Hashable] = {}
        self._models_for_service_type: dict[Hashable, set[type[Model]]] = {}
        # service type and Command
        self._service_type_for_command: dict[type[Command] | str, Hashable] = {}
        self._commands_for_service_type: dict[Hashable, set[type[Command]]] = {}
        self._crud_commands_for_service_type: dict[Hashable, set[type[CrudCommand]]] = (
            {}
        )
        # service type and Permission
        self._service_type_for_permission: dict[Permission, Hashable] = {}
        self._permissions_for_service_type: dict[Hashable, set[Permission]] = {}
        # Entity and Model
        self._entity_for_model: dict[type[Model] | str, Entity] = {}
        self._model_for_entity: dict[Entity, type[Model]] = {}
        # Entity and CrudCommand
        self._entity_for_crud_command: dict[type[CrudCommand] | str, Entity] = {}
        self._crud_command_for_entity: dict[Entity, type[CrudCommand]] = {}
        # Entity and Permission
        self._entity_for_permission: dict[Permission, Entity] = {}
        self._permissions_for_entity: dict[Entity, frozenset[Permission]] = {}
        # Model and CrudCommand
        self._crud_command_for_model: dict[type[Model] | str, type[CrudCommand]] = {}
        self._model_for_crud_command: dict[type[CrudCommand] | str, type[Model]] = {}
        # Model and Permission
        self._model_for_permission: dict[Permission, type[Model]] = {}
        self._permissions_for_model: dict[type[Model] | str, frozenset[Permission]] = {}
        # Command and Permission
        self._permissions_for_command: dict[
            type[Command] | str, frozenset[Permission]
        ] = {}
        self._command_for_permission: dict[Permission, type[Command]] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def service_types(self) -> frozenset[Hashable]:
        return frozenset(self._service_types)

    @property
    def service_names(self) -> frozenset[str]:
        return frozenset(self._service_type_for_name.keys())

    @property
    def entities(self) -> frozenset[Entity]:
        return frozenset(self._entities)

    @property
    def commands(self) -> frozenset[type[Command]]:
        return frozenset(self._commands)

    @property
    def command_names(self) -> frozenset[str]:
        return frozenset(self._command_for_name.keys())

    @property
    def crud_commands(self) -> frozenset[type[CrudCommand]]:
        return frozenset(self._crud_commands)

    @property
    def models(self) -> frozenset[type[Model]]:
        return frozenset(self._models)

    @property
    def permissions(self) -> frozenset[Permission]:
        return frozenset(self._permissions)

    def get_commands(
        self, include_crud: bool = False, frozen: bool = True
    ) -> set[type[Command]] | frozenset[type[Command]]:
        if include_crud:
            if frozen:
                return frozenset(self._commands)
            return set(self._commands)
        commands = {x for x in self._commands if x not in self._crud_commands}
        if frozen:
            return frozenset(commands)
        return set(commands)

    def get_service_type_for_entity(
        self, entity: Entity, verify: bool = False
    ) -> Hashable | None:
        if verify:
            self._verify_entity_exists(entity)
            return self._service_type_for_entity[entity]
        return self._service_type_for_entity.get(entity)

    def get_entities_for_service_type(
        self, service_type: Hashable, verify: bool = False, frozen: bool = True
    ) -> set[Entity] | frozenset[Entity] | None:
        if verify:
            self._verify_service_type_exists(service_type)
        entities = self._entities_for_service_type.get(service_type)
        if entities is None:
            return None
        return frozenset(entities) if frozen else entities

    def get_service_types(self) -> set[Hashable]:
        return set(self._service_types)

    def get_service_type_for_model(
        self, model_class: type[Model], verify: bool = False
    ) -> Hashable:
        if verify:
            self._verify_model_exists(model_class)
        return self._service_type_for_model.get(model_class)

    def get_models_for_service_type(
        self, service_type: Hashable, frozen: bool = True
    ) -> set[type[Model]] | frozenset[type[Model]]:
        self._verify_service_type_exists(service_type)
        if frozen:
            return frozenset(self._models_for_service_type[service_type])
        return set(self._models_for_service_type[service_type])

    def get_service_type_for_command(self, command_class: type[Command]) -> Hashable:
        self._verify_command_exists(command_class)
        return self._service_type_for_command[command_class]

    def get_commands_for_service_type(
        self,
        service_type: Hashable,
        frozen: bool = True,
        base_class: type[Command] | None = None,
    ) -> set[type[Command]] | frozenset[type[Command]]:
        self._verify_service_type_exists(service_type)
        if frozen:
            if base_class:
                return frozenset(
                    {
                        x
                        for x in self._commands_for_service_type[service_type]
                        if issubclass(x, base_class)
                    }
                )
            return frozenset(self._commands_for_service_type[service_type])
        if base_class:
            return {
                x
                for x in self._commands_for_service_type[service_type]
                if issubclass(x, base_class)
            }
        return set(self._commands_for_service_type[service_type])

    def get_crud_commands_for_service_type(
        self,
        service_type: Hashable,
        frozen: bool = True,
        base_class: type[CrudCommand] | None = None,
    ) -> set[type[CrudCommand]] | frozenset[type[CrudCommand]]:
        self._verify_service_type_exists(service_type)
        if frozen:
            if base_class:
                return frozenset(
                    {
                        x
                        for x in self._crud_commands_for_service_type[service_type]
                        if issubclass(x, base_class)
                    }
                )
            return frozenset(self._crud_commands_for_service_type[service_type])
        if base_class:
            return frozenset(
                {
                    x
                    for x in self._crud_commands_for_service_type[service_type]
                    if issubclass(x, base_class)
                }
            )
        return frozenset(self._crud_commands_for_service_type[service_type])

    def get_command_for_name(self, command_name: str) -> type[Command]:
        self._verify_command_exists(command_name)
        return self._command_for_name[command_name]

    def get_permissions_for_service_type(
        self, service_type: Hashable, frozen: bool = True
    ) -> set[Permission] | frozenset[Permission]:
        self._verify_service_type_exists(service_type)
        if frozen:
            return frozenset(self._permissions_for_service_type[service_type])
        return set(self._permissions_for_service_type[service_type])

    def get_permissions_for_domain(
        self, frozen: bool = True
    ) -> set[Permission] | frozenset[Permission]:
        """
        Get permissions for all the commands in the domain.
        """
        if frozen:
            return frozenset(self._permissions)
        return set(self._permissions)

    def get_model_excluded_permissions(self) -> dict[type[Model], PermissionTypeSet]:
        """
        For all registered CRUD commands, return a dict where the key is the
        model class and the value is a PermissionTypeSet that indicates which
        CRUD operations are not allowed. Only models that have missing
        permissions are included in the dict.
        """
        permission_type_map: dict[frozenset[PermissionType], PermissionTypeSet] = {
            x.value: x for x in PermissionTypeSet
        }
        excluded_permissions = {}
        for crud_command_class in self._crud_commands:
            assert crud_command_class._PERMISSIONS is not None
            curr_excluded_permissions = PermissionTypeSet.CRUD.value - {
                x.permission_type for x in crud_command_class._PERMISSIONS
            }
            if not curr_excluded_permissions:
                continue
            excluded_permissions[self._model_for_crud_command[crud_command_class]] = (
                permission_type_map[frozenset(curr_excluded_permissions)]
            )
        return excluded_permissions

    def get_service_type_for_permission(self, permission: Permission) -> Hashable:
        self._verify_permission_exists(permission)
        return self._service_type_for_permission[permission]

    def get_entity_for_model(self, model_class: type[Model]) -> Entity:
        self._verify_model_exists(model_class)
        return self._entity_for_model[model_class]

    def get_model_for_entity(self, entity: Entity) -> type[Model]:
        self._verify_entity_exists(entity)
        return self._model_for_entity[entity]

    def get_entity_for_crud_command(
        self, crud_command_class: type[CrudCommand]
    ) -> Entity:
        self._verify_command_exists(crud_command_class)
        return self._entity_for_crud_command[crud_command_class]

    def get_crud_command_for_entity(self, entity: Entity) -> type[CrudCommand]:
        self._verify_entity_exists(entity)
        return self._crud_command_for_entity[entity]

    def get_entity_for_permission(self, permission: Permission) -> Entity:
        self._verify_permission_exists(permission)
        return self._entity_for_permission[permission]

    def get_permissions_for_entity(
        self, entity: Entity, frozen: bool = True
    ) -> set[Permission] | frozenset[Permission]:
        self._verify_entity_exists(entity)
        if frozen:
            return frozenset(self._permissions_for_entity[entity])
        return set(self._permissions_for_entity[entity])

    def get_crud_command_for_model(self, model_class: type[Model]) -> type[CrudCommand]:
        self._verify_model_exists(model_class)
        return self._crud_command_for_model[model_class]

    def get_model_for_crud_command(
        self, crud_command_class: type[CrudCommand]
    ) -> type[Model]:
        self._verify_command_exists(crud_command_class)
        return self._model_for_crud_command[crud_command_class]

    def get_model_for_permission(self, permission: Permission) -> type[Model]:
        self._verify_permission_exists(permission)
        return self._model_for_permission[permission]

    def get_permissions_for_model(
        self,
        model_class: type[Model],
        frozen: bool = True,
        permission_type_set: PermissionTypeSet | None = None,
    ) -> set[Permission] | frozenset[Permission]:
        self._verify_model_exists(model_class)
        return self.get_permissions_for_command(
            self.get_crud_command_for_model(model_class),
            frozen=frozen,
            permission_type_set=permission_type_set,
        )

    def get_permissions_for_command(
        self,
        command_class: type[Command],
        frozen: bool = True,
        permission_type_set: PermissionTypeSet | None = None,
    ) -> set[Permission] | frozenset[Permission]:
        self._verify_command_exists(command_class)
        if permission_type_set:
            permissions = set(
                {
                    x
                    for x in self._permissions_for_command[command_class]
                    if x.permission_type in permission_type_set.value
                }
            )
            if frozen:
                return frozenset(permissions)
            return permissions
        if frozen:
            return self._permissions_for_command[command_class]
        return set(self._permissions_for_command[command_class])

    def get_command_for_permission(self, permission: Permission) -> type[Command]:
        self._verify_permission_exists(permission)
        return self._command_for_permission[permission]

    def get_permission(
        self,
        command_class_or_name: type[Command] | str,
        permission_type: PermissionType,
    ) -> Permission:
        self._verify_command_exists(command_class_or_name)
        return self._permission_for_tuple[(command_class_or_name, permission_type)]

    def get_permission_for_command_instance(
        self,
        cmd: Command,
    ) -> Permission:
        command_class = type(cmd)
        if issubclass(command_class, CrudCommand):
            permission_type = Domain.CRUD_PERMISSION_TYPE_MAP[cmd.operation]  # type: ignore
        else:
            permission_type = PermissionType.EXECUTE
        return self._permission_for_tuple[(command_class, permission_type)]

    def get_model_links(
        self,
        model_class: type[Model],
        as_tuple: bool = False,
        service_type: Hashable | None = None,
        url_name: str | None = None,
        database_name: str | None = None,
        schema_name: str | None = None,
        invert: bool = False,
    ) -> dict[int, tuple[str, type[Model], str | None]] | dict[int, Link]:
        self._verify_model_exists(model_class)
        entity = self.get_entity_for_model(model_class)
        links = {}
        for link_type_id, link in entity.links.items():
            link_entity = self.get_entity_for_model(link.link_model_class)  # type: ignore
            if (
                service_type
                and (self.get_service_type_for_entity(link_entity) != service_type)
                != invert
            ):
                continue
            if url_name and (link_entity.url_name != url_name) != invert:
                continue
            if database_name and (link_entity.database_name != database_name) != invert:
                continue
            if schema_name and (link_entity.schema_name != schema_name) != invert:
                continue
            links[link_type_id] = link
        if as_tuple:
            return {x: y.to_tuple() for x, y in links.items()}  # type: ignore
        return links

    def get_dag_sorted_entities(
        self,
        service_type: Hashable | None = None,
        persistable: bool | None = None,
        url_name: str | None = None,
        database_name: str | None = None,
        schema_name: str | None = None,
        invert: bool = False,
        reverse: bool = False,
        on_cycle: OnException = OnException.RAISE,
    ) -> list[Entity]:
        if service_type:
            self._verify_service_type_exists(service_type)
        entities = self._filter_entities(
            service_type,
            persistable,
            url_name,
            database_name,
            schema_name,
            invert,
        )
        # Perform topological sort on filtered entities based on links
        sorted_entities = Entity.topological_sort(entities, on_cycle=on_cycle)
        if reverse:
            return list(reversed(sorted_entities))
        return sorted_entities

    def get_dag_sorted_models(
        self,
        service_type: Hashable | None = None,
        persistable: bool | None = None,
        url_name: str | None = None,
        database_name: str | None = None,
        schema_name: str | None = None,
        invert: bool = False,
        reverse: bool = False,
        on_cycle: OnException = OnException.RAISE,
    ) -> list[type[Model]]:
        return [
            x.model_class  # type: ignore
            for x in self.get_dag_sorted_entities(
                service_type=service_type,
                persistable=persistable,
                url_name=url_name,
                database_name=database_name,
                schema_name=schema_name,
                invert=invert,
                reverse=reverse,
                on_cycle=on_cycle,
            )
        ]

    def get_dag_sorted_service_types(
        self,
        reverse: bool = False,
        on_cycle: OnException = OnException.RAISE,
    ) -> list[Hashable]:
        entities = self.get_dag_sorted_entities(reverse=reverse, on_cycle=on_cycle)
        if len(entities) == 0:
            return []

        entity_service_types = [self._service_type_for_entity[x] for x in entities]
        service_types = [entity_service_types[0]]
        seen_service_types = {entity_service_types[0]}
        for service_type in entity_service_types[1:]:
            if service_type == service_types[-1]:
                # Same service type as previous entity, nothing to do
                continue
            if service_type in seen_service_types:
                if on_cycle == OnException.RAISE:
                    raise exc.DomainException(
                        "f8b2c94d",
                        f"Service type {service_type} is part of a cycle in the entity DAG",
                    )
                elif on_cycle == OnException.IGNORE:
                    continue
            service_types.append(service_type)
            seen_service_types.add(service_type)
        return service_types

    def register_service_type(self, service_type: Hashable) -> Hashable:
        if service_type not in self._service_types:
            self._service_types.add(service_type)
            self._entities_for_service_type[service_type] = set()
            self._commands_for_service_type[service_type] = set()
            self._crud_commands_for_service_type[service_type] = set()
            self._models_for_service_type[service_type] = set()
            self._permissions_for_service_type[service_type] = set()
        return service_type

    def register_entity(
        self,
        entity: Entity,
        service_type: Hashable | None = None,
        model_class: type[Model] | None = None,
        crud_command_class: type[CrudCommand] | None = None,
        on_cycle: OnException = OnException.RAISE,
    ) -> Entity:
        # Set service type Model and CrudCommand
        if model_class:
            entity.set_model_class(model_class)
        if crud_command_class:
            entity.set_crud_command_class(crud_command_class)

        # Register new service_type
        self.register_service_type(service_type)

        # Register new Entity
        if entity not in self._entities:
            model_class = entity.model_class  # type: ignore
            if model_class is None:
                raise exc.InitializationServiceError(
                    "8066762a", f"Model class not set for entity {entity.id}"
                )
            model_name = Domain.get_model_name(model_class)
            if model_name in self._model_for_name:
                raise exc.DomainException(
                    "2601e5ce", f"Model name {model_name} is already registered"
                )
            # Add Entity and Model
            self._add_new_entity_and_model(entity, model_class, model_name)

            # Add relations between classes (service_type, Entity, Model)
            self._link_new_entity_and_model(
                entity, service_type, model_class, model_name
            )

            # Update entity DAG
            self._update_entity_dag(entity, on_cycle)

        # Register CrudCommand if necessary
        if entity.persistable and entity.crud_command_class:
            self.register_command(entity.crud_command_class, service_type=service_type)  # type: ignore

        return entity

    def _filter_entities(
        self,
        service_type: Hashable | None,
        persistable: bool | None,
        url_name: str | None,
        database_name: str | None,
        schema_name: str | None,
        invert: bool,
    ) -> list[Entity]:
        entities: list[Entity] = []
        for entity in self._dag_sorted_entities:
            if (
                service_type
                and (self.get_service_type_for_entity(entity) != service_type) != invert
            ):
                continue
            if (
                persistable is not None
                and (entity.persistable != persistable) != invert
            ):
                continue
            if url_name and (entity.url_name != url_name) != invert:
                continue
            if database_name and (entity.database_name != database_name) != invert:
                continue
            if schema_name and (entity.schema_name != schema_name) != invert:
                continue
            entities.append(entity)
        return entities

    def _update_entity_dag(
        self, entity: Entity, on_cycle: Literal[OnException.RAISE, OnException.IGNORE]
    ) -> None:
        for link in entity.links.values():
            if link.link_model_class not in self._models:
                if on_cycle == OnException.RAISE:
                    raise exc.DomainException(
                        "a91b5baa",
                        f"Entity {entity.name} references unknown model {link.link_model_class} - add entities in DAG sorted order",
                    )
                elif on_cycle == OnException.IGNORE:
                    continue
                else:
                    raise AssertionError(f"Unsupported on_cycle: {on_cycle.value}")
            link_entity = self.get_entity_for_model(link.link_model_class)  # type: ignore
            self._entity_dag[entity].append(link_entity)
        self._dag_sorted_entities.append(entity)

    def _link_new_entity_and_model(
        self,
        entity: Entity,
        service_type: Hashable,
        model_class: type[Model],
        model_name: str,
    ) -> None:
        self._service_type_for_entity[entity] = service_type
        self._entities_for_service_type[service_type].add(entity)
        self._service_type_for_model[model_class] = service_type
        self._service_type_for_model[model_name] = service_type
        self._models_for_service_type[service_type].add(model_class)
        self._entity_for_model[model_class] = entity
        self._entity_for_model[model_name] = entity
        self._model_for_entity[entity] = model_class

    def _add_new_entity_and_model(
        self, entity: Entity, model_class: type[Model], model_name: str
    ) -> None:
        self._entities.add(entity)
        self._entity_dag[entity] = []
        self._models.add(model_class)
        self._model_for_name[model_name] = model_class
        self._name_for_model[model_class] = model_name

    def register_command(
        self, command_class: type[Command], service_type: Hashable | None = None
    ) -> type[Command]:
        command_name = Domain.get_command_name(command_class)

        # Verify already registered Command
        if command_class in self._commands:
            self._verify_registered_command(command_class, service_type, command_name)
            return command_class

        # Register new service_type
        self.register_service_type(service_type)

        # Register new Command
        permissions = self._add_new_command(command_class, command_name)
        # Add relations between classes (service_type, Command, Permission)
        self._associate_command_with_service(
            command_class, service_type, command_name, permissions
        )

        # Add CrudCommand specific verifications and data
        if issubclass(command_class, CrudCommand):
            crud_command_class = command_class
            # Verify model class
            model_class = crud_command_class.MODEL_CLASS
            if not model_class:
                raise exc.DomainException(
                    "0656f627", f"Model class not set for CRUD command {command_name}"
                )
            # Verify entity
            entity = model_class.ENTITY
            if not entity:
                raise exc.DomainException(
                    "ca3ceeb9",
                    f"Entity not set for model {Domain.get_model_name(model_class)}",
                )
            if not entity.persistable:
                raise exc.DomainException(
                    "696111f4", f"Entity {entity.name} is not persistable"
                )
            # Set entity Model and CrudCommand if necessary
            if not entity.has_model():
                entity.set_model_class(model_class)
            if not entity.crud_command_class:
                entity.set_crud_command_class(crud_command_class)

            # Register new CrudCommand
            self._crud_commands.add(crud_command_class)
            # Add relations between classes (service_type, Entity, Model, CrudCommand, Permission)
            self._link_new_command(
                service_type,
                command_name,
                permissions,
                crud_command_class,
                model_class,
                entity,
            )

            # Set entity to be registered
            if entity not in self._entities:
                self.register_entity(
                    entity,
                    model_class=model_class,
                    crud_command_class=crud_command_class,
                    service_type=service_type,
                )
        return command_class

    def _link_new_command(
        self,
        service_type: Hashable,
        command_name: str,
        permissions: frozenset[Permission],
        crud_command_class: type[CrudCommand],
        model_class: type[Model],
        entity: Entity,
    ) -> None:
        model_name = Domain.get_model_name(model_class)
        self._crud_commands_for_service_type[service_type].add(crud_command_class)
        self._entity_for_crud_command[crud_command_class] = entity
        self._entity_for_crud_command[command_name] = entity
        self._crud_command_for_entity[entity] = crud_command_class
        self._model_for_crud_command[crud_command_class] = model_class
        self._model_for_crud_command[command_name] = model_class
        self._permissions_for_model[model_class] = permissions
        for permission in permissions:
            self._model_for_permission[permission] = model_class
        self._crud_command_for_model[model_class] = crud_command_class
        self._crud_command_for_model[model_name] = crud_command_class

    def _associate_command_with_service(
        self,
        command_class: type[Command],
        service_type: Hashable | None,
        command_name: str,
        permissions: frozenset[Permission],
    ) -> None:
        self._service_type_for_command[command_class] = service_type
        self._commands_for_service_type[service_type].add(command_class)
        self._permissions_for_service_type[service_type].update(permissions)
        self._permissions_for_command[command_class] = permissions
        self._permissions_for_command[command_name] = permissions
        for permission in permissions:
            self._service_type_for_permission[permission] = service_type
            self._command_for_permission[permission] = command_class
            self._permission_for_tuple[(command_class, permission.permission_type)] = (
                permission
            )
            self._permission_for_tuple[(command_name, permission.permission_type)] = (
                permission
            )

    def _add_new_command(
        self, command_class: type[Command], command_name: str
    ) -> frozenset[Permission]:
        permissions = Domain.get_command_permissions(command_class)
        self._commands.add(command_class)
        self._permissions.update(permissions)
        self._command_for_name[command_name] = command_class
        self._name_for_command[command_class] = command_name
        return permissions

    def _verify_registered_command(
        self,
        command_class: type[Command],
        service_type: Hashable | None,
        command_name: str,
    ) -> None:
        if command_name != self._name_for_command[command_class]:
            raise exc.DomainException(
                "e26100e6",
                f"Command {command_name} is already registered with different name {self._name_for_command[command_class]}",
            )
        linked_service_type = self._service_type_for_command[command_class]
        if linked_service_type != service_type:
            raise exc.DomainException(
                "002a9e50",
                f"Command {command_name} is already registered with service type {linked_service_type}",
            )
        if issubclass(command_class, CrudCommand):
            if command_class.MODEL_CLASS is None:
                raise exc.DomainException(
                    "349edda2", f"Model class not set for CrudCommand {command_name}"
                )
            linked_model_class = self._model_for_crud_command[command_class]
            if linked_model_class is not command_class.MODEL_CLASS:
                raise exc.DomainException(
                    "72de613a",
                    f"Command {command_name} is already registered and linked to model {linked_model_class.NAME}",
                )

    def _verify_model_has_entity(self, model_class: type[Model]) -> None:
        if model_class.ENTITY is None:
            raise exc.DomainException(
                "1689f54a",
                f"Entity not set for model {Domain.get_model_name(model_class)}",
            )

    def _verify_entity_exists(self, entity: Entity) -> None:
        if entity not in self._entities:
            raise exc.DomainException(
                "5a937380", f"Entity {entity.name} is not registered"
            )

    def _verify_service_type_exists(self, service_type: Hashable) -> None:
        if service_type not in self._service_types:
            raise exc.DomainException(
                "ef28d4ad", f"Service type {service_type} is not registered"
            )

    def _verify_command_exists(
        self, command_class_or_name: type[Command] | str
    ) -> None:
        if isinstance(command_class_or_name, str):
            command_name = command_class_or_name
            if command_name not in self._command_for_name:
                raise exc.DomainException(
                    "d990b867", f"Command {command_name} is not registered"
                )
        else:
            command_class = command_class_or_name
            if command_class not in self._commands:
                command_name = Domain.get_command_name(command_class)
                raise exc.DomainException(
                    "6b98defe", f"Command {command_name} is not registered"
                )

    def _verify_model_exists(self, model_class_or_name: type[Model] | str) -> None:
        if isinstance(model_class_or_name, str):
            model_name = model_class_or_name
            if model_name not in self._model_for_name:
                raise exc.DomainException(
                    "44107f04", f"Model {model_name} is not registered"
                )
        else:
            model_class = model_class_or_name
            if model_class not in self._models:
                raise exc.DomainException(
                    "9ac1d1d4",
                    f"Model {Domain.get_model_name(model_class)} is not registered",
                )

    def _verify_permission_exists(self, permission: Permission) -> None:
        if permission not in self._permissions:
            raise exc.DomainException(
                "b2cee1c1", f"Permission {permission} is not registered"
            )
