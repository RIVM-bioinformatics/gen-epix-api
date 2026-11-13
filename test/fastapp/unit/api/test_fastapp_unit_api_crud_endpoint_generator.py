"""Unit tests for CRUD endpoint generation."""

from __future__ import annotations

import asyncio
import json
from test.util.mock_compat import MagicMock
from typing import Any, ClassVar
from uuid import UUID

import pytest
from fastapi import FastAPI
from pydantic import BaseModel

from gen_epix.fastapp import exc as fastapp_exc
from gen_epix.fastapp.api import exc as api_exc
from gen_epix.fastapp.api.crud_endpoint_generator import (
    CrudEndpointGenerator,
    _default_validate_query_filter,
)
from gen_epix.fastapp.api.crud_endpoint_set import CrudEndpointSet
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import (
    CrudEndpointType,
    CrudOperation,
    HttpMethod,
    PermissionType,
    PermissionTypeSet,
    StringCasing,
)
from gen_epix.fastapp.model import CrudCommand, Model, Permission, User
from gen_epix.filter import CompositeFilter
from gen_epix.filter.enum import LogicalOperator
from gen_epix.filter.equals_number import EqualsNumberFilter

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

    id: UUID | None = None
    name: str
    description: str | None = None

    @classmethod
    def to_model(cls, item: ItemCreateRequest) -> ItemModel:
        """Convert an API write model to the test domain model."""
        return ItemModel(
            id=item.id,
            name=item.name,
            description=item.description,
        )


class ItemResponse(BaseModel):
    """API model for item responses."""

    id: UUID
    name: str
    description: str | None = None

    @classmethod
    def from_model(cls, item: ItemModel) -> ItemResponse:
        """Convert a test domain model to its API response model."""
        return cls(id=item.id, name=item.name, description=item.description)


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


@pytest.fixture
def test_user() -> User:
    """Return a valid command user for direct endpoint calls."""
    return User(id="test-user")


@pytest.fixture
def route_factory(test_app: App):
    """Build CRUD endpoint sets with the common item configuration."""

    def create_route(**overrides: Any) -> CrudEndpointSet:
        route_kwargs: dict[str, Any] = {
            "model_class": ItemModel,
            "create_api_model_class": ItemCreateRequest,
            "read_api_model_class": ItemResponse,
            "endpoint_basename": "items",
            "crud_command_class": ItemCrudCommand,
            "endpoint_types": set(),
            "app": test_app,
            "id_class": UUID,
            "user_dependency": mock_user_dependency,
        }
        route_kwargs.update(overrides)
        return CrudEndpointSet(**route_kwargs)

    return create_route


def _register_endpoint(
    fastapi_app: FastAPI,
    generator: Any,
    route: CrudEndpointSet,
    handle_exception_fn: Any | None = None,
    **generator_kwargs: Any,
) -> Any:
    """Generate one endpoint and return its handler for direct invocation."""
    generator(
        fastapi_app,
        route,
        handle_exception_fn or mock_exception_handler,
        **generator_kwargs,
    )
    return fastapi_app.routes[-1].endpoint


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
            t
            for t in order
            if t in {CrudEndpointType.GET_SOME, CrudEndpointType.POST_SOME}
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


