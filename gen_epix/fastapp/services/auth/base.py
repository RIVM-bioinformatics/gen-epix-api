import abc

from gen_epix.fastapp import BaseService
from gen_epix.fastapp.services.auth import model
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand


class BaseAuthService(BaseService):
    def register_handlers(self) -> None:
        self.app.register_handler(
            GetIdentityProvidersCommand, self.get_identity_providers
        )

    @abc.abstractmethod
    def get_identity_providers(
        self,
        cmd: GetIdentityProvidersCommand,
    ) -> list[model.IdentityProvider]:
        raise NotImplementedError
