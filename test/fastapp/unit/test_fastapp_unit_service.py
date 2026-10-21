from collections.abc import Hashable
from typing import Any, ClassVar, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import CrudCommand, Model
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import EqualsUuidFilter
from gen_epix.filter.enum import FilterType


class ServiceModel(Model):
    """Represents a model used to test BaseService CRUD behavior."""

    id: UUID | None = None

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="service_models",
        table_name="service_model",
        persistable=True,
        keys=create_keys({1: "id"}),
    )


class ServiceCrudCommand(CrudCommand):
    """Represents a BaseService test CRUD request."""

    MODEL_CLASS: ClassVar = ServiceModel


class ExistsRepository(BaseRepository):
    """Supplies configured existence and model results to BaseService tests."""

    def __init__(
        self, exists_results: list[bool] | bool, existing_models: list[ServiceModel]
    ) -> None:
        super().__init__()
        self.exists_results = exists_results
        self.existing_models = existing_models
        self.read_some_ids: list[Hashable] | None = None

    @classmethod
    def create_repository(cls, **kwargs: Any) -> "ExistsRepository":
        """Create a repository instance for the abstract base contract."""
        raise NotImplementedError()

    def crud(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        operation: CrudOperation,
        objs: Model | None = None,
        obj_ids: Hashable | list[Hashable] | None = None,
        return_id: bool = False,
        filter: Any = None,
        limit: int = 0,
        offset: int = 0,
        **kwargs: Any,
    ) -> Any:
        """Return configured raw existence results and existing models."""
        del uow, user_id, model_class, objs, return_id, filter, limit, offset, kwargs
        if operation == CrudOperation.EXISTS_SOME:
            return self.exists_results
        if operation == CrudOperation.EXISTS_ONE:
            return self.exists_results
        if operation == CrudOperation.READ_SOME:
            self.read_some_ids = list(cast(list[Hashable], obj_ids))
            return self.existing_models
        raise AssertionError(f"Unexpected operation: {operation}")

    def read_fields(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        field_names: list[str],
        filter: Any = None,
        **kwargs: Any,
    ) -> list[tuple]:
        """Satisfy the abstract repository interface for these tests."""
        raise NotImplementedError()

    def split_filter(self, model_class: type, filter: Any) -> tuple[None, None]:
        """Keep the complete access filter in the service layer."""
        del model_class, filter
        return None, None

    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: type[Model],
        obj_ids: list[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        """Satisfy the abstract repository interface for these tests."""
        del (
            uow,
            user_id,
            model_class,
            obj_ids,
            verify_exists,
            verify_duplicate,
        )

    def uow(self, **kwargs: Any) -> BaseUnitOfWork:
        """Reject unit-of-work creation, which these direct delegation tests avoid."""
        del kwargs
        raise NotImplementedError()


class ConcreteService(BaseService):
    """Provides a concrete BaseService type for direct delegation tests."""

    def register_handlers(self) -> None:
        """Avoid application registration in direct delegation tests."""


def _service_with_repository(repository: ExistsRepository) -> ConcreteService:
    """Build a minimal BaseService instance for direct CRUD delegation tests."""
    ServiceModel.ENTITY.set_model_class(ServiceModel)
    service = object.__new__(ConcreteService)
    service._repository = repository
    return service


@pytest.mark.parametrize(
    ("operation", "obj_ids", "exists_results", "expected"),
    [
        pytest.param(
            CrudOperation.EXISTS_SOME,
            "many",
            [True, False, True],
            [True, False, False],
            id="some-accessible-missing-and-inaccessible",
        ),
        pytest.param(
            CrudOperation.EXISTS_ONE,
            "one",
            True,
            False,
            id="one-inaccessible",
        ),
    ],
)
def test_crud_repository_hides_inaccessible_existing_ids(
    operation: CrudOperation,
    obj_ids: str,
    exists_results: list[bool] | bool,
    expected: list[bool] | bool,
) -> None:
    """Return false for missing and inaccessible identifiers in EXISTS commands."""
    accessible_id, missing_id, inaccessible_id = uuid4(), uuid4(), uuid4()
    command_obj_ids: UUID | list[UUID]
    existing_models: list[ServiceModel]
    if obj_ids == "many":
        command_obj_ids = [accessible_id, missing_id, inaccessible_id]
        existing_models = [
            ServiceModel(id=accessible_id),
            ServiceModel(id=inaccessible_id),
        ]
    else:
        command_obj_ids = inaccessible_id
        existing_models = [ServiceModel(id=inaccessible_id)]
    repository = ExistsRepository(exists_results, existing_models)
    service = _service_with_repository(repository)
    cmd = ServiceCrudCommand(
        operation=operation,
        obj_ids=command_obj_ids,
        access_filter=EqualsUuidFilter(
            type=FilterType.EQUALS_UUID.value,
            key="id",
            value=accessible_id,
        ),
    )

    retval = service.crud_repository(cast(BaseUnitOfWork, object()), cmd)

    assert retval == expected
    expected_read_ids = (
        [accessible_id, inaccessible_id]
        if operation == CrudOperation.EXISTS_SOME
        else [inaccessible_id]
    )
    assert repository.read_some_ids == expected_read_ids
