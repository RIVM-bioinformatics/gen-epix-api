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
    RetrieveSimilarProfilesRequestBody,
)
from gen_epix.seqdb.domain import DOMAIN, command, model


class SeqdbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.RetrievePhylogeneticTreeCommand: "/retrieve/phylogenetic_tree",
        command.RetrieveSeqFastaCommand: "/retrieve/seq_fasta",
        command.CreateFileCommand: "/create/file",
        command.RetrieveSimilarProfilesCommand: "/retrieve/similar_profiles",
        command.UploadSamplesCommand: "/upload/samples",
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)
        # Register routes and handlers
        self.register_route(
            command.RetrievePhylogeneticTreeCommand,
            self.ROUTE_MAP[command.RetrievePhylogeneticTreeCommand],
        )
        self.register_route(
            command.RetrieveSeqFastaCommand,
            self.ROUTE_MAP[command.RetrieveSeqFastaCommand],
        )
        self.register_route(
            command.CreateFileCommand,
            self.ROUTE_MAP[command.CreateFileCommand],
        )
        self.register_route(
            command.RetrieveSimilarProfilesCommand,
            self.ROUTE_MAP[command.RetrieveSimilarProfilesCommand],
        )
        self.register_route(
            command.UploadSamplesCommand,
            self.ROUTE_MAP[command.UploadSamplesCommand],
        )
        self.register_handler(
            command.RetrievePhylogeneticTreeCommand,
            self.retrieve_phylogenetic_tree,
        )
        self.register_handler(
            command.RetrieveSeqFastaCommand,
            self.retrieve_genetic_sequence_fasta_by_id,
        )
        self.register_handler(
            command.CreateFileCommand,
            self.create_file,
        )
        self.register_handler(
            command.RetrieveSimilarProfilesCommand,
            self.retrieve_similar_profiles,
        )
        self.register_handler(
            command.UploadSamplesCommand,
            self.upload_samples,
        )

    def retrieve_phylogenetic_tree(
        self,
        cmd: command.RetrievePhylogeneticTreeCommand,
    ) -> model.PhylogeneticTree | None:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = RetrievePhylogeneticTreeRequestBody(
            protocol_id=cmd.protocol_id,
            tree_algorithm=cmd.tree_algorithm,
            profile_ids=cmd.profile_ids,
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
        return model.PhylogeneticTree(**data)

    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: command.RetrieveSeqFastaCommand,
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
        cmd: command.CreateFileCommand,
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

    def retrieve_similar_profiles(
        self,
        cmd: command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = RetrieveSimilarProfilesRequestBody(
            protocol_id=cmd.protocol_id,
            profile_ids=cmd.profile_ids,
            max_distance=cmd.max_distance,
        )

        with httpx.Client(verify=self.ssl_context) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return [UUID(profile_id) for profile_id in data]

    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = cmd

        with httpx.Client(verify=self.ssl_context) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return model.SampleBatchUploadResult(**data)
