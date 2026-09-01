"""Implement seqdb application service behavior for services.remote_app."""

import base64
from collections.abc import Iterable
from datetime import datetime
from typing import Any, cast
from uuid import UUID

from gen_epix.commondb.services.remote_app import CommondbRemoteApp
from gen_epix.fastapp.enum import CrudOperation, HttpMethod
from gen_epix.fastapp.model import Command
from gen_epix.seqdb import api
from gen_epix.seqdb.domain import DOMAIN, command, enum, model


class SeqdbRemoteApp(CommondbRemoteApp):
    """Remote app client for the seqdb service."""

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.CalculatePhylogeneticTreeCommand: "/calculate/phylogenetic_tree",
        command.RetrieveBestSeqPerSampleCommand: "/retrieve/best_seq_per_sample",
        command.RetrieveBestSeqProfilePerSampleCommand: "/retrieve/best_seq_profile_per_sample",
        command.RetrieveBestSeqClassificationPerSampleCommand: "/retrieve/best_seq_classification_per_sample",
        command.RetrieveSeqFastaCommand: "/retrieve/seq_fasta",
        command.CreateFileCommand: "/create/file",
        command.RetrieveSimilarProfilesCommand: "/retrieve/similar_profiles",
        command.UpdateSeqDistancesCommand: "/update/seq_distances",
        command.UploadSamplesCommand: "/upload/samples",
        command.RetrieveSampleIdentifiersByIdCommand: "/retrieve/sample_identifiers_by_ids",
        command.RetrieveSamplesByIdCommand: "/retrieve/samples_by_ids",
        command.RetrieveSamplesByQueryCommand: "/retrieve/sample_ids_by_query",
        command.RetrieveSeqDistanceLastModifiedCommand: (
            "/retrieve/seq_distance_last_modified"
        ),
    }

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        command.UploadSamplesCommand: 45.0,
        command.UpdateSeqDistancesCommand: 300.0,
        command.RetrieveSampleIdentifiersByIdCommand: 45.0,
        command.RetrieveSamplesByIdCommand: 45.0,
        command.RetrieveSamplesByQueryCommand: 45.0,
        command.LocusCrudCommand: 45.0,
        command.RetrieveBestSeqPerSampleCommand: 15.0,
        command.RetrieveBestSeqProfilePerSampleCommand: 15.0,
        command.RetrieveBestSeqClassificationPerSampleCommand: 15.0,
        command.CalculatePhylogeneticTreeCommand: 45.0,
        command.RetrieveSimilarProfilesCommand: 45.0,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Register all seqdb routes and command handlers."""
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
            command.UpdateSeqDistancesCommand,
            self.update_seq_distances,
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
            command.RetrieveBestSeqClassificationPerSampleCommand,
            self.retrieve_best_seq_classification_per_sample,
        )
        self.register_handler(
            command.RetrieveSeqDistanceLastModifiedCommand,
            self.retrieve_seq_distance_last_modified,
        )

    def calculate_phylogenetic_tree(
        self,
        cmd: command.CalculatePhylogeneticTreeCommand,
    ) -> model.PhylogeneticTree | None:
        """Request phylogenetic tree calculation and return the result."""
        request_body = api.CalculatePhylogeneticTreeRequestBody(
            protocol_id=cmd.protocol_id,
            tree_algorithm=cmd.tree_algorithm,
            seq_profile_ids=cmd.seq_profile_ids,
            leaf_names=cmd.leaf_names,
        )
        response_body = self.request(cmd, HttpMethod.POST, model=request_body)
        if not response_body:
            return None
        return model.PhylogeneticTree(**response_body)

    def retrieve_genetic_sequence_fasta_by_id(
        self,
        cmd: command.RetrieveSeqFastaCommand,
    ) -> Iterable[str]:
        """Stream genetic sequence FASTA data by sequence IDs."""
        request_body = api.RetrieveSeqFastaRequestBody(
            seq_ids=cmd.seq_ids,
            file_name="dummy.fasta",
        )
        return self.stream(cmd, HttpMethod.POST, model=request_body)

    def create_file(
        self,
        cmd: command.CreateFileCommand,
    ) -> UUID:
        """Upload a file and return its assigned UUID."""
        request_body = api.CreateFileRequestBody(
            content=base64.b64encode(cmd.file.content).decode("utf-8"),
            format=cmd.format,
            compression=cmd.compression,
        )
        response_body: str = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, json_body=request_body
        )
        return UUID(response_body)

    def retrieve_similar_profiles(
        self,
        cmd: command.RetrieveSimilarProfilesCommand,
    ) -> list[UUID]:
        """Retrieve profile IDs similar to the given profiles within a distance threshold."""
        request_body = api.RetrieveSimilarProfilesRequestBody(
            protocol_id=cmd.protocol_id,
            profile_ids=cmd.profile_ids,
            max_distance=cmd.max_distance,
        )
        response_body: list[str] = self.request(cmd, HttpMethod.POST, model=request_body)  # type: ignore[assignment]
        return [UUID(x) for x in response_body]

    def retrieve_samples_by_id(
        self,
        cmd: command.RetrieveSamplesByIdCommand,
    ) -> list[model.FullSample]:
        """Retrieve full sample records by their IDs."""
        request_body = api.RetrieveSamplesByIdsRequestBody(sample_ids=cmd.sample_ids)
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.POST, model=request_body)  # type: ignore[assignment]
        return [model.FullSample(**x) for x in response_body]

    def retrieve_sample_identifiers_by_id(
        self,
        cmd: command.RetrieveSampleIdentifiersByIdCommand,
    ) -> list[model.SampleIdentifier]:
        """Retrieve sample identifiers by sample IDs."""
        request_body = api.RetrieveSampleIdentifiersByIdsRequestBody(
            sample_ids=cmd.sample_ids
        )
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.POST, model=request_body)  # type: ignore[assignment]
        return [model.SampleIdentifier(**x) for x in response_body]

    def retrieve_samples_by_query(
        self,
        cmd: command.RetrieveSamplesByQueryCommand,
    ) -> model.SampleQueryResult:
        """Retrieve samples matching the given query."""
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.POST, model=cmd.sample_query)  # type: ignore[assignment]
        return model.SampleQueryResult(**response_body)

    def update_seq_distances(
        self,
        cmd: command.UpdateSeqDistancesCommand,
    ) -> list[model.CalculateSeqDistancesResult]:
        """Trigger sequence distance calculation and return results."""
        response_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.POST, model=cmd, exclude={"user"})  # type: ignore[assignment]
        return [model.CalculateSeqDistancesResult(**x) for x in response_body]

    def retrieve_seq_distance_protocol_ids(self) -> list[UUID]:
        """Return IDs of all seq distance protocols."""
        protocols: list[model.Protocol] = self.handle(
            command.ProtocolCrudCommand(operation=CrudOperation.READ_ALL)
        )
        return [
            cast(UUID, x.id)
            for x in protocols
            if x.protocol_type == enum.ProtocolType.SEQ_DISTANCE
        ]

    def upload_samples(
        self,
        cmd: command.UploadSamplesCommand,
    ) -> model.SampleBatchUploadResult:
        """Upload a batch of samples."""
        response_body: dict[str, Any] = self.request(cmd, HttpMethod.POST, model=cmd, exclude={"user"})  # type: ignore[assignment]
        return model.SampleBatchUploadResult(**response_body)

    def retrieve_best_seq_per_sample(
        self,
        cmd: command.RetrieveBestSeqPerSampleCommand,
    ) -> dict[UUID, UUID]:
        """Retrieve the best sequence ID per sample ID."""
        response_body: dict[str, str] = self.request(cmd, HttpMethod.POST, model=cmd, exclude={"user"})  # type: ignore[assignment]
        return {UUID(x): UUID(y) for x, y in response_body.items()}

    def retrieve_best_seq_profile_per_sample(
        self,
        cmd: command.RetrieveBestSeqProfilePerSampleCommand,
    ) -> dict[UUID, UUID]:
        """Retrieve the best sequence profile ID per sample ID."""
        response_body: dict[str, str] = self.request(cmd, HttpMethod.POST, model=cmd, exclude={"user"})  # type: ignore[assignment]
        return {UUID(x): UUID(y) for x, y in response_body.items()}

    def retrieve_best_seq_classification_per_sample(
        self,
        cmd: command.RetrieveBestSeqClassificationPerSampleCommand,
    ) -> dict[UUID, UUID]:
        """Retrieve the best sequence classification ID per sample ID."""
        response_body: dict[str, str] = self.request(cmd, HttpMethod.POST, model=cmd, exclude={"user"})  # type: ignore[assignment]
        return {UUID(x): UUID(y) for x, y in response_body.items()}

    def retrieve_seq_distance_last_modified(
        self, cmd: command.RetrieveSeqDistanceLastModifiedCommand
    ) -> datetime | None:
        """Retrieve the last-modified timestamp for sequence distances of a protocol."""
        response_body: str = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, route=f"{self.get_route(cmd)}/{cmd.protocol_id}"
        )
        return datetime.fromisoformat(response_body) if response_body else None
