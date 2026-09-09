"""Unit tests for CrudEndpointSet configuration model."""

from __future__ import annotations

from typing import ClassVar
from uuid import UUID

import pytest
from pydantic import BaseModel

from gen_epix.fastapp.api.crud_endpoint_set import CrudEndpointSet
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import CrudEndpointType, CrudOperation
from gen_epix.fastapp.model import CrudCommand, Model

# Test fixtures and dummy models


class DummyModel(Model):
    """Test model for endpoint configuration."""

    id: UUID | None = None
    name: str = ""

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="dummy_models",
        table_name="dummy_model",
        persistable=True,
        keys=create_keys({1: "id"}),
    )


class DummyCrudCommand(CrudCommand):
    """Test CRUD command."""

    NAME = "DummyCrud"
    MODEL_CLASS = DummyModel

    operation: CrudOperation = CrudOperation.READ_ALL
    return_id: bool = False


@pytest.fixture
def test_app() -> App:
    """Create a test App instance."""
    domain = Domain(name="test")
    app: App = App(name="test_app", domain=domain)
    return app


class TestCrudEndpointSetCreation:
    """Tests for CrudEndpointSet creation and initialization."""

    def test_creates_with_minimal_fields(self, test_app: App) -> None:
        """Verify CrudEndpointSet creates with required fields."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.model_class == DummyModel
        assert endpoint_set.endpoint_basename == "/items"
        assert endpoint_set.id_class == UUID

    def test_read_api_model_class_defaults_to_model_class(self, test_app: App) -> None:
        """Verify read_api_model_class defaults to model_class."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.read_api_model_class == DummyModel

    def test_create_api_model_class_defaults_to_read_api_model_class(
        self, test_app: App
    ) -> None:
        """Verify create_api_model_class defaults to read_api_model_class."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.create_api_model_class == DummyModel

    def test_custom_read_api_model_class(self, test_app: App) -> None:
        """Verify can override read_api_model_class."""

        class ReadModel(BaseModel):
            id: UUID | None = None
            name: str = ""

        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            read_api_model_class=ReadModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.read_api_model_class == ReadModel

    def test_custom_create_api_model_class(self, test_app: App) -> None:
        """Verify can override create_api_model_class."""

        class CreateModel(BaseModel):
            name: str

        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            create_api_model_class=CreateModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.create_api_model_class == CreateModel


class TestCrudEndpointSetFlags:
    """Tests for CRUD endpoint response flags."""

    def test_post_returns_id_defaults_to_false(self, test_app: App) -> None:
        """Verify post_returns_id defaults to False."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.POST_ONE},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.post_returns_id is False

    def test_post_returns_id_can_be_set_true(self, test_app: App) -> None:
        """Verify post_returns_id can be set to True."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.POST_ONE},
            app=test_app,
            id_class=UUID,
            post_returns_id=True,
        )
        assert endpoint_set.post_returns_id is True

    def test_put_returns_id_defaults_to_false(self, test_app: App) -> None:
        """Verify put_returns_id defaults to False."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.PUT_ONE},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.put_returns_id is False

    def test_delete_all_returns_id_defaults_to_false(self, test_app: App) -> None:
        """Verify delete_all_returns_id defaults to False."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.DELETE_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.delete_all_returns_id is False


class TestCrudEndpointSetUserDependency:
    """Tests for user dependency in endpoint set."""

    def test_user_dependency_optional(self, test_app: App) -> None:
        """Verify user_dependency is optional."""
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.user_dependency is None

    def test_user_dependency_can_be_callable(self, test_app: App) -> None:
        """Verify user_dependency can be set to a callable."""

        def get_user() -> str:
            return "test_user"

        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
            user_dependency=get_user,
        )
        assert endpoint_set.user_dependency == get_user
        assert endpoint_set.user_dependency() == "test_user"


class TestCrudEndpointSetValidation:
    """Tests for CrudEndpointSet validation."""

    def test_requires_model_class(self, test_app: App) -> None:
        """Verify model_class is required."""
        with pytest.raises(Exception):  # Pydantic validation error
            CrudEndpointSet(  # type: ignore[call-overload]
                endpoint_basename="/items",
                crud_command_class=DummyCrudCommand,
                endpoint_types={CrudEndpointType.GET_ALL},
                app=test_app,
                id_class=UUID,
            )

    def test_requires_endpoint_basename(self, test_app: App) -> None:
        """Verify endpoint_basename is required."""
        with pytest.raises(Exception):  # Pydantic validation error
            CrudEndpointSet(  # type: ignore[call-overload]
                model_class=DummyModel,
                crud_command_class=DummyCrudCommand,
                endpoint_types={CrudEndpointType.GET_ALL},
                app=test_app,
                id_class=UUID,
            )

    def test_preserves_explicit_read_model_class(self, test_app: App) -> None:
        """Verify explicitly set read_api_model_class is preserved."""

        class CustomReadModel(BaseModel):
            id: UUID | None = None

        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            read_api_model_class=CustomReadModel,
            create_api_model_class=CustomReadModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types={CrudEndpointType.GET_ALL},
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.read_api_model_class == CustomReadModel
        assert endpoint_set.create_api_model_class == CustomReadModel


class TestCrudEndpointSetMultipleEndpointTypes:
    """Tests for endpoint sets with multiple endpoint types."""

    def test_multiple_endpoint_types(self, test_app: App) -> None:
        """Verify endpoint_types accepts multiple CrudEndpointType values."""
        types = {
            CrudEndpointType.GET_ALL,
            CrudEndpointType.GET_ONE,
            CrudEndpointType.POST_ONE,
        }
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types=types,
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.endpoint_types == types

    def test_endpoint_types_persisted(self, test_app: App) -> None:
        """Verify endpoint_types are preserved as provided."""
        types = {CrudEndpointType.DELETE_ALL, CrudEndpointType.DELETE_SOME}
        endpoint_set = CrudEndpointSet(
            model_class=DummyModel,
            endpoint_basename="/items",
            crud_command_class=DummyCrudCommand,
            endpoint_types=types,
            app=test_app,
            id_class=UUID,
        )
        assert endpoint_set.endpoint_types == types