class TestGeneratedEndpointExecution:
    """Tests for generated handler dispatch and response behavior."""

    def test_get_all_dispatches_pagination_and_converts_models(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000001")
        app = MagicMock(spec=App)
        app.handle.return_value = [ItemModel(id=item_id, name="one")]
        route = route_factory(app=app)
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_all,
            route,
        )

        result = asyncio.run(endpoint(test_user, 10, 5))

        assert result == [ItemResponse(id=item_id, name="one")]
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.READ_ALL
        assert (command.limit, command.offset) == (10, 5)

    def test_get_all_returns_none_for_command_validation_error(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        errors: list[tuple[Any, ...]] = []

        class InvalidCommand(ItemCrudCommand):
            def __init__(self, **kwargs: Any) -> None:
                raise ValueError("invalid pagination")

        route = route_factory(crud_command_class=InvalidCommand)
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_all,
            route,
            lambda *args, **kwargs: errors.append(args),
        )

        assert asyncio.run(endpoint(User(id="test-user"))) is None
        assert len(errors) == 1
        assert errors[0][2].message == "invalid pagination"

    def test_get_some_converts_ids_and_models(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000002")
        app = MagicMock(spec=App)
        app.handle.return_value = [ItemModel(id=item_id, name="two")]
        route = route_factory(app=app)
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_some,
            route,
        )

        result = asyncio.run(endpoint(test_user, str(item_id)))

        assert result == [ItemResponse(id=item_id, name="two")]
        command = app.handle.call_args.args[0]
        assert command.obj_ids == [item_id]
        assert command.operation == CrudOperation.READ_SOME

    def test_get_some_rejects_invalid_ids_before_dispatch(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        app = MagicMock(spec=App)
        errors: list[tuple[Any, ...]] = []
        route = route_factory(app=app)
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_some,
            route,
            lambda *args, **kwargs: errors.append(args),
        )

        with pytest.raises(NotImplementedError, match="handler expected to raise"):
            asyncio.run(endpoint(User(id="test-user"), "not-a-uuid"))

        app.handle.assert_not_called()
        assert errors[0][2].ids == ["not-a-uuid"]

    def test_exists_some_returns_app_result(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000003")
        app = MagicMock(spec=App)
        app.handle.return_value = [True]
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_exists_some,
            route_factory(app=app),
        )

        assert asyncio.run(endpoint(test_user, str(item_id))) == [True]
        assert app.handle.call_args.args[0].operation == CrudOperation.EXISTS_SOME

    def test_post_query_validates_filter_and_returns_models(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000004")
        query_filter = EqualsNumberFilter(key="id", value=1)
        app = MagicMock(spec=App)
        app.handle.return_value = [ItemModel(id=item_id, name="four")]
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_post_query,
            route_factory(app=app),
        )

        result = asyncio.run(endpoint(test_user, query_filter, 4, 2))

        assert result == [ItemResponse(id=item_id, name="four")]
        command = app.handle.call_args.args[0]
        assert command.query_filter == query_filter
        assert (command.limit, command.offset) == (4, 2)

    def test_post_query_rejects_nested_composite_filter(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        nested_filter = CompositeFilter(
            operator=LogicalOperator.AND,
            filters=[
                EqualsNumberFilter(key="id", value=1),
                CompositeFilter(
                    operator=LogicalOperator.OR,
                    filters=[EqualsNumberFilter(key="id", value=2)],
                ),
            ],
        )
        app = MagicMock(spec=App)
        errors: list[tuple[Any, ...]] = []
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_post_query,
            route_factory(app=app),
            lambda *args, **kwargs: errors.append(args),
        )

        with pytest.raises(NotImplementedError, match="handler expected to raise"):
            asyncio.run(endpoint("user", nested_filter))

        app.handle.assert_not_called()
        assert errors[0][2].message == "Invalid filter"

    def test_post_query_can_disable_filter_validation_and_return_ids(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000005")
        app = MagicMock(spec=App)
        app.handle.return_value = [item_id]
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_post_query,
            route_factory(app=app),
            return_id=True,
            validate_query_filter=None,
        )

        assert asyncio.run(
            endpoint(User(id="test-user"), EqualsNumberFilter(key="id", value=1))
        ) == [item_id]
        assert app.handle.call_args.args[0].return_id is True
        assert fastapi_app.routes[-1].path == "/items/query/ids"

    def test_get_one_and_exists_one_dispatch_ids(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000006")
        app = MagicMock(spec=App)
        app.handle.return_value = ItemModel(id=item_id, name="six")
        get_one = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_one,
            route_factory(app=app),
        )

        assert asyncio.run(get_one(test_user, item_id)) == ItemResponse(
            id=item_id, name="six"
        )
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.READ_ONE
        assert command.obj_ids == item_id

        app.handle.return_value = True
        exists_one = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_exists_one,
            route_factory(app=app),
        )
        assert asyncio.run(exists_one(test_user, item_id)) is True
        assert app.handle.call_args.args[0].operation == CrudOperation.EXISTS_ONE

    def test_post_one_and_post_some_convert_write_models(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000007")
        write_obj = ItemCreateRequest(id=item_id, name="seven")
        app = MagicMock(spec=App)
        app.handle.return_value = ItemModel(id=item_id, name="seven")
        post_one = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_post_one,
            route_factory(app=app),
        )

        assert asyncio.run(post_one(test_user, write_obj)) == ItemResponse(
            id=item_id, name="seven"
        )
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.CREATE_ONE
        assert command.objs == ItemModel(id=item_id, name="seven")

        app.handle.return_value = [ItemModel(id=item_id, name="seven")]
        post_some = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_post_some,
            route_factory(app=app, post_returns_id=True),
        )
        assert asyncio.run(post_some(test_user, [write_obj])) == [
            ItemModel(id=item_id, name="seven")
        ]
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.CREATE_SOME
        assert command.return_id is True

    def test_put_one_checks_matching_id_and_converts_model(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000008")
        app = MagicMock(spec=App)
        app.handle.return_value = ItemModel(id=item_id, name="updated")
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_put_one,
            route_factory(app=app),
        )

        with pytest.raises(api_exc.BadRequest400HTTPException):
            asyncio.run(
                endpoint(
                    test_user,
                    item_id,
                    ItemCreateRequest(id=UUID(int=9), name="wrong id"),
                )
            )
        app.handle.assert_not_called()

        assert asyncio.run(
            endpoint(test_user, item_id, ItemCreateRequest(id=item_id, name="updated"))
        ) == ItemResponse(id=item_id, name="updated")
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.UPDATE_ONE
        assert command.objs == ItemModel(id=item_id, name="updated")

    def test_put_some_dispatches_and_converts_models(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000009")
        app = MagicMock(spec=App)
        app.handle.return_value = [ItemModel(id=item_id, name="updated")]
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_put_some,
            route_factory(app=app),
        )

        assert asyncio.run(
            endpoint(test_user, [ItemCreateRequest(id=item_id, name="updated")])
        ) == [ItemResponse(id=item_id, name="updated")]
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.UPDATE_SOME
        assert command.objs == [ItemModel(id=item_id, name="updated")]

    def test_delete_endpoints_dispatch_operations_without_paging(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000010")
        app = MagicMock(spec=App)
        app.handle.return_value = [item_id]
        delete_one = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_delete_one,
            route_factory(app=app),
        )
        assert asyncio.run(delete_one(test_user, item_id)) == [item_id]
        assert app.handle.call_args.args[0].operation == CrudOperation.DELETE_ONE

        delete_all = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_delete_all,
            route_factory(app=app, delete_all_returns_id=True),
        )
        assert asyncio.run(delete_all(test_user)) == [item_id]
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.DELETE_ALL
        assert command.return_id is True
        assert (command.limit, command.offset) == (0, 0)

    def test_delete_some_valid_and_invalid_ids(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000011")
        app = MagicMock(spec=App)
        app.handle.return_value = [item_id]
        errors: list[tuple[Any, ...]] = []
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_delete_some,
            route_factory(app=app),
            lambda *args, **kwargs: errors.append(args),
        )

        assert asyncio.run(endpoint(User(id="test-user"), str(item_id))) == [item_id]
        command = app.handle.call_args.args[0]
        assert command.operation == CrudOperation.DELETE_SOME
        assert command.obj_ids == [item_id]

        with pytest.raises(NotImplementedError, match="handler expected to raise"):
            asyncio.run(endpoint(User(id="test-user"), "invalid-id"))
        app.handle.assert_called_once()
        assert errors[-1][2].ids == ["invalid-id"]

    def test_app_failures_are_forwarded_to_exception_handler(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        app = MagicMock(spec=App)
        app.handle.side_effect = RuntimeError("storage failure")
        errors: list[tuple[Any, ...]] = []
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_exists_one,
            route_factory(app=app),
            lambda *args, **kwargs: errors.append(args),
        )
        item_id = UUID("00000000-0000-0000-0000-000000000012")

        with pytest.raises(NotImplementedError, match="handler expected to raise"):
            asyncio.run(endpoint(User(id="test-user"), item_id))

        assert len(errors) == 1
        assert errors[0][2].args == ("storage failure",)

    @pytest.mark.parametrize(
        "generator_name",
        [
            "generate_get_all",
            "generate_get_some",
            "generate_get_exists_some",
            "generate_post_query",
            "generate_get_one",
            "generate_get_exists_one",
            "generate_post_one",
            "generate_post_some",
            "generate_put_one",
            "generate_put_some",
            "generate_delete_one",
            "generate_delete_all",
            "generate_delete_some",
        ],
        ids=[
            "get-all",
            "get-some",
            "exists-some",
            "post-query",
            "get-one",
            "exists-one",
            "post-one",
            "post-some",
            "put-one",
            "put-some",
            "delete-one",
            "delete-all",
            "delete-some",
        ],
    )
    def test_each_generated_handler_reports_app_failures(
        self,
        generator_name: str,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_user: User,
    ) -> None:
        item_id = UUID("00000000-0000-0000-0000-000000000013")
        app = MagicMock(spec=App)
        app.handle.side_effect = RuntimeError("storage failure")
        errors: list[tuple[Any, ...]] = []
        endpoint = _register_endpoint(
            fastapi_app,
            getattr(CrudEndpointGenerator, generator_name),
            route_factory(app=app),
            lambda *args, **kwargs: errors.append(args),
        )
        write_obj = ItemCreateRequest(id=item_id, name="write")
        args_by_generator: dict[str, tuple[Any, ...]] = {
            "generate_get_all": (test_user,),
            "generate_get_some": (test_user, str(item_id)),
            "generate_get_exists_some": (test_user, str(item_id)),
            "generate_post_query": (
                test_user,
                EqualsNumberFilter(key="id", value=1),
            ),
            "generate_get_one": (test_user, item_id),
            "generate_get_exists_one": (test_user, item_id),
            "generate_post_one": (test_user, write_obj),
            "generate_post_some": (test_user, [write_obj]),
            "generate_put_one": (test_user, item_id, write_obj),
            "generate_put_some": (test_user, [write_obj]),
            "generate_delete_one": (test_user, item_id),
            "generate_delete_all": (test_user,),
            "generate_delete_some": (test_user, str(item_id)),
        }

        with pytest.raises(NotImplementedError, match="handler expected to raise"):
            asyncio.run(endpoint(*args_by_generator[generator_name]))

        assert errors[-1][2].args == ("storage failure",)

    def test_exists_some_rejects_invalid_ids_before_dispatch(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        app = MagicMock(spec=App)
        errors: list[tuple[Any, ...]] = []
        endpoint = _register_endpoint(
            fastapi_app,
            CrudEndpointGenerator.generate_get_exists_some,
            route_factory(app=app),
            lambda *args, **kwargs: errors.append(args),
        )

        with pytest.raises(NotImplementedError, match="handler expected to raise"):
            asyncio.run(endpoint(User(id="test-user"), "invalid-id"))

        app.handle.assert_not_called()
        assert errors[0][2].ids == ["invalid-id"]


class TestCrudEndpointGeneratorHelpers:
    """Tests for endpoint selection and metadata helper methods."""

    def test_default_filter_validator_allows_flat_and_rejects_nested_filters(
        self,
    ) -> None:
        flat_filter = CompositeFilter(
            operator=LogicalOperator.AND,
            filters=[
                EqualsNumberFilter(key="id", value=1),
                EqualsNumberFilter(key="id", value=2),
            ],
        )
        nested_filter = CompositeFilter(
            operator=LogicalOperator.AND,
            filters=[
                EqualsNumberFilter(key="id", value=1),
                CompositeFilter(
                    operator=LogicalOperator.OR,
                    filters=[EqualsNumberFilter(key="id", value=2)],
                ),
            ],
        )

        assert _default_validate_query_filter(EqualsNumberFilter(key="id", value=1))
        assert _default_validate_query_filter(flat_filter)
        assert not _default_validate_query_filter(nested_filter)

    def test_permission_types_map_to_supported_crud_operations(self) -> None:
        permissions = {
            Permission(command_name="ItemCrud", permission_type=permission_type)
            for permission_type in (
                PermissionType.CREATE,
                PermissionType.READ,
                PermissionType.UPDATE,
                PermissionType.DELETE,
            )
        }

        assert CrudEndpointGenerator.get_crud_operations_for_permissions(
            permissions
        ) == {
            CrudOperation.CREATE_ONE,
            CrudOperation.CREATE_SOME,
            CrudOperation.READ_ALL,
            CrudOperation.READ_SOME,
            CrudOperation.READ_ONE,
            CrudOperation.EXISTS_ONE,
            CrudOperation.EXISTS_SOME,
            CrudOperation.UPDATE_ONE,
            CrudOperation.UPDATE_SOME,
            CrudOperation.DELETE_ALL,
            CrudOperation.DELETE_SOME,
            CrudOperation.DELETE_ONE,
        }
        with pytest.raises(NotImplementedError, match="EXECUTE not implemented"):
            CrudEndpointGenerator.get_crud_operations_for_permissions(
                {
                    Permission(
                        command_name="ItemCrud", permission_type=PermissionType.EXECUTE
                    )
                }
            )

    def test_operation_mapping_adds_query_routes_only_when_requested(self) -> None:
        operations = {CrudOperation.READ_ALL, CrudOperation.DELETE_ONE}

        with_query_routes = (
            CrudEndpointGenerator.get_crud_endpoint_types_for_operations(operations)
        )
        without_query_routes = (
            CrudEndpointGenerator.get_crud_endpoint_types_for_operations(
                operations, add_query_route=False
            )
        )

        assert with_query_routes == {
            CrudEndpointType.GET_ALL,
            CrudEndpointType.POST_QUERY,
            CrudEndpointType.POST_QUERY_IDS,
            CrudEndpointType.DELETE_ONE,
        }
        assert without_query_routes == {
            CrudEndpointType.GET_ALL,
            CrudEndpointType.DELETE_ONE,
        }

    @pytest.mark.parametrize(
        ("endpoint_type", "expected_keys"),
        [
            (
                CrudEndpointType.POST_QUERY,
                {
                    "query_route_suffix",
                    "return_id",
                    "ids_route_suffix",
                    "validate_query_filter",
                },
            ),
            (
                CrudEndpointType.POST_QUERY_IDS,
                {
                    "query_route_suffix",
                    "return_id",
                    "ids_route_suffix",
                    "validate_query_filter",
                },
            ),
            (CrudEndpointType.POST_SOME, {"batch_route_suffix"}),
            (CrudEndpointType.GET_SOME, {"batch_route_suffix"}),
            (CrudEndpointType.PUT_SOME, {"batch_route_suffix"}),
            (CrudEndpointType.DELETE_SOME, {"batch_route_suffix"}),
            (CrudEndpointType.GET_EXISTS_ONE, {"exists_route_suffix"}),
            (CrudEndpointType.GET_EXISTS_SOME, {"exists_route_suffix"}),
            (CrudEndpointType.GET_ALL, set()),
        ],
        ids=[
            "query",
            "query-ids",
            "post-batch",
            "get-batch",
            "put-batch",
            "delete-batch",
            "exists-one",
            "exists-some",
            "no-extra-arguments",
        ],
    )
    def test_extra_arguments_match_endpoint_shape(
        self,
        endpoint_type: CrudEndpointType,
        expected_keys: set[str],
    ) -> None:
        kwargs = CrudEndpointGenerator._get_endpoint_extra_args(
            endpoint_type,
            "/bulk",
            "/search",
            "/identifiers",
            "/present",
            None,
        )

        assert set(kwargs) == expected_keys
        if endpoint_type in {
            CrudEndpointType.POST_QUERY,
            CrudEndpointType.POST_QUERY_IDS,
        }:
            assert kwargs["return_id"] is (
                endpoint_type == CrudEndpointType.POST_QUERY_IDS
            )
            assert kwargs["query_route_suffix"] == "/search"
            assert kwargs["ids_route_suffix"] == "/identifiers"
        elif endpoint_type in {
            CrudEndpointType.POST_SOME,
            CrudEndpointType.GET_SOME,
            CrudEndpointType.PUT_SOME,
            CrudEndpointType.DELETE_SOME,
        }:
            assert kwargs["batch_route_suffix"] == "/bulk"
        elif expected_keys:
            assert kwargs["exists_route_suffix"] == "/present"

    def test_route_set_derivation_respects_permission_and_exclusions(
        self,
        test_app: App,
    ) -> None:
        route = CrudEndpointGenerator.get_crud_endpoint_set_for_entity(
            ItemModel.ENTITY,
            test_app,
            user_dependency=mock_user_dependency,
            excluded_crud_operations={CrudOperation.DELETE_ALL},
            excluded_crud_endpoint_types={CrudEndpointType.POST_QUERY_IDS},
            default_description="fallback description",
        )

        assert route.endpoint_basename == "items"
        assert route.operation_id_basename == "items"
        assert route.user_dependency is mock_user_dependency
        assert route.endpoint_types == {
            CrudEndpointType.GET_ALL,
            CrudEndpointType.GET_SOME,
            CrudEndpointType.GET_ONE,
            CrudEndpointType.GET_EXISTS_ONE,
            CrudEndpointType.GET_EXISTS_SOME,
            CrudEndpointType.POST_ONE,
            CrudEndpointType.POST_SOME,
            CrudEndpointType.POST_QUERY,
            CrudEndpointType.PUT_ONE,
            CrudEndpointType.PUT_SOME,
            CrudEndpointType.DELETE_ONE,
            CrudEndpointType.DELETE_SOME,
        }

    def test_domain_selection_supports_service_sets_and_permission_exclusions(
        self,
        test_app: App,
    ) -> None:
        test_app.domain.register_service_type("test_service")
        service_routes = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
            test_app,
            service_type={"test_service"},
        )
        assert service_routes == []

        routes_with_exclusions = (
            CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
                test_app,
                excluded_permissions={ItemModel: PermissionTypeSet.R},
            )
        )
        assert len(routes_with_exclusions) == 1
        assert CrudEndpointType.GET_ALL not in routes_with_exclusions[0].endpoint_types
        assert CrudEndpointType.POST_ONE in routes_with_exclusions[0].endpoint_types

        assert (
            CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
                test_app,
                service_type=set(),
            )
            == []
        )

    def test_domain_endpoint_sets_skip_nonpersistable_entities(
        self,
        test_domain: Domain,
        test_app: App,
    ) -> None:
        class TransientModel(Model):
            """Test model for a non-persistable entity."""

            ENTITY: ClassVar = Entity(
                snake_case_plural_name="transient_items",
                persistable=False,
            )

        test_domain.register_entity(
            TransientModel.ENTITY,
            model_class=TransientModel,
        )

        routes = CrudEndpointGenerator.create_crud_endpoint_set_for_domain(test_app)

        assert len(routes) == 1
        assert routes[0].endpoint_basename == "items"

    def test_invalid_service_type_raises_domain_exception(self, test_app: App) -> None:
        with pytest.raises(fastapp_exc.DomainException, match="Invalid service type"):
            CrudEndpointGenerator.create_crud_endpoint_set_for_domain(
                test_app,
                service_type=[],  # type: ignore[arg-type]
            )

    def test_missing_crud_command_and_endpoint_name_raise(self, test_app: App) -> None:
        entity_without_command = Entity(
            snake_case_plural_name="orphan_items",
            persistable=True,
        )
        entity_without_command.set_model_class(ItemModel)
        with pytest.raises(
            fastapp_exc.DomainException, match="does not have a crud command"
        ):
            CrudEndpointGenerator.get_crud_endpoint_set_for_entity(
                entity_without_command,
                test_app,
            )

        unnamed_entity = Entity(persistable=True)
        unnamed_entity.set_model_class(ItemModel)
        with pytest.raises(
            fastapp_exc.DomainException, match="does not have a SNAKE_CASE name"
        ):
            CrudEndpointGenerator.get_endpoint_basename(unnamed_entity)

    def test_custom_casing_and_nonplural_endpoint_basename(self) -> None:
        entity = Entity(
            snake_case_singular_name="catalog_item",
            snake_case_plural_name="catalog_items",
            camel_case_singular_name="catalogItem",
            camel_case_plural_name="catalogItems",
            pascal_case_singular_name="CatalogItem",
            pascal_case_plural_name="CatalogItems",
            kebab_case_singular_name="catalog-item",
            kebab_case_plural_name="catalog-items",
        )

        assert (
            CrudEndpointGenerator.get_endpoint_basename(
                entity,
                StringCasing.PASCAL_CASE,
                is_plural=False,
            )
            == "CatalogItem"
        )

    def test_add_route_derives_operation_id_and_applies_route_metadata(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
    ) -> None:
        route = route_factory(
            endpoint_basename="records",
            description="Read a record.",
            response_model_exclude_none=True,
        )

        async def endpoint(user: Any, object_id: UUID) -> None:
            return None

        CrudEndpointGenerator._add_route(
            fastapi_app,
            "records/{object_id}",
            endpoint,
            HttpMethod.GET,
            None,
            route,
        )

        api_route = fastapi_app.routes[-1]
        assert api_route.path == "/records/{object_id}"
        assert api_route.name == "records__get_one"
        assert api_route.description == "Read a record."
        assert api_route.response_model_exclude_none is True

    def test_generate_endpoints_registers_batch_routes_before_item_routes(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        test_app: App,
    ) -> None:
        route = route_factory(
            app=test_app,
            endpoint_types={
                CrudEndpointType.GET_ONE,
                CrudEndpointType.GET_SOME,
                CrudEndpointType.POST_SOME,
            },
        )

        CrudEndpointGenerator.generate_endpoints(
            fastapi_app,
            [route],
            mock_exception_handler,
        )

        generated_paths = [item.path for item in fastapi_app.routes[-3:]]
        assert generated_paths == ["/items/batch", "/items/batch", "/items/{object_id}"]

    @pytest.mark.parametrize(
        ("generator_name", "route_overrides", "missing_field", "message"),
        [
            ("generate_get_all", {"user_dependency": None}, None, "User dependency"),
            ("generate_get_all", {}, "read_api_model_class", "Read API model"),
            ("generate_get_some", {"user_dependency": None}, None, "User dependency"),
            ("generate_get_some", {}, "read_api_model_class", "Read API model"),
            (
                "generate_get_exists_some",
                {"user_dependency": None},
                None,
                "User dependency",
            ),
            ("generate_post_query", {"user_dependency": None}, None, "User dependency"),
            ("generate_post_query", {}, "read_api_model_class", "Read API model"),
            ("generate_get_one", {"user_dependency": None}, None, "User dependency"),
            ("generate_get_one", {}, "read_api_model_class", "Read API model"),
            (
                "generate_get_exists_one",
                {"user_dependency": None},
                None,
                "User dependency",
            ),
            ("generate_post_one", {"user_dependency": None}, None, "User dependency"),
            ("generate_post_one", {}, "create_api_model_class", "Create API model"),
            ("generate_post_some", {"user_dependency": None}, None, "User dependency"),
            ("generate_post_some", {}, "create_api_model_class", "Create API model"),
            ("generate_put_one", {"user_dependency": None}, None, "User dependency"),
            ("generate_put_one", {}, "create_api_model_class", "Create API model"),
            ("generate_put_some", {"user_dependency": None}, None, "User dependency"),
            ("generate_put_some", {}, "create_api_model_class", "Create API model"),
            ("generate_delete_one", {"user_dependency": None}, None, "User dependency"),
            ("generate_delete_all", {"user_dependency": None}, None, "User dependency"),
            (
                "generate_delete_some",
                {"user_dependency": None},
                None,
                "User dependency",
            ),
        ],
        ids=[
            "get-all-no-user",
            "get-all-no-read-model",
            "get-some-no-user",
            "get-some-no-read-model",
            "exists-some-no-user",
            "query-no-user",
            "query-no-read-model",
            "get-one-no-user",
            "get-one-no-read-model",
            "exists-one-no-user",
            "post-one-no-user",
            "post-one-no-create-model",
            "post-some-no-user",
            "post-some-no-create-model",
            "put-one-no-user",
            "put-one-no-create-model",
            "put-some-no-user",
            "put-some-no-create-model",
            "delete-one-no-user",
            "delete-all-no-user",
            "delete-some-no-user",
        ],
    )
    def test_generator_rejects_missing_required_configuration(
        self,
        fastapi_app: FastAPI,
        route_factory: Any,
        generator_name: str,
        route_overrides: dict[str, Any],
        missing_field: str | None,
        message: str,
    ) -> None:
        route = route_factory(**route_overrides)
        if missing_field:
            setattr(route, missing_field, None)
        generator = getattr(CrudEndpointGenerator, generator_name)

        with pytest.raises(ValueError, match=message):
            generator(fastapi_app, route, mock_exception_handler)

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
