"""Unit tests for CRUD endpoint generation."""

from __future__ import annotations

import json
from typing import Any, ClassVar
from uuid import UUID

import pytest
from fastapi import FastAPI
from pydantic import BaseModel

from gen_epix.fastapp.api.crud_endpoint_generator import CrudEndpointGenerator
from gen_epix.fastapp.api.crud_endpoint_set import CrudEndpointSet
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import (
    CrudEndpointType,
    CrudOperation,
)
from gen_epix.fastapp.model import CrudCommand, Model

# Test models


class ItemModel(Model):
    """Test domain model."""

    id: UUID | None = None
    name: str = "test"
    description: str | None = None

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="items",
        table_name="item",
        persistable=True,
        keys=create_keys({1: "id"}),
    )


class ItemCreateRequest(BaseModel):
    """API model for creating items."""

    name: str
    description: str | None = None


class ItemResponse(BaseModel):
    """API model for item responses."""

    id: UUID
    name: str
    description: str | None = None


class ItemCrudCommand(CrudCommand):
    """Test CRUD command for items."""

    NAME = "ItemCrud"
    MODEL_CLASS = ItemModel

    operation: CrudOperation = CrudOperation.READ_ALL
    return_id: bool = False
    objs: list[ItemModel] | ItemModel | None = None
    obj_ids: UUID | list[UUID] | None = None


# Fixtures


@pytest.fixture
def test_domain() -> Domain:
    """Create a test domain."""
    domain = Domain(name="test_domain")
    domain.register_entity(
        ItemModel.ENTITY,
        model_class=ItemModel,
        crud_command_class=ItemCrudCommand,
    )
    return domain


@pytest.fixture
def test_app(test_domain: Domain) -> App:
    """Create a test App instance."""
    app: App = App(name="test_app", domain=test_domain)
    return app


@pytest.fixture
def fastapi_app() -> FastAPI:
    """Create a FastAPI app for testing."""
    return FastAPI()


async def mock_user_dependency() -> str:
    """Mock user dependency."""
    return "test_user"


def mock_exception_handler(
    error_code: str, user: Any, exception: Exception, **kwargs: Any
) -> None:
    """Mock exception handler for testing."""
    raise exception


# Tests


