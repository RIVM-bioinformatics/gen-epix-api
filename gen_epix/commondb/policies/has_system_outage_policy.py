"""Restrict commondb commands during active system outages."""

import time
from typing import ClassVar

from cachetools import TTLCache, cached

from gen_epix.commondb.domain import command, exc, model
from gen_epix.commondb.domain.policy.system import BaseHasSystemOutagePolicy
from gen_epix.fastapp import Command, CrudOperation


class HasSystemOutagePolicy(BaseHasSystemOutagePolicy):
    """Encapsulates outage administration while restricting requests during active outages."""

    _IS_PERMITTED_CACHE: ClassVar[TTLCache] = TTLCache(maxsize=100, ttl=100)
    _IS_ALLOWED_CACHE: ClassVar[TTLCache] = TTLCache(maxsize=10, ttl=10)

    def is_allowed(self, cmd: Command) -> bool:
        """Determine whether a command may proceed under the current outage state.

        Outage CRUD commands, unauthenticated commands, and users with the configured
        outage-update permission remain allowed.

        Args:
            cmd: Command being evaluated by the policy lifecycle.

        Returns:
            True when the command is allowed during the current outage state.
        """
        if isinstance(cmd, command.OutageCrudCommand):
            return True
        if self._is_allowed():
            return True
        if not cmd.user:
            return True
        assert cmd.user.id
        return self._is_permitted(cmd.user)  # type: ignore[arg-type]

    def get_is_denied_exception(self) -> type[Exception]:
        """Return the exception type used when an outage denies a command.

        Returns:
            ServiceUnavailableError, indicating that service is temporarily unavailable.
        """
        return exc.ServiceUnavailableError

    @cached(cache=_IS_PERMITTED_CACHE, key=lambda self, tgt_user: tgt_user.id)
    def _is_permitted(self, tgt_user: model.User) -> bool:
        """Determine whether a user has permission to administer an outage.

        Args:
            tgt_user: User whose permissions are checked.

        Returns:
            True when the user holds the configured outage-update permission.
        """
        return (
            self.outage_update_permission
            in self.system_service.app.user_manager.retrieve_user_permissions(tgt_user)
        )

    @cached(cache=_IS_ALLOWED_CACHE)
    def _is_allowed(self) -> bool:
        """Determine whether no active outage currently restricts requests.

        Returns:
            True when no persisted outage is active in the current time window.
        """
        outages: list[model.Outage] = self.system_service.crud(  # type: ignore[assignment]
            command.OutageCrudCommand(
                user=None,
                operation=CrudOperation.READ_ALL,
            )
        )
        now = time.time()

        has_outage = any(
            x.is_active
            or (
                (x.active_from or x.active_to)
                and (
                    (x.active_from and x.active_from.timestamp() <= now)
                    or (x.active_to and x.active_to.timestamp() > now)
                )
            )
            for x in outages
        )
        return not has_outage
