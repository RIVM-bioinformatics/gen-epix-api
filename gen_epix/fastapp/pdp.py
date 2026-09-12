"""Policy decision point abstractions and policy evaluation results."""

from typing import Any

from gen_epix.fastapp import exc, model
from gen_epix.fastapp.enum import EventTiming


class PolicyDecisionPoint:
    """
    Encapsulates a policy Decision Point (PDP). This is the central point where policies are
    registered and applied. They are executed in order of registration.

    Policies must be registered for a particular command and timing (BEFORE, DURING
    or AFTER) of execution:
    - BEFORE: raise UnauthorizedAuthorityError if any policy denies the command.
    - DURING: add policies to command so that they can be used during command execution.
    - AFTER: filter the return value with each policy and return it.
    """

    def __init__(self) -> None:
        """Initialize a PolicyDecisionPoint instance."""
        self._policies: dict[
            type[model.Command], dict[EventTiming, list[model.Policy]]
        ] = {}

    def register_policy(
        self,
        command_class: type[model.Command],
        policy: model.Policy,
        timing: EventTiming = EventTiming.BEFORE,
    ) -> None:
        """Register a policy for one command class and lifecycle timing.

        Policies run in registration order. BEFORE policies authorize, DURING
        policies are attached to the command, and AFTER policies filter its result.

        Args:
            command_class: Command class to which the policy applies.
            policy: Policy instance to register.
            timing: Lifecycle phase at which the policy is evaluated.

        Raises:
            InitializationServiceError: If the policy is already registered for the
                command class and timing.
        """
        if command_class not in self._policies:
            self._policies[command_class] = {}
        if timing not in self._policies[command_class]:
            self._policies[command_class][timing] = []
        if policy in self._policies[command_class][timing]:
            raise exc.InitializationServiceError(
                "96738faa",
                f"Policy {policy} already registered for command class {command_class} and timing {timing}",
            )
        self._policies[command_class][timing].append(policy)

    def unregister_policy(
        self,
        command_class: type[model.Command],
        policy: model.Policy,
        timing: EventTiming | None = None,
    ) -> None:
        """Remove a registered policy from one or all lifecycle timings.

        Args:
            command_class: Command class associated with the policy.
            policy: Policy instance to remove.
            timing: Specific lifecycle timing, or all timings when omitted.

        Raises:
            InitializationServiceError: If no policy registration matches the supplied
                command class, policy, and timing.
        """
        if command_class not in self._policies:
            raise exc.InitializationServiceError(
                "380afa27", f"No policies registered for command class {command_class}"
            )
        if timing is not None:
            if timing not in self._policies[command_class]:
                raise exc.InitializationServiceError(
                    "9ca24301",
                    f"No policies registered for command class {command_class} and timing {timing}",
                )
            if policy not in self._policies[command_class][timing]:
                raise exc.InitializationServiceError(
                    "52274845",
                    f"Policy {policy} not registered for command class {command_class} and timing {timing}",
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
                    "8674aea7",
                    f"Policy {policy} not registered for command class {command_class}, any timing",
                )

    def get_policies(
        self, command_class: type[model.Command], timing: EventTiming
    ) -> list[model.Policy]:
        """Get all policies registered for a command class and timing. The list is a copy."""
        return list(self._policies.get(command_class, {}).get(timing, []))

    def apply(
        self, cmd: model.Command, timing: EventTiming, retval: Any | None = None
    ) -> Any | None:
        """Apply policies for a command at one lifecycle phase.

        BEFORE policies authorize the command, DURING policies are attached to it,
        and AFTER policies successively filter the handler result.

        Args:
            cmd: Command to authorize, annotate, or whose result to filter.
            timing: Lifecycle phase whose policies should run.
            retval: Handler result passed through AFTER policies.

        Returns:
            Filtered result for AFTER policies; otherwise ``None``.

        Raises:
            UnauthorizedAuthError: If a BEFORE policy denies the command.
        """
        policies = self.get_policies(type(cmd), timing)
        if not policies:
            return retval if timing == EventTiming.AFTER else None
        if timing == EventTiming.BEFORE:
            for policy in policies:
                if not policy.is_allowed(cmd):
                    raise policy.get_is_denied_exception()(
                        f"Policy {policy.__class__.__name__} denied"
                        f" {cmd.__class__.__name__} command {cmd.id}"
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
