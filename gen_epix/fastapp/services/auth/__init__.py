"""Public authentication services, commands, clients, and identity models.

The package re-exports the authentication service contract and implementation,
the command for listing identity providers, provider clients for mock and OAuth
flows, identity-provider configuration and claims models, and helpers for
extracting validated identity data. These symbols support application
composition without exposing the authentication package's internal layout.
"""

# pylint: disable=useless-import-alias
from typing import TYPE_CHECKING

from gen_epix._lazy import LazyExport, exports_from, lazy_exports
from gen_epix.fastapp.services.auth.base import BaseAuthService as BaseAuthService
from gen_epix.fastapp.services.auth.command import (
    GetIdentityProvidersCommand as GetIdentityProvidersCommand,
)
from gen_epix.fastapp.services.auth.literal import EMAIL_PATTERN as EMAIL_PATTERN
from gen_epix.fastapp.services.auth.model import Claims as Claims
from gen_epix.fastapp.services.auth.model import IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth.model import IDPUser as IDPUser
from gen_epix.fastapp.services.auth.model import OidcServerCfg as OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_token_client import (
    OauthTokenClient as OauthTokenClient,
)
from gen_epix.fastapp.services.auth.util import (
    get_email_from_claims as get_email_from_claims,
)

if TYPE_CHECKING:
    from gen_epix.fastapp.services.auth.idp_client import IdpClient as IdpClient
    from gen_epix.fastapp.services.auth.mock_idp_client import (
        MockIDPClient as MockIDPClient,
    )
    from gen_epix.fastapp.services.auth.oauth_idp_client import (
        OauthIdpClient as OauthIdpClient,
    )
    from gen_epix.fastapp.services.auth.service import AuthService as AuthService

# The server-side classes depend on FastAPI and are resolved on first access,
# so that clients can use the models and token retrieval without FastAPI installed
_LAZY_EXPORTS: dict[str, LazyExport] = {
    **exports_from("gen_epix.fastapp.services.auth.idp_client", "IdpClient"),
    **exports_from("gen_epix.fastapp.services.auth.mock_idp_client", "MockIDPClient"),
    **exports_from("gen_epix.fastapp.services.auth.oauth_idp_client", "OauthIdpClient"),
    **exports_from("gen_epix.fastapp.services.auth.service", "AuthService"),
}

if not TYPE_CHECKING:
    # Not visible to type checkers, which would otherwise accept any attribute
    __getattr__, __dir__ = lazy_exports(__name__, _LAZY_EXPORTS)
