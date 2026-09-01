"""Application command dispatch, policy enforcement, and event handling.

The ``App`` mediator coordinates command handlers registered by services. It
applies policies and listeners across command lifecycle phases, records command
execution, and manages command-triggered cache invalidation.
"""

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
    DEFAULT_LOG_MAX_STRING_LENGTH: int = 500
    DEFAULT_LOG_MAX_DICT_ITEMS: int = 30
    # Exceptions (e.g. DB integrity errors) get a longer, separate budget than
    # ordinary strings: their useful content (the driver's actual error) is
    # often at the very end, after a long echoed SQL statement.
    DEFAULT_LOG_MAX_EXCEPTION_MESSAGE_LENGTH: int = 2000
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
        log_cmd_object_on_error: bool = True,
        feature_flags: dict[Hashable, bool] | None = None,
        **kwargs: Any,
    ):
        """Initialize an application command mediator and its runtime dependencies.

        Omitted domain and policy decision point dependencies are created for the
        application identifier. The application starts with no handlers, listeners,
        or cache invalidators, and reads command-object logging limits from ``cfg``.

        Args:
            domain: Domain metadata registry used to validate and register commands.
            pdp: Policy decision point applied during command execution.
            logger: Logger used for application and command lifecycle events.
            user_manager: Provider of users and permissions for authorization policies.
            cfg: Runtime configuration, including command-object log summarization.
            impl: Application-specific implementation details exposed to services.
            log_item_class: Structured log message class used by ``create_log_message``.
            id_factory: Factory for the application identifier when ``id`` is omitted.
            id: Stable application identifier.
            name: Human-readable application name; defaults to ``id``.
            timestamp_factory: Factory for application creation timestamps.
            log_cmd_object_on_error: Whether error logs include serialized commands.
            feature_flags: Initial feature flags available to command handlers.
        """
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
        self._command_stack: list[Command] = []
        self._cache_invalidator_map: dict[
            type[Command], list[Callable[[Command], None]]
        ] = {}
        self._auto_invalidate_cache_set: set[type[Command]] = set()
        self._log_cmd_object_on_error: bool = log_cmd_object_on_error
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
        """Id the requested value."""
        return self._id

    @property
    def name(self) -> str:
        """Name the requested value."""
        return self._name

    @property
    def created_at(self) -> datetime:
        """Created at."""
        return self._created_at

    @property
    def domain(self) -> Domain:
        """Domain the requested value."""
        return self._domain

    @property
    def pdp(self) -> PolicyDecisionPoint:
        """Return the policy decision point configured for command execution.

        Returns:
            The policy decision point used during command execution.

        Raises:
            InitializationServiceError: If no policy decision point is configured.
        """
        if self._pdp is None:
            raise exc.InitializationServiceError(
                "a336efaf", "Policy decision point not set"
            )
        return self._pdp

    @property
    def user_manager(self) -> BaseUserManager:
        """Return the user manager used by authorization policies.

        Returns:
            The user manager used by authorization policies.

        Raises:
            InitializationServiceError: If no user manager is configured.
        """
        if self._user_manager is None:
            raise exc.InitializationServiceError("3a557c34", "User manager not set")
        return self._user_manager

    @user_manager.setter
    def user_manager(self, user_manager: BaseUserManager | None) -> None:
        """User manager."""
        self._user_manager = user_manager

    @property
    def logger(self) -> logging.Logger | None:
        """Logger the requested value."""
        return self._logger

    @logger.setter
    def logger(self, logger: logging.Logger | None) -> None:
        """Logger the requested value."""
        self._logger = logger

    @property
    def cfg(self) -> Any:
        """Return application configuration required by configured services.

        Returns:
            The configured application settings.

        Raises:
            InitializationServiceError: If no configuration is configured.
        """
        if self._cfg is None:
            raise exc.InitializationServiceError(
                "67bd528f", "Configuration data is not set"
            )
        return self._cfg

    @property
    def impl(self) -> Any:
        """Return application-specific implementation details.

        Returns:
            The configured application implementation details.

        Raises:
            InitializationServiceError: If no implementation details are configured.
        """
        if self._impl is None:
            raise exc.InitializationServiceError(
                "0fe120d0", "Implementation details are not set"
            )
        return self._impl

    @property
    def log_item_class(self) -> type[BaseLogItem]:
        """Log item class."""
        return self._log_item_class

    @property
    def feature_flags(self) -> dict[Hashable, bool]:
        """Return a copy of the feature flags dict to prevent external mutation."""
        return dict(self._feature_flags)

    def generate_id(self) -> Hashable:
        """Generate id."""
        return self._id_factory()

    def generate_timestamp(self) -> datetime:
        """Generate timestamp."""
        return self._timestamp_factory()

    def set_feature_flag(self, key: Hashable, value: bool) -> None:
        """Set the enabled state for a feature flag.

        Args:
            key: Identifier used to retrieve the feature flag.
            value: Enabled state to store for ``key``.

        Raises:
            ValueError: If ``value`` is not a boolean.
        """
        if not isinstance(value, bool):
            raise ValueError("Feature flag value must be a boolean")
        self._feature_flags[key] = value

    def get_feature_flag(self, key: Hashable, default: bool = False) -> bool:
        """Return feature flag."""
        return self._feature_flags.get(key, default)

    def register_command(
        self,
        command_class: type[Command],
    ) -> None:
        """Register command."""
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
        """Register policy."""
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
        """Unregister policy."""
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
        """Register a lifecycle listener for a command class and timing.

        Listeners receive the command and its current result. They execute in
        registration order at the supplied lifecycle timing.

        Args:
            command_class: Command class observed by the listener.
            listener: Callable receiving the command and its current result.
            timing: Lifecycle phase at which to invoke the listener.

        Raises:
            InitializationServiceError: If this listener is already registered for
                the command class and timing.
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

    def register_cache_invalidator(
        self,
        command_class: type[Command],
        invalidator_fn: Callable[[Command], None],
    ) -> None:
        """Register a cache invalidator for successful commands of an exact type.

        Args:
            command_class: Exact command class that triggers invalidation.
            invalidator_fn: Callable invoked with the successfully handled command.

        Raises:
            InitializationServiceError: If the invalidator is already registered for
                ``command_class``.
        """
        if self._logger and self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    "66a90fdb",
                    "REGISTERING_CACHE_INVALIDATOR",
                    command={"class": command_class.__name__},
                    invalidator_fn={
                        "name": getattr(invalidator_fn, "__name__", str(invalidator_fn))
                    },
                ),
            )
        invalidators = self._cache_invalidator_map.setdefault(command_class, [])
        if invalidator_fn in invalidators:
            raise exc.InitializationServiceError(
                "a252c748",
                f"Cache invalidator already registered for {command_class.__name__}",
            )
        invalidators.append(invalidator_fn)

    def invalidate_cache(self, cmd: Command) -> None:
        """Execute cache invalidators registered for the exact command type."""
        for invalidator_fn in self._cache_invalidator_map.get(type(cmd), []):
            invalidator_fn(cmd)

    def set_auto_invalidate_cache(
        self,
        command_class: type[Command],
        enabled: bool,
    ) -> None:
        """Enable or disable automatic cache invalidation for a command type."""
        if enabled:
            self._auto_invalidate_cache_set.add(command_class)
        else:
            self._auto_invalidate_cache_set.discard(command_class)

    def unregister_listener(
        self,
        command_class: type[Command],
        listener: Callable[[Command, Any], None],
        timing: EventTiming,
    ) -> None:
        """Remove a previously registered command lifecycle listener.

        Args:
            command_class: Command class associated with the listener.
            listener: Listener to remove.
            timing: Lifecycle phase at which the listener was registered.

        Raises:
            InitializationServiceError: If the listener is not registered for the
                command class and timing.
        """
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
        """Register the handler that executes a command class.

        The handler is resolved for the command class and its base classes when
        ``handle`` dispatches a command.

        Args:
            command_class: Command class handled by ``handler_fn``.
            handler_fn: Callable that receives a command instance and returns its result.
            replace: Whether to replace an existing handler for ``command_class``.

        Raises:
            InitializationServiceError: If ``command_class`` is not a command class, or
                a handler already exists and ``replace`` is false.
        """
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
        """Return the nearest registered handler for a command class.

        Searches the class method-resolution order, allowing a base command handler
        to serve subclasses that do not define their own handler.

        Args:
            command_class: Command class whose handler is required.

        Returns:
            The registered callable that handles instances of ``command_class``.

        Raises:
            InitializationServiceError: If neither the class nor its bases has a
                registered handler.
        """
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
        """Dispatch a command through its complete application lifecycle.

        For the initial command in a dispatch stack, applies BEFORE policies,
        resolves a handler, applies DURING and AFTER policies, runs registered
        listeners, and invalidates configured caches after successful execution.
        Nested commands are treated as trusted service calls and skip policy
        enforcement.

        Args:
            cmd: Command instance to execute.

        Returns:
            The handler result, after any AFTER policy transforms it.

        Raises:
            UnauthorizedAuthError: If a BEFORE policy rejects the initial command.
            InitializationServiceError: If no handler is registered for the command
                class or its base classes.
            ServiceException: If a handler, listener, or policy raises a service error.
            DomainException: If a handler, listener, or policy raises another domain
                error.
            Exception: If command processing raises an unexpected error.
        """
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
        """Log command finish."""
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
        """Execute a resolved command handler and its remaining lifecycle phases.

        Runs BEFORE listeners, applies DURING policies for initial commands,
        invokes the handler, applies AFTER policies to its result, runs AFTER
        listeners, and then performs configured cache invalidation. Logs and
        re-raises every failure after removing the command from the dispatch stack.

        Args:
            cmd: Command currently being dispatched.
            is_initial_command: Whether ``cmd`` originated at the application boundary.
            handler: Resolved callable that executes ``cmd``.

        Returns:
            The handler result, optionally transformed by AFTER policies.

        Raises:
            ServiceException: Re-raised after being logged as a service failure.
            DomainException: Re-raised after being logged as an expected domain error.
            Exception: Re-raised after being logged as an unexpected failure from a
                listener, policy, handler, or cache invalidator.
        """
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
            if type(cmd) in self._auto_invalidate_cache_set:
                self.invalidate_cache(cmd)
        except exc.ServiceException as exception:
            # Service errors should always capture the stack trace to aid diagnosis.
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "f3c7a1d9",
                        "SERVICE_EXCEPTION",
                        add_debug_info=self._log_cmd_object_on_error,
                        cmd=cmd,
                        exception=exception,
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
                        "e8891b42",
                        "DOMAIN_EXCEPTION",
                        add_debug_info=self._log_cmd_object_on_error,
                        cmd=cmd,
                        exception=exception,
                    )
                )
            self._pop_command_stack()
            raise exception
        except Exception as exception:
            # Any other unexpected error: add stack trace
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "b575040c",
                        "ERROR",
                        add_debug_info=self._log_cmd_object_on_error,
                        cmd=cmd,
                        exception=exception,
                    ),
                    exc_info=True,
                    stack_info=True,
                )
            self._pop_command_stack()
            raise exception
        return retval

    def _get_command_handler(self, cmd: Command) -> Callable:
        """Resolve a command handler while logging and unwinding a failed dispatch.

        Args:
            cmd: Command currently at the top of the execution stack.

        Returns:
            The handler resolved for ``cmd`` or one of its base command classes.

        Raises:
            InitializationServiceError: If no matching handler is registered.
        """
        try:
            handler = self.get_handler(type(cmd))
        except Exception as exception:
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "ad536c0b",
                        "ERROR",
                        add_debug_info=self._log_cmd_object_on_error,
                        cmd=cmd,
                        exception=exception,
                    ),
                    exc_info=True,
                    stack_info=True,
                )
            self._pop_command_stack()
            raise exception
        return handler

    def _handle_initial_command(self, cmd: Command) -> None:
        """Apply BEFORE policies to the outermost command in a dispatch stack.

        Args:
            cmd: Initial command whose authorization policies must be evaluated.

        Raises:
            UnauthorizedAuthError: If a BEFORE policy denies the command.
            Exception: If policy evaluation fails for another reason.
        """
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
                        "abd561ff",
                        "ERROR",
                        add_debug_info=self._log_cmd_object_on_error,
                        cmd=cmd,
                        exception=exception,
                    ),
                    exc_info=True,
                    stack_info=True,
                )
            self._pop_command_stack()
            raise exception

    def _log_command_start(self, cmd: Command, is_initial_command: bool) -> None:
        """Log command start."""
        log_code = "e94cad9b"
        if self._logger.level <= logging.DEBUG:
            self._logger.debug(
                self.create_log_message(
                    log_code,
                    "STARTED_COMMAND",
                    add_debug_info=self._log_cmd_object_on_error,
                    cmd=cmd,
                )
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
        """Apply handler."""
        retval = cast(Any, handler(cmd))
        return retval

    def _init_log_settings(self) -> None:
        """Initialize command-object log summarization from runtime configuration.

        Uses framework defaults when the ``log.command_object_summarization`` section
        is absent. Parsed settings control whether command objects are summarized and
        the maximum retained list, string, dictionary, and exception-message content.

        Raises:
            ValueError: If a configured boolean or integer setting is invalid.
        """
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
        self._log_max_string_length = App._get_int_from_cfg_value(
            cfg.get("max_string_length", self.DEFAULT_LOG_MAX_STRING_LENGTH)
        )
        self._log_max_dict_items = App._get_int_from_cfg_value(
            cfg.get("max_dict_items", self.DEFAULT_LOG_MAX_DICT_ITEMS)
        )
        self._log_max_exception_message_length = App._get_int_from_cfg_value(
            cfg.get(
                "max_exception_message_length",
                self.DEFAULT_LOG_MAX_EXCEPTION_MESSAGE_LENGTH,
            )
        )

    def create_log_message(
        self,
        code: str,
        msg: str | None,
        add_debug_info: bool = True,
        cmd: Command | None = None,
        **kwargs: Any,
    ) -> str:
        """Create log message."""
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
                if self._log_summarization_enabled:
                    kwargs = self._summarise_command_object_for_log(kwargs)
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
        """Recursively walk *data* and replace any list or mapping longer than their
        respective thresholds with a compact ``{"_count": N, "_sample": ...}`` summary,
        and truncate any string longer than *max_string_length* to its first N chars
        with a suffix showing the total length. Exceptions get their own, longer
        budget (*max_exception_message_length*) and are truncated from the middle
        rather than the end, since DB driver errors often echo the full SQL
        statement first and put the actual error message at the very end. All of
        this keeps the serialised log payload within downstream log-sink size
        constraints.
        """

        def _walk(obj: Any) -> Any:
            """Walk the requested value."""
            if isinstance(obj, Exception):
                return App._truncate_middle(
                    str(obj), self._log_max_exception_message_length
                )
            if isinstance(obj, dict):
                if len(obj) > self._log_max_dict_items:
                    return {
                        "_count": len(obj),
                        "_sample": {
                            x: _walk(y)
                            for x, y in list(obj.items())[: self._log_max_list_items]
                        },
                    }
                return {x: _walk(y) for x, y in obj.items()}
            if isinstance(obj, list):
                if len(obj) > self._log_max_list_items:
                    return {
                        "_count": len(obj),
                        "_sample": [_walk(x) for x in obj[: self._log_max_list_items]],
                    }
                return [_walk(x) for x in obj]
            if isinstance(obj, str) and len(obj) > self._log_max_string_length:
                return f"{obj[:self._log_max_string_length]}…[{len(obj)} chars]"
            return obj

        return _walk(data)  # type: ignore[return-value]

    @staticmethod
    def create_static_log_message(
        code: str,
        msg: str,
        log_item_class: type[BaseLogItem] = DEFAULT_LOG_ITEM_CLASS,
        **kwargs: Any,
    ) -> str:
        """Create static log message."""
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
        """Del the requested value."""
        if self._logger:
            self._logger.info(self.create_log_message("aa21c54a", "STOPPING_APP"))

    @staticmethod
    def _get_bool_from_cfg_value(value: Any) -> bool:
        """Parse a boolean command-log configuration value.

        Args:
            value: Boolean or case-insensitive configured true/false string.

        Returns:
            Parsed boolean value.

        Raises:
            InitializationServiceError: If ``value`` is not a supported boolean form.
        """
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
        """Parse an integer command-log configuration value.

        Args:
            value: Value accepted by Python's ``int`` conversion.

        Returns:
            Parsed integer value.

        Raises:
            InitializationServiceError: If ``value`` cannot be converted to an integer.
        """
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise exc.InitializationServiceError(
                "d9c8e1b1",
                f"Invalid integer config value: {value}",
            )
        return parsed

    @staticmethod
    def _truncate_middle(text: str, max_length: int) -> str:
        """Truncate *text* to *max_length* chars, keeping a prefix and a suffix
        rather than just the head. DB driver error strings (e.g. FK/unique
        constraint violations) often echo the full SQL statement first and put
        the actual error message at the end, so a head-only cut hides it.
        """
        if max_length <= 0:
            return f"…[{len(text)} chars omitted]…"
        if len(text) <= max_length:
            return text
        prefix_len = max_length // 2
        suffix_len = max_length - prefix_len
        omitted = len(text) - max_length
        prefix = text[:prefix_len] if prefix_len else ""
        suffix = text[-suffix_len:] if suffix_len else ""
        return f"{prefix}…[{omitted} chars omitted]…{suffix}"
