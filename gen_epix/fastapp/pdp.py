from typing import Any, Type

from gen_epix.fastapp import exc, model
from gen_epix.fastapp.enum import EventTiming


class PolicyDecisionPoint:
    """
    Policy Decision Point (PDP). This is the central point where policies are
    registered and applied. They are executed in order of registration.

    Policies must be registered for a particular command and timing (BEFORE, DURING
    or AFTER) of execution:
    - BEFORE: raise UnauthorizedAuthorityError if any policy denies the command.
    - DURING: add policies to command so that they can be used during command execution.
    - AFTER: filter the return value with each policy and return it.
    """

    def __init__(self) -> None:
        self._policies: dict[
            Type[model.Command], dict[EventTiming, list[model.Policy]]
        ] = {}

    def register_policy(
        self,
        command_class: Type[model.Command],
        policy: model.Policy,
        timing: EventTiming = EventTiming.BEFORE,
    ) -> None:
        """
        Register a policy for a command class and timing before, during or after command execution.
        """
        if command_class not in self._policies:
            self._policies[command_class] = {}
        if timing not in self._policies[command_class]:
            self._policies[command_class][timing] = []
        if policy in self._policies[command_class][timing]:
            raise exc.InitializationServiceError(
                f"Policy {policy} already registered for command class {command_class} and timing {timing}"
            )
        self._policies[command_class][timing].append(policy)

    def unregister_policy(
        self,
        command_class: Type[model.Command],
        policy: model.Policy,
        timing: EventTiming | None = None,
    ) -> None:
        """
        Unregister a policy for a command class and timing (all timings if None).
        """
        if command_class not in self._policies:
            raise exc.InitializationServiceError(
                f"No policies registered for command class {command_class}"
            )
        if timing is not None:
            if timing not in self._policies[command_class]:
                raise exc.InitializationServiceError(
                    f"No policies registered for command class {command_class} and timing {timing}"
                )
            if policy not in self._policies[command_class][timing]:
                raise exc.InitializationServiceError(
                    f"Policy {policy} not registered for command class {command_class} and timing {timing}"
                )
            self._policies[command_class][timing].remove(policy)
        else:
            has_policy = False
            for timing in self._policies[command_class]:
                if policy in self._policies[command_class][timing]:
                    has_policy = True
                    self._policies[command_class][timing].remove(policy)
            if not has_policy:
                raise exc.InitializationServiceError(
                    f"Policy {policy} not registered for command class {command_class}, any timing"
                )

    def get_policies(
        self, command_class: Type[model.Command], timing: EventTiming
    ) -> list[model.Policy]:
        """
        Get all policies registered for a command class and timing. The list is a copy.
        """
        return list(self._policies.get(command_class, {}).get(timing, []))

    def apply(
        self, cmd: model.Command, timing: EventTiming, retval: Any | None = None
    ) -> Any | None:
        """
        Apply policies for a command class and timing.
        In case of BEFORE, raise unauthorized error if any policy denies the command.
        In case of DURING, add policies to command so that they can be used during command execution.
        In case of AFTER, filter the return value with each policy and return it.
        """
        policies = self.get_policies(type(cmd), timing)
        if not policies:
            return retval if timing == EventTiming.AFTER else None
        if timing == EventTiming.BEFORE:
            for policy in policies:
                if not policy.is_allowed(cmd):
                    raise policy.get_is_denied_exception()(
                        f"Policy {policy.__class__.__name__} denied {cmd.__class__.__name__} command {cmd}"
                    )
            return None
        elif timing == EventTiming.DURING:
            # Add policies to command so that they can be used during command execution
            cmd._policies.extend(policies)
            return None
        elif timing == EventTiming.AFTER:
            # Execute policies that may alter the return value
            for policy in policies:
                retval = policy.filter(cmd, retval)
            return retval
