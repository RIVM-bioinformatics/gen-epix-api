import logging
import ssl
import threading
import time
from collections.abc import Callable
from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Request, Security
from fastapi.security import SecurityScopes

from gen_epix.fastapp import App, enum, exc, model
from gen_epix.fastapp.services.auth.base import BaseAuthService
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand
from gen_epix.fastapp.services.auth.idp_client import IdpClient
from gen_epix.fastapp.services.auth.mock_idp_client import MockIDPClient
from gen_epix.fastapp.services.auth.model import (
    Claims,
    IdentityProvider,
    IDPUser,
    OidcServerCfg,
)
from gen_epix.fastapp.services.auth.oauth_idp_client import OauthIdpClient
from gen_epix.fastapp.user_manager import BaseUserManager


class AuthService(BaseAuthService):

    DEFAULT_IS_PUBLIC_IDP = False  # Security: IDPs are not public by default
    DEFAULT_ROOT_TOKEN_TIME_TO_LIVE = (
        15 * 60
    )  # 15 minutes, to mitigate risk of leaked root tokens being used by attackers

    _MAX_N_IDP_CLIENTS = 5  # Maximum currently supported number of IDP clients, can be increased if needed but requires code changes

    def __init__(
        self,
        app: App,
        auto_create_new_users: bool = False,
        root_token_time_to_live: (
            int | None
        ) = None,  # None will set the default, negative value or zero will disable root token expiration
        logger: logging.Logger | None = None,
        setup_logger: logging.Logger | None = None,
        idps_cfg: list[dict[str, str | list]] | None = None,
        ssl_context: ssl.SSLContext | bool = True,
        repository: None = None,
        **kwargs: Any,
    ):
        super().__init__(
            app,
            repository=repository,
            logger=logger,
            setup_logger=setup_logger,
            **kwargs,
        )

        # Initialize authentication services
        self._idp_client_by_id: dict[UUID, IdpClient] = {}
        self._idp_client_by_name: dict[str, IdpClient] = {}
        self._idp_clients: list[IdpClient] = []
        self._exposed_idp_clients: list[IdpClient] = []
        self._no_auth_user: model.User
        self._no_auth_idp_client: IdpClient = MockIDPClient(logger=logger)
        self._pending_idp_client_cfgs: list[dict[str, str | list]] = []
        self._pending_idp_clients_lock = threading.Lock()
        self._init_idp_clients(app, idps_cfg, ssl_context)

        # Parse and set auto_create_new_users, and expose as feature flag
        self._auto_create_new_users = auto_create_new_users
        self.app.set_feature_flag("auto_create_new_users", auto_create_new_users)

        # Parse and set root_token_time_to_live
        if root_token_time_to_live is not None and root_token_time_to_live <= 0:
            # Root token expiration disabled, log this decision because it has security implications
            self._root_token_time_to_live = None
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "d1cbb7e8",
                        "Root token expiration disabled by configuration, ensure this is an intentional decision due to security implications",
                    )
                )
        else:
            self._root_token_time_to_live = (
                root_token_time_to_live or self.DEFAULT_ROOT_TOKEN_TIME_TO_LIVE
            )

    @property
    def idp_clients(self) -> list[IdpClient]:
        return list(self._idp_clients)

    async def get_existing_user_from_token(self, token: str) -> model.User | None:
        """Get existing user based on provided token,
        return None if token is invalid or user does not exist"""
        for idp_client in self._idp_clients:
            jwt_claims = await idp_client.get_claims_from_jwt(token)
            if jwt_claims:
                try:
                    claims = Claims(
                        claims=jwt_claims,
                        scheme="BEARER",
                        token=token,
                        idp_client_id=idp_client.id,
                    )
                    user = await self.get_existing_user_from_claims(claims)
                    # If root token time to live is configured, verify that the token is not too old if the user is a root user, to mitigate risk of leaked root tokens being used by attackers
                    if self._root_token_time_to_live is not None:
                        self._verify_root_user_for_token_time_to_live(claims, user)
                    return user
                except exc.UnauthorizedAuthError:
                    continue
        # No valid user found for any of the IDP clients
        raise exc.UnauthorizedAuthError("665ae487")

    def create_user_dependencies(
        self,
    ) -> tuple[model.User, model.User, IDPUser]:

        if not self._idp_clients:
            # No authentication -> create/retrieve root user
            return self._create_no_auth_dependencies()

        # Init get_current_user function definition and environment
        # TODO: generate get_current_user and get_new_user functions
        # dynamically based on number of authentication services
        n_idp_clients = len(self._idp_clients)
        if self._logger:
            self._logger.info(
                self.create_log_message(
                    "1e3d75cb",
                    "Generating user authentication function per security base",
                )
            )

        if n_idp_clients > self._MAX_N_IDP_CLIENTS:
            msg = (
                f"Number of configured IDP clients ({n_idp_clients}) exceeds "
                f"maximum supported number ({self._MAX_N_IDP_CLIENTS})"
            )
            if self._logger:
                self._logger.error(self.create_log_message("ba1e6d14", msg))
            raise exc.InitializationServiceError("194759ad", msg)
        idp_client_list = self._idp_clients + (
            [None] * (self._MAX_N_IDP_CLIENTS - n_idp_clients)
        )

        async def get_current_user1(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
        ) -> model.User:
            if claims_0:
                return await self.get_existing_user_from_claims(claims_0)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("93e20d00")

        async def get_new_user1(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
        ) -> model.User:
            if claims_0:
                return await self.get_new_user_from_claims(claims_0)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("0bc81b09")

        async def get_idp_user1(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
        ) -> IDPUser:
            if claims_0:
                return await self.get_idp_user_from_claims(claims_0)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("94254114")

        async def get_current_user2(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
        ) -> model.User:
            if claims_0:
                return await self.get_existing_user_from_claims(claims_0)
            if claims_1:
                return await self.get_existing_user_from_claims(claims_1)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("45a21268")

        async def get_new_user2(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
        ) -> model.User:
            if claims_0:
                return await self.get_new_user_from_claims(claims_0)
            if claims_1:
                return await self.get_new_user_from_claims(claims_1)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("55fcd25b")

        async def get_idp_user2(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
        ) -> IDPUser:
            if claims_0:
                return await self.get_idp_user_from_claims(claims_0)
            if claims_1:
                return await self.get_idp_user_from_claims(claims_1)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("6f9e825f")

        async def get_current_user3(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
        ) -> model.User:
            if claims_0:
                return await self.get_existing_user_from_claims(claims_0)
            if claims_1:
                return await self.get_existing_user_from_claims(claims_1)
            if claims_2:
                return await self.get_existing_user_from_claims(claims_2)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("5c471bf9")

        async def get_new_user3(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
        ) -> model.User:
            if claims_0:
                return await self.get_new_user_from_claims(claims_0)
            if claims_1:
                return await self.get_new_user_from_claims(claims_1)
            if claims_2:
                return await self.get_new_user_from_claims(claims_2)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("2cc43625")

        async def get_idp_user3(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
        ) -> IDPUser:
            if claims_0:
                return await self.get_idp_user_from_claims(claims_0)
            if claims_1:
                return await self.get_idp_user_from_claims(claims_1)
            if claims_2:
                return await self.get_idp_user_from_claims(claims_2)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("5b18f27e")

        async def get_current_user4(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
            claims_3: Claims = Depends(idp_client_list[3]),
        ) -> model.User:
            if claims_0:
                return await self.get_existing_user_from_claims(claims_0)
            if claims_1:
                return await self.get_existing_user_from_claims(claims_1)
            if claims_2:
                return await self.get_existing_user_from_claims(claims_2)
            if claims_3:
                return await self.get_existing_user_from_claims(claims_3)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("ee9803d2")

        async def get_new_user4(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
            claims_3: Claims = Depends(idp_client_list[3]),
        ) -> model.User:
            if claims_0:
                return await self.get_new_user_from_claims(claims_0)
            if claims_1:
                return await self.get_new_user_from_claims(claims_1)
            if claims_2:
                return await self.get_new_user_from_claims(claims_2)
            if claims_3:
                return await self.get_new_user_from_claims(claims_3)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("8bcef011")

        async def get_idp_user4(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
            claims_3: Claims = Depends(idp_client_list[3]),
        ) -> IDPUser:
            if claims_0:
                return await self.get_idp_user_from_claims(claims_0)
            if claims_1:
                return await self.get_idp_user_from_claims(claims_1)
            if claims_2:
                return await self.get_idp_user_from_claims(claims_2)
            if claims_3:
                return await self.get_idp_user_from_claims(claims_3)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("4c7b18ec")

        async def get_current_user5(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
            claims_3: Claims = Depends(idp_client_list[3]),
            claims_4: Claims = Depends(idp_client_list[4]),
        ) -> model.User:
            if claims_0:
                return await self.get_existing_user_from_claims(claims_0)
            if claims_1:
                return await self.get_existing_user_from_claims(claims_1)
            if claims_2:
                return await self.get_existing_user_from_claims(claims_2)
            if claims_3:
                return await self.get_existing_user_from_claims(claims_3)
            if claims_4:
                return await self.get_existing_user_from_claims(claims_4)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("af2370e8")

        async def get_new_user5(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
            claims_3: Claims = Depends(idp_client_list[3]),
            claims_4: Claims = Depends(idp_client_list[4]),
        ) -> model.User:
            if claims_0:
                return await self.get_new_user_from_claims(claims_0)
            if claims_1:
                return await self.get_new_user_from_claims(claims_1)
            if claims_2:
                return await self.get_new_user_from_claims(claims_2)
            if claims_3:
                return await self.get_new_user_from_claims(claims_3)
            if claims_4:
                return await self.get_new_user_from_claims(claims_4)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("d4a829df")

        async def get_idp_user5(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
            claims_1: Claims = Depends(idp_client_list[1]),
            claims_2: Claims = Depends(idp_client_list[2]),
            claims_3: Claims = Depends(idp_client_list[3]),
            claims_4: Claims = Depends(idp_client_list[4]),
        ) -> IDPUser:
            if claims_0:
                return await self.get_idp_user_from_claims(claims_0)
            if claims_1:
                return await self.get_idp_user_from_claims(claims_1)
            if claims_2:
                return await self.get_idp_user_from_claims(claims_2)
            if claims_3:
                return await self.get_idp_user_from_claims(claims_3)
            if claims_4:
                return await self.get_idp_user_from_claims(claims_4)
            self._warn_too_many_idps(request)
            raise exc.UnauthorizedAuthError("be1b8ad7")

        get_idp_user_functions = [
            get_idp_user1,
            get_idp_user2,
            get_idp_user3,
            get_idp_user4,
            get_idp_user5,
        ]
        get_current_user_functions = [
            get_current_user1,
            get_current_user2,
            get_current_user3,
            get_current_user4,
            get_current_user5,
        ]
        get_new_user_functions = [
            get_new_user1,
            get_new_user2,
            get_new_user3,
            get_new_user4,
            get_new_user5,
        ]

        # Create CurrentUser/NewUser, injecting get_current_user/get_new_user
        return self._create_user_dependencies_from_callables(
            n_idp_clients,
            get_idp_user_functions,
            get_current_user_functions,
            get_new_user_functions,
        )

    def _create_no_auth_dependencies(self) -> tuple[model.User, model.User, IDPUser]:
        user_manager = self.app.user_manager
        if not user_manager:
            raise exc.InitializationServiceError(
                "b44906d1",
                "No authentication services configured and no user generator provided",
            )
        self._no_auth_user = user_manager.create_root_user_from_claims({})

        async def dummy_get_existing_user(
            request: Request, _security_scopes: SecurityScopes
        ) -> model.User:
            claims = await self._no_auth_idp_client(request)
            if claims:
                user = await self.get_existing_user_from_claims(
                    claims, request_userinfo=False
                )
                if user:
                    return user
            return self._no_auth_user

        async def dummy_get_new_user(
            request: Request, _security_scopes: SecurityScopes
        ) -> model.User:
            claims = await self._no_auth_idp_client(request)
            if claims:
                user = await self.get_new_user_from_claims(
                    claims, request_userinfo=False
                )
                if user:
                    return user
            raise exc.UnauthorizedAuthError(
                "05dcbc82", "Unable to create user due to missing header or claims"
            )

        registered_user_dependency: model.User = Annotated[  # type: ignore
            model.User,
            Security(dummy_get_existing_user, scopes=["openid", "profile"]),
        ]
        new_user_dependency: model.User = Annotated[  # type: ignore
            model.User,
            Security(dummy_get_new_user, scopes=["openid", "profile"]),
        ]
        idp_user_dependency: IDPUser = Annotated[  # type: ignore
            IDPUser,
            Security(dummy_get_new_user, scopes=["openid", "profile"]),
        ]

        return registered_user_dependency, new_user_dependency, idp_user_dependency

    def _warn_too_many_idps(self, request: Request) -> None:
        if self._logger:
            self._logger.warning(
                self.create_log_message(
                    "f8853e9e",
                    "Unable to verify provided user",
                    request=request,
                )
            )

    def _create_user_dependencies_from_callables(
        self,
        n_idp_clients: int,
        get_idp_user_functions: list[Callable],
        get_current_user_functions: list[Callable],
        get_new_user_functions: list[Callable],
    ) -> tuple[model.User, model.User, IDPUser]:
        if n_idp_clients > len(get_current_user_functions):
            msg = (
                f"More than {len(get_current_user_functions)} "
                f"({n_idp_clients}) not implemented"
            )
            if self._logger:
                self._logger.error(self.create_log_message("d6f4ede7", msg))
            raise exc.InitializationServiceError("7341942b", msg)
        registered_user_dependency: model.User = Annotated[  # type: ignore
            model.User,
            Security(
                get_current_user_functions[n_idp_clients - 1],
                scopes=["openid", "profile"],
            ),
        ]
        new_user_dependency: model.User = Annotated[  # type: ignore
            model.User,
            Security(
                get_new_user_functions[n_idp_clients - 1],
                scopes=["openid", "profile"],
            ),
        ]
        idp_user_dependency: IDPUser = Annotated[  # type: ignore
            IDPUser,
            Security(
                get_idp_user_functions[n_idp_clients - 1],
                scopes=["openid", "profile"],
            ),
        ]

        return registered_user_dependency, new_user_dependency, idp_user_dependency

    def get_identity_providers(
        self,
        cmd: GetIdentityProvidersCommand,
    ) -> list[IdentityProvider]:
        try:
            self._retry_pending_idp_clients()
        except Exception as e:
            # ensure this call never raises because of IDP initialization attempts
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "b2c6a1d4",
                        "Unexpected error while retrying pending IDPs",
                        exception=e,
                    )
                )
        identity_providers = [x.get_identity_provider() for x in self._idp_clients]
        if cmd.public:
            return [x for x in identity_providers if x.public]
        return identity_providers

    async def get_idp_user_from_claims(self, claims: Claims) -> IDPUser:
        claims_dict = claims.claims
        issuer: str = claims_dict["iss"]  # type: ignore
        sub: str = claims_dict["sub"]  # type: ignore

        return IDPUser(issuer=issuer, sub=sub)

    async def get_new_user_from_claims(
        self, claims: Claims, request_userinfo: bool = True
    ) -> model.User:
        # Get userinfo
        if request_userinfo:
            claims.claims.update(
                self._idp_client_by_id[claims.idp_client_id].get_claims_from_userinfo(
                    claims.token
                )
            )
        # Create user obj
        user_manager = self.app.user_manager
        if user_manager:
            # Use user manager to create user
            new_user = user_manager.construct_user_instance_from_claims(claims.claims)
            if new_user is None:
                if self._logger:
                    self._logger.warning(
                        self.create_log_message(
                            "c1e4f2b3",
                            "User manager could not create user from claims",
                            claim_keys=sorted(list(claims.claims.keys())),
                        )
                    )
                raise exc.UnauthorizedAuthError(
                    "1dabe07d", "Unable to create user from claims"
                )
        else:
            # No user manager configured, create user obj directly from claims
            new_user = model.User(**claims.claims)  # type: ignore
        return new_user

    def _verify_root_user_for_token_time_to_live(
        self, claims: Claims, user: model.User
    ) -> None:
        """
        Verify that if the user is a root user, the token is not too old based on the
        configured root token time to live, to mitigate risk of leaked root tokens
        being used by attackers.
        """
        if not self._root_token_time_to_live:
            # No root token time to live configured, no need to verify
            return
        if not self.app.user_manager.is_root_user(user):
            # Not a root user, no need to verify
            return
        token_iat: int = claims.claims.get("iat", 0)
        if (
            token_iat == 0
            or int(time.time()) - token_iat <= self._root_token_time_to_live
        ):
            # Token is not too old, allow authentication
            return
        # Token is too old, log and reject authentication
        if self._logger:
            self._logger.warning(
                self.create_log_message(
                    "548f1e15",
                    "Root token lifetime longer than root token max time to live, rejecting authentication",
                    token_iat=token_iat,
                )
            )
        raise exc.UnauthorizedAuthError(
            "bb487982",
            f"Root tokens must have a lifetime of less than {self._root_token_time_to_live} seconds",
        )

    async def get_existing_user_from_claims(
        self, claims: Claims, request_userinfo: bool = True
    ) -> model.User:
        issuer: str = claims.claims["iss"]  # type: ignore
        sub: str = claims.claims["sub"]  # type: ignore
        user_manager: BaseUserManager = self.app.user_manager
        user_key = self._generate_user_key_from_claims(
            claims, request_userinfo, sub, user_manager
        )
        user: model.User = None
        try:
            # Retrieve existing user
            user = user_manager.retrieve_user_by_key(user_key)
            try:
                # Retrieve user name from claims and update if necessary
                new_user_name = user_manager.get_user_name_from_claims(claims.claims)
                if new_user_name:
                    updated_user = user_manager.update_user_name(user, new_user_name)
                    if updated_user:
                        user = updated_user
            except exc.DomainException as exception:
                if self._logger:
                    self._logger.error(
                        self.create_log_message(
                            "a7d93f8c",
                            "Failed to update user name from claims",
                            issuer=issuer,
                            sub=sub,
                            user_key=user_key,
                            exception=exception,
                        )
                    )
            self._verify_root_user_for_token_time_to_live(claims, user)

            return user

        except exc.NoResultsError:
            # User does not exist
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "ec9625ad",
                        "User not found",
                        issuer=issuer,
                        sub=sub,
                        user_key=user_key,
                    )
                )

            # Check if this is the root user, if so create it and and its dependencies
            if user_manager.is_root_user_claims(claims.claims):
                if self._logger:
                    self._logger.warning(
                        self.create_log_message(
                            "d4f37b85",
                            "User is root user, creating",
                            issuer=issuer,
                            sub=sub,
                            user_key=user_key,
                        )
                    )
                return user_manager.create_root_user_from_claims(claims.claims)

            # Auto-create the user if configured
            if self._auto_create_new_users:
                return self._auto_create_new_user(
                    claims, issuer, sub, user_manager, user_key
                )

            raise exc.UnauthorizedAuthError(
                "f14da79c", "User does not exist and auto-creation is disabled"
            )

    def _auto_create_new_user(
        self,
        claims: Claims,
        issuer: str,
        sub: str,
        user_manager: BaseUserManager,
        user_key: str,
    ) -> model.User:
        try:
            user = user_manager.auto_create_new_user(claims.claims)
            if user is None:
                raise exc.UnauthorizedAuthError(
                    "61a09279", "Failed to auto-create user from claims"
                )
            if self._logger:
                self._logger.info(
                    self.create_log_message(
                        "fe8bfbd0",
                        "Auto-created user",
                        issuer=issuer,
                        sub=sub,
                        user_key=user_key,
                    )
                )
            return user
        except Exception as exception:
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "08e3c18b",
                        "Could not auto-create user",
                        issuer=issuer,
                        sub=sub,
                        user_key=user_key,
                        exception=exception,
                    )
                )
            raise exc.UnauthorizedAuthError(
                "daa7920f", "Failed to auto-create user from claims"
            )

    def _generate_user_key_from_claims(
        self,
        claims: Claims,
        request_userinfo: bool,
        sub: str,
        user_manager: BaseUserManager | None,
    ) -> str:
        if not user_manager:
            # No user generator configured
            raise exc.UnauthorizedAuthError("cd3d76d6")

        user_key = user_manager.get_user_key_from_claims(claims.claims)
        if not user_key and request_userinfo:
            claims.claims.update(
                self._idp_client_by_id[claims.idp_client_id].get_claims_from_userinfo(
                    claims.token
                )
            )
            user_key = user_manager.get_user_key_from_claims(claims.claims)
        if not user_key:
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "d3b7e9f1",
                        "No user key found in claims",
                        sub=sub,
                        user_key=user_key,
                    )
                )
            raise exc.UnauthorizedAuthError("fd116007")
        return user_key

    def _init_idp_client(
        self, idp_cfg: dict[str, str | list], ssl_context: ssl.SSLContext | bool = True
    ) -> IdpClient | None:
        """
        Try to initialize a single IDP client from its configuration.
        If unsuccessful, log and return None.
        """
        try:
            protocol = enum.AuthProtocol[str(idp_cfg["protocol"])]
            if protocol == enum.AuthProtocol.OIDC:
                # TODO: only select actual discovery doc keys, should be class variable of OidcServerCfg containing a set of property names
                discovery_doc = {
                    x: y
                    for x, y in idp_cfg.items()
                    if x in set(OidcServerCfg.model_fields.keys())
                }
                idp_client = OauthIdpClient(
                    OidcServerCfg(**idp_cfg),  # type: ignore
                    logger=self._logger,
                    log_item_class=self.app.log_item_class,
                    discovery_doc=discovery_doc,
                    ssl_context=idp_cfg.get("ssl_context", ssl_context),  # type: ignore
                )
                return idp_client
            else:
                raise NotImplementedError(
                    f"Initialization of Protocol {protocol.value} not implemented"
                )
        except NotImplementedError as not_implemented_error:
            if self._logger:
                self._logger.error(
                    self.create_log_message(
                        "9f5b6c3e",
                        f"IDP {idp_cfg.get('name')} could not be initialized",
                        exception=not_implemented_error,
                    )
                )
            raise NotImplementedError from not_implemented_error
        except Exception as exception:
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "e2c6f4a5",
                        f"IDP {idp_cfg.get('name')} could not be initialized",
                        exception=exception,
                    )
                )
        return None

    def _init_idp_clients(
        self,
        app: App,
        idp_cfgs: list[dict[str, str | list]] | None,
        ssl_context: ssl.SSLContext | bool,
    ) -> None:
        # Parse input
        logger = app.logger
        if not idp_cfgs:
            idp_cfgs = []
        self._validate_idp_cfgs(app, idp_cfgs)
        # Try to initialize all IDP clients
        for idp_cfg in idp_cfgs:
            # Attempt to initialize IDP client
            idp_client = self._init_idp_client(idp_cfg, ssl_context=ssl_context)
            if not idp_client:
                # Initialization failed, add to pending list
                with self._pending_idp_clients_lock:
                    self._pending_idp_client_cfgs.append(idp_cfg)
                continue
            # Add initialized IDP client to lists and dicts
            idp_name: str = idp_cfg["name"]  # type: ignore[assignment]
            is_public: bool = idp_cfg.get("is_exposed", self.DEFAULT_IS_PUBLIC_IDP)  # type: ignore[assignment]
            self._idp_clients.append(idp_client)
            self._idp_client_by_id[idp_client.id] = idp_client
            self._idp_client_by_name[idp_name] = idp_client
            if is_public:
                self._exposed_idp_clients.append(idp_client)
            # Log successful initialization
            if logger:
                logger.info(
                    app.create_log_message(
                        "7e0b64cc",
                        f"IDP client {idp_name} initialized",
                    )
                )

    def _validate_idp_cfgs(
        self, app: App, idp_cfgs: list[dict[str, str | list]]
    ) -> None:
        """
        Verify non-unique names and labels in the provided IDP configurations and
        raise InitializationServiceError if duplicates are found
        """
        for key in ["name", "label"]:
            duplicate_values: set[str] = set()
            seen_values: set[str] = set()
            for x in idp_cfgs:
                value: str = x[key]  # type: ignore[assignment]
                if value in seen_values:
                    duplicate_values.add(value)
                else:
                    seen_values.add(value)
            if duplicate_values:
                duplicate_values_str = ", ".join(sorted(duplicate_values))
                msg = f"Authentication services do not have unique {key}: {duplicate_values_str}"
                if app.logger:
                    app.logger.error(app.create_log_message("d4e8f3b1", msg))
                raise exc.InitializationServiceError("85447b4a", msg)

    def _retry_pending_idp_clients(self) -> None:
        with self._pending_idp_clients_lock:
            if not self._pending_idp_client_cfgs:
                return
            retry_clients = list(self._pending_idp_client_cfgs)
        for idp_cfg in retry_clients:
            idp_name: str = idp_cfg["name"]  # type: ignore[assignment]
            # Avoid re-adding already existing clients
            # Remove lock and skip if in the meantime another thread initialized it
            if idp_name in self._idp_client_by_name:
                with self._pending_idp_clients_lock:
                    try:
                        self._pending_idp_client_cfgs.remove(idp_cfg)
                    except ValueError:
                        pass
                continue
            # Attempt to initialize IDP client
            idp_client = self._init_idp_client(idp_cfg)
            if not idp_client:
                # Could not be initialized
                continue
            # Add newly initialized client
            self._idp_clients.append(idp_client)
            self._idp_client_by_id[idp_client.id] = idp_client
            self._idp_client_by_name[idp_name] = idp_client
            is_public: bool = idp_cfg.get(
                "is_exposed", self.DEFAULT_IS_PUBLIC_IDP
            )  # type: ignore[assignment]
            if is_public:
                self._exposed_idp_clients.append(idp_client)
            # Remove lock
            with self._pending_idp_clients_lock:
                try:
                    self._pending_idp_client_cfgs.remove(idp_cfg)
                except ValueError:
                    pass
            # Log
            if self._logger:
                self._logger.info(
                    self.create_log_message(
                        "c3f4e2b1",
                        f"IDP {idp_cfg.get('name')} initialized after retry",
                    )
                )
