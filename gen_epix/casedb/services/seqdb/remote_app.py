import json
from collections.abc import Iterable
from datetime import datetime
from logging import Logger
from typing import Any

import httpx
from jose import jwt

from gen_epix.fastapp import HttpProtocol, RemoteApp, exc
from gen_epix.fastapp.enum import AuthProtocol, OAuthFlow
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.services.auth.model import OidcServerCfg
from gen_epix.fastapp.services.auth.oidc_client import OidcClient
from gen_epix.seqdb.api import RetrievePhylogeneticTreeRequestBody
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import model as seqdb_model


class SeqdbRemoteApp(RemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1/"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        seqdb_command.RetrievePhylogeneticTreeCommand: "retrieve/phylogenetic_tree",
        seqdb_command.RetrieveSeqFastaCommand: "retrieve/genetic_sequence/fasta",
    }

    def __init__(
        self,
        host: str,
        port: int | None,
        http_protocol: HttpProtocol = HttpProtocol.HTTPS,
        default_route_prefix: str | None = None,
        default_headers: dict[str, str] | None = None,
        ssl_cert_file: str | None = None,
        auth_protocol: AuthProtocol | str = AuthProtocol.NONE,
        oauth_flow: OAuthFlow | str | None = None,
        oauth_discovery_url: str | None = None,
        oauth_client_id: str | None = None,
        oauth_client_secret: str | None = None,
        oauth_scope: str | None = None,
        oauth_token_endpoint: str | None = None,
        oauth_token_refresh_margin: float | None = None,
        logger: Logger | None = None,
        log_item_class: type[LogItem] = LogItem,
        **kwargs: Any,
    ) -> None:
        if isinstance(auth_protocol, str):
            auth_protocol = AuthProtocol(auth_protocol)
        if isinstance(oauth_flow, str):
            oauth_flow = OAuthFlow(oauth_flow)
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
            ssl_cert_file=ssl_cert_file,
            **kwargs,
        )

        # Initialize IDP client if needed
        oidc_client: OidcClient | None = None
        if auth_protocol == AuthProtocol.NONE:
            pass
        elif auth_protocol == AuthProtocol.OAUTH2:
            if oauth_discovery_url is None:
                raise exc.InitializationServiceError(
                    "OAuth discovery endpoint must be provided for OAUTH2 auth protocol"
                )
            if oauth_client_id is None:
                raise exc.InitializationServiceError(
                    "OAuth client ID must be provided for OAUTH2 auth protocol"
                )
            if oauth_scope is None:
                raise exc.InitializationServiceError(
                    "OAuth scope must be provided for OAUTH2 auth protocol"
                )
            oidc_client = OidcClient(
                server_cfg=OidcServerCfg(
                    name="",
                    label="",
                    discovery_url=oauth_discovery_url,
                    client_id=oauth_client_id,
                    client_secret=oauth_client_secret,
                    token_endpoint=oauth_token_endpoint,
                    scope=oauth_scope,
                ),
                ssl_context=self.ssl_context,
                logger=logger,
                log_item_class=log_item_class,
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
        self._oauth_header_cache: tuple[int, dict[str, str]] | None = None

        # Register routes and handlers
        self.register_route(
            seqdb_command.RetrievePhylogeneticTreeCommand,
            self.ROUTE_MAP[seqdb_command.RetrievePhylogeneticTreeCommand],
        )
        self.register_route(
            seqdb_command.RetrieveSeqFastaCommand,
            self.ROUTE_MAP[seqdb_command.RetrieveSeqFastaCommand],
        )
        self.register_handler(
            seqdb_command.RetrievePhylogeneticTreeCommand,
            self.retrieve_phylogenetic_tree,
        )
        self.register_handler(
            seqdb_command.RetrieveSeqFastaCommand,
            self.retrieve_genetic_sequence_fasta_by_id,
        )

    def get_headers(self, cmd: Command) -> dict[str, str]:
        # Call identity provider to get JWT
        if self._auth_protocol == AuthProtocol.NONE:
            return self._default_headers
        if self._auth_protocol == AuthProtocol.OAUTH2:
            assert self._oidc_client is not None
            assert self._oauth_scope is not None
            # Check if cached token is still valid
            if self._oauth_header_cache and self._oauth_header_cache[0] > (
                datetime.now().timestamp() - self._oauth_token_refresh_margin
            ):
                # Return cached header
                return self._oauth_header_cache[1]
            # Retrieve new token

            jwt_token = self._oidc_client.retrieve_jwt_with_client_credentials_flow(
                scope=self._oauth_scope
            )
            # Create headers
            headers = dict(self._default_headers)
            headers["Authorization"] = f"Bearer {jwt_token}"
            # Put header in cache together with its expiry time
            claims = jwt.get_unverified_claims(jwt_token)
            exp: int | None = claims.get("exp")
            if exp is None:
                # No expiration claim, valid forever
                self._oauth_header_cache = (int(datetime.max.timestamp()), headers)
            else:
                self._oauth_headers_cache = (exp, headers)
            return headers
        raise exc.InitializationServiceError(
            f"Auth protocol {self._auth_protocol.value} not supported for token retrieval"
        )

    def retrieve_phylogenetic_tree(
        self,
        cmd: seqdb_command.RetrievePhylogeneticTreeCommand,
    ) -> seqdb_model.PhylogeneticTree | None:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        # Create request body matching seqdb API expectations

        request_body = RetrievePhylogeneticTreeRequestBody(
            seq_distance_protocol_id=cmd.seq_distance_protocol_id,
            tree_algorithm=cmd.tree_algorithm,
            seq_ids=cmd.seq_ids,
            leaf_codes=cmd.leaf_names,
        )

        with httpx.Client(verify=self.ssl_context) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return seqdb_model.PhylogeneticTree(**data)

    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: seqdb_command.RetrieveSeqFastaCommand,
    ) -> Iterable[str]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body: dict[str, Any] = {
            "user": cmd.user,
            "seq_ids": cmd.seq_ids,
            "wrap": cmd.wrap,
        }

        def _iter_fasta_generator() -> Iterable[str]:
            with httpx.Client(verify=self.ssl_context) as client:
                with client.stream(
                    "POST", route, json=request_body, headers=headers
                ) as resp:
                    resp.raise_for_status()
                    for chunk in resp.iter_bytes():
                        yield chunk.decode()

        return _iter_fasta_generator()
