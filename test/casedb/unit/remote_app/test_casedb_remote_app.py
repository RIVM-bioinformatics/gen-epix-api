"""Unit tests for the non-CRUD command handlers on CasedbRemoteApp.

Each test builds a real CasedbRemoteApp, mocks the underlying httpx client,
invokes the handler directly, and checks the HTTP call it makes (method,
URL, body) plus that the response is parsed into the right model. This
guards against route/model drift between the API and the RemoteApp handler.
"""

from __future__ import annotations

import base64
import json
from test.util.mock_compat import MagicMock, Mock, patch
from typing import Any
from uuid import uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.casedb.services.remote_app import CasedbRemoteApp
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model


def _mock_response(json_data: Any, status_code: int = 200) -> Mock:
    response = Mock()
    response.status_code = status_code
    response.content = b"1"
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


@pytest.fixture
def app() -> CasedbRemoteApp:
    return CasedbRemoteApp(host="example.org", port=8000)


@pytest.fixture
def mock_client() -> Any:
    with patch("gen_epix.fastapp.remote_app.httpx.Client") as mock_client_class:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        mock_client_class.return_value = client
        yield client


class TestNonCrudHandlers:
    """Test the hand-written (non-CRUD) command handlers."""

    def test_case_type_set_case_type_update_association(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_set_id = uuid4()
        member = model.CaseTypeSetMember(
            case_type_set_id=case_type_set_id, case_type_id=uuid4()
        )
        cmd = command.CaseTypeSetCaseTypeUpdateAssociationCommand(
            user=None, obj_id1=case_type_set_id, association_objs=[member]
        )
        data = [json.loads(member.model_dump_json())]
        mock_client.request.return_value = _mock_response(data)
        result = app.case_type_set_case_type_update_association(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "PUT"
        route = app._routes[command.CaseTypeSetCaseTypeUpdateAssociationCommand]
        assert url == f"{route}/{case_type_set_id}/case_types"
        assert json_body == {
            "case_type_set_members": [json.loads(member.model_dump_json())]
        }
        assert result == [model.CaseTypeSetMember(**data[0])]

    def test_col_set_col_update_association(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        col_set_id = uuid4()
        member = model.ColSetMember(col_set_id=col_set_id, col_id=uuid4())
        cmd = command.ColSetColUpdateAssociationCommand(
            user=None, obj_id1=col_set_id, association_objs=[member]
        )
        data = [json.loads(member.model_dump_json())]
        mock_client.request.return_value = _mock_response(data)
        result = app.col_set_col_update_association(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "PUT"
        route = app._routes[command.ColSetColUpdateAssociationCommand]
        assert url == f"{route}/{col_set_id}/cols"
        assert result == [model.ColSetMember(**data[0])]

    def test_retrieve_complete_case_type(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_id = uuid4()
        data: dict[str, Any] = {
            "name": "CT",
            "user_id": None,
            "etiologies": {},
            "etiological_agents": {},
            "ref_dims": {},
            "ref_cols": {},
            "dims": {},
            "cols": {},
            "genetic_distance_protocols": {},
            "tree_algorithms": {},
            "case_type_access_abacs": {},
            "case_type_share_abacs": {},
            "case_date_dim_id": None,
        }
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_complete_case_type(
            command.RetrieveCompleteCaseTypeCommand(
                user=None, case_type_id=case_type_id
            )
        )
        method, url = mock_client.request.call_args.args
        params = mock_client.request.call_args.kwargs["params"]
        assert method == "GET"
        assert url == app._routes[command.RetrieveCompleteCaseTypeCommand]
        assert params == {"case_type_id": str(case_type_id)}
        assert result == model.CompleteCaseType(**data)

    def test_create_case_set(self, app: CasedbRemoteApp, mock_client: Any) -> None:
        case_set = model.CaseSet(
            case_type_id=uuid4(),
            created_in_data_collection_id=uuid4(),
            name="Set 1",
            code="S1",
            description="desc",
            case_set_category_id=uuid4(),
            case_set_status_id=uuid4(),
        )
        data_collection_ids = {uuid4()}
        case_ids = {uuid4()}
        cmd = command.CreateCaseSetCommand(
            user=None,
            case_set=case_set,
            data_collection_ids=data_collection_ids,
            case_ids=case_ids,
        )
        data = json.loads(case_set.model_dump_json())
        mock_client.request.return_value = _mock_response(data)
        result = app.create_case_set(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.CreateCaseSetCommand]
        assert json_body["case_set"] == json.loads(case_set.model_dump_json())
        assert set(json_body["data_collection_ids"]) == {
            str(x) for x in data_collection_ids
        }
        assert set(json_body["case_ids"]) == {str(x) for x in case_ids}
        assert result == model.CaseSet(**data)

    def test_retrieve_case_stats_by_case_type(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_id = uuid4()
        cmd = command.RetrieveCaseTypeStatsCommand(
            user=None, case_type_ids={case_type_id}
        )
        data = [{"case_type_id": str(case_type_id)}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_case_type_stats(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        assert url == app._routes[command.RetrieveCaseTypeStatsCommand]
        assert result == [model.CaseStats(**data[0])]

    def test_retrieve_case_stats_by_case_set(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_set_id = uuid4()
        case_type_id = uuid4()
        cmd = command.RetrieveCaseSetStatsCommand(user=None, case_set_ids={case_set_id})
        data = [{"case_set_id": str(case_set_id), "case_type_id": str(case_type_id)}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_case_set_stats(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        base_route = app._routes[command.RetrieveCaseSetStatsCommand]
        assert url == base_route
        assert json_body == {
            "case_set_ids": [str(case_set_id)],
            "datetime_range_filter": None,
        }
        assert result == [model.CaseStats(**data[0])]

    def test_retrieve_cases_by_id(self, app: CasedbRemoteApp, mock_client: Any) -> None:
        case_type_id = uuid4()
        case_id = uuid4()
        cmd = command.RetrieveCasesByIdCommand(
            user=None, case_type_id=case_type_id, case_ids=[case_id]
        )
        data = [
            {
                "case_type_id": str(case_type_id),
                "created_in_data_collection_id": str(uuid4()),
                "timed_at": "2024-01-01T00:00:00Z",
                "content": {},
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_cases_by_id(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.RetrieveCasesByIdCommand]
        assert json_body == {
            "case_type_id": str(case_type_id),
            "case_ids": [str(case_id)],
        }
        assert result == [model.Case(**data[0])]

    def test_retrieve_case_rights(self, app: CasedbRemoteApp, mock_client: Any) -> None:
        case_type_id = uuid4()
        case_id = uuid4()
        cmd = command.RetrieveCaseRightsCommand(
            user=None, case_type_id=case_type_id, case_ids=[case_id]
        )
        data = [
            {
                "created_in_data_collection_id": str(uuid4()),
                "case_type_id": str(case_type_id),
                "data_collection_ids": [],
                "is_full_access": True,
                "add_data_collection_ids": [],
                "remove_data_collection_ids": [],
                "can_delete": True,
                "shared_in_data_collection_ids": [],
                "case_id": str(case_id),
                "read_col_ids": [],
                "write_col_ids": [],
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_case_rights(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        assert url == app._routes[command.RetrieveCaseRightsCommand]
        assert result == [model.CaseRights(**data[0])]

    def test_retrieve_case_set_rights(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_set_id = uuid4()
        cmd = command.RetrieveCaseSetRightsCommand(
            user=None, case_set_ids=[case_set_id]
        )
        data = [
            {
                "created_in_data_collection_id": str(uuid4()),
                "case_type_id": str(uuid4()),
                "data_collection_ids": [],
                "is_full_access": True,
                "add_data_collection_ids": [],
                "remove_data_collection_ids": [],
                "can_delete": True,
                "shared_in_data_collection_ids": [],
                "case_set_id": str(case_set_id),
                "read_case_set": True,
                "write_case_set": True,
            }
        ]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_case_set_rights(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.RetrieveCaseSetRightsCommand]
        assert json_body == [str(case_set_id)]
        assert result == [model.CaseSetRights(**data[0])]

    def test_retrieve_phylogenetic_tree_by_cases(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_id = uuid4()
        genetic_distance_col_id = uuid4()
        case_id = uuid4()
        cmd = command.RetrievePhylogeneticTreeByCasesCommand(
            user=None,
            case_type_id=case_type_id,
            tree_algorithm=enum.TreeAlgorithmType.UPGMA,
            genetic_distance_col_id=genetic_distance_col_id,
            case_ids=[case_id],
        )
        data = {"tree_algorithm_code": "UPGMA", "newick_repr": "(a,b);"}
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_phylogenetic_tree_by_cases(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.RetrievePhylogeneticTreeByCasesCommand]
        assert json_body == {
            "case_type_id": str(case_type_id),
            "genetic_distance_col_id": str(genetic_distance_col_id),
            "tree_algorithm_code": "UPGMA",
            "case_ids": [str(case_id)],
        }
        assert result == model.PhylogeneticTree(**data)

    def test_retrieve_similar_cases(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_id = uuid4()
        genetic_distance_col_id = uuid4()
        case_id = uuid4()
        cmd = command.RetrieveSimilarCasesCommand(
            user=None,
            case_type_id=case_type_id,
            max_distance=1.5,
            genetic_distance_col_id=genetic_distance_col_id,
            case_ids=[case_id],
        )
        data = {"cases": [{"id": str(uuid4()), "timed_at": "2024-01-01T00:00:00Z"}]}
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_similar_cases(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.RetrieveSimilarCasesCommand]
        assert json_body == {
            "case_type_id": str(case_type_id),
            "case_ids": [str(case_id)],
            "genetic_distance_col_id": str(genetic_distance_col_id),
            "max_distance": 1.5,
        }
        assert result == command.RetrieveSimilarCasesReturnValue(**data)

    def test_retrieve_genetic_sequence_fasta_by_case(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_id = uuid4()
        genetic_sequence_col_id = uuid4()
        case_id = uuid4()
        cmd = command.RetrieveGeneticSequenceFastaByCaseCommand(
            user=None,
            case_type_id=case_type_id,
            genetic_sequence_col_id=genetic_sequence_col_id,
            case_ids=[case_id],
        )
        stream_response = MagicMock()
        stream_response.raise_for_status.return_value = None
        stream_response.iter_bytes.return_value = [b">seq1\n", b"ACGT\n"]
        mock_client.stream.return_value.__enter__.return_value = stream_response
        mock_client.stream.return_value.__exit__.return_value = None

        result = list(app.retrieve_genetic_sequence_fasta_by_case(cmd))

        assert result == [">seq1\n", "ACGT\n"]
        call_args = mock_client.stream.call_args
        assert call_args.args[0] == "POST"
        assert (
            call_args.args[1]
            == app._routes[command.RetrieveGeneticSequenceFastaByCaseCommand]
        )
        form_data = call_args.kwargs["data"]
        assert form_data["case_type_id"] == str(case_type_id)
        assert form_data["genetic_sequence_col_id"] == str(genetic_sequence_col_id)
        assert form_data["case_ids"] == [str(case_id)]

    def test_create_file_for_read_set(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_id = uuid4()
        col_id = uuid4()
        file_id = uuid4()
        cmd = command.CreateFileForReadSetCommand(
            user=None,
            case_id=case_id,
            col_id=col_id,
            file_content=b"raw-bytes",
            is_fwd=True,
        )
        mock_client.request.return_value = _mock_response(str(file_id))
        result = app.create_file_for_read_set(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        route = app._routes[command.CreateFileForReadSetCommand]
        assert url == f"{route}/{case_id}/{col_id}"
        assert json_body["file_content"] == base64.b64encode(b"raw-bytes").decode()
        assert json_body["is_fwd"] is True
        assert result == file_id

    def test_create_file_for_seq(self, app: CasedbRemoteApp, mock_client: Any) -> None:
        case_id = uuid4()
        col_id = uuid4()
        file_id = uuid4()
        cmd = command.CreateFileForSeqCommand(
            user=None, case_id=case_id, col_id=col_id, file_content=b"raw-bytes"
        )
        mock_client.request.return_value = _mock_response(str(file_id))
        result = app.create_file_for_seq(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "POST"
        route = app._routes[command.CreateFileForSeqCommand]
        assert url == f"{route}/{case_id}/{col_id}"
        assert result == file_id

    def test_retrieve_protocols_sequencing(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        cmd = command.RetrieveProtocolsCommand(
            user=None, protocol_type=seqdb_enum.ProtocolType.SEQUENCING
        )
        data = [{"code": "P1", "protocol_type": "SEQUENCING"}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_protocols(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "GET"
        assert url == app._routes[command.RetrieveProtocolsCommand]
        assert result == [seqdb_model.Protocol(**data[0])]

    def test_retrieve_protocols_assembly(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        cmd = command.RetrieveProtocolsCommand(
            user=None, protocol_type=seqdb_enum.ProtocolType.ASSEMBLY
        )
        data = [{"code": "P2", "protocol_type": "ASSEMBLY"}]
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_protocols(cmd)
        method, url = mock_client.request.call_args.args
        base_route = app._routes[command.RetrieveProtocolsCommand]
        assert method == "GET"
        assert url == base_route.replace(
            "/retrieve/sequencing_protocols", "/retrieve/assembly_protocols"
        )
        assert result == [seqdb_model.Protocol(**data[0])]

    def test_retrieve_is_own_cases(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        case_type_id = uuid4()
        case_id = uuid4()
        cmd = command.RetrieveIsOwnCasesCommand(
            user=None, case_type_id=case_type_id, case_ids=[case_id]
        )
        data = {str(case_id): True}
        mock_client.request.return_value = _mock_response(data)
        result = app.retrieve_is_own_cases(cmd)
        method, url = mock_client.request.call_args.args
        json_body = mock_client.request.call_args.kwargs["json"]
        assert method == "POST"
        assert url == app._routes[command.RetrieveIsOwnCasesCommand]
        assert json_body == {
            "case_type_id": str(case_type_id),
            "case_ids": [str(case_id)],
        }
        assert result == {case_id: True}

    def test_disease_etiological_agent_update_association(
        self, app: CasedbRemoteApp, mock_client: Any
    ) -> None:
        disease_id = uuid4()
        etiology = model.Etiology(disease_id=disease_id, etiological_agent_id=uuid4())
        cmd = command.DiseaseEtiologicalAgentUpdateAssociationCommand(
            user=None, obj_id1=disease_id, association_objs=[etiology]
        )
        data = [json.loads(etiology.model_dump_json())]
        mock_client.request.return_value = _mock_response(data)
        result = app.disease_etiological_agent_update_association(cmd)
        method, url = mock_client.request.call_args.args
        assert method == "PUT"
        route = app._routes[command.DiseaseEtiologicalAgentUpdateAssociationCommand]
        assert url == f"{route}/{disease_id}/etiological_agents"
        assert result == [model.Etiology(**data[0])]
