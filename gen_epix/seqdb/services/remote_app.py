import json
from collections.abc import Iterable
from typing import Any
from uuid import UUID

import httpx

from gen_epix.commondb.services.remote_app import CommondbRemoteApp
from gen_epix.fastapp.model import Command
from gen_epix.seqdb.api import (
    RetrievePhylogeneticTreeRequestBody,
    RetrieveSeqFastaRequestBody,
)
from gen_epix.seqdb.domain import DOMAIN
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import model as seqdb_model


class SeqdbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        seqdb_command.RetrievePhylogeneticTreeCommand: "/retrieve/phylogenetic_tree",
        seqdb_command.RetrieveSeqFastaCommand: "/retrieve/seq_fasta",
        seqdb_command.CreateFileCommand: "/create/file",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)
        # Register routes and handlers
        self.register_route(
            seqdb_command.RetrievePhylogeneticTreeCommand,
            self.ROUTE_MAP[seqdb_command.RetrievePhylogeneticTreeCommand],
        )
        self.register_route(
            seqdb_command.RetrieveSeqFastaCommand,
            self.ROUTE_MAP[seqdb_command.RetrieveSeqFastaCommand],
        )
        self.register_route(
            seqdb_command.CreateFileCommand,
            self.ROUTE_MAP[seqdb_command.CreateFileCommand],
        )
        self.register_handler(
            seqdb_command.RetrievePhylogeneticTreeCommand,
            self.retrieve_phylogenetic_tree,
        )
        self.register_handler(
            seqdb_command.RetrieveSeqFastaCommand,
            self.retrieve_genetic_sequence_fasta_by_id,
        )
        self.register_handler(
            seqdb_command.CreateFileCommand,
            self.create_file,
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

        request_body = RetrieveSeqFastaRequestBody(
            seq_ids=cmd.seq_ids,
            file_name="dummy.fasta",
        )

        def _iter_fasta_generator() -> Iterable[str]:
            with httpx.Client(verify=self.ssl_context) as client:
                with client.stream(
                    "POST",
                    route,
                    json=json.loads(request_body.model_dump_json()),
                    headers=headers,
                ) as resp:
                    resp.raise_for_status()
                    for chunk in resp.iter_bytes():
                        yield chunk.decode()

        return _iter_fasta_generator()

    def create_file(
        self,
        cmd: seqdb_command.CreateFileCommand,
    ) -> UUID:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body: dict[str, Any] = {
            "user": cmd.user,
            "file_content": cmd.file.content,
            "file_format": cmd.format.value,
            "file_compression": cmd.compression.value,
        }

        with httpx.Client(verify=self.ssl_context) as client:
            response = client.post(
                route,
                json=request_body,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return UUID(data)
