import time
from typing import Type

from cachetools import TTLCache, cached

from gen_epix.common.domain import command, exc, model
from gen_epix.common.domain.policy.system import BaseHasSystemOutagePolicy
from gen_epix.fastapp import Command, CrudOperation


class HasSystemOutagePolicy(BaseHasSystemOutagePolicy):
    def is_allowed(self, cmd: Command) -> bool:
        if isinstance(cmd, command.OutageCrudCommand):
            return True
        if self._is_allowed():
            return True
        if not cmd.user:
            return True
        assert cmd.user.id
        return self._is_permitted(cmd.user)  # type: ignore[arg-type]

    def get_is_denied_exception(self) -> Type[Exception]:
        return exc.ServiceUnavailableError

    @cached(cache=TTLCache(maxsize=100, ttl=100))
    def _is_permitted(self, tgt_user: model.User) -> bool:
        return (
            self.outage_update_permission
            in self.system_service.app.user_manager.retrieve_user_permissions(tgt_user)  # type: ignore[arg-type]
        )

    @cached(cache=TTLCache(maxsize=10, ttl=10))
    def _is_allowed(self) -> bool:
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
