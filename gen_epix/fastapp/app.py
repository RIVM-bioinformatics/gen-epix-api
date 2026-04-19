from __future__ import annotations

import json
import logging
import threading
import uuid
from collections.abc import Callable, Hashable
from datetime import datetime
from typing import Any, cast

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
    DEFAULT_LOG_SUMMARIZATION_ENABLED: bool = True
    DEFAULT_LOG_MAX_LIST_ITEMS: int = 3
    _CFG_TRUE_VALUES: set[str] = {"1", "true", "yes", "on"}
    _CFG_FALSE_VALUES: set[str] = {"0", "false", "no", "off"}

    def __init__(
        self,
        domain: Domain | None = None,
        pdp: PolicyDecisionPoint | None = None,
        logger: logging.Logger | None = logging.getLogger(__name__),
        user_manager: BaseUserManager | None = None,
        cfg: Any | None = None,
        impl: Any | None = None,
        log_item_class: type[BaseLogItem] = DEFAULT_LOG_ITEM_CLASS,
        id_factory: Callable[[], Hashable] = uuid.uuid4,
        id: str | None = None,
        name: str | None = None,
        timestamp_factory: Callable[[], datetime] = datetime.now,
        feature_flags: dict[Hashable, bool] | None = None,
        **kwargs: Any,
    ):
        # Set input members
        self._id_factory: Callable[[], Hashable] = id_factory
        self._id: str = id or str(self._id_factory())
        self._name: str = name or self._id
        self._domain = domain or Domain(self._id)
        self._pdp: PolicyDecisionPoint = pdp or PolicyDecisionPoint()
        self._user_manager = user_manager
        self._cfg = cfg
        self._impl = impl
        self._logger = logger
        self._log_item_class = log_item_class
        self._timestamp_factory = timestamp_factory
        self._feature_flags = feature_flags or {}

        # Initialize other members
        self._created_at = self.generate_timestamp()
        self._command_handler_map: dict[type[Command], Callable[[Command], Any]] = {}
        self._model_crud_command_map: dict[type[Model], type[CrudCommand]] = {}
        self._command_listeners: dict[
            EventTiming, dict[type[Command], list[Callable[[Command, Any], None]]]
        ] = {x: {} for x in EventTiming}
        self._command_stack_local = threading.local()
        self._init_log_settings()

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
        if self._pdp is None:
            raise exc.InitializationServiceError(
                "a336efaf", "Policy decision point not set"
            )
        return self._pdp

    @property
    def user_manager(self) -> BaseUserManager:
        if self._user_manager is None:
            raise exc.InitializationServiceError("3a557c34", "User manager not set")
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
    def cfg(self) -> Any:
        if self._cfg is None:
            raise exc.InitializationServiceError(
                "67bd528f", "Configuration data is not set"
            )
        return self._cfg

    @property
    def impl(self) -> Any:
        if self._impl is None:
            raise exc.InitializationServiceError(
                "0fe120d0", "Implementation details are not set"
            )
        return self._impl

    @property
    def log_item_class(self) -> type[BaseLogItem]:
        return self._log_item_class

    @property
    def feature_flags(self) -> dict[Hashable, bool]:
        """Return a copy of the feature flags dict to prevent external mutation."""
        return dict(self._feature_flags)

    def generate_id(self) -> Hashable:
        return self._id_factory()

    def generate_timestamp(self) -> datetime:
        return self._timestamp_factory()

    def set_feature_flag(self, key: Hashable, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Feature flag value must be a boolean")
        self._feature_flags[key] = value

    def get_feature_flag(self, key: Hashable, default: bool = False) -> bool:
        return self._feature_flags.get(key, default)

    def register_command(
        self,
        command_class: type[Command],
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
        command_class: type[Command],
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
                    timing=str(timing.value),
                ),
            )
        self.pdp.register_policy(command_class, policy, timing)

    def unregister_policy(
        self,
        command_class: type[Command],
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
                    timing=str(timing.value),
                ),
            )
        self.pdp.unregister_policy(command_class, policy, timing)

    def register_listener(
        self,
        command_class: type[Command],
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
                    timing=str(timing.value),
                ),
            )
        listeners = self._command_listeners[timing]
        if command_class in listeners:
            if listener in listeners[command_class]:
                raise exc.InitializationServiceError(
                    "3c93380c",
                    f"Listener already registered for {command_class.__name__}",
                )
            listeners[command_class].append(listener)
        else:
            listeners[command_class] = [listener]

    def unregister_listener(
        self,
        command_class: type[Command],
        listener: Callable[[Command, Any], None],
        timing: EventTiming,
    ) -> None:
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "a4f89615",
                    "UNREGISTERING_LISTENER",
                    command_class=command_class.__name__,
                    listener=listener.__name__,
                    timing=str(timing.value),
                ),
            )
        listeners = self._command_listeners[timing]
        if command_class not in listeners or listener not in listeners[command_class]:
            raise exc.InitializationServiceError(
                "ede03a66", f"Listener not registered for {command_class}"
            )
        listeners[command_class].remove(listener)

    def register_handler(
        self,
        command_class: type[Command],
        handler_fn: Callable,  # Takes a Command and returns Any, no type hint here (would be Callable[[Command], Any]) to avoid linter messages
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
                    handler_fn={
                        "name": (
                            handler_fn.__name__
                            if hasattr(handler_fn, "__name__")
                            else str(handler_fn)
                        )
                    },
                ),
            )
        if not issubclass(command_class, Command):
            raise exc.InitializationServiceError(
                "2d5ea504",
                "Handler can only be set for event and command message subclasses",
            )
        if command_class in self._command_handler_map and not replace:
            raise exc.InitializationServiceError(
                "3fc33bf3",
                f"Command handler already added for {command_class}: {handler_fn}",
            )
        self._command_handler_map[command_class] = handler_fn

    def get_handler(self, command_class: type[Command]) -> Callable:
        for type_ in command_class.__mro__:
            handler = self._command_handler_map.get(type_)
            if handler:
                return handler
        raise exc.InitializationServiceError(
            "6ce523f9", f"No handler set for {command_class} or any of its superclasses"
        )

    def _get_command_stack(self) -> list[Command]:
        command_stack = getattr(self._command_stack_local, "value", None)
        if command_stack is None:
            command_stack = []
            self._command_stack_local.value = command_stack
        return command_stack

    def _pop_command_stack(self) -> None:
        command_stack = self._get_command_stack()
        if command_stack:
            command_stack.pop()

    def handle(self, cmd: Command) -> Any:
        command_stack = self._get_command_stack()
        command_stack.append(cmd)
        is_initial_command = len(command_stack) == 1
        if self._logger:
            self._log_command_start(cmd, is_initial_command)
        # Policy Enforcement Point 1: apply policies from PDP, resulting in
        # unauthorized error. Only applied to the initial command: subsequent commands
        # issued by this command are trusted since requested by a service rather than
        # a user.
        if is_initial_command:
            self._handle_initial_command(cmd)
        # Get handler
        handler: Callable = self._get_command_handler(cmd)
        # Execute command
        retval = self._execute_command(cmd, is_initial_command, handler)
        if self._logger:
            self._log_command_finish(cmd, is_initial_command)
        self._pop_command_stack()
        return retval

    def _log_command_finish(self, cmd: Command, is_initial_command: bool) -> None:
        msg = self.create_log_message(
            "14a19691", "FINISHED_COMMAND", add_debug_info=False, cmd=cmd
        )
        if self._logger.level <= logging.DEBUG:
            self._logger.debug(msg)
        elif is_initial_command:
            self._logger.info(msg)

    def _execute_command(
        self, cmd: Command, is_initial_command: bool, handler: Callable
    ) -> Any:
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
            retval = self.apply_handler(cmd, handler)
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
        except exc.ServiceException as exception:
            # Service errors should always capture the stack trace to aid diagnosis.
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "f3c7a1d9", "SERVICE_EXCEPTION", cmd=cmd, exception=exception
                    ),
                    exc_info=True,
                )
            self._pop_command_stack()
            raise exception
        except exc.DomainException as exception:
            # Other domain exceptions are expected; log without stack trace to reduce noise.
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "e8891b42", "DOMAIN_EXCEPTION", cmd=cmd, exception=exception
                    )
                )
            self._pop_command_stack()
            raise exception
        except Exception as exception:
            # Any other unexpected error: add stack trace
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "b575040c", "ERROR", cmd=cmd, exception=exception
                    ),
                    exc_info=True,
                    stack_info=True,
                )
            self._pop_command_stack()
            raise exception
        return retval

    def _get_command_handler(self, cmd: Command) -> Callable:
        try:
            handler = self.get_handler(type(cmd))
        except Exception as exception:
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "ad536c0b", "ERROR", cmd=cmd, exception=exception
                    ),
                    exc_info=True,
                    stack_info=True,
                )
            self._pop_command_stack()
            raise exception
        return handler

    def _handle_initial_command(self, cmd: Command) -> None:
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
            self._pop_command_stack()
            raise exception
        except Exception as exception:
            # Any other error: add stack trace
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "abd561ff", "ERROR", cmd=cmd, exception=exception
                    ),
                    exc_info=True,
                    stack_info=True,
                )
            self._pop_command_stack()
            raise exception

    def _log_command_start(self, cmd: Command, is_initial_command: bool) -> None:
        log_code = "e94cad9b"
        if self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(log_code, "STARTED_COMMAND", cmd=cmd)
            )
        elif is_initial_command:
            self._logger.info(
                self.create_log_message(
                    log_code,
                    "STARTED_COMMAND",
                    add_debug_info=False,
                    cmd=cmd,
                )
            )

    def apply_handler(self, cmd: Command, handler: Callable) -> Any:
        retval = cast(Any, handler(cmd))
        return retval

    def _init_log_settings(self) -> None:
        self._log_summarization_enabled = self.DEFAULT_LOG_SUMMARIZATION_ENABLED
        self._log_max_list_items = self.DEFAULT_LOG_MAX_LIST_ITEMS
        cfg: dict = (
            (self._cfg or {}).get("log", {}).get("command_object_summarization", {})
        )
        self._log_summarization_enabled = App._get_bool_from_cfg_value(
            cfg.get("enabled", self.DEFAULT_LOG_SUMMARIZATION_ENABLED)
        )
        self._log_max_list_items = App._get_int_from_cfg_value(
            cfg.get("max_list_items", self.DEFAULT_LOG_MAX_LIST_ITEMS)
        )

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
                command_stack = self._get_command_stack()
                is_initial_command = len(command_stack) < 2
                cmd_object = json.loads(cmd.model_dump_json(exclude_none=True))
                if self._log_summarization_enabled:
                    cmd_object = self._summarise_command_object_for_log(cmd_object)
                content["command"] = kwargs.pop("command", {}) | {
                    "class": cmd.__class__.__name__,
                    # Optionally summarize large list fields based on config.
                    "object": cmd_object,
                    "parent_command_id": (
                        None if is_initial_command else f"{command_stack[-2].id}"
                    ),
                    "stack_trace": (
                        "->".join([f"{x.__class__.__name__}" for x in command_stack])
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
        log_item = self._log_item_class(code=code, msg=msg, **content)
        return log_item.dumps()

    def _summarise_command_object_for_log(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Recursively walk *data* and replace any list longer than *max_items* with
        a compact ``{"_count": N, "_sample": [...]}`` dict so the serialised log
        payload stays within downstream log-sink size constraints."""

        def _walk(obj: Any) -> Any:
            if isinstance(obj, dict):
                return {x: _walk(y) for x, y in obj.items()}
            if isinstance(obj, list):
                if len(obj) > self._log_max_list_items:
                    return {
                        "_count": len(obj),
                        "_sample": [_walk(x) for x in obj[: self._log_max_list_items]],
                    }
                return [_walk(x) for x in obj]
            return obj

        return _walk(data)  # type: ignore[return-value]

    @staticmethod
    def create_static_log_message(
        code: str,
        msg: str,
        log_item_class: type[BaseLogItem] = DEFAULT_LOG_ITEM_CLASS,
        **kwargs: Any,
    ) -> str:
        cmd: Command | None = kwargs.pop("cmd", None)
        content = kwargs
        if cmd:
            content["command"] = kwargs.pop("command", {}) | {
                "class": cmd.__class__.__name__,
                "id": str(cmd.id),
                "user_id": cmd.user.id if cmd.user else None,
            }
        log_item = log_item_class(code=code, msg=msg, **content)
        return log_item.dumps()

    def __del__(self) -> None:
        if self._logger:
            self._logger.info(self.create_log_message("aa21c54a", "STOPPING_APP"))

    @staticmethod
    def _get_bool_from_cfg_value(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in App._CFG_TRUE_VALUES:
                return True
            if lowered in App._CFG_FALSE_VALUES:
                return False
        raise exc.InitializationServiceError(
            "d9c8e1b0",
            f"Invalid boolean config value: {value}",
        )

    @staticmethod
    def _get_int_from_cfg_value(value: Any) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise exc.InitializationServiceError(
                "d9c8e1b1",
                f"Invalid integer config value: {value}",
            )
        return parsed
