import logging
import ssl
import threading
from typing import Annotated, Any

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


class AuthService(BaseAuthService):

    DEFAULT_IS_PUBLIC_IDP = False  # Security: IDPs are not public by default

    def __init__(
        self,
        app: App,
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
        self._pending_idp_clients: list[dict[str, str | list]] = []
        self._pending_lock = threading.Lock()

        self._init_idp_clients(app, idps_cfg, ssl_context)
        self._idp_client_by_id = {x.id: x for x in self._idp_clients or []}

        # Initialize no authentication user
        self._no_auth_user: model.User
        self._no_auth_idp_client: IdpClient = MockIDPClient(logger=logger)

    @property
    def idp_clients(self) -> list[IdpClient]:
        return list(self._idp_clients)

    async def get_existing_user_from_token(self, token: str) -> model.User | None:
        for idp_client in self._idp_clients:
            jwt_claims = await idp_client.get_claims_from_jwt(token)
            if jwt_claims:
                try:
                    user = await self.get_existing_user_from_claims(
                        Claims(
                            claims=jwt_claims,
                            scheme="BEARER",
                            token=token,
                            idp_client_id=idp_client.id,
                        )
                    )
                    return user
                except exc.UnauthorizedAuthError:
                    continue
        # No valid user found for any of the IDP clients
        raise exc.UnauthorizedAuthError()

    def create_user_dependencies(
        self,
    ) -> tuple[model.User, model.User, IDPUser]:

        if not self._idp_clients:
            # No authentication -> create/retrieve root user
            user_manager = self.app.user_manager
            if not user_manager:
                raise exc.InitializationServiceError(
                    "No authentication services configured and no user generator provided"
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
                    "Unable to create user due to missing header or claims"
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

        # Init get_current_user function definition and environment
        # TODO: generate get_current_user and get_new_user functions
        # dynamically based on number of authentication services
        n_security_bases = len(self._idp_clients)
        if self._logger:
            self._logger.info(
                self.create_log_message(
                    "1e3d75cb",
                    "Generating user authentication function per security base",
                )
            )

        def _warn(request: Request) -> None:
            if self._logger:
                self._logger.warning(
                    self.create_log_message(
                        "f8853e9e",
                        "Unable to verify provided user",
                        request=request,
                    )
                )

        idp_client_list = self._idp_clients + ([None] * (5 - len(self._idp_clients)))

        async def get_current_user1(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
        ) -> model.User:
            if claims_0:
                return await self.get_existing_user_from_claims(claims_0)
            _warn(request)
            raise exc.UnauthorizedAuthError()

        async def get_new_user1(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
        ) -> model.User:
            if claims_0:
                return await self.get_new_user_from_claims(claims_0)
            _warn(request)
            raise exc.UnauthorizedAuthError()

        async def get_idp_user1(
            request: Request,
            _security_scopes: SecurityScopes,
            claims_0: Claims = Depends(idp_client_list[0]),
        ) -> IDPUser:
            if claims_0:
                return await self.get_idp_user_from_claims(claims_0)
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
            _warn(request)
            raise exc.UnauthorizedAuthError()

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
        if n_security_bases > len(get_current_user_functions):
            msg = (
                f"More than {len(get_current_user_functions)} "
                "({n_security_bases}) not implemented"
            )
            if self._logger:
                self._logger.error(self.create_log_message("d6f4ede7", msg))
            raise exc.InitializationServiceError(msg)
        registered_user_dependency: model.User = Annotated[  # type: ignore
            model.User,
            Security(
                get_current_user_functions[n_security_bases - 1],  # type: ignore
                scopes=["openid", "profile"],
            ),
        ]
        new_user_dependency: model.User = Annotated[  # type: ignore
            model.User,
            Security(
                get_new_user_functions[n_security_bases - 1],  # type: ignore
                scopes=["openid", "profile"],
            ),
        ]
        idp_user_dependency: IDPUser = Annotated[  # type: ignore
            IDPUser,
            Security(
                get_idp_user_functions[n_security_bases - 1],  # type: ignore
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
        except Exception:
            # ensure this call never raises because of IDP initialization attempts
            if self._logger:
                self._logger.exception(
                    self.create_log_message(
                        "b2c6a1d4",
                        "Unexpected error while retrying pending IDPs",
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
            new_user = user_manager.get_user_instance_from_claims(claims.claims)
            if new_user:
                return new_user
        else:
            # No user manager configured, create user obj directly from claims
            new_user = model.User(**claims.claims)  # type: ignore
        return new_user

    async def get_existing_user_from_claims(
        self, claims: Claims, request_userinfo: bool = True
    ) -> model.User:
        issuer: str = claims.claims["iss"]  # type: ignore
        sub: str = claims.claims["sub"]  # type: ignore
        user_manager = self.app.user_manager
        if not user_manager:
            # No user generator configured
            raise exc.UnauthorizedAuthError()

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
            raise exc.UnauthorizedAuthError()

        try:
            # Retrieve existing user
            user = user_manager.retrieve_user_by_key(user_key)
            try:
                # Retrieve user name from claims and update if necessary
                new_user_name = user_manager.get_user_name_from_claims(claims.claims)
                if new_user_name:
                    updated_user = user_manager.update_user_name(user, new_user_name)
                    if updated_user:
                        return updated_user
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

            # Automatically create the user if configured
            try:
                user = user_manager.create_user_from_claims(claims.claims)
                if not user:
                    raise exc.UnauthorizedAuthError()
                if self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "fe8bfbd0",
                            "Automatically created user",
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
                            "Could not automatically create user",
                            issuer=issuer,
                            sub=sub,
                            user_key=user_key,
                            exception=exception,
                        )
                    )
                raise exc.UnauthorizedAuthError()

    def _init_idp_clients(
        self,
        app: App,
        idps_cfg: list[dict[str, str | list]] | None,
        ssl_context: ssl.SSLContext | bool,
    ) -> None:
        # Initialize list of all IDP clients and list of exposed IDP clients
        if not idps_cfg:
            idps_cfg = []
        idp_clients: list[IdpClient] = []
        exposed_idp_clients: list[IdpClient] = []
        idp_names: set[str] = set()
        idp_labels: set[str] = set()
        logger = app.logger
        for idp_cfg in idps_cfg:
            idp_name: str = idp_cfg["name"]  # type: ignore[assignment]
            idp_label: str = idp_cfg["label"]  # type: ignore[assignment]
            is_public: bool = idp_cfg.get("is_exposed", self.DEFAULT_IS_PUBLIC_IDP)  # type: ignore[assignment]
            if idp_name in idp_names or idp_label in idp_labels:
                msg = (
                    "Authentication service name and/or label are not unique: "
                    f"{idp_cfg['name']}, {idp_cfg['label']}"
                )
                if logger:
                    logger.error(app.create_log_message("30a9a272", msg))
                raise exc.InitializationServiceError(msg)
            idp_names.add(idp_name)
            idp_labels.add(idp_label)

            oidc_discovery_doc_keys = set(OidcServerCfg.model_fields.keys())
            try:
                protocol = enum.AuthProtocol[str(idp_cfg["protocol"])]
                if protocol == enum.AuthProtocol.OIDC:
                    discovery_doc = {
                        x: y for x, y in idp_cfg.items() if x in oidc_discovery_doc_keys
                    }
                    idp_client = OauthIdpClient(
                        OidcServerCfg(**idp_cfg),  # type: ignore
                        logger=self._logger,
                        log_item_class=app.log_item_class,
                        discovery_doc=discovery_doc,  # Provide again to avoid fetching from discovery URL (again).
                        ssl_context=ssl_context,
                    )
                else:
                    raise exc.InitializationServiceError(
                        f"Protocol {protocol.value} not implemented"
                    )
                idp_clients.append(idp_client)
                if is_public:
                    exposed_idp_clients.append(idp_client)
            except Exception as exception:
                # Unable to initialize authentication service: do not raise
                # an error to avoid entire app not starting up
                msg = (
                    "Could not initialize authentication client for service "
                    f"{idp_cfg['name']}"
                )
                if logger:
                    logger.error(
                        app.create_log_message("48b7e021", msg, exception=exception)
                    )
                with self._pending_lock:
                    self._pending_idp_clients.append(idp_client)
        for idp_client in idp_clients:  # type: ignore
            if isinstance(idp_client, OauthIdpClient):
                if logger:
                    logger.info(
                        app.create_log_message(
                            "7e0b64cc",
                            f"Authentication client on {idp_client.issuer} initialized",
                        )
                    )
            else:
                raise exc.InitializationServiceError(
                    f"Authentication client of type {type(idp_client)} "
                    "not implemented"
                )
        self._idp_clients = idp_clients
        self._exposed_idp_clients = exposed_idp_clients

    def _attempt_init_single_idp_client(
        self, idp_cfg: dict[str, str | list]
    ) -> IdpClient | None:
        try:
            protocol = enum.AuthProtocol[str(idp_cfg["protocol"])]
            if protocol == enum.AuthProtocol.OIDC:
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
                    ssl_context=True,
                )
                return idp_client
            else:
                if self._logger:
                    self._logger.error(
                        self.create_log_message(
                            "b1f4c3d2",
                            f"Protocol {protocol.value} not implemented",
                        )
                    )
                return None
        except Exception as exception:
            if self._logger:
                self._logger.debug(
                    self.create_log_message(
                        "e2c6f4a5",
                        "Pending IDP still not initialized",
                        idp_name=idp_cfg.get("name"),
                        exception=exception,
                    )
                )
        return None

    def _retry_pending_idp_clients(self) -> None:
        with self._pending_lock:
            if not self._pending_idp_clients:
                return
            retry_clients = list(self._pending_idp_clients)
        newly_added: list[IdpClient] = []
        newly_exposed: list[IdpClient] = []
        for idp_cfg in retry_clients:
            idp_name: str = idp_cfg["name"]  # type: ignore[assignment]
            idp_label: str = idp_cfg["label"]  # type: ignore[assignment]
            # avoid re-adding already existing clients
            if any(
                getattr(getattr(x, "server_cfg", None), "name", None) == idp_name
                for x in self._idp_clients
            ) or any(
                getattr(getattr(x, "server_cfg", None), "label", None) == idp_label
                for x in self._idp_clients
            ):
                with self._pending_lock:
                    try:
                        self._pending_idp_clients.remove(idp_cfg)
                    except ValueError:
                        pass
                continue
            idp_client = self._attempt_init_single_idp_client(idp_cfg)
            if idp_client:
                newly_added.append(idp_client)
                is_public: bool = idp_cfg.get(
                    "is_exposed", self.DEFAULT_IS_PUBLIC_IDP
                )  # type: ignore[assignment]
                if is_public:
                    newly_exposed.append(idp_client)
                with self._pending_lock:
                    try:
                        self._pending_idp_clients.remove(idp_cfg)
                    except ValueError:
                        pass
        if newly_added:
            self._idp_clients.extend(newly_added)
            self._exposed_idp_clients.extend(newly_exposed)
            self._idp_client_by_id = {x.id: x for x in self._idp_clients or []}
            for idp_client in newly_added:
                if isinstance(idp_client, OauthIdpClient) and self._logger:
                    self._logger.info(
                        self.create_log_message(
                            "c3f4e2b1",
                            f"Recovered authentication client on {idp_client.issuer}",
                        )
                    )
