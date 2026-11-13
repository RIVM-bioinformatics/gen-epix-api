from test.util.mock_compat import Mock

from gen_epix.fastapp import App
from gen_epix.fastapp.services.auth.base import BaseAuthService
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand


def test_register_handlers_registers_identity_provider_command() -> None:
    service = Mock(spec=BaseAuthService)
    service.app = Mock(spec=App)

    BaseAuthService.register_handlers(service)

    service.app.register_handler.assert_called_once_with(
        GetIdentityProvidersCommand, service.get_identity_providers
    )
