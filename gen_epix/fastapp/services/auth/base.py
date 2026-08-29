"""Base authentication service contract."""

import abc

from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.services.auth import model
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand


class BaseAuthService(BaseService):
    """Provide the base auth service framework abstraction."""

    def register_handlers(self) -> None:
        """Perform the register handlers operation."""
        self.app.register_handler(
            GetIdentityProvidersCommand, self.get_identity_providers
        )

    @abc.abstractmethod
    def get_identity_providers(
        self,
        cmd: GetIdentityProvidersCommand,
    ) -> list[model.IdentityProvider]:
        """Retrieve a list of available identity providers for authentication."""
        raise NotImplementedError()
