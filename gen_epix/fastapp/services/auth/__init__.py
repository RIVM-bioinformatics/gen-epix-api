# pylint: disable=useless-import-alias
from gen_epix.fastapp.services.auth.base import \
    BaseAuthService as BaseAuthService
from gen_epix.fastapp.services.auth.command import \
    GetIdentityProvidersCommand as GetIdentityProvidersCommand
from gen_epix.fastapp.services.auth.idp_client import IdpClient as IdpClient
from gen_epix.fastapp.services.auth.literal import \
    EMAIL_PATTERN as EMAIL_PATTERN
from gen_epix.fastapp.services.auth.mock_idp_client import \
    MockIDPClient as MockIDPClient
from gen_epix.fastapp.services.auth.model import Claims as Claims
from gen_epix.fastapp.services.auth.model import \
    IdentityProvider as IdentityProvider
from gen_epix.fastapp.services.auth.model import IDPUser as IDPUser
from gen_epix.fastapp.services.auth.model import OidcServerCfg as OidcServerCfg
from gen_epix.fastapp.services.auth.oauth_idp_client import \
    OauthIdpClient as OauthIdpClient
from gen_epix.fastapp.services.auth.service import AuthService as AuthService
from gen_epix.fastapp.services.auth.util import \
    get_email_from_claims as get_email_from_claims
