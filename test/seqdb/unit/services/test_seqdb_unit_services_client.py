"""Unit tests for SeqdbClient create_calculate_phylogenetic_tree_handler function."""

import json
from datetime import datetime
from test.util.mock_compat import MagicMock, Mock, patch
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import httpx
import pytest

from gen_epix.casedb.domain import enum as enum
from gen_epix.casedb.domain import model as model
from gen_epix.fastapp.enum import CrudOperation, HttpMethod
from gen_epix.seqdb.api import CalculatePhylogeneticTreeRequestBody
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.seqdb.services.client import SeqdbClient


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestSeqdbClient:
    """Test the SeqdbClient class with focus on create_calculate_phylogenetic_tree_handler."""

    @pytest.fixture
    def mock_user(self) -> seqdb_model.User:
        """Create a mock user for testing."""
        from gen_epix.seqdb.domain.enum import Role

        return seqdb_model.User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            name="Test User",
            organization_id=uuid4(),
            roles={Role.APP_ADMIN},
        )

    @pytest.fixture
    def client(self) -> SeqdbClient:
        """Create a SeqdbClient instance for testing."""
        return SeqdbClient(host="localhost", port=8001)

    @pytest.fixture
    def sample_command(
        self, mock_user: seqdb_model.User
    ) -> seqdb_command.CalculatePhylogeneticTreeCommand:
        """Create a sample command for testing."""
        return seqdb_command.CalculatePhylogeneticTreeCommand(
            user=mock_user,
            protocol_id=uuid4(),
            tree_algorithm=seqdb_enum.TreeAlgorithm.UPGMA,
            seq_profile_ids=[uuid4(), uuid4()],
            leaf_names=["seq1", "seq2"],
        )

    @pytest.fixture
    def sample_response_data(self) -> dict[str, Any]:
        """Create sample response data for testing."""
        return {
            "profile_ids": [str(uuid4()), str(uuid4())],
            "leaf_names": ["seq1", "seq2"],
            "newick_repr": "(seq1:0.1,seq2:0.2);",
            "tree_algorithm": "UPGMA",
            "protocol_id": str(uuid4()),
        }

    def test_route_registration(self, client: SeqdbClient) -> None:
        """Test that the handler registers the correct route."""
        expected_route = (
            client.host_url
            + client._default_route_prefix
            + "/calculate/phylogenetic_tree"
        )

        # Verify the route is registered
        assert seqdb_command.CalculatePhylogeneticTreeCommand in client._routes
        registered_route = client._routes[
            seqdb_command.CalculatePhylogeneticTreeCommand
        ]
        assert registered_route == expected_route

    @patch("httpx.Client")
    def test_successful_request_with_full_response(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
        sample_response_data: dict[str, Any],
        mock_user: seqdb_model.User,
    ) -> None:
        """Test successful HTTP request with complete response data."""
        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_data
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # No need to modify command attributes - they're already set in fixture

        # Mock get_headers to return test headers (now synchronous function)
        client.get_headers = Mock(return_value={"Authorization": "Bearer test_token"})

        # Call the handler directly
        result = client.calculate_phylogenetic_tree(sample_command)

        # Verify the result - since SeqdbClient returns seqdb_model.PhylogeneticTree,
        # we need to check for seqdb model attributes
        assert isinstance(result, seqdb_model.PhylogeneticTree)
        assert result.tree_algorithm == seqdb_enum.TreeAlgorithm.UPGMA
        assert result.profile_ids is not None
        assert len(result.profile_ids) == 2
        assert result.leaf_names is not None
        assert len(result.leaf_names) == 2
        assert result.newick_repr == "(seq1:0.1,seq2:0.2);"

        # Verify the HTTP request was made correctly
        expected_request_body = CalculatePhylogeneticTreeRequestBody(
            protocol_id=sample_command.protocol_id,
            tree_algorithm=sample_command.tree_algorithm,
            seq_profile_ids=sample_command.seq_profile_ids,
            leaf_names=sample_command.leaf_names,
        )

        mock_client.request.assert_called_once_with(
            "POST",
            client.get_route(sample_command),
            json=json.loads(expected_request_body.model_dump_json()),
            params=None,
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("httpx.Client")
    def test_successful_request_without_leaf_ids(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
        mock_user: seqdb_model.User,
    ) -> None:
        """Test successful HTTP request with response data missing leaf_ids."""
        # Setup response without leaf_names
        response_data = {
            "profile_ids": [str(uuid4()), str(uuid4())],
            "newick_repr": "(seq1:0.1,seq2:0.2);",
            "tree_algorithm": "UPGMA",
            "protocol_id": str(uuid4()),
        }

        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = response_data
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup remote app mock
        client.get_headers = Mock(return_value={})

        # Call the handler directly
        result = client.calculate_phylogenetic_tree(sample_command)

        # Verify the result - check seqdb model attributes
        assert isinstance(result, seqdb_model.PhylogeneticTree)
        assert result.leaf_names is None
        assert result.profile_ids is not None
        assert len(result.profile_ids) == 2
        assert result.newick_repr == "(seq1:0.1,seq2:0.2);"

    @patch("httpx.Client")
    def test_empty_response_returns_none(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
    ) -> None:
        """Test that empty/null response data returns None."""
        # Setup mock HTTP client with empty response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = None
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        client.get_headers = Mock(return_value={})

        # Call the handler directly
        result = client.calculate_phylogenetic_tree(sample_command)

        # Verify None is returned
        assert result is None

    @patch("httpx.Client")
    def test_empty_dict_response_returns_none(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
    ) -> None:
        """Test that empty dict response returns None."""
        # Setup mock HTTP client with empty dict response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        client.get_headers = Mock(return_value={})

        # Call the handler directly
        result = client.calculate_phylogenetic_tree(sample_command)

        # Verify None is returned
        assert result is None

    @patch("httpx.Client")
    def test_http_error_propagates(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
    ) -> None:
        """Test that HTTP errors are properly propagated."""
        # Setup mock HTTP client with error response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        client.get_headers = Mock(return_value={})

        # Call the handler directly and verify exception is raised
        with pytest.raises(httpx.HTTPStatusError):
            client.calculate_phylogenetic_tree(sample_command)

    @patch("httpx.Client")
    def test_authentication_headers_included(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
        sample_response_data: dict[str, Any],
    ) -> None:
        """Test that authentication headers are properly included in requests."""
        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_data
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup mock headers
        expected_headers = {
            "Authorization": "Bearer test_jwt_token",
            "Content-Type": "application/json",
        }
        client.get_headers = Mock(return_value=expected_headers)

        # Call the handler directly
        client.calculate_phylogenetic_tree(sample_command)

        # Verify headers were requested and used
        client.get_headers.assert_called_with(sample_command)
        mock_client.request.assert_called_once()
        call_kwargs = mock_client.request.call_args.kwargs
        assert call_kwargs["headers"] == expected_headers

    @patch("httpx.Client")
    def test_request_body_construction(
        self,
        mock_client_class: Mock,
        client: SeqdbClient,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
        sample_response_data: dict[str, Any],
    ) -> None:
        """Test that RetrievePhylogeneticTreeRequestBody is constructed correctly."""
        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_data
        mock_client.request.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup remote app mock
        client.get_headers = Mock(return_value={})

        # Call the handler directly
        client.calculate_phylogenetic_tree(sample_command)

        # Verify request body construction
        expected_request_body = CalculatePhylogeneticTreeRequestBody(
            protocol_id=sample_command.protocol_id,
            tree_algorithm=sample_command.tree_algorithm,
            seq_profile_ids=sample_command.seq_profile_ids,
            leaf_names=sample_command.leaf_names,
        )

        mock_client.request.assert_called_once_with(
            "POST",
            client.get_route(sample_command),
            json=json.loads(expected_request_body.model_dump_json()),
            params=None,
            headers={},
        )

    def test_route_mapping_exists(self, client: SeqdbClient) -> None:
        """Test that the ROUTE_MAP contains the expected mapping."""
        assert seqdb_command.CalculatePhylogeneticTreeCommand in client.ROUTE_MAP
        assert (
            client.ROUTE_MAP[seqdb_command.CalculatePhylogeneticTreeCommand]
            == "/calculate/phylogenetic_tree"
        )

    def test_calculate_phylogenetic_tree_method_exists(
        self, client: SeqdbClient
    ) -> None:
        """Test that the calculate_phylogenetic_tree method exists and is callable."""
        assert hasattr(client, "calculate_phylogenetic_tree")
        assert callable(client.calculate_phylogenetic_tree)

    def test_host_url_construction(self) -> None:
        """Test that base URL is constructed correctly."""
        host = "test-host"
        port = 9999
        app = SeqdbClient(host=host, port=port)
        expected_host_url = f"https://{host}:{port}"
        assert app.host_url == expected_host_url

    def test_client_initialization(self) -> None:
        """Test that the remote app initializes correctly with default values."""
        app = SeqdbClient(host="localhost", port=8001)

        # Verify app was created with basic properties
        assert app is not None
        assert app.host == "localhost"
        assert app.port == 8001
        assert hasattr(app, "calculate_phylogenetic_tree")
        assert seqdb_command.CalculatePhylogeneticTreeCommand in app.ROUTE_MAP

    def test_locus_crud_command_has_extended_timeout(self) -> None:
        """Use the extended timeout for large Locus CRUD batches."""
        assert SeqdbClient.DEFAULT_HTTP_TIMEOUTS[seqdb_command.LocusCrudCommand] == 45.0

    def test_delete_all_ref_data_route_and_timeout_are_registered(self) -> None:
        assert (
            SeqdbClient.ROUTE_MAP[seqdb_command.DeleteAllRefDataCommand] == "/ref_data"
        )
        assert (
            SeqdbClient.DEFAULT_HTTP_TIMEOUTS[seqdb_command.DeleteAllRefDataCommand]
            == 300.0
        )


class TestSeqdbClientHandlers:
    @pytest.fixture
    def client(self) -> SeqdbClient:
        return SeqdbClient(host="localhost", port=8001)

    def test_convert_seq_format_posts_conversion_and_returns_ids(
        self, client: SeqdbClient
    ) -> None:
        seq_id = uuid4()
        converted_id = uuid4()
        cmd = seqdb_command.ConvertSeqFormatCommand(
            seq_ids=[seq_id],
            from_format=seqdb_enum.SeqFormat.STR_DNA,
            to_format=seqdb_enum.SeqFormat.STR_DNA_GZB64,
        )
        with patch.object(
            client, "request", return_value=[str(converted_id)]
        ) as request:
            result = client.convert_seq_format(cmd)

        assert result == [converted_id]
        request.assert_called_once()
        assert request.call_args.args == (cmd, HttpMethod.POST)
        body = request.call_args.kwargs["model"]
        assert body.seq_ids == [seq_id]
        assert body.from_format == seqdb_enum.SeqFormat.STR_DNA
        assert body.to_format == seqdb_enum.SeqFormat.STR_DNA_GZB64

    def test_retrieve_fasta_streams_sequences(self, client: SeqdbClient) -> None:
        seq_ids = [uuid4()]
        cmd = seqdb_command.RetrieveSeqFastaCommand(seq_ids=seq_ids, wrap=60)
        with patch.object(
            client, "stream", return_value=iter([">seq", "ACGT"])
        ) as stream:
            result = list(client.retrieve_genetic_sequence_fasta_by_id(cmd))

        assert result == [">seq", "ACGT"]
        stream.assert_called_once()
        assert stream.call_args.args == (cmd, HttpMethod.POST)
        body = stream.call_args.kwargs["model"]
        assert body.seq_ids == seq_ids
        assert body.wrap == 60
        assert body.file_name == "dummy.fasta"

    def test_create_file_base64_encodes_content(self, client: SeqdbClient) -> None:
        file_id = uuid4()
        cmd = seqdb_command.CreateFileCommand(
            file=seqdb_model.File(content=b"ACGT"),
            format=seqdb_enum.FileFormat.FASTA,
            compression=seqdb_enum.FileCompression.GZIP,
        )
        with patch.object(client, "request", return_value=str(file_id)) as request:
            result = client.create_file(cmd)

        assert result == file_id
        request.assert_called_once()
        assert request.call_args.args == (cmd, HttpMethod.POST)
        body = request.call_args.kwargs["json_body"]
        assert body.content == "QUNHVA=="
        assert body.format == seqdb_enum.FileFormat.FASTA
        assert body.compression == seqdb_enum.FileCompression.GZIP

    def test_retrieve_similar_profiles_returns_uuids(self, client: SeqdbClient) -> None:
        protocol_id, profile_id, similar_id = uuid4(), uuid4(), uuid4()
        cmd = seqdb_command.RetrieveSimilarProfilesCommand(
            protocol_id=protocol_id,
            profile_ids=[profile_id],
            max_distance=1.5,
        )
        with patch.object(client, "request", return_value=[str(similar_id)]) as request:
            result = client.retrieve_similar_profiles(cmd)

        assert result == [similar_id]
        request.assert_called_once()
        assert request.call_args.args == (cmd, HttpMethod.POST)
        body = request.call_args.kwargs["model"]
        assert body.protocol_id == protocol_id
        assert body.profile_ids == [profile_id]
        assert body.max_distance == 1.5

    def test_retrieve_samples_by_id_parses_full_sample(
        self, client: SeqdbClient
    ) -> None:
        sample_id = uuid4()
        collection_id = uuid4()
        cmd = seqdb_command.RetrieveSamplesByIdCommand(sample_ids=[sample_id])
        response = [{"sample": {"created_in_data_collection_id": str(collection_id)}}]
        with patch.object(client, "request", return_value=response) as request:
            result = client.retrieve_samples_by_id(cmd)

        assert result[0].sample.created_in_data_collection_id == collection_id
        request.assert_called_once()
        assert request.call_args.args == (cmd, HttpMethod.POST)
        assert request.call_args.kwargs["model"].sample_ids == [sample_id]

    def test_retrieve_sample_identifiers_parses_records(
        self, client: SeqdbClient
    ) -> None:
        sample_id, issuer_id = uuid4(), uuid4()
        cmd = seqdb_command.RetrieveSampleIdentifiersByIdCommand(sample_ids=[sample_id])
        response = [
            {
                "identifier_issuer_id": str(issuer_id),
                "external_id": "external",
                "internal_id": str(sample_id),
            }
        ]
        with patch.object(client, "request", return_value=response) as request:
            result = client.retrieve_sample_identifiers_by_id(cmd)

        assert result[0].identifier_issuer_id == issuer_id
        assert result[0].external_id == "external"
        request.assert_called_once()
        assert request.call_args.args == (cmd, HttpMethod.POST)
        assert request.call_args.kwargs["model"].sample_ids == [sample_id]

    def test_retrieve_samples_by_query_parses_result(self, client: SeqdbClient) -> None:
        query = seqdb_model.SampleQuery(modified_since=datetime(2024, 1, 1))
        sample_id = uuid4()
        cmd = seqdb_command.RetrieveSamplesByQueryCommand(sample_query=query)
        response = {
            "sample_query": query.model_dump(mode="json"),
            "sample_ids": [str(sample_id)],
            "is_max_results_exceeded": False,
        }
        with patch.object(client, "request", return_value=response) as request:
            result = client.retrieve_samples_by_query(cmd)

        assert result.sample_ids == [sample_id]
        request.assert_called_once_with(cmd, HttpMethod.POST, model=query)

    def test_update_seq_distances_parses_results(self, client: SeqdbClient) -> None:
        protocol_id, profile_id = uuid4(), uuid4()
        cmd = seqdb_command.UpdateSeqDistancesCommand(protocol_id=protocol_id)
        response = [{"seq_distance_profile_id": str(profile_id)}]
        with patch.object(client, "request", return_value=response) as request:
            result = client.update_seq_distances(cmd)

        assert result[0].seq_distance_profile_id == profile_id
        request.assert_called_once_with(
            cmd, HttpMethod.POST, model=cmd, exclude={"user"}
        )

    def test_retrieve_seq_distance_protocol_ids_filters_protocols(
        self, client: SeqdbClient
    ) -> None:
        distance_id, sequencing_id = uuid4(), uuid4()
        protocols = [
            SimpleNamespace(
                id=distance_id, protocol_type=seqdb_enum.ProtocolType.SEQ_DISTANCE
            ),
            SimpleNamespace(
                id=sequencing_id, protocol_type=seqdb_enum.ProtocolType.SEQUENCING
            ),
        ]
        with patch.object(client, "handle", return_value=protocols) as handle:
            result = client.retrieve_seq_distance_protocol_ids()

        assert result == [distance_id]
        cmd = handle.call_args.args[0]
        assert isinstance(cmd, seqdb_command.ProtocolCrudCommand)
        assert cmd.operation == CrudOperation.READ_ALL

    def test_upload_samples_sends_command_and_parses_result(
        self, client: SeqdbClient
    ) -> None:
        cmd = seqdb_command.UploadSamplesCommand(
            sample_batch=seqdb_model.SampleBatchForUpload(samples=[])
        )
        response = {"samples": []}
        with patch.object(client, "request", return_value=response) as request:
            result = client.upload_samples(cmd)

        assert result.samples == []
        request.assert_called_once_with(
            cmd, HttpMethod.POST, model=cmd, exclude={"user"}
        )

    def test_retrieve_best_seq_per_sample_converts_ids(
        self, client: SeqdbClient
    ) -> None:
        sample_id, seq_id = uuid4(), uuid4()
        cmd = seqdb_command.RetrieveBestSeqPerSampleCommand(sample_ids=[sample_id])
        with patch.object(
            client, "request", return_value={str(sample_id): str(seq_id)}
        ) as request:
            result = client.retrieve_best_seq_per_sample(cmd)

        assert result == {sample_id: seq_id}
        request.assert_called_once_with(
            cmd, HttpMethod.POST, model=cmd, exclude={"user"}
        )

    def test_retrieve_best_seq_profile_per_sample_converts_ids(
        self, client: SeqdbClient
    ) -> None:
        sample_id, profile_id, protocol_id = uuid4(), uuid4(), uuid4()
        cmd = seqdb_command.RetrieveBestSeqProfilePerSampleCommand(
            protocol_ids=[protocol_id], sample_ids=[sample_id]
        )
        with patch.object(
            client, "request", return_value={str(sample_id): str(profile_id)}
        ) as request:
            result = client.retrieve_best_seq_profile_per_sample(cmd)

        assert result == {sample_id: profile_id}
        request.assert_called_once_with(
            cmd, HttpMethod.POST, model=cmd, exclude={"user"}
        )

    def test_retrieve_best_seq_classification_per_sample_converts_ids(
        self, client: SeqdbClient
    ) -> None:
        sample_id, classification_id, protocol_id = uuid4(), uuid4(), uuid4()
        cmd = seqdb_command.RetrieveBestSeqClassificationPerSampleCommand(
            protocol_ids=[protocol_id], sample_ids=[sample_id]
        )
        with patch.object(
            client, "request", return_value={str(sample_id): str(classification_id)}
        ) as request:
            result = client.retrieve_best_seq_classification_per_sample(cmd)

        assert result == {sample_id: classification_id}
        request.assert_called_once_with(
            cmd, HttpMethod.POST, model=cmd, exclude={"user"}
        )


class TestRetrieveSeqDistanceLastModified:
    """Test the retrieve_seq_distance_last_modified handler."""

    @pytest.fixture
    def client(self) -> SeqdbClient:
        return SeqdbClient(host="localhost", port=8001)

    @pytest.fixture
    def mock_client(self) -> Any:
        with patch("gen_epix.fastapp.client.httpx.Client") as mock_client_class:
            client = MagicMock()
            client.__enter__.return_value = client
            client.__exit__.return_value = None
            mock_client_class.return_value = client
            yield client

    def test_returns_parsed_datetime(
        self, client: SeqdbClient, mock_client: Any
    ) -> None:
        protocol_id = uuid4()
        response = Mock()
        response.status_code = 200
        response.content = b'"2024-01-02T03:04:05"'
        response.json.return_value = "2024-01-02T03:04:05"
        response.raise_for_status.return_value = None
        mock_client.request.return_value = response

        cmd = seqdb_command.RetrieveSeqDistanceLastModifiedCommand(
            user=None, protocol_id=protocol_id
        )
        result = client.retrieve_seq_distance_last_modified(cmd)

        method, url = mock_client.request.call_args.args
        route = client._routes[seqdb_command.RetrieveSeqDistanceLastModifiedCommand]
        assert method == "POST"
        assert url == f"{route}/{protocol_id}"
        assert result == datetime(2024, 1, 2, 3, 4, 5)

    def test_returns_none_when_never_modified(
        self, client: SeqdbClient, mock_client: Any
    ) -> None:
        response = Mock()
        response.status_code = 200
        response.content = b""
        response.raise_for_status.return_value = None
        mock_client.request.return_value = response

        cmd = seqdb_command.RetrieveSeqDistanceLastModifiedCommand(
            user=None, protocol_id=uuid4()
        )
        result = client.retrieve_seq_distance_last_modified(cmd)
        assert result is None


class TestRetrieveSeqDistancesBySeqProfiles:
    """Test remote retrieval of sequence distances by profile IDs."""

    @pytest.fixture
    def client(self) -> SeqdbClient:
        return SeqdbClient(host="localhost", port=8001)

    @pytest.fixture
    def mock_client(self) -> Any:
        with patch("gen_epix.fastapp.client.httpx.Client") as mock_client_class:
            client = MagicMock()
            client.__enter__.return_value = client
            client.__exit__.return_value = None
            mock_client_class.return_value = client
            yield client

    @pytest.fixture
    def command(self) -> seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand:
        return seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand(
            user=None,
            seq_profile_ids=[uuid4(), uuid4()],
            protocol_id=uuid4(),
        )

    def test_route_is_registered(self, client: SeqdbClient) -> None:
        """Register the profile-distance command on the existing Seqdb route."""
        command_class = seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand
        assert (
            client.ROUTE_MAP[command_class] == "/retrieve/seq_distances_by_seq_profiles"
        )
        assert client._routes[command_class] == (
            client.host_url
            + client._default_route_prefix
            + "/retrieve/seq_distances_by_seq_profiles"
        )

    def test_request_and_response_conversion(
        self,
        client: SeqdbClient,
        mock_client: Any,
        command: seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand,
    ) -> None:
        """Serialize the command and hydrate returned distance models."""
        distance = seqdb_model.SeqDistance(
            id=uuid4(),
            sample_id=uuid4(),
            protocol_id=command.protocol_id,
            seq_profile_id=command.seq_profile_ids[0],
            format=seqdb_enum.SeqDistanceFormat.PROFILE_DISTANCE_MAP,
            content=json.dumps({str(command.seq_profile_ids[1]): 1.5}),
        )
        response = Mock(status_code=200)
        response.json.return_value = [json.loads(distance.model_dump_json())]
        response.raise_for_status.return_value = None
        mock_client.request.return_value = response
        client.get_headers = Mock(return_value={})

        result = client.retrieve_seq_distances_by_seq_profiles(command)

        assert result == [distance]
        request_kwargs = mock_client.request.call_args.kwargs
        assert request_kwargs["json"] == {
            "seq_profile_ids": [str(x) for x in command.seq_profile_ids],
            "protocol_id": str(command.protocol_id),
        }
        assert request_kwargs["headers"] == {}

    def test_http_error_propagates(
        self,
        client: SeqdbClient,
        mock_client: Any,
        command: seqdb_command.RetrieveSeqDistancesBySeqProfilesCommand,
    ) -> None:
        """Propagate a failed remote request."""
        response = Mock(status_code=500)
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=response
        )
        mock_client.request.return_value = response
        client.get_headers = Mock(return_value={})

        with pytest.raises(httpx.HTTPStatusError):
            client.retrieve_seq_distances_by_seq_profiles(command)
