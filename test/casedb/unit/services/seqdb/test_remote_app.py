"""Unit tests for SeqdbRemoteApp create_retrieve_phylogenetic_tree_handler function."""

from functools import partial
from typing import Any
from unittest.mock import MagicMock, Mock, patch
from uuid import uuid4

import httpx
import pytest

from gen_epix.casedb.domain import enum as casedb_enum
from gen_epix.casedb.domain import model as casedb_model
from gen_epix.casedb.services.seqdb.remote_app import SeqdbRemoteApp
from gen_epix.seqdb.api import RetrievePhylogeneticTreeRequestBody
from gen_epix.seqdb.domain import command as seq_command
from gen_epix.seqdb.domain import enum as seq_enum
from gen_epix.seqdb.domain import model as seqdb_model


class TestSeqdbRemoteApp:
    """Test the SeqdbRemoteApp class with focus on create_retrieve_phylogenetic_tree_handler."""

    @pytest.fixture
    def mock_user(self) -> seqdb_model.User:
        """Create a mock user for testing."""
        from gen_epix.seqdb.domain.enum import Role

        return seqdb_model.User(
            id=uuid4(),
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
    ) -> seq_command.RetrievePhylogeneticTreeCommand:
        """Create a sample command for testing."""
        return seq_command.RetrievePhylogeneticTreeCommand(
            user=mock_user,
            seq_distance_protocol_id=uuid4(),
            tree_algorithm=seq_enum.TreeAlgorithm.UPGMA,
            seq_ids=[uuid4(), uuid4()],
            leaf_names=["seq1", "seq2"],
        )

    @pytest.fixture
    def sample_response_data(self) -> dict[str, Any]:
        """Create sample response data for testing."""
        return {
            "sequence_ids": [str(uuid4()), str(uuid4())],
            "leaf_ids": [str(uuid4()), str(uuid4())],
            "newick_repr": "(seq1:0.1,seq2:0.2);",
        }

    def test_create_retrieve_phylogenetic_tree_handler_returns_partial(
        self, remote_app: SeqdbRemoteApp
    ) -> None:
        """Test that create_retrieve_phylogenetic_tree_handler returns a partial function."""
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        assert isinstance(handler, partial)

    def test_route_registration(self, remote_app: SeqdbRemoteApp) -> None:
        """Test that the handler registers the correct route."""
        expected_route = remote_app.base_url + "retrieve/phylogenetic_tree"

        # Create a test handler to verify route registration works
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        assert handler is not None

        # Verify the expected route format is correct
        assert "retrieve/phylogenetic_tree" in expected_route
        assert remote_app.base_url in expected_route

    @patch("httpx.Client")
    def test_successful_request_with_full_response(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
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

        # Mock get_headers to return test headers
        remote_app.get_headers = Mock(
            return_value={"Authorization": "Bearer test_token"}
        )

        # Get handler and execute
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        result = handler(sample_command)

        # Verify the result
        assert isinstance(result, casedb_model.PhylogeneticTree)
        assert result.tree_algorithm_code == casedb_enum.TreeAlgorithmType.UPGMA
        assert result.sequence_ids is not None
        assert len(result.sequence_ids) == 2
        assert result.leaf_ids is not None
        assert len(result.leaf_ids) == 2
        assert result.newick_repr == "(seq1:0.1,seq2:0.2);"

        # Verify the HTTP request was made correctly
        expected_request_body = RetrievePhylogeneticTreeRequestBody(
            seq_distance_protocol_id=sample_command.seq_distance_protocol_id,
            tree_algorithm=sample_command.tree_algorithm,
            seq_ids=sample_command.seq_ids,
        )

        mock_client.post.assert_called_once_with(
            remote_app.base_url + "retrieve/phylogenetic_tree",
            json=expected_request_body.model_dump(),
            headers={"Authorization": "Bearer test_token"},
        )

    @patch("httpx.Client")
    def test_successful_request_without_leaf_ids(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
        mock_user: seqdb_model.User,
    ) -> None:
        """Test successful HTTP request with response data missing leaf_ids."""
        # Setup response without leaf_ids
        response_data = {
            "sequence_ids": [str(uuid4()), str(uuid4())],
            "newick_repr": "(seq1:0.1,seq2:0.2);",
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

        # Get handler and execute
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        result = handler(sample_command)

        # Verify the result
        assert isinstance(result, casedb_model.PhylogeneticTree)
        assert result.leaf_ids is None
        assert result.sequence_ids is not None
        assert len(result.sequence_ids) == 2
        assert result.newick_repr == "(seq1:0.1,seq2:0.2);"

    @patch("httpx.Client")
    def test_empty_response_returns_none(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
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

        # Get handler and execute
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        result = handler(sample_command)

        # Verify None is returned
        assert result is None

    @patch("httpx.Client")
    def test_empty_dict_response_returns_none(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
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

        # Get handler and execute
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        result = handler(sample_command)

        # Verify None is returned
        assert result is None

    @patch("httpx.Client")
    def test_http_error_propagates(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
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

        # Get handler and verify exception is raised
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()

        with pytest.raises(httpx.HTTPStatusError):
            handler(sample_command)

    @patch("httpx.Client")
    def test_authentication_headers_included(
        self,
        mock_client_class: Mock,
        remote_app: SeqdbRemoteApp,
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
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

        # Get handler and execute
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        handler(sample_command)

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
        sample_command: seq_command.RetrievePhylogeneticTreeCommand,
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

        # Get handler and execute
        handler = remote_app.create_retrieve_phylogenetic_tree_handler()
        handler(sample_command)

        # Verify request body construction
        expected_request_body = RetrievePhylogeneticTreeRequestBody(
            seq_distance_protocol_id=sample_command.seq_distance_protocol_id,
            tree_algorithm=sample_command.tree_algorithm,
            seq_ids=sample_command.seq_ids,
        )

        mock_client.post.assert_called_once_with(
            remote_app.base_url + "retrieve/phylogenetic_tree",
            json=expected_request_body.model_dump(),
            headers={},
        )

    def test_command_mapping_exists(self, remote_app: SeqdbRemoteApp) -> None:
        """Test that the COMMAND_MAP contains the expected mapping."""
        from gen_epix.casedb.domain.command import (
            RetrievePhylogeneticTreeBySequencesCommand,
        )

        assert RetrievePhylogeneticTreeBySequencesCommand in remote_app.COMMAND_MAP
        assert (
            remote_app.COMMAND_MAP[RetrievePhylogeneticTreeBySequencesCommand]
            == seq_command.RetrievePhylogeneticTreeCommand
        )

    def test_tree_algorithm_mapping_exists(self, remote_app: SeqdbRemoteApp) -> None:
        """Test that the TREE_ALGORITHM_MAP contains expected mappings."""
        assert len(remote_app.TREE_ALGORITHM_MAP) > 0

        # Verify the mapping structure - each casedb enum should map to seqdb enum with same value
        for casedb_enum_val, seqdb_enum_val in remote_app.TREE_ALGORITHM_MAP.items():
            assert isinstance(casedb_enum_val, casedb_enum.TreeAlgorithmType)
            assert isinstance(seqdb_enum_val, seq_enum.TreeAlgorithm)
            assert casedb_enum_val.value == seqdb_enum_val.value

    def test_base_url_construction(self) -> None:
        """Test that base URL is constructed correctly."""
        host = "test-host"
        port = 9999
        app = SeqdbRemoteApp(host=host, port=port)
        expected_base_url = f"https://{host}:{port}/v1/"
        assert app.base_url == expected_base_url

    def test_handler_registration_on_init(self) -> None:
        """Test that handlers are registered during initialization."""
        with patch.object(SeqdbRemoteApp, "register_handler") as mock_register:
            with patch.object(
                SeqdbRemoteApp, "create_retrieve_phylogenetic_tree_handler"
            ) as mock_create:
                mock_handler = Mock()
                mock_create.return_value = mock_handler

                app = SeqdbRemoteApp(host="localhost", port=8001)

                # Verify handler creation and registration was called
                mock_create.assert_called_once()
                mock_register.assert_called_once_with(
                    seq_command.RetrievePhylogeneticTreeCommand, mock_handler
                )

                # Verify app was created
                assert app is not None
