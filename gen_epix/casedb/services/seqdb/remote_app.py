from logging import Logger
from typing import Any, Callable
from uuid import UUID

import httpx

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.command import RetrievePhylogeneticTreeBySequencesCommand
from gen_epix.fastapp import HttpProtocol, RemoteApp, exc
from gen_epix.fastapp.enum import AuthProtocol, OauthFlow
from gen_epix.fastapp.log import LogItem
from gen_epix.fastapp.model import Command
from gen_epix.fastapp.services.auth.model import OidcCfg
from gen_epix.fastapp.services.auth.oidc_client import OidcClient
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import command as seq_command
from gen_epix.seqdb.domain import enum as seq_enum


class SeqdbRemoteApp(RemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1/"

    COMMAND_MAP: dict[type[Command], type[Command]] = {
        command.RetrievePhylogeneticTreeBySequencesCommand: seq_command.RetrievePhylogeneticTreeCommand,
    }
    ROUTE_MAP: dict[type[Command], str] = {
        seq_command.RetrievePhylogeneticTreeCommand: "retrieve/phylogenetic_tree",
    }

    TREE_ALGORITHM_MAP = {
        x: y
        for x in enum.TreeAlgorithmType
        for y in seq_enum.TreeAlgorithm
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
        logger: Logger | None = None,
        log_item_class: type[LogItem] = LogItem,
        **kwargs: Any,
    ) -> None:
        default_route_prefix = default_route_prefix or self.DEFAULT_ROUTE_PREFIX

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
                oidc_configuration=OidcCfg(**kwargs),
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

        # Register handlers
        self.register_handler(
            self.COMMAND_MAP[RetrievePhylogeneticTreeBySequencesCommand],
            self.create_retrieve_phylogenetic_tree_handler,
        )

    def get_headers(self, cmd: Command) -> dict[str, str]:
        headers = super().get_headers(cmd)
        # Call identity provider to get token through OAuth Client Credentials flow
        token_data = {
            "grant_type": "client_credentials",
            "client_id": "casedb-service",
            "client_secret": "service-secret",
            "scope": "seqdb:read seqdb:write",
        }

        # Get token endpoint from config or use default
        token_url = "http://localhost:8080/oauth/token"

        with httpx.Client() as client:
            response = client.post(
                token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_response = response.json()
            token = token_response["access_token"]

        headers["Authorization"] = f"Bearer {token}"
        return headers

    def create_retrieve_phylogenetic_tree_handler(self) -> Callable:

        seqdb_command_class = seq_command.RetrievePhylogeneticTreeCommand
        self.register_route(
            self.COMMAND_MAP[command.RetrievePhylogeneticTreeBySequencesCommand],
            self.ROUTE_MAP[seqdb_command_class],
        )

        def handler(
            cmd: seq_command.RetrievePhylogeneticTreeCommand,
        ) -> model.PhylogeneticTree | None:
            headers = self.get_headers(cmd)
            route = self.get_route(cmd)

            with httpx.Client() as client:
                response = client.post(
                    route,
                    json=seqdb_command_class(
                        seq_distance_protocol_id=cmd.seq_distance_protocol_id,
                        tree_algorithm=cmd.tree_algorithm,
                        seq_ids=cmd.seq_ids,
                        leaf_names=cmd.leaf_names,
                    ).model_dump(),
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
