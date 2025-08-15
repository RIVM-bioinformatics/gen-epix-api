import logging
from typing import Annotated, Any, Type

from fastapi import Depends, Request, Security
from fastapi.security import SecurityScopes

from gen_epix.fastapp import App, exc, model
from gen_epix.fastapp.services.auth.base import BaseAuthService
from gen_epix.fastapp.services.auth.command import GetIdentityProvidersCommand
from gen_epix.fastapp.services.auth.idp_client import IDPClient
from gen_epix.fastapp.services.auth.mock_idp_client import MockIDPClient
from gen_epix.fastapp.services.auth.model import Claims, IdentityProvider, IDPUser
from gen_epix.fastapp.services.auth.util import create_idp_clients_from_config


class AuthService(BaseAuthService):
    SERVICE_TYPE = "AUTH"

    def __init__(
        self,
        app: App,
        logger: logging.Logger | None = None,
        idps_cfg: list[dict[str, str | list]] | None = None,
        repository: None = None,
        **kwargs: Any,
    ):
        super().__init__(app, repository=repository, logger=logger, **kwargs)
        self._idp_clients: list[IDPClient] = []

        # Initialize authentication services
        self._idp_clients = create_idp_clients_from_config(app, idps_cfg)
        self._idp_client_by_id = {x.id: x for x in self._idp_clients or []}

        # Initialize no authentication user
        self._no_auth_user: model.User
        self._no_auth_idp_client: IDPClient = MockIDPClient(logger=logger)

    @property
    def idp_clients(self) -> list[IDPClient]:
        return list(self._idp_clients)

    def create_user_dependencies(
        self,
    ) -> tuple[Type[model.User], Type[model.User], Type[IDPUser]]:

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
                    f"Unable to create user due to missing header or claims"
                )

            registered_user_dependency = Annotated[
                model.User,
                Security(dummy_get_existing_user, scopes=["openid", "profile"]),
            ]
            new_user_dependency = Annotated[
                model.User,
                Security(dummy_get_new_user, scopes=["openid", "profile"]),
            ]
            idp_user_dependency = Annotated[
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
        _cmd: GetIdentityProvidersCommand,
    ) -> list[IdentityProvider]:
        return [x.get_identity_provider() for x in self._idp_clients]

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
            user = user_manager.retrieve_user_by_key(user_key)
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
            if user_manager.is_root_user(claims.claims):
                if self._logger:
                    self._logger.warning(
                        self.create_log_message(
                            "d4f37b85",
                            "User is root user, creating",
                            issuer=issuer,
                            sub=sub,
                        )
                    )
                return user_manager.create_root_user_from_claims(claims.claims)

            # Automatically create the user if configured
            try:
                user = user_manager.create_user_from_claims(claims.claims)
                if not user:
                    raise exc.UnauthorizedAuthError()
                if self._logger and self._logger.level <= logging.DEBUG:
                    self._logger.debug(
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
