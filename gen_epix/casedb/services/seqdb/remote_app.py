from functools import partial
from typing import Callable
from uuid import UUID

import httpx

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.domain.command import RetrievePhylogeneticTreeBySequencesCommand
from gen_epix.fastapp.remote_app import RemoteApp
from gen_epix.seqdb.api import RetrievePhylogeneticTreeRequestBody
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import command as seq_command
from gen_epix.seqdb.domain import enum as seq_enum


class SeqdbRemoteApp(RemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1/"

    TREE_ALGORITHM_MAP = {
        x: y
        for x in enum.TreeAlgorithmType
        for y in seq_enum.TreeAlgorithm
        if x.value == y.value
    }

    COMMAND_MAP = {
        command.RetrievePhylogeneticTreeBySequencesCommand: seq_command.RetrievePhylogeneticTreeCommand,
    }

    def __init__(self, host: str, port: int, **kwargs: dict) -> None:
        default_route_prefix: str = kwargs.pop(  # type:ignore[assignment]
            "default_route_prefix", self.DEFAULT_ROUTE_PREFIX
        )
        super().__init__(
            DOMAIN,
            host,
            port,
            default_route_prefix=default_route_prefix,
            **kwargs,
        )
        self._host = host
        self._port = port
        self.base_url = f"https://{self._host}:{self._port}{self._default_route_prefix}"

        handler = self.create_retrieve_phylogenetic_tree_handler()
        self.register_handler(
            self.COMMAND_MAP[RetrievePhylogeneticTreeBySequencesCommand], handler
        )

    def create_retrieve_phylogenetic_tree_handler(self) -> Callable:

        route = self.base_url + "retrieve/phylogenetic_tree"
        self.register_route(
            self.COMMAND_MAP[RetrievePhylogeneticTreeBySequencesCommand],
            route,
            add_prefix=False,
        )

        def handler(
            cmd: seq_command.RetrievePhylogeneticTreeCommand,
        ) -> model.PhylogeneticTree | None:
            headers = self.get_headers(cmd)

            with httpx.Client() as client:
                response = client.post(
                    route,
                    json=RetrievePhylogeneticTreeRequestBody(
                        seq_distance_protocol_id=cmd.seq_distance_protocol_id,
                        tree_algorithm=cmd.tree_algorithm,
                        seq_ids=cmd.seq_ids,
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

        return partial(handler)
