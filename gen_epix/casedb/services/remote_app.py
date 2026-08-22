import base64
import json
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from gen_epix.casedb.domain import DOMAIN, command, model
from gen_epix.commondb.services import CommondbRemoteApp as CommondbRemoteApp
from gen_epix.fastapp.model import Command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model


class CasedbRemoteApp(CommondbRemoteApp):

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.UploadCasesCommand: "/upload/cases",
        command.RetrieveCasesByQueryCommand: "/retrieve/case_ids_by_query",
        command.RetrieveCaseCohortLinksByCaseTypeCommand: "/retrieve/case_cohort_links_by_case_type",
        command.CaseTypeSetCaseTypeUpdateAssociationCommand: "/case_type_sets",
        command.ColSetColUpdateAssociationCommand: "/col_sets",
        command.RetrieveCompleteCaseTypeCommand: "/complete_case_types",
        command.CreateCaseSetCommand: "/create/case_set",
        command.RetrieveCaseStatsCommand: "/retrieve/case_type_stats",
        command.RetrieveCasesByIdCommand: "/retrieve/cases_by_ids",
        command.RetrieveCaseRightsCommand: "/retrieve/case_rights",
        command.RetrieveCaseSetRightsCommand: "/retrieve/case_set_rights",
        command.RetrievePhylogeneticTreeByCasesCommand: "/calculate/phylogenetic_tree",
        command.RetrieveSimilarCasesCommand: "/retrieve/similar_cases",
        command.RetrieveGeneticSequenceFastaByCaseCommand: (
            "/retrieve/genetic_sequence/fasta"
        ),
        command.CreateFileForReadSetCommand: "/create_file_for_read_set",
        command.CreateFileForSeqCommand: "/create_file_for_seq",
        command.RetrieveProtocolsCommand: "/retrieve/sequencing_protocols",
        command.RetrieveIsOwnCasesCommand: "/retrieve/is_own_cases",
        command.DiseaseEtiologicalAgentUpdateAssociationCommand: "/diseases",
    }

    DEFAULT_HTTP_TIMEOUTS: dict[type[Command], float] = {
        command.UploadCasesCommand: 45.0,
        command.RetrieveCasesByIdCommand: 45.0,
        command.RetrieveCasesByQueryCommand: 45.0,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(DOMAIN, *args, **kwargs)

        # Register routes
        for cmd_class, route in self.ROUTE_MAP.items():
            self.register_route(cmd_class, route)
        # Register handlers
        self.register_handler(
            command.UploadCasesCommand,
            self.upload_cases,
        )
        self.register_handler(
            command.RetrieveCasesByQueryCommand,
            self.retrieve_cases_by_query,
        )
        self.register_handler(
            command.RetrieveCaseCohortLinksByCaseTypeCommand,
            self.retrieve_case_cohort_links_by_case_type,
        )
        self.register_handler(
            command.CaseTypeSetCaseTypeUpdateAssociationCommand,
            self.case_type_set_case_type_update_association,
        )
        self.register_handler(
            command.ColSetColUpdateAssociationCommand,
            self.col_set_col_update_association,
        )
        self.register_handler(
            command.RetrieveCompleteCaseTypeCommand,
            self.retrieve_complete_case_type,
        )
        self.register_handler(command.CreateCaseSetCommand, self.create_case_set)
        self.register_handler(
            command.RetrieveCaseStatsCommand, self.retrieve_case_stats
        )
        self.register_handler(
            command.RetrieveCasesByIdCommand, self.retrieve_cases_by_id
        )
        self.register_handler(
            command.RetrieveCaseRightsCommand, self.retrieve_case_rights
        )
        self.register_handler(
            command.RetrieveCaseSetRightsCommand, self.retrieve_case_set_rights
        )
        self.register_handler(
            command.RetrievePhylogeneticTreeByCasesCommand,
            self.retrieve_phylogenetic_tree_by_cases,
        )
        self.register_handler(
            command.RetrieveSimilarCasesCommand, self.retrieve_similar_cases
        )
        self.register_handler(
            command.RetrieveGeneticSequenceFastaByCaseCommand,
            self.retrieve_genetic_sequence_fasta_by_case,
        )
        self.register_handler(
            command.CreateFileForReadSetCommand, self.create_file_for_read_set
        )
        self.register_handler(command.CreateFileForSeqCommand, self.create_file_for_seq)
        self.register_handler(command.RetrieveProtocolsCommand, self.retrieve_protocols)
        self.register_handler(
            command.RetrieveIsOwnCasesCommand, self.retrieve_is_own_cases
        )
        self.register_handler(
            command.DiseaseEtiologicalAgentUpdateAssociationCommand,
            self.disease_etiological_agent_update_association,
        )

    def retrieve_case_cohort_links_by_case_type(
        self,
        cmd: command.RetrieveCaseCohortLinksByCaseTypeCommand,
    ) -> list[model.CaseCohortLink]:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)
        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json={"case_type_id": str(cmd.case_type_id)},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return [model.CaseCohortLink(**item) for item in data]

    def retrieve_cases_by_query(
        self,
        cmd: command.RetrieveCasesByQueryCommand,
    ) -> model.CaseQueryResult:
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)
        request_body = cmd.case_query
        with self.get_client(cmd) as client:
            response = client.post(
                route,
                json=json.loads(request_body.model_dump_json()),
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return model.CaseQueryResult(**data)

    def upload_cases(
        self,
        cmd: command.UploadCasesCommand,
    ) -> model.CaseBatchUploadResult:
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
        return model.CaseBatchUploadResult(**data)

    def case_type_set_case_type_update_association(
        self,
        cmd: command.CaseTypeSetCaseTypeUpdateAssociationCommand,
    ) -> list[model.CaseTypeSetMember]:
        data = self._call_json(
            cmd,
            "PUT",
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/case_types",
            json_body={
                "case_type_set_members": [
                    json.loads(x.model_dump_json()) for x in cmd.association_objs
                ]
            },
        )
        return [model.CaseTypeSetMember(**item) for item in data]

    def col_set_col_update_association(
        self,
        cmd: command.ColSetColUpdateAssociationCommand,
    ) -> list[model.ColSetMember]:
        data = self._call_json(
            cmd,
            "PUT",
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/cols",
            json_body={
                "col_set_members": [
                    json.loads(x.model_dump_json()) for x in cmd.association_objs
                ]
            },
        )
        return [model.ColSetMember(**item) for item in data]

    def retrieve_complete_case_type(
        self, cmd: command.RetrieveCompleteCaseTypeCommand
    ) -> model.CompleteCaseType:
        data = self._call_json(
            cmd, "GET", params={"case_type_id": str(cmd.case_type_id)}
        )
        return model.CompleteCaseType(**data)

    def create_case_set(self, cmd: command.CreateCaseSetCommand) -> model.CaseSet:
        data = self._call_json(
            cmd,
            "POST",
            json_body={
                "case_set": json.loads(cmd.case_set.model_dump_json()),
                "data_collection_ids": [str(x) for x in cmd.data_collection_ids],
                "case_ids": (
                    [str(x) for x in cmd.case_ids] if cmd.case_ids is not None else None
                ),
            },
        )
        return model.CaseSet(**data)

    def retrieve_case_stats(
        self, cmd: command.RetrieveCaseStatsCommand
    ) -> list[model.CaseStats]:
        # RetrieveCaseStatsCommand is handled by two different endpoints depending on
        # which filter is set: by CaseType (default route) or by CaseSet.
        base_route = self.get_route(cmd)
        if cmd.case_set_ids is not None:
            route = base_route.replace(
                "/retrieve/case_type_stats", "/retrieve/case_set_stats"
            )
            json_body: dict[str, Any] = {
                "case_set_ids": [str(x) for x in cmd.case_set_ids]
            }
        else:
            route = base_route
            json_body = {
                "case_type_ids": (
                    [str(x) for x in cmd.case_type_ids]
                    if cmd.case_type_ids is not None
                    else None
                ),
                "datetime_range_filter": (
                    json.loads(cmd.datetime_range_filter.model_dump_json())
                    if cmd.datetime_range_filter is not None
                    else None
                ),
            }
        data = self._call_json(cmd, "POST", route=route, json_body=json_body)
        return [model.CaseStats(**item) for item in data]

    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        data = self._call_json(
            cmd,
            "POST",
            json_body={
                "case_type_id": str(cmd.case_type_id),
                "case_ids": [str(x) for x in cmd.case_ids],
            },
        )
        return [model.Case(**item) for item in data]

    def retrieve_case_rights(
        self, cmd: command.RetrieveCaseRightsCommand
    ) -> list[model.CaseRights]:
        data = self._call_json(
            cmd,
            "POST",
            json_body={
                "case_type_id": str(cmd.case_type_id),
                "case_ids": [str(x) for x in cmd.case_ids],
            },
        )
        return [model.CaseRights(**item) for item in data]

    def retrieve_case_set_rights(
        self, cmd: command.RetrieveCaseSetRightsCommand
    ) -> list[model.CaseSetRights]:
        data = self._call_json(
            cmd, "POST", json_body=[str(x) for x in cmd.case_set_ids]
        )
        return [model.CaseSetRights(**item) for item in data]

    def retrieve_phylogenetic_tree_by_cases(
        self, cmd: command.RetrievePhylogeneticTreeByCasesCommand
    ) -> model.PhylogeneticTree:
        data = self._call_json(
            cmd,
            "POST",
            json_body={
                "case_type_id": str(cmd.case_type_id),
                "genetic_distance_col_id": str(cmd.genetic_distance_col_id),
                "tree_algorithm_code": cmd.tree_algorithm.value,
                "case_ids": [str(x) for x in cmd.case_ids],
            },
        )
        return model.PhylogeneticTree(**data)

    def retrieve_similar_cases(
        self, cmd: command.RetrieveSimilarCasesCommand
    ) -> command.RetrieveSimilarCasesReturnValue:
        data = self._call_json(
            cmd,
            "POST",
            json_body={
                "case_type_id": str(cmd.case_type_id),
                "case_ids": [str(x) for x in cmd.case_ids],
                "genetic_distance_col_id": str(cmd.genetic_distance_col_id),
                "max_distance": cmd.max_distance,
            },
        )
        return command.RetrieveSimilarCasesReturnValue(**data)

    def retrieve_genetic_sequence_fasta_by_case(
        self, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
    ) -> Iterable[str]:
        # Streams multipart form data, so this can't go through _call_json.
        # This endpoint also authenticates via a form field rather than a header,
        # so the bearer token is pulled back out of the normal Authorization header.
        headers = self.get_headers(cmd)
        route = self.get_route(cmd)
        token = headers.get("Authorization", "").removeprefix("Bearer ")
        form_data = {
            "token": token,
            "case_type_id": str(cmd.case_type_id),
            "genetic_sequence_col_id": str(cmd.genetic_sequence_col_id),
            "case_ids": [str(x) for x in cmd.case_ids],
            "file_name": "cases.fasta",
        }

        def _iter_fasta_generator() -> Iterable[str]:
            with self.get_client(cmd) as client:
                with client.stream("POST", route, data=form_data) as resp:
                    resp.raise_for_status()
                    for chunk in resp.iter_bytes():
                        yield chunk.decode()

        return _iter_fasta_generator()

    def create_file_for_read_set(
        self, cmd: command.CreateFileForReadSetCommand
    ) -> UUID:
        data = self._call_json(
            cmd,
            "POST",
            route=f"{self.get_route(cmd)}/{cmd.case_id}/{cmd.col_id}",
            json_body={
                "file_content": base64.b64encode(cmd.file_content).decode(),
                "is_fwd": cmd.is_fwd,
                "file_format": cmd.file_format.value,
                "file_compression": cmd.file_compression.value,
            },
        )
        return UUID(data)

    def create_file_for_seq(self, cmd: command.CreateFileForSeqCommand) -> UUID:
        data = self._call_json(
            cmd,
            "POST",
            route=f"{self.get_route(cmd)}/{cmd.case_id}/{cmd.col_id}",
            json_body={
                "file_content": base64.b64encode(cmd.file_content).decode(),
                "file_format": cmd.file_format.value,
                "file_compression": cmd.file_compression.value,
            },
        )
        return UUID(data)

    def retrieve_protocols(
        self, cmd: command.RetrieveProtocolsCommand
    ) -> list[seqdb_model.Protocol]:
        # RetrieveProtocolsCommand is handled by two different GET endpoints
        # depending on protocol_type; the registered route is just a placeholder
        # so RemoteApp.apply_handler finds a route for this command class.
        base_route = self.get_route(cmd)
        if cmd.protocol_type == seqdb_enum.ProtocolType.ASSEMBLY:
            route = base_route.replace(
                "/retrieve/sequencing_protocols", "/retrieve/assembly_protocols"
            )
        else:
            route = base_route
        data = self._call_json(cmd, "GET", route=route)
        return [seqdb_model.Protocol(**item) for item in data]

    def retrieve_is_own_cases(
        self, cmd: command.RetrieveIsOwnCasesCommand
    ) -> dict[UUID, bool]:
        data = self._call_json(
            cmd,
            "POST",
            json_body={
                "case_type_id": str(cmd.case_type_id),
                "case_ids": [str(x) for x in cmd.case_ids],
            },
        )
        return {UUID(k): v for k, v in data.items()}

    def disease_etiological_agent_update_association(
        self, cmd: command.DiseaseEtiologicalAgentUpdateAssociationCommand
    ) -> list[model.Etiology]:
        data = self._call_json(
            cmd,
            "PUT",
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/etiological_agents",
            json_body={
                "etiologies": [
                    json.loads(x.model_dump_json()) for x in cmd.association_objs
                ]
            },
        )
        return [model.Etiology(**item) for item in data]