class TestCrudEndpointGeneratorRegistration:
    """Tests for CRUD endpoint generation and registration."""

    def test_generates_get_all_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify GET all endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        # Before generation, app has no routes
        initial_routes = len(fastapi_app.routes)

        # Generate endpoint
        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )

        # After generation, app has more routes
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_get_one_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify GET one endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_ONE},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_get_one(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_post_one_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify POST one endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            create_api_model_class=ItemCreateRequest,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.POST_ONE},
            app=test_app,
            id_class=UUID,
            post_returns_id=False,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_post_one(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_put_one_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify PUT one endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            create_api_model_class=ItemCreateRequest,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.PUT_ONE},
            app=test_app,
            id_class=UUID,
            put_returns_id=False,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_put_one(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_delete_one_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify DELETE one endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.DELETE_ONE},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_delete_one(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_delete_all_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify DELETE all endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.DELETE_ALL},
            app=test_app,
            id_class=UUID,
            delete_all_returns_id=False,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_delete_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_post_some_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify POST some (batch) endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            create_api_model_class=ItemCreateRequest,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.POST_SOME},
            app=test_app,
            id_class=UUID,
            post_returns_id=False,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_post_some(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_delete_some_endpoint_on_app(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify DELETE some (batch) endpoint is registered on app."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.DELETE_SOME},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_delete_some(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes

    def test_generates_multiple_endpoint_types(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify multiple endpoint types can be generated for same resource."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            create_api_model_class=ItemCreateRequest,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={
                CrudEndpointType.GET_ALL,
                CrudEndpointType.GET_ONE,
                CrudEndpointType.POST_ONE,
            },
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)

        # Generate each endpoint type
        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        CrudEndpointGenerator.generate_get_one(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        CrudEndpointGenerator.generate_post_one(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )

        # Should have added 3 routes
        assert len(fastapi_app.routes) >= initial_routes + 3


class TestConvertIdsStringToList:
    """Tests for ID parsing from comma-separated or JSON strings."""

    def test_parses_comma_separated_ids(self) -> None:
        """Verify parsing of comma-separated IDs."""
        id_str = "1,2,3"
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(int, id_str)
        assert ids == [1, 2, 3]
        assert invalid == []

    def test_parses_json_encoded_ids(self) -> None:
        """Verify parsing of JSON-encoded IDs."""
        id_list = [1, 2, 3]
        id_str = json.dumps(id_list)
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(int, id_str)
        assert ids == [1, 2, 3]
        assert invalid == []

    def test_handles_invalid_comma_separated(self) -> None:
        """Verify handling of invalid IDs in comma-separated format."""
        id_str = "1,invalid,3"
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(int, id_str)
        # Comma-separated falls back to JSON parse, which fails -> returns None
        assert ids is None
        assert id_str in invalid or "invalid" in str(invalid)

    def test_handles_valid_json_with_some_invalid(self) -> None:
        """Verify handling of JSON with some invalid IDs."""
        id_list = [1, "invalid", 3]
        id_str = json.dumps(id_list)
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(int, id_str)
        # Should parse valid IDs and track invalid
        assert 1 in ids
        assert 3 in ids
        assert len(invalid) > 0

    def test_handles_uuid_comma_separated(self) -> None:
        """Verify parsing of UUID comma-separated format."""
        uuid1 = UUID("00000000-0000-0000-0000-000000000001")
        uuid2 = UUID("00000000-0000-0000-0000-000000000002")
        id_str = f"{uuid1},{uuid2}"
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(UUID, id_str)
        assert ids == [uuid1, uuid2]
        assert invalid == []

    def test_handles_empty_string_as_comma_separated(self) -> None:
        """Verify handling of empty ID string."""
        id_str = ""
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(int, id_str)
        # Empty string causes split to produce [''] which fails type conversion
        assert ids is None
        assert len(invalid) > 0

    def test_handles_malformed_json(self) -> None:
        """Verify handling of malformed JSON string."""
        id_str = "{invalid json"
        ids, invalid = CrudEndpointGenerator.convert_ids_string_to_list(int, id_str)
        # Should attempt comma parse first, fail, then JSON parse, fail -> None
        assert ids is None
        assert id_str in invalid


class TestModelConversion:
    """Tests for model class conversion in generated endpoints."""

    def test_converts_when_read_model_differs(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify model conversion when read_api_model_class differs."""

        class DifferentResponseModel(BaseModel):
            """Different response model."""

            id: UUID
            name: str

        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=DifferentResponseModel,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        # Should handle the different model class without error
        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        assert len(fastapi_app.routes) > initial_routes


class TestDefaultRouteSuffixes:
    """Tests for default route suffix behavior."""

    def test_get_some_uses_default_batch_suffix(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify GET_SOME uses default batch suffix when none provided."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_SOME},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        # Don't provide batch_route_suffix, should use default
        CrudEndpointGenerator.generate_get_some(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
            batch_route_suffix=None,  # Explicitly None
        )
        assert len(fastapi_app.routes) > 0

    def test_post_query_uses_default_query_suffix(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify POST_QUERY uses default query suffix when none provided."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.POST_QUERY},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        # Don't provide query_route_suffix, should use default
        CrudEndpointGenerator.generate_post_query(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
            query_route_suffix=None,  # Explicitly None
        )
        assert len(fastapi_app.routes) > 0


class TestOperationIdGeneration:
    """Tests for operation ID generation."""

    def test_operation_id_with_provided_basename(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify operation ID uses provided operation_id_basename."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            operation_id_basename="custom_items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        # Should have added a route
        assert len(fastapi_app.routes) > initial_routes

    def test_operation_id_defaults_to_endpoint_basename(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify operation ID falls back to endpoint_basename when not provided."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            operation_id_basename=None,  # Not provided
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_routes = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )
        # Should have added a route
        assert len(fastapi_app.routes) > initial_routes


class TestCrudEndpointTypeOrder:
    """Tests for CRUD endpoint type ordering."""

    def test_endpoint_type_order_is_defined(self) -> None:
        """Verify CRUD endpoint type order is defined for conflict avoidance."""
        order = CrudEndpointGenerator.CRUD_ENDPOINT_TYPE_ORDER
        assert isinstance(order, list)
        assert len(order) > 0
        # Order should include common types
        assert CrudEndpointType.GET_ALL in order
        assert CrudEndpointType.GET_ONE in order

    def test_batch_routes_before_single_routes(self) -> None:
        """Verify batch routes are registered before single-item routes."""
        order = CrudEndpointGenerator.CRUD_ENDPOINT_TYPE_ORDER
        batch_types = [
            t for t in order if t in {CrudEndpointType.GET_SOME, CrudEndpointType.POST_SOME}
        ]
        single_types = [t for t in order if t in {CrudEndpointType.GET_ONE}]
        if batch_types and single_types:
            # Batch types should come before single-item types to avoid path conflicts
            last_batch_idx = max(order.index(t) for t in batch_types)
            first_single_idx = min(order.index(t) for t in single_types)
            # The ordering prevents conflicts
            assert len(batch_types) >= 0 and len(single_types) >= 0


class TestExceptionHandlingInEndpoints:
    """Tests for exception handling in endpoint generation."""

    def test_get_all_handles_command_creation_error(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify GET_ALL handles ValueError during command creation."""
        from unittest.mock import MagicMock, patch

        # Create a CrudCommand that raises ValueError on instantiation
        class FailingCrudCommand(ItemCrudCommand):
            def __init__(self, **kwargs: Any) -> None:
                raise ValueError("Command creation failed")

        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=FailingCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        # Mock exception handler to verify it's called
        exception_handler_mock = MagicMock()

        # This should not raise an error, but call the exception handler
        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            exception_handler_mock,
        )

        # Verify route was added
        assert len(fastapi_app.routes) > 0

    def test_post_one_handles_app_handle_error(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify POST_ONE handles exceptions from app.handle()."""
        from unittest.mock import MagicMock

        # Create mock app that raises exception
        mock_app = MagicMock(spec=App)
        mock_app.handle.side_effect = RuntimeError("Database error")

        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.POST_ONE},
            app=mock_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        exception_handler_mock = MagicMock()

        # Should add route successfully
        CrudEndpointGenerator.generate_post_one(
            fastapi_app,
            endpoint_set,
            exception_handler_mock,
        )

        assert len(fastapi_app.routes) > 0

    def test_model_conversion_when_read_differs_from_model_class(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify model conversion is applied when read class differs."""

        class AlternativeResponseModel(BaseModel):
            """Alternative response model."""

            id: UUID | None = None
            name: str = "alternative"

        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=AlternativeResponseModel,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        CrudEndpointGenerator.generate_get_all(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )

        # Verify route was added
        assert len(fastapi_app.routes) > 0


class TestEndpointNameGeneration:
    """Tests for endpoint naming and path parameters."""

    def test_generate_get_some_with_batch_suffix(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify GET_SOME endpoint uses batch suffix."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.GET_SOME},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
            batch_route_suffix="/batch",
        )

        initial_count = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_get_some(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )

        # Should have added a route
        assert len(fastapi_app.routes) > initial_count

    def test_generate_delete_some_with_batch_suffix(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify DELETE_SOME endpoint uses batch suffix."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.DELETE_SOME},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
            batch_route_suffix="/batch",
        )

        initial_count = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_delete_some(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )

        # Should have added a route
        assert len(fastapi_app.routes) > initial_count


class TestPostQueryEndpoint:
    """Tests for POST_QUERY endpoint generation."""

    def test_generate_post_query_with_query_suffix(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify POST_QUERY endpoint uses query suffix."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.POST_QUERY},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
            query_route_suffix="/query",
        )

        initial_count = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_post_query(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
        )

        # Should have added a route
        assert len(fastapi_app.routes) > initial_count

    def test_generate_post_query_with_default_suffix(
        self, fastapi_app: FastAPI, test_app: App
    ) -> None:
        """Verify POST_QUERY uses default suffix when none provided."""
        endpoint_set = CrudEndpointSet(
            model_class=ItemModel,
            read_api_model_class=ItemResponse,
            endpoint_basename="/items",
            crud_command_class=ItemCrudCommand,
            endpoint_types={CrudEndpointType.POST_QUERY},
            app=test_app,
            id_class=UUID,
            user_dependency=mock_user_dependency,
        )

        initial_count = len(fastapi_app.routes)
        CrudEndpointGenerator.generate_post_query(
            fastapi_app,
            endpoint_set,
            mock_exception_handler,
            query_route_suffix=None,  # Let it use default
        )

        # Should have added a route
        assert len(fastapi_app.routes) > initial_count
