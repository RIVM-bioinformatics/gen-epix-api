"""Unit tests for SeqdbRemoteApp create_calculate_phylogenetic_tree_handler function."""

import json
from typing import Any
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import httpx
import pytest

from gen_epix.casedb.domain import enum as enum
from gen_epix.casedb.domain import model as model
from gen_epix.seqdb.api import CalculatePhylogeneticTreeRequestBody
from gen_epix.seqdb.domain import command as seqdb_command
from gen_epix.seqdb.domain import enum as seqdb_enum
from gen_epix.seqdb.domain import model as seqdb_model
from gen_epix.seqdb.services.remote_app import SeqdbRemoteApp


@pytest.mark.scenario_ids("TC-SEC-28-06")
class TestSeqdbRemoteApp:
    """Test the SeqdbRemoteApp class with focus on create_calculate_phylogenetic_tree_handler."""

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
    def remote_app(self) -> SeqdbRemoteApp:
        """Create a SeqdbRemoteApp instance for testing."""
        return SeqdbRemoteApp(host="localhost", port=8001)

    @pytest.fixture
    def sample_command(
        self, mock_user: seqdb_model.User
    ) -> seqdb_command.CalculatePhylogeneticTreeCommand:
        """Create a sample command for testing."""
        return seqdb_command.CalculatePhylogeneticTreeCommand(
            user=mock_user,
            protocol_id=uuid4(),
            tree_algorithm=seqdb_enum.TreeAlgorithm.UPGMA,
            profile_ids=[uuid4(), uuid4()],
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

    def test_route_registration(self, remote_app: SeqdbRemoteApp) -> None:
        """Test that the handler registers the correct route."""
        expected_route = (
            remote_app.host_url
            + remote_app._default_route_prefix
            + "/calculate/phylogenetic_tree"
        )

        # Verify the route is registered
        assert seqdb_command.CalculatePhylogeneticTreeCommand in remote_app._routes
        registered_route = remote_app._routes[
            seqdb_command.CalculatePhylogeneticTreeCommand
        ]
        assert registered_route == expected_route

    @patch("httpx.Client")
    def test_successful_request_with_full_response(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
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
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # No need to modify command attributes - they're already set in fixture

        # Mock get_headers to return test headers (now synchronous function)
        remote_app.get_headers = Mock(
            return_value={"Authorization": "Bearer test_token"}
        )

        # Call the handler directly
        result = remote_app.calculate_phylogenetic_tree(sample_command)

        # Verify the result - since SeqdbRemoteApp returns seqdb_model.PhylogeneticTree,
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
            profile_ids=sample_command.profile_ids,
            leaf_codes=sample_command.leaf_names,
        )

        mock_client.post.assert_called_once_with(
            # remote_app.host_url + "calculate/phylogenetic_tree",
            remote_app.get_route(sample_command),
            json=json.loads(expected_request_body.model_dump_json()),
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("httpx.Client")
    def test_successful_request_without_leaf_ids(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
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
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup remote app mock
        remote_app.get_headers = Mock(return_value={})

        # Call the handler directly
        result = remote_app.calculate_phylogenetic_tree(sample_command)

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
        remote_app: SeqdbRemoteApp,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
    ) -> None:
        """Test that empty/null response data returns None."""
        # Setup mock HTTP client with empty response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = None
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        remote_app.get_headers = Mock(return_value={})

        # Call the handler directly
        result = remote_app.calculate_phylogenetic_tree(sample_command)

        # Verify None is returned
        assert result is None

    @patch("httpx.Client")
    def test_empty_dict_response_returns_none(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
    ) -> None:
        """Test that empty dict response returns None."""
        # Setup mock HTTP client with empty dict response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        remote_app.get_headers = Mock(return_value={})

        # Call the handler directly
        result = remote_app.calculate_phylogenetic_tree(sample_command)

        # Verify None is returned
        assert result is None

    @patch("httpx.Client")
    def test_http_error_propagates(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
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
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        remote_app.get_headers = Mock(return_value={})

        # Call the handler directly and verify exception is raised
        with pytest.raises(httpx.HTTPStatusError):
            remote_app.calculate_phylogenetic_tree(sample_command)

    @patch("httpx.Client")
    def test_authentication_headers_included(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
        sample_response_data: dict[str, Any],
    ) -> None:
        """Test that authentication headers are properly included in requests."""
        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_data
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup mock headers
        expected_headers = {
            "Authorization": "Bearer test_jwt_token",
            "Content-Type": "application/json",
        }
        remote_app.get_headers = Mock(return_value=expected_headers)

        # Call the handler directly
        remote_app.calculate_phylogenetic_tree(sample_command)

        # Verify headers were requested and used
        remote_app.get_headers.assert_called_with(sample_command)
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args[1]
        assert call_kwargs["headers"] == expected_headers

    @patch("httpx.Client")
    def test_request_body_construction(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seqdb_command.CalculatePhylogeneticTreeCommand,
        sample_response_data: dict[str, Any],
    ) -> None:
        """Test that RetrievePhylogeneticTreeRequestBody is constructed correctly."""
        # Setup mock HTTP client
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_response_data
        mock_client.post.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        # Setup remote app mock
        remote_app.get_headers = Mock(return_value={})

        # Call the handler directly
        remote_app.calculate_phylogenetic_tree(sample_command)

        # Verify request body construction
        expected_request_body = CalculatePhylogeneticTreeRequestBody(
            protocol_id=sample_command.protocol_id,
            tree_algorithm=sample_command.tree_algorithm,
            profile_ids=sample_command.profile_ids,
            leaf_codes=sample_command.leaf_names,
        )

        mock_client.post.assert_called_once_with(
            remote_app.get_route(sample_command),
            json=json.loads(expected_request_body.model_dump_json()),
            headers={},
        )

    def test_route_mapping_exists(self, remote_app: SeqdbRemoteApp) -> None:
        """Test that the ROUTE_MAP contains the expected mapping."""
        assert seqdb_command.CalculatePhylogeneticTreeCommand in remote_app.ROUTE_MAP
        assert (
            remote_app.ROUTE_MAP[seqdb_command.CalculatePhylogeneticTreeCommand]
            == "/calculate/phylogenetic_tree"
        )

    def test_calculate_phylogenetic_tree_method_exists(
        self, remote_app: SeqdbRemoteApp
    ) -> None:
        """Test that the calculate_phylogenetic_tree method exists and is callable."""
        assert hasattr(remote_app, "calculate_phylogenetic_tree")
        assert callable(remote_app.calculate_phylogenetic_tree)

    def test_host_url_construction(self) -> None:
        """Test that base URL is constructed correctly."""
        host = "test-host"
        port = 9999
        app = SeqdbRemoteApp(host=host, port=port)
        expected_host_url = f"https://{host}:{port}"
        assert app.host_url == expected_host_url

    def test_remote_app_initialization(self) -> None:
        """Test that the remote app initializes correctly with default values."""
        app = SeqdbRemoteApp(host="localhost", port=8001)

        # Verify app was created with basic properties
        assert app is not None
        assert app.host == "localhost"
        assert app.port == 8001
        assert hasattr(app, "calculate_phylogenetic_tree")
        assert seqdb_command.CalculatePhylogeneticTreeCommand in app.ROUTE_MAP
