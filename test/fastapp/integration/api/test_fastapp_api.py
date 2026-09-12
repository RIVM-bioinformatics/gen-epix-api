"""Integration tests for FastAPI CRUD endpoints.

Tests the full lifecycle of CRUD endpoint generation and invocation,
including all CRUD operations, parameter combinations, and error conditions.
"""

from __future__ import annotations

from typing import ClassVar
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

from gen_epix.fastapp.api.crud_endpoint_generator import (
    CrudEndpointGenerator,
)
from gen_epix.fastapp.api.crud_endpoint_set import CrudEndpointSet
from gen_epix.fastapp.app import App
from gen_epix.fastapp.domain.domain import Domain
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import CrudEndpointType, CrudOperation
from gen_epix.fastapp.model import CrudCommand, Model
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.service import BaseService

pytestmark = pytest.mark.integration


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for test row models."""


# ============================================================================
# Test Models
# ============================================================================


class Model1(Model):
    """First test model for CRUD endpoint testing."""

    id: UUID | None = None
    name: str = ""
    description: str | None = None

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="model1s",
        table_name="model1",
        persistable=True,
        keys=create_keys({1: "id"}),
    )
    NAME: ClassVar = "Model1"


# Set model_class on Entity
Model1.ENTITY.set_model_class(Model1)


class Model2(Model):
    """Second test model for CRUD endpoint testing."""

    id: UUID | None = None
    title: str = ""
    count: int = 0

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="model2s",
        table_name="model2",
        persistable=True,
        keys=create_keys({1: "id"}),
    )
    NAME: ClassVar = "Model2"


# Set model_class on Entity
Model2.ENTITY.set_model_class(Model2)


# ============================================================================
# SQLAlchemy Row Models
# ============================================================================


class SAModel1(Base):
    """SQLAlchemy row model for Model1."""

    __tablename__ = "model1"
    __table_args__ = ()

    id = sa.Column(sa.UUID, primary_key=True, default=uuid4)
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String, nullable=True)


class SAModel2(Base):
    """SQLAlchemy row model for Model2."""

    __tablename__ = "model2"
    __table_args__ = ()

    id = sa.Column(sa.UUID, primary_key=True, default=uuid4)
    title = sa.Column(sa.String, nullable=False)
    count = sa.Column(sa.Integer, default=0)


# Set db_model_class on entities
Model1.ENTITY.set_db_model_class(SAModel1)
Model2.ENTITY.set_db_model_class(SAModel2)


# ============================================================================
# API Request/Response Models
# ============================================================================


class Model1ReadAPI(BaseModel):
    """Read API model for Model1."""

    id: UUID | None = None
    name: str
    description: str | None = None

    @classmethod
    def from_model(cls, model: Model1) -> "Model1ReadAPI":
        """Convert domain model to API model."""
        return cls(
            id=model.id,
            name=model.name,
            description=model.description,
        )


class Model1CreateAPI(BaseModel):
    """Create API model for Model1."""

    id: UUID | None = None
    name: str
    description: str | None = None

    @classmethod
    def to_model(cls, api_model: "Model1CreateAPI") -> Model1:
        """Convert API model to domain model."""
        return Model1(
            id=api_model.id,
            name=api_model.name,
            description=api_model.description,
        )


class Model2ReadAPI(BaseModel):
    """Read API model for Model2."""

    id: UUID | None = None
    title: str
    count: int

    @classmethod
    def from_model(cls, model: Model2) -> "Model2ReadAPI":
        """Convert domain model to API model."""
        return cls(
            id=model.id,
            title=model.title,
            count=model.count,
        )


class Model2CreateAPI(BaseModel):
    """Create API model for Model2."""

    id: UUID | None = None
    title: str
    count: int = 0

    @classmethod
    def to_model(cls, api_model: "Model2CreateAPI") -> Model2:
        """Convert API model to domain model."""
        return Model2(
            id=api_model.id,
            title=api_model.title,
            count=api_model.count,
        )


# ============================================================================
# CRUD Commands
# ============================================================================


class Model1CrudCommand(CrudCommand):
    """CRUD command for Model1."""

    NAME: ClassVar = "Model1Crud"
    MODEL_CLASS: ClassVar = Model1

    operation: CrudOperation = CrudOperation.READ_ALL
    return_id: bool = False


class Model2CrudCommand(CrudCommand):
    """CRUD command for Model2."""

    NAME: ClassVar = "Model2Crud"
    MODEL_CLASS: ClassVar = Model2

    operation: CrudOperation = CrudOperation.READ_ALL
    return_id: bool = False


# ============================================================================
# Test Service
# ============================================================================


class CrudTestService(BaseService):
    """A test service for handling CRUD commands."""

    def register_handlers(self) -> None:
        """Register command handlers."""
        self.app.register_handler(Model1CrudCommand, self.crud)
        self.app.register_handler(Model2CrudCommand, self.crud)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def domain() -> Domain:
    """Create a test Domain."""
    dom = Domain(name="test_crud_api")
    # Register entities with domain
    dom.register_entity(
        Model1.ENTITY,
        model_class=Model1,
        crud_command_class=Model1CrudCommand,
    )
    dom.register_entity(
        Model2.ENTITY,
        model_class=Model2,
        crud_command_class=Model2CrudCommand,
    )
    return dom


@pytest.fixture
def app_instance(domain: Domain) -> App:
    """Create a test App instance."""
    return App(name="test_crud_app", domain=domain)


@pytest.fixture
def repository(domain: Domain) -> SARepository:
    """Create an in-memory SQLite repository for testing."""
    # For SQLite in-memory databases, we need to use URI mode to ensure
    # multiple connections share the same database
    shared_in_memory_uri = (
        f"sqlite:///file:test_db_{uuid4().hex}?mode=memory&cache=shared&uri=true"
    )

    # Create SARepository WITHOUT auto-creating tables (we'll do it manually)
    repo = SARepository.create_sa_repository(
        entities=[Model1.ENTITY, Model2.ENTITY],
        connection_string=shared_in_memory_uri,
        create_all=False,  # We'll create tables manually
        register_mappers=True,
    )

    # Now create all tables using the same engine the repository will use
    Base.metadata.create_all(repo._engine)

    return repo


@pytest.fixture
def test_service(app_instance: App, repository: SARepository) -> CrudTestService:
    """Create a test service with handlers registered."""
    # Create and return the service, which registers handlers on initialization
    return CrudTestService(
        app=app_instance,
        repository=repository,
        service_type="test_service",
    )


@pytest.fixture
def fastapi_app(app_instance: App, test_service: CrudTestService) -> FastAPI:
    """Create a FastAPI app with CRUD endpoints."""
    from collections.abc import Callable
    from typing import Annotated, cast

    from fastapi import Security

    from gen_epix.fastapp.model import User

    fapp = FastAPI(title="Test CRUD API")

    # Create a simple user dependency
    async def _get_current_user() -> User:
        """Get the current user for testing."""
        return User()

    get_current_user = cast(
        Callable[[], User],
        Annotated[
            User,
            Security(
                _get_current_user,
                scopes=["openid", "profile"],
            ),
        ],
    )

    # Define exception handler
    def handle_exception(
        error_code: str,
        user: User,
        exception: Exception,
        request_ids: list | None = None,
    ) -> None:
        """Handle exceptions from endpoint handlers."""
        from gen_epix.fastapp import exc
        from gen_epix.fastapp.api.exc import (
            BadRequest400HTTPException,
            Forbidden403HTTPException,
            ResourceNotFound404HTTPException,
        )

        if isinstance(exception, exc.InvalidArgumentsError):
            raise BadRequest400HTTPException(detail=str(exception))
        elif isinstance(exception, exc.InvalidIdsError):
            # Check if this is a "not found" error (should be 404)
            exception_str = str(exception).lower()
            if "no row found" in exception_str or "do not exist" in exception_str:
                raise ResourceNotFound404HTTPException(detail=str(exception))
            else:
                raise BadRequest400HTTPException(detail=str(exception))
        elif isinstance(exception, exc.NoResultsError):
            raise ResourceNotFound404HTTPException(detail=str(exception))
        elif isinstance(exception, exc.UnauthorizedAuthError):
            raise Forbidden403HTTPException(detail=str(exception))
        else:
            # Default to 400 for other exceptions
            raise BadRequest400HTTPException(detail=str(exception))

    # Register endpoints for Model1
    Model1_endpoint_set = CrudEndpointSet(
        model_class=Model1,
        read_api_model_class=Model1ReadAPI,
        create_api_model_class=Model1CreateAPI,
        endpoint_basename="model1",
        crud_command_class=Model1CrudCommand,
        endpoint_types={
            CrudEndpointType.GET_ALL,
            CrudEndpointType.GET_SOME,
            CrudEndpointType.POST_QUERY,
            CrudEndpointType.GET_ONE,
            CrudEndpointType.POST_ONE,
            CrudEndpointType.POST_SOME,
            CrudEndpointType.PUT_ONE,
            CrudEndpointType.PUT_SOME,
            CrudEndpointType.DELETE_ONE,
            CrudEndpointType.DELETE_SOME,
            CrudEndpointType.DELETE_ALL,
        },
        app=app_instance,
        id_class=UUID,
        user_dependency=get_current_user,
        operation_id_basename="Model1",
    )

    # Register endpoints for Model2
    Model2_endpoint_set = CrudEndpointSet(
        model_class=Model2,
        read_api_model_class=Model2ReadAPI,
        create_api_model_class=Model2CreateAPI,
        endpoint_basename="model2",
        crud_command_class=Model2CrudCommand,
        endpoint_types={
            CrudEndpointType.GET_ALL,
            CrudEndpointType.GET_SOME,
            CrudEndpointType.POST_QUERY,
            CrudEndpointType.GET_ONE,
            CrudEndpointType.POST_ONE,
            CrudEndpointType.POST_SOME,
            CrudEndpointType.PUT_ONE,
            CrudEndpointType.PUT_SOME,
            CrudEndpointType.DELETE_ONE,
            CrudEndpointType.DELETE_SOME,
            CrudEndpointType.DELETE_ALL,
        },
        app=app_instance,
        id_class=UUID,
        user_dependency=get_current_user,
        operation_id_basename="Model2",
    )

    # Generate and mount endpoints using the static method
    CrudEndpointGenerator.generate_endpoints(
        fast_api=fapp,
        routes=[Model1_endpoint_set, Model2_endpoint_set],
        handle_exception_fn=handle_exception,
    )

    return fapp


@pytest.fixture
def client(fastapi_app: FastAPI) -> TestClient:
    """Create a TestClient for the FastAPI app."""
    return TestClient(fastapi_app)


# ============================================================================
# Tests: GET_ALL Endpoint
# ============================================================================


class TestGetAllEndpoint:
    """Tests for GET_ALL CRUD endpoint."""

    def test_get_all_model1_empty(self, client: TestClient) -> None:
        """Verify GET /model1 returns empty list when no records exist."""
        response = client.get("/model1")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_model2_empty(self, client: TestClient) -> None:
        """Verify GET /model2 returns empty list when no records exist."""
        response = client.get("/model2")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_model1_with_records(self, client: TestClient) -> None:
        """Verify GET /model1 returns all records."""
        # Create records
        model1_id = uuid4()
        model2_id = uuid4()

        client.post(
            "/model1",
            json={"id": str(model1_id), "name": "Test 1", "description": "Desc 1"},
        )
        client.post(
            "/model1",
            json={"id": str(model2_id), "name": "Test 2", "description": "Desc 2"},
        )

        # Get all
        response = client.get("/model1")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2


# ============================================================================
# Tests: GET_ONE Endpoint
# ============================================================================


class TestGetOneEndpoint:
    """Tests for GET_ONE CRUD endpoint."""

    def test_get_one_model1_success(self, client: TestClient) -> None:
        """Verify GET /model1/{id} returns the correct record."""
        # Create a record
        create_response = client.post(
            "/model1",
            json={"name": "Test", "description": "Description"},
        )
        assert create_response.status_code == status.HTTP_200_OK
        created_data = create_response.json()
        model_id = created_data["id"]

        # Get one
        response = client.get(f"/model1/{model_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == model_id
        assert data["name"] == "Test"

    def test_get_one_model1_not_found(self, client: TestClient) -> None:
        """Verify GET /model1/{id} returns 404 when record not found."""
        model_id = uuid4()
        response = client.get(f"/model1/{model_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Tests: POST_ONE Endpoint
# ============================================================================


class TestPostOneEndpoint:
    """Tests for POST_ONE CRUD endpoint."""

    def test_post_one_model1_success(self, client: TestClient) -> None:
        """Verify POST /model1 creates a new record."""
        response = client.post(
            "/model1",
            json={"name": "New Item", "description": "A new item"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "New Item"
        assert data["description"] == "A new item"
        assert "id" in data

    def test_post_one_model2_success(self, client: TestClient) -> None:
        """Verify POST /model2 creates a new record."""
        response = client.post(
            "/model2",
            json={"title": "Title", "count": 5},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Title"
        assert data["count"] == 5

    def test_post_one_model1_invalid_request(self, client: TestClient) -> None:
        """Verify POST /model1 with invalid data returns error."""
        response = client.post(
            "/model1",
            json={"description": "Missing name field"},
        )
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_CONTENT,
        )


# ============================================================================
# Tests: PUT_ONE Endpoint
# ============================================================================


class TestPutOneEndpoint:
    """Tests for PUT_ONE CRUD endpoint."""

    def test_put_one_model1_success(self, client: TestClient) -> None:
        """Verify PUT /model1/{id} updates an existing record."""
        # Create a record
        create_response = client.post(
            "/model1",
            json={"name": "Original", "description": "Original desc"},
        )
        assert create_response.status_code == status.HTTP_200_OK
        created_data = create_response.json()
        model_id = created_data["id"]

        # Update it
        response = client.put(
            f"/model1/{model_id}",
            json={
                "id": model_id,
                "name": "Updated",
                "description": "Updated desc",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated"

    def test_put_one_model1_not_found(self, client: TestClient) -> None:
        """Verify PUT /model1/{id} returns 404 when record not found."""
        model_id = uuid4()
        response = client.put(
            f"/model1/{model_id}",
            json={
                "id": str(model_id),
                "name": "Updated",
                "description": "Updated desc",
            },
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Tests: DELETE_ONE Endpoint
# ============================================================================


class TestDeleteOneEndpoint:
    """Tests for DELETE_ONE CRUD endpoint."""

    def test_delete_one_model1_success(self, client: TestClient) -> None:
        """Verify DELETE /model1/{id} deletes an existing record."""
        # Create a record
        create_response = client.post(
            "/model1",
            json={"name": "To Delete", "description": "Desc"},
        )
        assert create_response.status_code == status.HTTP_200_OK
        created_data = create_response.json()
        model_id = created_data["id"]

        # Delete it
        response = client.delete(f"/model1/{model_id}")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        )

        # Verify it's gone
        response = client.get(f"/model1/{model_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_one_model1_not_found(self, client: TestClient) -> None:
        """Verify DELETE /model1/{id} returns 404 when record not found."""
        model_id = uuid4()
        response = client.delete(f"/model1/{model_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ============================================================================
# Tests: DELETE_ALL Endpoint
# ============================================================================


class TestDeleteAllEndpoint:
    """Tests for DELETE_ALL CRUD endpoint."""

    def test_delete_all_model1_success(self, client: TestClient) -> None:
        """Verify DELETE /model1 deletes all records."""
        # Create multiple records
        for i in range(3):
            client.post(
                "/model1",
                json={"name": f"Item {i}", "description": f"Desc {i}"},
            )

        # Verify they exist
        response = client.get("/model1")
        assert len(response.json()) == 3

        # Delete all
        response = client.delete("/model1")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        )

        # Verify all are gone
        response = client.get("/model1")
        assert response.json() == []

    def test_delete_all_model1_empty(self, client: TestClient) -> None:
        """Verify DELETE /model1 succeeds even when no records exist."""
        response = client.delete("/model1")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        )


# ============================================================================
# Tests: Parameterized Endpoint Tests
# ============================================================================


@pytest.mark.parametrize(
    "model_endpoint,create_payload",
    [
        (
            "/model1",
            {"name": "Test Name", "description": "Test Description"},
        ),
        (
            "/model2",
            {"title": "Test Title", "count": 10},
        ),
    ],
)
class TestParametrizedCRUD:
    """Parameterized tests for CRUD operations across models."""

    def test_post_get_cycle(
        self,
        client: TestClient,
        model_endpoint: str,
        create_payload: dict,
    ) -> None:
        """Verify create then read cycle works for all models."""
        # Create
        response = client.post(model_endpoint, json=create_payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item_id = data["id"]

        # Read back
        response = client.get(f"{model_endpoint}/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        retrieved = response.json()
        assert retrieved["id"] == item_id

    def test_post_update_cycle(
        self,
        client: TestClient,
        model_endpoint: str,
        create_payload: dict,
    ) -> None:
        """Verify create then update cycle works for all models."""
        # Create
        response = client.post(model_endpoint, json=create_payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item_id = data["id"]

        # Update payload (modify first field)
        update_payload = create_payload.copy()
        update_payload["id"] = item_id
        key = list(create_payload.keys())[0]
        if isinstance(create_payload[key], str):
            update_payload[key] = f"{create_payload[key]}_updated"
        else:
            update_payload[key] = create_payload[key] + 1

        # Update
        response = client.put(f"{model_endpoint}/{item_id}", json=update_payload)
        assert response.status_code == status.HTTP_200_OK

    def test_post_delete_cycle(
        self,
        client: TestClient,
        model_endpoint: str,
        create_payload: dict,
    ) -> None:
        """Verify create then delete cycle works for all models."""
        # Create
        response = client.post(model_endpoint, json=create_payload)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        item_id = data["id"]

        # Delete
        response = client.delete(f"{model_endpoint}/{item_id}")
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_204_NO_CONTENT,
        )

        # Verify deleted
        response = client.get(f"{model_endpoint}/{item_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
