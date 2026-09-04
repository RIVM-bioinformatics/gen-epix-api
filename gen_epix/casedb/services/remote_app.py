"""Provide an HTTP command client for remote casedb applications.

The client extends commondb collaboration with casedb routes, request models,
response conversion, streaming, and command-specific timeouts.
"""

import base64
from collections.abc import Iterable
from typing import Any
from uuid import UUID

from gen_epix.casedb import api
from gen_epix.casedb.domain import DOMAIN, command, model
from gen_epix.commondb.services import CommondbRemoteApp as CommondbRemoteApp
from gen_epix.fastapp.enum import HttpMethod
from gen_epix.fastapp.model import Command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model


class CasedbRemoteApp(CommondbRemoteApp):
    """Encapsulates remote casedb command dispatch over HTTP.

    Initialization first registers inherited commondb collaboration and generated
    CRUD handling, then adds casedb-specific routes and handlers. Handler methods
    translate command data to API request bodies and convert responses back to
    domain models.
    """

    DEFAULT_ROUTE_PREFIX = "/v1"

    DEFAULT_OAUTH_TOKEN_REFRESH_MARGIN = 60  # seconds

    ROUTE_MAP: dict[type[Command], str] = {
        command.UploadCasesCommand: "/upload/cases",
        command.UpdateCaseCreatedInDataCollectionCommand: (
            "/update_case_created_in_data_collection"
        ),
        command.RetrieveCasesByQueryCommand: "/retrieve/case_ids_by_query",
        command.RetrieveCaseCohortLinksByCaseTypeCommand: "/retrieve/case_cohort_links_by_case_type",
        command.CaseTypeSetCaseTypeUpdateAssociationCommand: "/case_type_sets",
        command.ColSetColUpdateAssociationCommand: "/col_sets",
        command.RetrieveCompleteCaseTypeCommand: "/complete_case_types",
        command.CreateCaseSetCommand: "/create/case_set",
        command.RetrieveCaseSetStatsCommand: "/retrieve/case_set_stats",
        command.RetrieveCaseTypeStatsCommand: "/retrieve/case_type_stats",
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
        command.RegionRelationCrudCommand: 45.0,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the client and register casedb routes and command handlers.

        Args:
            *args: Positional remote-app connection and authentication settings.
            **kwargs: Keyword remote-app connection and authentication settings.
        """
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
            command.UpdateCaseCreatedInDataCollectionCommand,
            self.update_case_created_in_data_collection,
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
            command.RetrieveCaseSetStatsCommand, self.retrieve_case_set_stats
        )
        self.register_handler(
            command.RetrieveCaseTypeStatsCommand, self.retrieve_case_type_stats
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
        """Retrieve cohort links for a given case type."""
        request_body = api.RetrieveCaseCohortLinksByCaseTypeRequestBody(
            case_type_id=cmd.case_type_id
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return [model.CaseCohortLink(**x) for x in response_body]

    def retrieve_cases_by_query(
        self,
        cmd: command.RetrieveCasesByQueryCommand,
    ) -> model.CaseQueryResult:
        """Retrieve cases matching the given query."""
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=cmd.case_query,
        )
        return model.CaseQueryResult(**response_body)

    def upload_cases(
        self,
        cmd: command.UploadCasesCommand,
    ) -> model.CaseBatchUploadResult:
        """Upload a batch of cases."""
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, model=cmd, exclude={"user"}
        )
        return model.CaseBatchUploadResult(**response_body)

    def update_case_created_in_data_collection(
        self,
        cmd: command.UpdateCaseCreatedInDataCollectionCommand,
    ) -> list[model.Case]:
        """Move cases to a different creating data collection over HTTP."""
        request_body = api.UpdateCaseCreatedInDataCollectionRequestBody(
            case_ids=cmd.case_ids,
            data_collection_id=cmd.data_collection_id,
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return [model.Case(**x) for x in response_body]

    def case_type_set_case_type_update_association(
        self,
        cmd: command.CaseTypeSetCaseTypeUpdateAssociationCommand,
    ) -> list[model.CaseTypeSetMember]:
        """Update case type associations for a case type set."""
        request_body = api.CaseTypeSetCaseTypeUpdateAssociationRequestBody(
            case_type_set_members=cmd.association_objs
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.PUT,
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/case_types",
            model=request_body,
        )
        return [model.CaseTypeSetMember(**x) for x in response_body]

    def col_set_col_update_association(
        self,
        cmd: command.ColSetColUpdateAssociationCommand,
    ) -> list[model.ColSetMember]:
        """Update column associations for a column set."""
        request_body = api.ColSetColUpdateAssociationRequestBody(
            col_set_members=cmd.association_objs
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.PUT,
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/cols",
            model=request_body,
        )
        return [model.ColSetMember(**x) for x in response_body]

    def retrieve_complete_case_type(
        self, cmd: command.RetrieveCompleteCaseTypeCommand
    ) -> model.CompleteCaseType:
        """Retrieve the full definition of a case type."""
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.GET, params={"case_type_id": str(cmd.case_type_id)}
        )
        return model.CompleteCaseType(**response_body)

    def create_case_set(self, cmd: command.CreateCaseSetCommand) -> model.CaseSet:
        """Create a new case set."""
        request_body = api.CreateCaseSetRequestBody(
            case_set=cmd.case_set,
            data_collection_ids=cmd.data_collection_ids,
            case_ids=cmd.case_ids,
        )
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return model.CaseSet(**response_body)

    def retrieve_case_type_stats(
        self, cmd: command.RetrieveCaseTypeStatsCommand
    ) -> list[model.CaseStats]:
        """Retrieve statistics per case type."""
        request_body = api.RetrieveCaseTypeStatsRequestBody(
            case_type_ids=cmd.case_type_ids,
            datetime_range_filter=cmd.datetime_range_filter,
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, route=self.get_route(cmd), model=request_body
        )
        return [model.CaseStats(**x) for x in response_body]

    def retrieve_case_set_stats(
        self, cmd: command.RetrieveCaseSetStatsCommand
    ) -> list[model.CaseStats]:
        """Retrieve statistics per case set."""
        request_body = api.RetrieveCaseSetStatsRequestBody(
            case_set_ids=cmd.case_set_ids
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, model=request_body
        )
        return [model.CaseStats(**x) for x in response_body]

    def retrieve_cases_by_id(
        self, cmd: command.RetrieveCasesByIdCommand
    ) -> list[model.Case]:
        """Retrieve cases by their IDs."""
        request_body = api.RetrieveCasesByIdRequestBody(
            case_type_id=cmd.case_type_id,
            case_ids=cmd.case_ids,
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, model=request_body
        )
        return [model.Case(**x) for x in response_body]

    def retrieve_case_rights(
        self, cmd: command.RetrieveCaseRightsCommand
    ) -> list[model.CaseRights]:
        """Retrieve access rights for cases."""
        request_body = api.RetrieveCaseRightsRequestBody(
            case_type_id=cmd.case_type_id,
            case_ids=cmd.case_ids,
        )
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, model=request_body
        )
        return [model.CaseRights(**x) for x in response_body]

    def retrieve_case_set_rights(
        self, cmd: command.RetrieveCaseSetRightsCommand
    ) -> list[model.CaseSetRights]:
        """Retrieve access rights for case sets."""
        json_body = [str(x) for x in cmd.case_set_ids]
        response_body: list[dict[str, Any]] = self.request(  # type: ignore[assignment]
            cmd, HttpMethod.POST, json_body=json_body
        )
        return [model.CaseSetRights(**x) for x in response_body]

    def retrieve_phylogenetic_tree_by_cases(
        self, cmd: command.RetrievePhylogeneticTreeByCasesCommand
    ) -> model.PhylogeneticTree:
        """Compute and retrieve a phylogenetic tree for the given cases."""
        request_body = api.RetrievePhylogeneticTreeRequestBody(
            case_type_id=cmd.case_type_id,
            genetic_distance_col_id=cmd.genetic_distance_col_id,
            tree_algorithm_code=cmd.tree_algorithm,
            case_ids=cmd.case_ids,
        )
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return model.PhylogeneticTree(**response_body)

    def retrieve_similar_cases(
        self, cmd: command.RetrieveSimilarCasesCommand
    ) -> command.RetrieveSimilarCasesReturnValue:
        """Retrieve cases similar to the given cases within a distance threshold."""
        request_body = api.RetrieveSimilarCasesRequestBody(
            case_type_id=cmd.case_type_id,
            case_ids=cmd.case_ids,
            genetic_distance_col_id=cmd.genetic_distance_col_id,
            max_distance=cmd.max_distance,
        )
        response_body: dict[str, Any] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return command.RetrieveSimilarCasesReturnValue(**response_body)

    def retrieve_genetic_sequence_fasta_by_case(
        self, cmd: command.RetrieveGeneticSequenceFastaByCaseCommand
    ) -> Iterable[str]:
        """Stream genetic sequence FASTA data for cases."""
        # Auth token is passed as a form field; the endpoint does not use the
        # Authorization header.
        token = self.get_headers(cmd).get("Authorization", "").removeprefix("Bearer ")
        return self.stream(
            cmd,
            HttpMethod.POST,
            form_data={
                "token": token,
                "case_type_id": str(cmd.case_type_id),
                "genetic_sequence_col_id": str(cmd.genetic_sequence_col_id),
                "case_ids": [str(x) for x in cmd.case_ids],
                "file_name": "cases.fasta",
            },
        )

    def create_file_for_read_set(
        self, cmd: command.CreateFileForReadSetCommand
    ) -> UUID:
        """Create a file associated with a read set column."""
        request_body = api.CreateFileForReadSetRequestBody(
            file_content=base64.b64encode(cmd.file_content).decode(),
            is_fwd=cmd.is_fwd,
            file_format=cmd.file_format,
            file_compression=cmd.file_compression,
        )
        route = f"{self.get_route(cmd)}/{cmd.case_id}/{cmd.col_id}"
        response_body = self.request(
            cmd,
            HttpMethod.POST,
            route=route,
            model=request_body,
        )
        return UUID(response_body)

    def create_file_for_seq(self, cmd: command.CreateFileForSeqCommand) -> UUID:
        """Create a file associated with a sequence column."""
        request_body = api.CreateFileForSeqRequestBody(
            file_content=base64.b64encode(cmd.file_content).decode(),
            file_format=cmd.file_format,
            file_compression=cmd.file_compression,
        )
        route = f"{self.get_route(cmd)}/{cmd.case_id}/{cmd.col_id}"
        response_body = self.request(
            cmd,
            HttpMethod.POST,
            route=route,
            model=request_body,
        )
        return UUID(response_body)

    def retrieve_protocols(
        self, cmd: command.RetrieveProtocolsCommand
    ) -> list[seqdb_model.Protocol]:
        """Retrieve sequencing or assembly protocols."""
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
        request_body: list[dict[str, Any]] = self.request(cmd, HttpMethod.GET, route=route)  # type: ignore[assignment]
        return [seqdb_model.Protocol(**x) for x in request_body]

    def retrieve_is_own_cases(
        self, cmd: command.RetrieveIsOwnCasesCommand
    ) -> dict[UUID, bool]:
        """Check whether the user owns each of the given cases."""
        request_body = api.RetrieveCasesByIdRequestBody(
            case_type_id=cmd.case_type_id,
            case_ids=cmd.case_ids,
        )
        response_body: dict[str, bool] = self.request(  # type: ignore[assignment]
            cmd,
            HttpMethod.POST,
            model=request_body,
        )
        return {UUID(x): y for x, y in response_body.items()}

    def disease_etiological_agent_update_association(
        self, cmd: command.DiseaseEtiologicalAgentUpdateAssociationCommand
    ) -> list[model.Etiology]:
        """Update etiological agent associations for a disease."""
        request_body = api.DiseaseEtiologicalAgentUpdateAssociationRequestBody(
            etiologies=cmd.association_objs
        )
        response_body = self.request(
            cmd,
            HttpMethod.PUT,
            model=request_body,
            route=f"{self.get_route(cmd)}/{cmd.obj_id1}/etiological_agents",
        )
        return [model.Etiology(**x) for x in response_body]
