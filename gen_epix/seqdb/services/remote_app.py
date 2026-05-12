import json
from collections.abc import Iterable
from typing import Any
from uuid import UUID

import httpx

from gen_epix.commondb.services.remote_app import CommondbRemoteApp
from gen_epix.fastapp.model import Command
from gen_epix.seqdb.api import (
    CalculatePhylogeneticTreeRequestBody,
    RetrieveBestSeqPerSampleRequestBody,
    RetrieveBestSeqProfilePerSampleRequestBody,
    RetrieveSampleIdentifiersByIdsRequestBody,
    RetrieveSamplesByIdsRequestBody,
    RetrieveSeqFastaRequestBody,
    RetrieveSimilarProfilesRequestBody,
)
from gen_epix.seqdb.domain import DOMAIN, command, model


class SeqdbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.CalculatePhylogeneticTreeCommand: "/calculate/phylogenetic_tree",
        command.RetrieveBestSeqPerSampleCommand: "/retrieve/best_seq_per_sample",
        command.RetrieveBestSeqProfilePerSampleCommand: "/retrieve/best_seq_profile_per_sample",
        command.RetrieveSeqFastaCommand: "/retrieve/seq_fasta",
        command.CreateFileCommand: "/create/file",
        command.RetrieveSimilarProfilesCommand: "/retrieve/similar_profiles",
        command.UploadSamplesCommand: "/upload/samples",
        command.RetrieveSampleIdentifiersByIdCommand: "/retrieve/sample_identifiers_by_ids",
        command.RetrieveSamplesByIdCommand: "/retrieve/samples_by_ids",
        command.RetrieveSamplesByQueryCommand: "/retrieve/sample_ids_by_query",
        command.RetrieveBestSeqPerSampleCommand: "/retrieve/best_seq_per_sample",
        command.RetrieveBestSeqProfilePerSampleCommand: "/retrieve/best_seq_profile_per_sample",
    }

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        command.UploadSamplesCommand: 45.0,
        command.RetrieveSampleIdentifiersByIdCommand: 45.0,
        command.RetrieveSamplesByIdCommand: 45.0,
        command.RetrieveSamplesByQueryCommand: 45.0,
        command.RetrieveBestSeqPerSampleCommand: 15.0,
        command.RetrieveBestSeqProfilePerSampleCommand: 15.0,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)
        # Register routes
        for cmd_class, route in self.ROUTE_MAP.items():
            self.register_route(cmd_class, route)
        # Register handlers
        self.register_handler(
            command.RetrieveBestSeqPerSampleCommand,
            self.retrieve_best_seq_per_sample,
        )
        self.register_handler(
            command.RetrieveBestSeqProfilePerSampleCommand,
            self.retrieve_best_seq_profile_per_sample,
        )
        self.register_handler(
            command.CalculatePhylogeneticTreeCommand,
            self.calculate_phylogenetic_tree,
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
        self.register_handler(
            command.RetrieveSampleIdentifiersByIdCommand,
            self.retrieve_sample_identifiers_by_id,
        )
        self.register_handler(
            command.RetrieveSamplesByIdCommand,
            self.retrieve_samples_by_id,
        )
        self.register_handler(
            command.RetrieveSamplesByQueryCommand,
            self.retrieve_samples_by_query,
        )
        self.register_handler(
            command.RetrieveBestSeqPerSampleCommand,
            self.retrieve_best_seq_per_sample,
        )
        self.register_handler(
            command.RetrieveBestSeqProfilePerSampleCommand,
            self.retrieve_best_seq_profile_per_sample,
        )

    def calculate_phylogenetic_tree(
        self,
        cmd: command.CalculatePhylogeneticTreeCommand,
    ) -> model.PhylogeneticTree | None:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = CalculatePhylogeneticTreeRequestBody(
            protocol_id=cmd.protocol_id,
            tree_algorithm=cmd.tree_algorithm,
            profile_ids=cmd.seq_profile_ids,
            leaf_codes=cmd.leaf_names,
        )

        with self.get_client(cmd) as client:
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
            with self.get_client(cmd) as client:
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

        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return [UUID(profile_id) for profile_id in data]

    def retrieve_samples_by_id(
        self,
        cmd: command.RetrieveSamplesByIdCommand,
    ) -> list[model.FullSample]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)
        request_body = RetrieveSamplesByIdsRequestBody(sample_ids=cmd.sample_ids)
        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return [model.FullSample(**item) for item in data]

    def retrieve_sample_identifiers_by_id(
        self,
        cmd: command.RetrieveSampleIdentifiersByIdCommand,
    ) -> list[model.SampleIdentifier]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)
        request_body = RetrieveSampleIdentifiersByIdsRequestBody(sample_ids=cmd.sample_ids)
        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return [model.SampleIdentifier(**item) for item in data]

    def retrieve_samples_by_query(
        self,
        cmd: command.RetrieveSamplesByQueryCommand,
    ) -> model.SampleQueryResult:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)
        request_body = cmd.sample_query
        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return model.SampleQueryResult(**data)

    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = cmd

        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return model.SampleBatchUploadResult(**data)

    def retrieve_best_seq_per_sample(
        self,
        cmd: command.RetrieveBestSeqPerSampleCommand,
    ) -> dict[UUID, UUID]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = RetrieveBestSeqPerSampleRequestBody(
            **cmd.model_dump(),
        )

        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return {UUID(k): UUID(v) for k, v in data.items()}

    def retrieve_best_seq_profile_per_sample(
        self,
        cmd: command.RetrieveBestSeqProfilePerSampleCommand,
    ) -> dict[UUID, UUID]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)

        request_body = RetrieveBestSeqProfilePerSampleRequestBody(
            **cmd.model_dump(),
        )

        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return {UUID(k): UUID(v) for k, v in data.items()}
