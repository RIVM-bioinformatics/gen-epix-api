"""Base service lifecycle and application integration abstractions."""

from __future__ import annotations

import abc
import datetime
import logging
from collections.abc import Callable, Hashable, Iterable
from typing import Any

from gen_epix.fastapp import exc
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.enum import (
    CrudOperation,
    CrudOperationSet,
    EventTiming,
    OnException,
)
from gen_epix.fastapp.model import (
    Command,
    CrudCommand,
    Model,
    UpdateAssociationCommand,
    User,
)
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import CompositeFilter, LogicalOperator


class BaseService[Repository: BaseRepository = BaseRepository](abc.ABC):
    """Encapsulates a service that groups together related domain models
    and logic, and which may have an associated repository for persistence.

    Implement this class to provide specific domain service functionality
    while cleanly separating business logic from other services through
    the app instance's handle() method.
    """

    SERVICE_TYPE: Hashable = None

    def __init__(
        self,
        app: App,
        service_type: Hashable = None,  # TODO: service_type this required
        repository: Repository | None = None,
        logger: logging.Logger | None = None,
        setup_logger: logging.Logger | None = None,
        id: str | None = None,
        name: str | None = None,
        register_handlers: bool = True,
        id_factory: Callable[[], Hashable] | None = None,
        timestamp_factory: Callable[[], datetime.datetime] | None = None,
        props: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        # Set input members
        """Initialize a BaseService instance."""
        self._id_factory: Callable[[], Hashable] = id_factory or app.generate_id
        self._timestamp_factory: Callable[[], datetime.datetime] = (
            timestamp_factory or app.generate_timestamp
        )
        self._id: str = id or str(self._id_factory())
        self._name: str = name or str(self._id)
        self._service_type = service_type
        self._created_at: datetime.datetime = self._timestamp_factory()
        self._app: App = app
        self._repository: Repository | None = repository
        self._logger: logging.Logger | None = logger
        self._setup_logger: logging.Logger | None = setup_logger
        self._props: dict[str, Any] = props or {}

        # Initialize other members
        self._crud_listeners: dict[
            tuple[type[CrudCommand], EventTiming],
            list[Callable[[BaseService, CrudCommand, Any], tuple[CrudCommand, Any]]],
        ] = {}

        # Log start
        if self._setup_logger:
            self._setup_logger.info(
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
        """Id the requested value."""
        return self._id

    @property
    def service_type(self) -> Hashable:
        """Service type."""
        return self._service_type

    @property
    def name(self) -> str:
        """Name the requested value."""
        return self._name

    @property
    def created_at(self) -> datetime.datetime:
        """Created at."""
        return self._created_at

    @property
    def app(self) -> App:
        """App the requested value."""
        return self._app

    @property
    def logger(self) -> logging.Logger | None:
        """Logger the requested value."""
        return self._logger

    @logger.setter
    def logger(self, logger: logging.Logger | None) -> None:
        """Logger the requested value."""
        self._logger = logger

    @property
    def repository(self) -> Repository:
        """Repository the requested value."""
        if not self._repository:
            raise exc.ServiceException("529122a8", "Repository not set")
        return self._repository

    @repository.setter
    def repository(self, repository: Repository) -> None:
        """Repository the requested value."""
        self._repository = repository

    @property
    def props(self) -> dict[str, Any]:
        """Props the requested value."""
        return self._props

    @abc.abstractmethod
    def register_handlers(self) -> None:
        """
        Register command handlers for this service. This method is normally called
        during service initialization, and should be used to register handlers for
        commands that this service should handle. The app.register_handler method can be
        used to register a handler for a specific command class.

        """
        raise NotImplementedError()

    def register_default_crud_handlers(
        self, exclude: set[type[CrudCommand]] | None = None
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
        """Generate id."""
        return self._id_factory()

    def generate_timestamp(self) -> datetime.datetime:
        """Generate timestamp."""
        return self._timestamp_factory()

    def register_crud_listener(
        self,
        command_class: type[CrudCommand],
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
        command_class: type[CrudCommand],
        timing: EventTiming,
        listener: Callable[[BaseService, CrudCommand, Any], tuple[CrudCommand, Any]],
    ) -> None:
        """Unregister crud listener."""
        key = (command_class, timing)
        if key not in self._crud_listeners:
            raise ValueError(f"Listener not registered for {key}")
        if listener not in self._crud_listeners[key]:
            raise ValueError(f"Listener not registered for {key}")
        self._crud_listeners[key].remove(listener)

    def crud(self, cmd: CrudCommand) -> Any:
        """Crud the requested value."""
        assert cmd.MODEL_CLASS.ENTITY is not None
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
            raise exc.ServiceException("334086fe", "Repository not set")
        # Call BEFORE listeners
        for listener in self._crud_listeners.get((type(cmd), EventTiming.BEFORE), []):
            cmd, _ = listener(self, cmd, None)
        # Set object ids for CREATE operations
        if cmd.is_create():
            if cmd.objs is None:
                raise exc.InvalidArgumentsError(
                    "645674fa", f"No object provided for operation {cmd.operation}"
                )
            assert id_field_name is not None
            if isinstance(cmd.objs, list):
                for obj in cmd.objs:
                    self.set_object_id(obj, id_field_name, cmd.on_id_set)
            else:
                self.set_object_id(cmd.objs, id_field_name, cmd.on_id_set)
        # Determine which links are handled by this service and which by other services
        if cmd.is_write():
            same_service_links, other_service_links = self._get_model_links(cmd)
        else:
            same_service_links = {}
            other_service_links = {}
        # Start unit of work
        with self.repository.uow() as uow:
            # Verify write operation object links are valid
            if cmd.is_write():
                if cmd.objs is None:
                    raise exc.InvalidArgumentsError(
                        "2bd2ca33", f"No object provided for operation {cmd.operation}"
                    )
                objs = cmd.objs if isinstance(cmd.objs, list) else [cmd.objs]
                # TODO: verifying links from the same service should be the responsibility
                # of the repository
                self._verify_same_service_links(uow, cmd, objs, same_service_links)
                self._verify_other_service_links(cmd, objs, other_service_links)

            # Call repository CRUD operation
            retval = self.crud_repository(uow, cmd, links=same_service_links)

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
    ) -> Any:
        # Get filters depending on the operation
        """Crud repository."""
        if cmd.operation in CrudOperationSet.ANY_ALL.value:
            # Query filter is applied, access filter is added to query filter
            query_filter = cmd.query_filter
            access_filter = cmd.access_filter
            if query_filter and access_filter:
                query_filter = CompositeFilter(
                    filters=[query_filter, access_filter],
                    operator=LogicalOperator.AND,
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
            if cmd.is_write():
                # Operations with one or more objs as input -> check if they match the
                # access filter
                objs = cmd.get_objs()
            elif cmd.is_delete() or cmd.is_exists():
                # Delete/exists one or some (delete all is not possible since there is
                # an access filter) -> check if the ids match the access filter
                assert cmd.user is not None
                objs: list[Model] = self.repository.crud(
                    uow,
                    cmd.user.id,
                    cmd.MODEL_CLASS,
                    CrudOperation.READ_SOME,
                    obj_ids=cmd.get_obj_ids(),
                )
            if objs is not None and not all(
                cmd.access_filter.match_rows(objs, is_model=True)
            ):
                raise exc.UnauthorizedAuthError(
                    "914fc9af", f"Unauthorized access to objects"
                )

        # Split query_filter into repository and service filters
        repository_query_filter, service_query_filter = self.repository.split_filter(
            cmd.MODEL_CLASS, query_filter
        )

        # Call repository CRUD operation
        reserved_arg_names = {"filter", "obj_filter", "links"}
        retval = self.repository.crud(
            uow,
            cmd.user.id if cmd.user else None,
            cmd.MODEL_CLASS,
            cmd.operation,
            objs=cmd.objs,
            obj_ids=cmd.obj_ids,
            return_id=cmd.return_id,
            filter=repository_query_filter,
            limit=cmd.limit,
            offset=cmd.offset,
            obj_filter=service_query_filter,
            links=links,
        )

        return retval

    def update_association(
        self, cmd: UpdateAssociationCommand, **kwargs: Any
    ) -> list[Hashable] | list[Model] | None:
        """Update association."""
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "ea2aee86",
                    "STARTING_UPDATE_ASSOCIATION",
                    cmd=cmd,
                )
            )
        if not self.repository:
            raise exc.ServiceException("ca36f8e8", "Repository not set")

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
            retval = self.repository.update_association(  # type: ignore[assignment]
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

    def set_object_id(
        self, obj: Model, id_field_name: str, on_id_set: OnException = OnException.RAISE
    ) -> None:
        """Set object id."""
        if getattr(obj, id_field_name):
            if on_id_set == OnException.RAISE:
                raise exc.InvalidArgumentsError(
                    "679f8bd9", "Object already has id filled in"
                )
            if on_id_set == OnException.REPLACE:
                # Assign new id
                setattr(obj, id_field_name, self.generate_id())
            elif on_id_set == OnException.IGNORE:
                # Keep id
                pass
            else:
                raise ValueError(f"Invalid on_id_set: {on_id_set}")
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
        """Create log message."""
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
        """Return model links."""
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
        """Return user and repository."""
        user = cmd.user
        if user is None:
            raise exc.UnauthorizedAuthError("a621f6fc", "No user provided")
        if self.repository is None:
            raise exc.InitializationServiceError("04eaee6a", "No repository provided")
        return user, self.repository

    def _verify_other_service_links(
        self,
        cmd: CrudCommand | UpdateAssociationCommand,
        objs: Iterable[Model],
        other_service_links: dict[int, Link],
    ) -> None:
        """Verify other service links."""
        if not cmd.verify_other_service_links or not other_service_links:
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
                        "2141a205",
                        f"Invalid {link.link_model_class.__name__} id(s) among input",
                    )

    def _verify_same_service_links(
        self,
        uow: BaseUnitOfWork,
        cmd: CrudCommand | UpdateAssociationCommand,
        objs: Iterable[Model],
        same_service_links: dict[int, Link],
    ) -> None:
        """Verify same service links."""
        if not self.repository:
            raise exc.ServiceException("63baf129", "Repository not set")
        if not cmd.verify_same_service_links or not same_service_links:
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
                except exc.InvalidIdsError as e:
                    raise exc.InvalidLinkIdsError(
                        "1f342acf",
                        f"Invalid {link.link_model_class.__name__} id(s) among input",
                    )

    def __del__(self) -> None:
        """Del the requested value."""
        if getattr(self, "_setup_logger", None):
            self._setup_logger.info(
                self.create_log_message("d84f9d21", "STOPPING_SERVICE")
            )
