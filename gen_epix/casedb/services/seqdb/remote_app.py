from datetime import datetime
from logging import Logger
from typing import Any, Callable
from uuid import UUID

import httpx
from jose import jwt

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.command import RetrievePhylogeneticTreeBySequencesCommand
from gen_epix.fastapp import HttpProtocol, RemoteApp, exc
from gen_epix.fastapp.enum import AuthProtocol, OauthFlow
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oidc_client import OidcClient
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum


class SeqdbRemoteApp(RemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1/"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    COMMAND_MAP: dict[type[Command], type[Command]] = {
        command.RetrievePhylogeneticTreeBySequencesCommand: seqdb_command.RetrievePhylogeneticTreeCommand,
    }
    ROUTE_MAP: dict[type[Command], str] = {
        seqdb_command.RetrievePhylogeneticTreeCommand: "retrieve/phylogenetic_tree",
    }

    TREE_ALGORITHM_MAP = {
        x: y
        for x in enum.TreeAlgorithmType
        for y in seqdb_enum.TreeAlgorithm
        if x.value == y.value
    }

    def __init__(
        self,
        host: str,
        port: int | None,
        http_protocol: HttpProtocol = HttpProtocol.HTTPS,
        default_route_prefix: str | None = None,
        default_headers: dict[str, str] | None = None,
        auth_protocol: AuthProtocol = AuthProtocol.NONE,
        oauth_flow: OauthFlow | None = None,
        oauth_scope: str | None = None,
        oauth_token_refresh_margin: float | None = None,
        logger: Logger | None = None,
        log_item_class: type[LogItem] = LogItem,
        **kwargs: Any,
    ) -> None:
        default_route_prefix = default_route_prefix or self.DEFAULT_ROUTE_PREFIX
        oauth_token_refresh_margin = (
            oauth_token_refresh_margin or self.DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN
        )

        super().__init__(
            DOMAIN,
            host,
            port,
            http_protocol=http_protocol,
            default_route_prefix=default_route_prefix,
            default_headers=default_headers,
            add_generated_crud_route_handlers=True,
            **kwargs,
        )

        # Initialize IDP client if needed
        oidc_client: OidcClient | None = None
        if auth_protocol == AuthProtocol.NONE:
            pass
        elif auth_protocol == AuthProtocol.OAUTH2:
            oidc_client = OidcClient(
                server_cfg=OidcServerCfg(**kwargs),
                logger=logger,
                log_item_class=log_item_class,
            )
            if oauth_scope is None:
                raise exc.InitializationServiceError(
                    "OAuth scope must be provided for OAUTH2 auth protocol"
                )
        else:
            raise exc.InitializationServiceError(
                f"Auth protocol {auth_protocol} not supported"
            )
        self._auth_protocol = auth_protocol
        self._oauth_flow = oauth_flow
        self._oidc_client = oidc_client
        self._oauth_scope = oauth_scope
        self._oauth_token_refresh_margin = oauth_token_refresh_margin
        self._oauth_token_cache: tuple[int, str] | None = None

        # Register routes and handlers
        seqdb_command_class = seqdb_command.RetrievePhylogeneticTreeCommand
        self.register_route(
            self.COMMAND_MAP[RetrievePhylogeneticTreeBySequencesCommand],
            self.ROUTE_MAP[seqdb_command_class],
        )
        self.register_handler(
            self.COMMAND_MAP[RetrievePhylogeneticTreeBySequencesCommand],
            self.create_retrieve_phylogenetic_tree_handler(),
        )

    def get_headers(self, cmd: Command) -> dict[str, str]:
        headers = super().get_headers(cmd)
        # Call identity provider to get JWT
        assert self._oidc_client is not None
        assert self._oauth_scope is not None
        if self._auth_protocol == AuthProtocol.OAUTH2:
            # Check if cached token is still valid
            if self._oauth_token_cache and self._oauth_token_cache[0] > (
                datetime.now().timestamp() - self._oauth_token_refresh_margin
            ):
                jwt_token = self._oauth_token_cache[1]
            else:
                # Retrieve new token
                jwt_token = self._oidc_client.retrieve_jwt_with_client_credentials_flow(
                    scope=self._oauth_scope
                )
                # Put token in cache together with its expiry time
                claims = jwt.get_unverified_claims(jwt_token)
                exp: int | None = claims.get("exp")
                if exp is None:
                    # No expiration claim, valid forever
                    self._oauth_token_cache = (int(datetime.max.timestamp()), jwt_token)
                else:
                    self._oauth_token_cache = (exp, jwt_token)
        else:
            raise exc.InitializationServiceError(
                f"Auth protocol {self._auth_protocol.value} not supported for token retrieval"
            )
        headers["Authorization"] = f"Bearer {jwt_token}"
        return headers

    def create_retrieve_phylogenetic_tree_handler(self) -> Callable:

        seqdb_command_class = seqdb_command.RetrievePhylogeneticTreeCommand
        # Route registration is handled during initialization

        def handler(
            cmd: seqdb_command.RetrievePhylogeneticTreeCommand,
        ) -> model.PhylogeneticTree | None:
            headers = self.get_headers(cmd)
            route = self.get_route(cmd)

            # Create request body matching seqdb API expectations
            from gen_epix.seqdb.api import RetrievePhylogeneticTreeRequestBody

            request_body = RetrievePhylogeneticTreeRequestBody(
                seq_distance_protocol_id=cmd.seq_distance_protocol_id,
                tree_algorithm=cmd.tree_algorithm,
                seq_ids=cmd.seq_ids,
                leaf_codes=cmd.leaf_names,
            )

            with httpx.Client() as client:
                response = client.post(
                    route,
                    json=request_body.model_dump(),
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    return None

                # Map seqdb TreeAlgorithm to casedb TreeAlgorithmType
                tree_algorithm_code = None
                for casedb_alg, seqdb_alg in self.TREE_ALGORITHM_MAP.items():
                    if seqdb_alg == cmd.tree_algorithm:
                        tree_algorithm_code = casedb_alg
                        break

                if tree_algorithm_code is None:
                    raise ValueError(f"Unknown tree algorithm: {cmd.tree_algorithm}")

                phylogenetic_tree = model.PhylogeneticTree(
                    tree_algorithm_code=tree_algorithm_code,
                    sequence_ids=[UUID(sid) for sid in data["sequence_ids"]],
                    leaf_ids=(
                        [UUID(lid) for lid in data["leaf_ids"]]
                        if data.get("leaf_ids")
                        else None
                    ),
                    newick_repr=data["newick_repr"],
                )
                return phylogenetic_tree

        return handler
