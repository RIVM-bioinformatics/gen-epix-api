from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Hashable, Type

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain import Domain
from gen_epix.fastapp.enum import EventTiming
from gen_epix.fastapp.log import BaseLogItem, LogItem
from gen_epix.fastapp.model import Command, CrudCommand, Model, Policy
from gen_epix.fastapp.pdp import PolicyDecisionPoint
from gen_epix.fastapp.user_manager import BaseUserManager


class App:
    """
    Implementation of the Mediator pattern for handling Commands, which represent a
    unit of execution. Each Command class has one handler function that is called when
    the Command is executed. The handler needs to be registered, typically by a
    Service. As a result, a Service or any function that wants to execute a Command
    can do so by calling the App, without requiring knowledge of which other
    Service or function actually executes the Command.

    The App addresses the following concerns:
    1) Coupling is strongly reduced, which is the primary goal of this pattern.
    2) Policies, including for authorization, can be applied in one place.
    3) Logging of Command execution is centralized and can be kept out of the handlers.
    4) Events can be triggered centrally for particular Commands.

    The App is aware of the domain through the Domain instance passed to it on
    construction. The Domain instance contains all the entities, models, commands and
    permissions.

    The App serves as a Policy Enforcement Point (PEP) by applying Policies at different
    stages of the Command execution. Policies can be registered for a particular Command
    and timing (BEFORE, DURING or AFTER) and are verified by a Policy Decision Point
    (PDP). As such, both Role Based Access Control (RBAC) and Attribute Based Access
    Control (ABAC) can be implemented. The implementation of RBAC is further supported
    by the UserManager that can be provided on construction, and which is used to
    retrieve the user and their permissions.
    """

    DEFAULT_LOG_ITEM_CLASS = LogItem

    def __init__(
        self,
        domain: Domain | None = None,
        pdp: PolicyDecisionPoint | None = None,
        logger: logging.Logger | None = logging.getLogger(__name__),
        user_manager: BaseUserManager | None = None,
        log_item_class: Type[BaseLogItem] = DEFAULT_LOG_ITEM_CLASS,
        id_factory: Callable[[], Hashable] = uuid.uuid4,
        timestamp_factory: Callable[[], datetime] = datetime.now,
        **kwargs: Any,
    ):
        # Set input members
        self._id: str = kwargs.get("id", str(id_factory()))  # type: ignore[assignment]
        self._name: str = kwargs.get("name", self._id)  # type: ignore[assignment]
        self._logger = logger
        self._pdp: PolicyDecisionPoint = pdp or PolicyDecisionPoint()
        self._domain = domain or Domain(self._id)
        self._user_manager = user_manager
        self._log_item_class = log_item_class
        self._id_factory: Callable[[], Hashable] = id_factory
        self._timestamp_factory = timestamp_factory
        # Initialize other members
        self._created_at = self.generate_timestamp()
        self._command_handler_map: dict[Type[Command], Callable[[Command], Any]] = {}
        self._model_crud_command_map: dict[Type[Model], Type[CrudCommand]] = {}
        self._command_listeners: dict[
            EventTiming, dict[Type[Command], list[Callable[[Command, Any], None]]]
        ] = {x: {} for x in EventTiming}
        self._command_stack: list[Command] = []
        # Log start
        if self._logger:
            self._logger.info(
                self.create_log_message(
                    "e8aafcec",
                    "STARTING_APP",
                    app={"created_at": self.created_at},
                )
            )

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def domain(self) -> Domain:
        return self._domain

    @property
    def pdp(self) -> PolicyDecisionPoint:
        return self._pdp

    @property
    def user_manager(self) -> BaseUserManager:
        if self._user_manager is None:
            raise exc.InitializationServiceError("User manager not set")
        return self._user_manager

    @user_manager.setter
    def user_manager(self, user_manager: BaseUserManager | None) -> None:
        self._user_manager = user_manager

    @property
    def logger(self) -> logging.Logger | None:
        return self._logger

    @logger.setter
    def logger(self, logger: logging.Logger | None) -> None:
        self._logger = logger

    @property
    def log_item_class(self) -> Type[BaseLogItem]:
        return self._log_item_class

    def generate_id(self) -> Hashable:
        return self._id_factory()

    def generate_timestamp(self) -> datetime:
        return self._timestamp_factory()

    def register_command(
        self,
        command_class: Type[Command],
    ) -> None:
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "dcf32f06",
                    "REGISTERING_COMMAND",
                    command={"class": command_class.__name__},
                ),
            )
        self.domain.register_command(command_class)

    def register_policy(
        self,
        command_class: Type[Command],
        policy: Policy,
        timing: EventTiming = EventTiming.BEFORE,
    ) -> None:
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "f26cc078",
                    "REGISTERING_POLICY",
                    command={"class": command_class.__name__},
                    policy={"class": policy.__class__.__name__},
                    timing=str(timing.value),  # type: ignore[arg-type]
                ),
            )
        self.pdp.register_policy(command_class, policy, timing)

    def unregister_policy(
        self,
        command_class: Type[Command],
        policy: Policy,
        timing: EventTiming,
    ) -> None:
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "fc0142e1",
                    "UNREGISTERING_POLICY",
                    command={"class": command_class.__name__},
                    policy={"class": policy.__class__.__name__},
                    timing=str(timing.value),  # type: ignore[arg-type]
                ),
            )
        self.pdp.unregister_policy(command_class, policy, timing)

    def register_listener(
        self,
        command_class: Type[Command],
        listener: Callable[[Command, Any], None],
        timing: EventTiming,
    ) -> None:
        """
        Register a listener for a command class that is executed BEFORE the command
        is executed.
        """
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "cb6226db",
                    "REGISTERING_LISTENER",
                    command={"class": command_class.__name__},
                    listener={"name": listener.__name__},
                    timing=str(timing.value),  # type: ignore[arg-type]
                ),
            )
        listeners = self._command_listeners[timing]
        if command_class in listeners:
            if listener in listeners[command_class]:
                raise exc.InitializationServiceError(
                    f"Listener already registered for {command_class.__name__}"
                )
            listeners[command_class].append(listener)
        else:
            listeners[command_class] = [listener]

    def unregister_listener(
        self,
        command_class: Type[Command],
        listener: Callable[[Command, Any], None],
        timing: EventTiming,
    ) -> None:
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "a4f89615",
                    "UNREGISTERING_LISTENER",
                    command_class=command_class.__name__,  # type: ignore[arg-type]
                    listener=listener.__name__,  # type: ignore[arg-type]
                    timing=str(timing.value),  # type: ignore[arg-type]
                ),
            )
        listeners = self._command_listeners[timing]
        if command_class not in listeners or listener not in listeners[command_class]:
            raise exc.InitializationServiceError(
                f"Listener not registered for {command_class}"
            )
        listeners[command_class].remove(listener)

    def register_handler(
        self,
        command_class: Type[Command],
        handler_fun: Callable,  # Takes a Command and returns Any, no type hint here (would be Callable[[Command], Any]) to avoid linter messages
        replace: bool = True,
    ) -> None:
        # Pydantic classes have pydantic.main.ModelMetaClass as type
        # rather than the intended type
        # Workaround: create an obj
        # (using model_construct() to avoid having to supply parameters),
        # and that obj does have the correct type
        # The actual message handling does not have this issue
        # since it is supplied objs of types
        command_class = type(command_class.model_construct())
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "e56517f7",
                    "REGISTERING_HANDLER",
                    command={"class": command_class.__name__},
                    handler_fun={"name": handler_fun.__name__},
                ),
            )
        if not issubclass(command_class, Command):
            raise exc.InitializationServiceError(
                "Handler can only be set for event and command message subclasses"
            )
        if command_class in self._command_handler_map and not replace:
            raise exc.InitializationServiceError(
                f"Command handler already added for {command_class}: {handler_fun}"
            )
        self._command_handler_map[command_class] = handler_fun

    def get_handler(self, command_class: Type[Command]) -> Callable:
        for type_ in command_class.__mro__:
            handler = self._command_handler_map.get(type_)
            if handler:
                return handler
        raise exc.InitializationServiceError(
            f"No handler set for {command_class} or any of its superclasses"
        )

    def handle(self, cmd: Command) -> Any:
        self._command_stack.append(cmd)
        is_initial_command = len(self._command_stack) == 1
        if self._logger:
            if self._logger.level <= logging.DEBUG:
                self._logger.debug(
                    self.create_log_message("e94cad9b", "STARTED_COMMAND", cmd=cmd)
                )
            elif is_initial_command:
                self._logger.info(
                    self.create_log_message(
                        "e94cad9b",
                        "STARTED_COMMAND",
                        add_debug_info=False,
                        cmd=cmd,
                    )
                )
        # Policy Enforcement Point 1: apply policies from PDP, resulting in
        # unauthorized error. Only applied to the initial command: subsequent commands
        # issued by this command are trusted since requested by a service rather than
        # a user.
        if is_initial_command:
            try:
                self.pdp.apply(cmd, EventTiming.BEFORE)
            except exc.UnauthorizedAuthError as exception:
                # Not authorized
                if self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "fd923dbf", "NOT_AUTHORIZED", add_debug_info=False, cmd=cmd
                        )
                    )
                self._command_stack.pop()
                raise exception
            except Exception as exception:
                # Any other error: add stack trace
                if self._logger:
                    self._logger.error(
                        self.create_log_message(
                            "abd561ff", "ERROR", cmd=cmd, exception=exception  # type: ignore[arg-type]
                        ),
                        exc_info=True,
                        stack_info=True,
                    )
                self._command_stack.pop()
                raise exception
        # Get handler
        try:
            handler = self.get_handler(type(cmd))
        except Exception as exception:
            if self._logger:
                self._logger.error(
                    self.create_log_message("ad536c0b", "ERROR", cmd=cmd, exception=exception),  # type: ignore[arg-type]
                    exc_info=True,
                    stack_info=True,
                )
            self._command_stack.pop()
            raise exception

        # Execute command
        try:
            # Apply BEFORE listeners
            for listener in self._command_listeners[EventTiming.BEFORE].get(
                type(cmd), []
            ):
                listener(cmd, None)
            # Policy Enforcement Point 2: add policies from PDP to command, so that
            # they can be used by the handler. Only applied to the initial command:
            # subsequent commands issued by this command are expected to have these
            # policies added by the caller.
            if is_initial_command:
                self.pdp.apply(cmd, EventTiming.DURING)
            # Execute command
            retval = handler(cmd)
            # Policy Enforcement Point 3: apply policies from PDP, resulting in
            # updating the return value. Only applied to the initial command:
            # subsequent commands are expected to have these policies applied
            # by the caller.
            if is_initial_command:
                retval = self.pdp.apply(cmd, EventTiming.AFTER, retval=retval)
            # Apply AFTER listeners
            for listener in self._command_listeners[EventTiming.AFTER].get(
                type(cmd), []
            ):
                listener(cmd, retval)
        except exc.DomainException as exception:
            # Domain exception does not require stack trace
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "e8891b42", "DOMAIN_EXCEPTION", cmd=cmd, exception=exception  # type: ignore[arg-type]
                    )
                )
            self._command_stack.pop()
            raise exception
        except Exception as exception:
            # Any other unexpected error: add stack trace
            if self._logger:
                self._logger.error(
                    self.create_log_message("b575040c", "ERROR", cmd=cmd, exception=exception),  # type: ignore[arg-type]
                    exc_info=True,
                    stack_info=True,
                )
            self._command_stack.pop()
            raise exception

        if self._logger:
            msg = self.create_log_message(
                "5ab6c248", "FINISHED_COMMAND", add_debug_info=False, cmd=cmd
            )
            if self._logger.level <= logging.DEBUG:
                self._logger.debug(msg)
            elif is_initial_command:
                self._logger.info(msg)
        self._command_stack.pop()
        return retval

    def create_log_message(
        self,
        code: str,
        msg: str | None,
        add_debug_info: bool = True,
        cmd: Command | None = None,
        **kwargs: Any,
    ) -> str:
        content = {}
        if add_debug_info:
            content["app"] = kwargs.pop("app", {}) | {
                "id": self._id,
                "name": self.name,
            }
            if cmd:
                is_initial_command = len(self._command_stack) < 2
                content["command"] = kwargs.pop("command", {}) | {
                    "class": cmd.__class__.__name__,
                    "object": json.loads(cmd.model_dump_json(exclude_none=True)),
                    "parent_command_id": (
                        None if is_initial_command else f"{self._command_stack[-2].id}"
                    ),
                    "stack_trace": (
                        "->".join(
                            [f"{x.__class__.__name__}" for x in self._command_stack]
                        )
                    ),
                }
            if kwargs:
                content = {**content, **kwargs}
        else:
            content = kwargs
            if cmd:
                content["command"] = kwargs.pop("command", {}) | {
                    "class": cmd.__class__.__name__,
                    "id": str(cmd.id),
                    "user_id": cmd.user.id if cmd.user else None,
                }
        log_item = self._log_item_class(code=code, msg=msg, **content)  # type: ignore[arg-type]
        return log_item.dumps()

    @staticmethod
    def create_static_log_message(
        code: str,
        msg: str,
        log_item_class: Type[BaseLogItem] = DEFAULT_LOG_ITEM_CLASS,
        **kwargs: Any,
    ) -> str:
        cmd: Command | None = kwargs.pop("cmd", None)  # type: ignore[assignment]
        content = kwargs
        if cmd:
            content["command"] = kwargs.pop("command", {}) | {
                "class": cmd.__class__.__name__,
                "id": str(cmd.id),
                "user_id": cmd.user.id if cmd.user else None,
            }
        log_item = log_item_class(code=code, msg=msg, **content)  # type: ignore[arg-type]
        return log_item.dumps()

    def __del__(self) -> None:
        if self._logger:
            self._logger.info(self.create_log_message("aa21c54a", "STOPPING_APP"))
