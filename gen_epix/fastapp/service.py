from __future__ import annotations

import abc
import datetime
import logging
from typing import Any, Callable, Hashable, Iterable, Type

from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain import Domain
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.enum import CrudOperation, CrudOperationSet, EventTiming
from gen_epix.fastapp.model import (
    Command,
    CrudCommand,
    Model,
    UpdateAssociationCommand,
    User,
)
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import BooleanOperator, CompositeFilter


class BaseService(abc.ABC):
    SERVICE_TYPE: Hashable = None

    def __init__(
        self,
        app: App,
        repository: BaseRepository | None = None,
        logger: logging.Logger | None = None,
        props: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        # Parse kwargs
        if props is None:
            props = {}
        id_factory: Callable[[], Hashable] = kwargs.pop("id_factory", app.generate_id)
        timestamp_factory: Callable[[], datetime.datetime] = kwargs.pop(
            "timestamp_factory", app.generate_timestamp
        )
        register_handlers = kwargs.pop("register_handlers", True)
        # Set input members
        self._id: str = kwargs.pop("id", str(id_factory()))
        self._service_type: Hashable = kwargs.pop(
            "service_type", self.__class__.SERVICE_TYPE
        )
        self._name: str = Domain.get_service_name(self._service_type)
        self._created_at: datetime.datetime = timestamp_factory()
        self._app: App = app
        self._repository: BaseRepository | None = repository
        self._logger: logging.Logger | None = logger
        self._props: dict[str, Any] = props
        self._id_factory: Callable[[], Hashable] = id_factory
        self._timestamp_factory: Callable[[], datetime.datetime] = timestamp_factory
        # Initialize other members
        self._crud_listeners: dict[
            tuple[Type[CrudCommand], EventTiming],
            list[Callable[[BaseService, CrudCommand, Any], tuple[CrudCommand, Any]]],
        ] = {}
        # Log start
        if self._logger:
            self._logger.info(
                self.create_log_message(
                    "c10677fe",
                    "STARTING_SERVICE",
                    service={"created_at": self.created_at},
                )
            )
        # Register service if not yet, and handlers
        self.app.domain.register_service_type(self.service_type)
        if register_handlers:
            self.register_handlers()

    @property
    def id(self) -> str:
        return self._id

    @property
    def service_type(self) -> Hashable:
        return self._service_type

    @property
    def name(self) -> str:
        return self._name

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @property
    def app(self) -> App:
        return self._app

    @property
    def logger(self) -> logging.Logger | None:
        return self._logger

    @logger.setter
    def logger(self, logger: logging.Logger | None) -> None:
        self._logger = logger

    @property
    def repository(self) -> BaseRepository:
        if not self._repository:
            raise exc.ServiceException("Repository not set")
        return self._repository

    @repository.setter
    def repository(self, repository: BaseRepository) -> None:
        self._repository = repository

    @property
    def props(self) -> dict[str, Any]:
        return self._props

    @abc.abstractmethod
    def register_handlers(self) -> None:
        raise NotImplementedError()

    def register_default_crud_handlers(
        self, exclude: set[Type[CrudCommand]] | None = None
    ) -> None:
        """
        Register the crud method as the handler for all registered CRUD
        commands. The exclude parameter can be used to exclude specific CRUD
        commands from being registered.
        """
        for crud_command_class in self.app.domain.get_crud_commands_for_service_type(
            self.service_type
        ):
            if exclude and crud_command_class in exclude:
                continue
            self.app.register_handler(crud_command_class, self.crud)

    def generate_id(self) -> Hashable:
        return self._id_factory()

    def generate_timestamp(self) -> datetime.datetime:
        return self._timestamp_factory()

    def register_crud_listener(
        self,
        command_class: Type[CrudCommand],
        timing: EventTiming,
        listener: Callable[[BaseService, CrudCommand, Any], tuple[CrudCommand, Any]],
    ) -> None:
        """
        Register a listener for a CRUD command class and timing BEFORE or AFTER
        the CRUD operation is executed. The listener should take the command obj
        and the return value of the CRUD operation. The listener should return a
        tuple of the command obj and the return value of the CRUD operation.
        Listeners registered for BEFORE timing can modify the command obj before
        the CRUD operation is executed. Listeners registered for AFTER timing
        can modify the return value of the CRUD operation.
        """
        if timing == EventTiming.DURING:
            raise ValueError("Cannot register listener for DURING timing")
        key = (command_class, timing)
        if key in self._crud_listeners:
            if listener in self._crud_listeners[key]:
                raise ValueError(f"Listener already registered for {key}")
            self._crud_listeners[key].append(listener)
        else:
            self._crud_listeners[key] = [listener]

    def unregister_crud_listener(
        self,
        command_class: Type[CrudCommand],
        timing: EventTiming,
        listener: Callable[[BaseService, CrudCommand, Any], tuple[CrudCommand, Any]],
    ) -> None:
        key = (command_class, timing)
        if key not in self._crud_listeners:
            raise ValueError(f"Listener not registered for {key}")
        if listener not in self._crud_listeners[key]:
            raise ValueError(f"Listener not registered for {key}")
        self._crud_listeners[key].remove(listener)

    def crud(
        self, cmd: CrudCommand
    ) -> Hashable | list[Hashable] | Model | list[Model] | bool | list[bool] | None:
        id_field_name = cmd.MODEL_CLASS.ENTITY.id_field_name
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "a7aa40b3",
                    "STARTING_CRUD",
                    cmd=cmd,
                    command={"operation": str(cmd.operation.value)},
                )
            )
        if not self.repository:
            raise exc.ServiceException("Repository not set")
        # Call BEFORE listeners
        for listener in self._crud_listeners.get((type(cmd), EventTiming.BEFORE), []):
            cmd, _ = listener(self, cmd, None)
        # Set object ids for CREATE operations
        if cmd.operation in CrudOperationSet.CREATE.value:
            id_present = cmd.props.get("id_present", "raise")
            if cmd.objs is None:
                raise exc.InvalidArgumentsError(
                    f"No object provided for operation {cmd.operation}"
                )
            if isinstance(cmd.objs, list):
                for obj in cmd.objs:
                    self.set_object_id(obj, id_field_name, id_present)
            else:
                self.set_object_id(cmd.objs, id_field_name, id_present)
        # Prepare for cascaded read if necessary: determine which links
        # are handled by this service and which by other services
        cascade_read = cmd.props.get("cascade_read", False)
        if cascade_read or cmd.operation in CrudOperationSet.WRITE.value:
            same_service_links, other_service_links = self._get_model_links(cmd)
        else:
            same_service_links = {}
            other_service_links = {}
        # Start unit of work
        with self.repository.uow() as uow:
            # Verify write operation object links are valid
            if cmd.operation in CrudOperationSet.WRITE.value:
                if cmd.objs is None:
                    raise exc.InvalidArgumentsError(
                        f"No object provided for operation {cmd.operation}"
                    )
                objs = cmd.objs if isinstance(cmd.objs, list) else [cmd.objs]
                # TODO: verifying links from the same service should be the responsibility
                # of the repository
                self._verify_same_service_links(uow, cmd, objs, same_service_links)
                self._verify_other_service_links(cmd, objs, other_service_links)

            # Call repository CRUD operation
            retval = self.crud_repository(uow, cmd, links=same_service_links)

            # Cascade read objects handled by other services
            if (
                cascade_read
                and len(other_service_links)
                and cmd.operation in CrudOperationSet.READ.value
            ):
                if issubclass(type(retval), Model):
                    objs = [retval]  # type: ignore
                else:
                    objs = retval  # type: ignore
                for link in other_service_links.values():
                    if link.relationship_field_name is None:
                        continue
                    # Read in unique linked objects for this relationship_field_name
                    link_map: dict = {}
                    for i, obj in enumerate(objs):
                        link_obj_id = getattr(obj, link.link_field_name)
                        if link_obj_id:
                            idxs = link_map.get(link_obj_id, [])
                            if not idxs:
                                link_map[link_obj_id] = idxs
                            idxs.append(i)
                    link_map_ids = list(link_map.keys())
                    if not link_map_ids:
                        continue
                    cmd = self._app.domain.get_crud_command_for_model(
                        link.link_model_class
                    )(
                        user=cmd.user,
                        objs=None,
                        obj_ids=link_map_ids,
                        operation=CrudOperation.READ_SOME,
                        **{
                            x: y
                            for x, y in cmd.props.items()
                            if x not in {"cascade_read"}
                        },
                    )
                    linked_objects = self._app.handle(cmd)
                    # Add linked objects to their parent(s)
                    for link_obj_id, linked_obj in zip(link_map_ids, linked_objects):
                        for idx in link_map[link_obj_id]:
                            setattr(objs[idx], link.relationship_field_name, linked_obj)
        # Call AFTER listeners
        for listener in self._crud_listeners.get((type(cmd), EventTiming.AFTER), []):
            _, retval = listener(self, cmd, retval)

        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "e2adcd64",
                    "FINISHING_CRUD",
                    cmd=cmd,
                    command={
                        "operation": str(cmd.operation.value),
                        "n": len(retval) if isinstance(retval, list) else 1,
                    },
                )
            )
        return retval

    def crud_repository(
        self,
        uow: BaseUnitOfWork,
        cmd: CrudCommand,
        links: dict[int, Link] | None = None,
    ) -> Hashable | list[Hashable] | Model | list[Model] | bool | list[bool] | None:
        # Get filters depending on the operation
        if cmd.operation in CrudOperationSet.ANY_ALL.value:
            # Query filter is applied, access filter is added to query filter
            query_filter = cmd.query_filter
            access_filter = cmd.access_filter
            if query_filter and access_filter:
                query_filter = CompositeFilter(
                    filters=[query_filter, access_filter],
                    operator=BooleanOperator.AND,
                )
            elif not query_filter:
                query_filter = access_filter
            access_filter = None
        else:
            # Query filter is not applied, access filter is applied separately
            query_filter = None
            access_filter = cmd.access_filter

        # Verify access through access_filter for create, exists, update and delete
        # operations (read operations are verified later to avoid unnecessary reads)
        if access_filter:
            objs = None
            if cmd.operation in CrudOperationSet.WRITE.value:
                # Operations with one or more objs as input -> check if they match the
                # access filter
                objs = cmd.get_objs()
            elif (
                cmd.operation in CrudOperationSet.DELETE.value
                or cmd.operation in CrudOperationSet.EXISTS.value
            ):
                # Delete/exists one or some (delete all is not possible since there is
                # an access filter) -> check if the ids match the access filter
                objs: list[Model] = self.repository.crud(
                    uow,
                    cmd.user.id,
                    cmd.MODEL_CLASS,
                    None,
                    cmd.get_obj_ids(),
                    CrudOperation.READ_SOME,
                )
            if objs is not None and not all(
                cmd.access_filter.match_rows(objs, is_model=True)
            ):
                raise exc.UnauthorizedAuthError(f"Unauthorized access to objects")

        # Split query_filter into repository and service filters
        repository_query_filter, service_query_filter = self.repository.split_filter(
            cmd.MODEL_CLASS, query_filter
        )

        # Call repository CRUD operation
        reserved_arg_names = {"filter", "obj_filter", "links"}
        props = {x: y for x, y in cmd.props.items() if x not in reserved_arg_names}
        retval = self.repository.crud(
            uow,
            cmd.user.id if cmd.user else None,
            cmd.MODEL_CLASS,
            cmd.objs,
            cmd.obj_ids,
            cmd.operation,
            filter=repository_query_filter,
            obj_filter=service_query_filter,
            links=links,
            **props,
        )

        return retval

    def update_association(
        self, cmd: UpdateAssociationCommand, **kwargs: Any
    ) -> list[Hashable] | list[Model] | None:
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "ea2aee86",
                    "STARTING_UPDATE_ASSOCIATION",
                    cmd=cmd,
                )
            )
        if not self.repository:
            raise exc.ServiceException("Repository not set")

        same_service_links, other_service_links = self._get_model_links(cmd)
        id_field_name = cmd.ASSOCIATION_CLASS.ENTITY.id_field_name
        with self.repository.uow() as uow:
            # Call repository CRUD operation
            for obj in cmd.association_objs:
                if not getattr(obj, id_field_name):
                    self.set_object_id(obj, id_field_name, "raise")
            self._verify_same_service_links(
                uow, cmd, cmd.association_objs, same_service_links
            )
            self._verify_other_service_links(
                cmd, cmd.association_objs, other_service_links
            )
            retval = self.repository.update_association(  # type: ignore
                uow,
                cmd.user.id if cmd.user else None,
                cmd.ASSOCIATION_CLASS,
                cmd.LINK_FIELD_NAME1,
                cmd.LINK_FIELD_NAME2,
                cmd.obj_id1,
                cmd.obj_id2,
                cmd.association_objs,
                **cmd.props,
                **kwargs,
            )
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "dd1875fe",
                    "FINISHING_UPDATE_ASSOCIATION",
                    cmd=cmd,
                    command={"n": len(retval) if isinstance(retval, list) else 1},
                )
            )
        return retval

    def set_object_id(self, obj: Model, id_field_name: str, id_present: str) -> None:
        if getattr(obj, id_field_name):
            if id_present == "raise":
                raise exc.InvalidArgumentsError("Object already has id filled in")
            if id_present == "ignore":
                # Assign new id
                setattr(obj, id_field_name, self.generate_id())
            elif id_present == "keep":
                # Keep id
                pass
            else:
                raise ValueError(f"Invalid id_present: {id_present}")
        else:
            # Assign id
            setattr(obj, id_field_name, self.generate_id())

    def create_log_message(
        self,
        code: str,
        msg: str,
        add_debug_info: bool = True,
        **kwargs: Any,
    ) -> str:
        if add_debug_info:
            service = kwargs.pop("service", {}) | {"id": self.id, "name": self.name}
            return self.app.create_log_message(
                code,
                msg,
                add_debug_info=add_debug_info,
                service=service,
                **kwargs,
            )
        return self.app.create_log_message(
            code, msg, add_debug_info=add_debug_info, **kwargs
        )

    def _get_model_links(self, cmd: CrudCommand | UpdateAssociationCommand) -> tuple[
        dict[int, Link],
        dict[int, Link],
    ]:
        if isinstance(cmd, CrudCommand):
            model_class = cmd.MODEL_CLASS
        elif isinstance(cmd, UpdateAssociationCommand):
            model_class = cmd.ASSOCIATION_CLASS
        else:
            raise NotImplementedError
        same_service_links = self.app.domain.get_model_links(
            model_class, service_type=self.service_type
        )
        other_service_links = self.app.domain.get_model_links(
            model_class, service_type=self.service_type, invert=True
        )
        return same_service_links, other_service_links

    def _get_user_and_repository(self, cmd: Command) -> tuple[User, BaseRepository]:
        user = cmd.user
        if user is None or user.id is None:
            raise exc.UnauthorizedAuthError("No user provided")
        if self.repository is None:
            raise exc.InitializationServiceError("No repository provided")
        return user, self.repository

    def _verify_other_service_links(
        self,
        cmd: CrudCommand | UpdateAssociationCommand,
        objs: Iterable[Model],
        other_service_links: dict[int, Link],
    ) -> None:
        verify_other_service_links = cmd.props.get("verify_other_service_links", True)
        if not verify_other_service_links or not other_service_links:
            return
        for link in other_service_links.values():
            link_obj_ids = list(
                set(
                    getattr(x, link.link_field_name)
                    for x in objs
                    if getattr(x, link.link_field_name) is not None
                )
            )
            if link_obj_ids:
                link_cmd = self._app.domain.get_crud_command_for_model(
                    link.link_model_class  # type: ignore
                )(
                    user=cmd.user,
                    objs=None,
                    obj_ids=link_obj_ids,
                    operation=CrudOperation.READ_SOME,
                )
                try:
                    _ = self._app.handle(link_cmd)
                except exc.InvalidIdsError:
                    raise exc.InvalidLinkIdsError(
                        f"Invalid {link.link_model_class.__name__} id(s) among input"
                    )

    def _verify_same_service_links(
        self,
        uow: BaseUnitOfWork,
        cmd: CrudCommand | UpdateAssociationCommand,
        objs: Iterable[Model],
        same_service_links: dict[int, Link],
    ) -> None:
        verify_same_service_links = cmd.props.get("verify_same_service_links", True)
        if not self.repository:
            raise exc.ServiceException("Repository not set")
        if not verify_same_service_links or not same_service_links:
            return
        for link in same_service_links.values():
            link_obj_ids = list(
                set(
                    getattr(x, link.link_field_name)
                    for x in objs
                    if getattr(x, link.link_field_name) is not None
                )
            )
            if link_obj_ids:
                try:
                    self.repository.verify_valid_ids(
                        uow,
                        cmd.user.id if cmd.user else None,
                        link.link_model_class,  # type: ignore
                        link_obj_ids,
                        verify_duplicate=False,
                    )
                except exc.InvalidIdsError:
                    raise exc.InvalidLinkIdsError(
                        f"Invalid {link.link_model_class.__name__} id(s) among input"
                    )

    def __del__(self) -> None:
        if self.logger:
            self.logger.info(self.create_log_message("d84f9d21", "STOPPING_SERVICE"))
