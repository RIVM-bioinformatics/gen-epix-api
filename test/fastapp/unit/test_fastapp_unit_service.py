import logging
from collections.abc import Hashable
from datetime import datetime, timezone
from test.util.mock_compat import MagicMock
from typing import Any, ClassVar, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.domain.util import create_keys
from gen_epix.fastapp.enum import CrudOperation, EventTiming, OnException
from gen_epix.fastapp.model import CrudCommand, Model, UpdateAssociationCommand, User
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


class OtherServiceCrudCommand(ServiceCrudCommand):
    """Provides a second command class for handler registration tests."""


class ServiceAssociation(Model):
    """Represents an association used to test update-association handling."""

    id: UUID | None = None
    service_model_id: UUID | None

    ENTITY: ClassVar = Entity(
        snake_case_plural_name="service_associations",
        table_name="service_association",
        persistable=True,
        keys=create_keys({1: "id"}),
    )


class ServiceUpdateAssociationCommand(UpdateAssociationCommand):
    """Represents an association update request for BaseService tests."""

    ASSOCIATION_CLASS: ClassVar = ServiceAssociation
    LINK_FIELD_NAME1: ClassVar = "service_model_id"
    LINK_FIELD_NAME2: ClassVar = "service_model_id"


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


def _service_with_mock_repository() -> tuple[ConcreteService, MagicMock]:
    """Build a service and repository mock for orchestration tests."""
    ServiceModel.ENTITY.set_model_class(ServiceModel)
    ServiceAssociation.ENTITY.set_model_class(ServiceAssociation)
    repository = MagicMock(spec=BaseRepository)
    repository.uow.return_value.__enter__.return_value = object()
    service = object.__new__(ConcreteService)
    service._repository = repository
    service._crud_listeners = {}
    service._logger = None
    service._app = MagicMock()
    service._service_type = "test-service"
    service._id = "test-service-id"
    service._name = "test-service"
    service._id_factory = lambda: uuid4()
    return service, repository


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


def test_crud_listener_lifecycle_and_validation() -> None:
    """Listeners register in order, unregister cleanly, and reject invalid states."""
    service, _ = _service_with_mock_repository()
    listener = lambda service, cmd, retval: (cmd, retval)
    other_listener = lambda service, cmd, retval: (cmd, retval)

    service.register_crud_listener(ServiceCrudCommand, EventTiming.BEFORE, listener)
    service.register_crud_listener(
        ServiceCrudCommand, EventTiming.BEFORE, other_listener
    )
    assert service._crud_listeners[(ServiceCrudCommand, EventTiming.BEFORE)] == [
        listener,
        other_listener,
    ]
    with pytest.raises(ValueError, match="DURING"):
        service.register_crud_listener(ServiceCrudCommand, EventTiming.DURING, listener)
    with pytest.raises(ValueError, match="already registered"):
        service.register_crud_listener(ServiceCrudCommand, EventTiming.BEFORE, listener)

    service.unregister_crud_listener(ServiceCrudCommand, EventTiming.BEFORE, listener)
    assert service._crud_listeners[(ServiceCrudCommand, EventTiming.BEFORE)] == [
        other_listener
    ]
    with pytest.raises(ValueError, match="not registered"):
        service.unregister_crud_listener(
            ServiceCrudCommand, EventTiming.BEFORE, listener
        )
    with pytest.raises(ValueError, match="not registered"):
        service.unregister_crud_listener(
            ServiceCrudCommand, EventTiming.AFTER, listener
        )


@pytest.mark.parametrize(
    ("current_id", "on_id_set", "should_raise", "preserve_id"),
    [
        pytest.param(None, OnException.IGNORE, False, False, id="assign-missing"),
        pytest.param(uuid4(), OnException.IGNORE, False, True, id="ignore"),
        pytest.param(uuid4(), OnException.REPLACE, False, False, id="replace"),
        pytest.param(uuid4(), OnException.RAISE, True, True, id="raise"),
        pytest.param(uuid4(), "invalid", True, True, id="invalid-mode"),
    ],
)
def test_set_object_id_modes(
    current_id: UUID | None,
    on_id_set: OnException | str,
    should_raise: bool,
    preserve_id: bool,
) -> None:
    """Assign, preserve, replace, or reject existing object identifiers."""
    service, _ = _service_with_mock_repository()
    generated_id = uuid4()
    service._id_factory = lambda: generated_id
    obj = ServiceModel(id=current_id)

    if should_raise:
        exception = ValueError if on_id_set == "invalid" else exc.InvalidArgumentsError
        with pytest.raises(exception):
            service.set_object_id(obj, "id", on_id_set)
    else:
        service.set_object_id(obj, "id", on_id_set)
        assert obj.id == (current_id if preserve_id else generated_id)


def test_set_create_object_ids_rejects_missing_objects() -> None:
    """Create operations require payload objects before assigning identifiers."""
    service, _ = _service_with_mock_repository()
    cmd = ServiceCrudCommand(operation=CrudOperation.CREATE_ONE, objs=ServiceModel())
    cmd.objs = None

    with pytest.raises(exc.InvalidArgumentsError, match="No object provided"):
        service._set_create_object_ids(cmd, "id")


def test_get_repository_filters_combines_read_all_filters() -> None:
    """READ_ALL applies query and access constraints together."""
    service, _ = _service_with_mock_repository()
    query_filter = EqualsUuidFilter(
        type=FilterType.EQUALS_UUID.value, key="id", value=uuid4()
    )
    access_filter = EqualsUuidFilter(
        type=FilterType.EQUALS_UUID.value, key="id", value=uuid4()
    )
    cmd = ServiceCrudCommand(
        operation=CrudOperation.READ_ALL,
        query_filter=query_filter,
        access_filter=access_filter,
    )

    query, access = service._get_repository_filters(object(), cmd)

    assert query is not None
    assert list(query.match_rows([{"id": query_filter.value}])) == [False]
    assert access is None


def test_get_repository_filters_checks_write_access() -> None:
    """Writes with requested IDs fail when any object is outside the access filter."""
    service, repository = _service_with_mock_repository()
    allowed_id, denied_id = uuid4(), uuid4()
    repository.crud.return_value = [
        ServiceModel(id=allowed_id),
        ServiceModel(id=denied_id),
    ]
    cmd = ServiceCrudCommand(
        operation=CrudOperation.UPDATE_SOME,
        obj_ids=[allowed_id, denied_id],
        objs=[ServiceModel(id=allowed_id), ServiceModel(id=denied_id)],
        access_filter=EqualsUuidFilter(
            type=FilterType.EQUALS_UUID.value, key="id", value=allowed_id
        ),
    )

    with pytest.raises(exc.UnauthorizedAuthError, match="Unauthorized access"):
        service._get_repository_filters(object(), cmd)


def test_get_repository_filters_create_ignores_unassigned_ids() -> None:
    """CREATE access checks only read IDs already assigned in the payload."""
    service, repository = _service_with_mock_repository()
    assigned_id = uuid4()
    repository.crud.return_value = [ServiceModel(id=assigned_id)]
    cmd = ServiceCrudCommand(
        operation=CrudOperation.CREATE_SOME,
        objs=[ServiceModel(id=assigned_id), ServiceModel(id=None)],
        access_filter=EqualsUuidFilter(
            type=FilterType.EQUALS_UUID.value, key="id", value=assigned_id
        ),
    )

    query, access = service._get_repository_filters(object(), cmd)

    assert query is None
    assert access is cmd.access_filter
    assert repository.crud.call_args.kwargs["obj_ids"] == [assigned_id]


def test_get_user_and_repository_requires_user_and_repository() -> None:
    """Reject absent command users and uninitialized repositories."""
    service, _ = _service_with_mock_repository()
    with pytest.raises(exc.UnauthorizedAuthError, match="No user provided"):
        service._get_user_and_repository(
            ServiceCrudCommand(operation=CrudOperation.READ_ALL)
        )

    user = User(id=uuid4())
    cmd = ServiceCrudCommand(operation=CrudOperation.READ_ALL, user=user)
    service._repository = None
    with pytest.raises(exc.InitializationServiceError, match="No repository provided"):
        service._get_user_and_repository(cmd)


def test_get_model_links_for_association_update() -> None:
    """Resolve link metadata using an association command's model class."""
    service, _ = _service_with_mock_repository()
    same_service_links = {
        1: Link(link_field_name="service_model_id", link_model_class=ServiceModel)
    }
    other_service_links = {
        2: Link(link_field_name="service_model_id", link_model_class=ServiceModel)
    }
    service.app.domain.get_model_links.side_effect = [
        same_service_links,
        other_service_links,
    ]
    cmd = ServiceUpdateAssociationCommand(obj_id1=uuid4())

    actual = service._get_model_links(cmd)

    assert actual == (same_service_links, other_service_links)
    assert service.app.domain.get_model_links.call_args_list[0].args == (
        ServiceAssociation,
    )


def test_crud_runs_before_and_after_listeners() -> None:
    """CRUD listener changes to the result are returned to the caller."""
    service, repository = _service_with_mock_repository()
    repository.split_filter.return_value = (None, None)
    repository.crud.return_value = "repository-result"
    cmd = ServiceCrudCommand(operation=CrudOperation.READ_ONE, obj_ids=uuid4())
    before = MagicMock(side_effect=lambda service, command, retval: (command, retval))
    after = MagicMock(side_effect=lambda service, command, retval: (command, "updated"))
    service.register_crud_listener(ServiceCrudCommand, EventTiming.BEFORE, before)
    service.register_crud_listener(ServiceCrudCommand, EventTiming.AFTER, after)

    result = service.crud(cmd)

    assert result == "updated"
    before.assert_called_once_with(service, cmd, None)
    after.assert_called_once_with(service, cmd, "repository-result")


def test_crud_create_assigns_id_and_persists_object() -> None:
    """CREATE_ONE assigns a missing identifier and passes the object to storage."""
    service, repository = _service_with_mock_repository()
    repository.split_filter.return_value = (None, None)
    service.app.domain.get_model_links.return_value = {}
    created_id = uuid4()
    service._id_factory = lambda: created_id
    obj = ServiceModel(id=None)
    cmd = ServiceCrudCommand(operation=CrudOperation.CREATE_ONE, objs=obj)

    result = service.crud(cmd)

    assert obj.id == created_id
    assert result == repository.crud.return_value
    assert repository.crud.call_args.kwargs["objs"] is obj
    assert repository.crud.call_args.kwargs["links"] == {}


def test_update_association_assigns_ids_and_forwards_options() -> None:
    """Association updates generate missing IDs and forward command and call props."""
    service, repository = _service_with_mock_repository()
    repository.update_association.return_value = ["updated"]
    service.app.domain.get_model_links.return_value = {}
    service._verify_same_service_links = MagicMock()
    service._verify_other_service_links = MagicMock()
    association_id = uuid4()
    service._id_factory = lambda: association_id
    endpoint_id = uuid4()
    cmd = ServiceUpdateAssociationCommand(
        obj_id1=endpoint_id,
        association_objs=[ServiceAssociation(service_model_id=endpoint_id)],
        props={"replace": True},
    )

    result = service.update_association(cmd, extra=True)

    assert result == ["updated"]
    assert cmd.association_objs[0].id == association_id
    assert repository.update_association.call_args.kwargs == {
        "replace": True,
        "extra": True,
    }


def test_service_initialization_and_factory_properties() -> None:
    """Initialize service metadata, custom factories, logging, and registration."""
    app = MagicMock()
    app.create_log_message.return_value = "startup"
    created_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
    setup_logger = MagicMock()
    service = ConcreteService(
        app,
        service_type="test-service",
        id="fixed-id",
        name="fixed-name",
        register_handlers=False,
        id_factory=lambda: "generated-id",
        timestamp_factory=lambda: created_at,
        props={"flag": True},
        setup_logger=setup_logger,
    )

    assert service.id == "fixed-id"
    assert service.name == "fixed-name"
    assert service.service_type == "test-service"
    assert service.created_at == created_at
    assert service.app is app
    assert service.props == {"flag": True}
    assert service.generate_id() == "generated-id"
    assert service.generate_timestamp() == created_at
    app.domain.register_service_type.assert_called_once_with("test-service")
    setup_logger.info.assert_called_once_with("startup")
    app.register_handler.assert_not_called()


def test_service_uses_app_factories_and_registers_crud_handlers() -> None:
    """Use application factories and omit excluded CRUD handlers."""
    app = MagicMock()
    app.generate_id.return_value = 123
    created_at = datetime(2026, 3, 4, tzinfo=timezone.utc)
    app.generate_timestamp.return_value = created_at
    app.domain.get_crud_commands_for_service_type.return_value = [
        ServiceCrudCommand,
        OtherServiceCrudCommand,
    ]
    service = ConcreteService(app, service_type="test-service")

    assert service.id == "123"
    assert service.name == "123"
    assert service.created_at == created_at
    service.register_default_crud_handlers(exclude={OtherServiceCrudCommand})

    app.register_handler.assert_called_once_with(ServiceCrudCommand, service.crud)


def test_base_service_abstract_handler_and_repository_property() -> None:
    """The abstract handler rejects direct use and an unset repository is explicit."""
    service, _ = _service_with_mock_repository()
    with pytest.raises(NotImplementedError):
        BaseService.register_handlers(service)

    service._repository = None
    with pytest.raises(exc.ServiceException, match="Repository not set"):
        _ = service.repository


def test_logger_setter_and_log_message_debug_modes() -> None:
    """Delegate log messages and add service context only in debug mode."""
    service, _ = _service_with_mock_repository()
    logger = MagicMock(spec=logging.Logger)
    service.logger = logger
    assert service.logger is logger

    service.app.create_log_message.return_value = "formatted"
    service.create_log_message("abcd1234", "EVENT", request={"id": 1})
    service.app.create_log_message.assert_called_once_with(
        "abcd1234",
        "EVENT",
        add_debug_info=True,
        service={"id": "test-service-id", "name": "test-service"},
        request={"id": 1},
    )
    service.app.create_log_message.reset_mock()

    service.create_log_message("abcd1234", "EVENT", add_debug_info=False)
    service.app.create_log_message.assert_called_once_with(
        "abcd1234", "EVENT", add_debug_info=False
    )
    service.logger = None
    assert service.logger is None


def test_get_repository_filters_handles_single_and_unfiltered_operations() -> None:
    """Keep single-object filters separate and combine no-filter reads as empty."""
    service, _ = _service_with_mock_repository()
    access_filter = EqualsUuidFilter(
        type=FilterType.EQUALS_UUID.value, key="id", value=uuid4()
    )
    query, access = service._get_repository_filters(
        object(),
        ServiceCrudCommand(
            operation=CrudOperation.READ_ONE,
            obj_ids=uuid4(),
            access_filter=access_filter,
        ),
    )
    assert query is None
    assert access is access_filter

    query, access = service._get_repository_filters(
        object(), ServiceCrudCommand(operation=CrudOperation.READ_ALL)
    )
    assert query is None
    assert access is None


def test_get_repository_filters_skips_empty_create_access_lookup() -> None:
    """CREATE payloads with only unassigned IDs do not query existing objects."""
    service, repository = _service_with_mock_repository()
    access_filter = EqualsUuidFilter(
        type=FilterType.EQUALS_UUID.value, key="id", value=uuid4()
    )
    cmd = ServiceCrudCommand(
        operation=CrudOperation.CREATE_ONE,
        objs=ServiceModel(id=None),
        access_filter=access_filter,
    )

    query, access = service._get_repository_filters(object(), cmd)

    assert query is None
    assert access is access_filter
    repository.crud.assert_not_called()


def test_verify_same_service_links_deduplicates_ids_and_maps_invalid_ids() -> None:
    """Validate unique non-null linked IDs and translate repository failures."""
    service, repository = _service_with_mock_repository()
    link = Link(link_field_name="service_model_id", link_model_class=ServiceModel)
    cmd = ServiceUpdateAssociationCommand(
        association_objs=[
            ServiceAssociation(service_model_id=uuid4()),
            ServiceAssociation(service_model_id=uuid4()),
        ],
    )
    linked_ids = [obj.service_model_id for obj in cmd.association_objs]
    BaseService._verify_same_service_links(
        service, object(), cmd, cmd.association_objs, {1: link}
    )
    repository.verify_valid_ids.assert_called_once()
    assert set(repository.verify_valid_ids.call_args.args[3]) == set(linked_ids)
    assert repository.verify_valid_ids.call_args.kwargs["verify_duplicate"] is False

    repository.verify_valid_ids.side_effect = exc.InvalidIdsError("bad", "invalid")
    with pytest.raises(exc.InvalidLinkIdsError, match="Invalid ServiceModel"):
        BaseService._verify_same_service_links(
            service, object(), cmd, cmd.association_objs, {1: link}
        )


def test_verify_same_service_links_can_be_disabled_and_requires_repository() -> None:
    """Honor the command flag and reject invocation without repository setup."""
    service, repository = _service_with_mock_repository()
    cmd = ServiceUpdateAssociationCommand(
        association_objs=[ServiceAssociation(service_model_id=uuid4())],
        verify_same_service_links=False,
    )
    link = Link(link_field_name="service_model_id", link_model_class=ServiceModel)
    BaseService._verify_same_service_links(
        service, object(), cmd, cmd.association_objs, {1: link}
    )
    repository.verify_valid_ids.assert_not_called()

    service._repository = None
    with pytest.raises(exc.ServiceException, match="Repository not set"):
        BaseService._verify_same_service_links(service, object(), cmd, [], {})


def test_verify_write_links_rejects_missing_write_objects() -> None:
    """Write-link verification requires objects for a write command."""
    service, _ = _service_with_mock_repository()
    cmd = ServiceCrudCommand.model_construct(
        operation=CrudOperation.CREATE_ONE,
        objs=None,
        obj_ids=None,
        verify_same_service_links=False,
        verify_other_service_links=False,
    )

    with pytest.raises(exc.InvalidArgumentsError, match="No object provided"):
        service._verify_write_links(object(), cmd, {}, {})


def test_verify_other_service_links_deduplicates_and_translates_invalid_ids() -> None:
    """Resolve remote links once per unique ID and wrap invalid identifiers."""
    service, _ = _service_with_mock_repository()
    first_id, second_id = uuid4(), uuid4()
    cmd = ServiceUpdateAssociationCommand(
        association_objs=[
            ServiceAssociation(service_model_id=first_id),
            ServiceAssociation(service_model_id=first_id),
        ],
        verify_other_service_links=True,
    )
    link = Link(link_field_name="service_model_id", link_model_class=ServiceModel)
    service.app.domain.get_crud_command_for_model.return_value = ServiceCrudCommand

    service._verify_other_service_links(cmd, cmd.association_objs, {1: link})

    service.app.handle.assert_called_once()
    assert service.app.handle.call_args.args[0].obj_ids == [first_id]
    service.app.handle.reset_mock()
    service.app.handle.side_effect = exc.InvalidIdsError("bad", "invalid")
    cmd.association_objs[0].service_model_id = second_id
    with pytest.raises(exc.InvalidLinkIdsError, match="Invalid ServiceModel"):
        service._verify_other_service_links(cmd, cmd.association_objs, {1: link})


def test_verify_other_service_links_skips_disabled_empty_and_null_links() -> None:
    """Avoid remote commands when verification is disabled or no IDs are linked."""
    service, _ = _service_with_mock_repository()
    link = Link(link_field_name="service_model_id", link_model_class=ServiceModel)
    obj = ServiceAssociation(service_model_id=None)
    cmd = ServiceUpdateAssociationCommand(association_objs=[obj])
    service._verify_other_service_links(cmd, [obj], {1: link})
    cmd.verify_other_service_links = True
    service._verify_other_service_links(cmd, [], {1: link})
    service._verify_other_service_links(cmd, [obj], {})
    service.app.handle.assert_not_called()


def test_service_destructor_logs_shutdown() -> None:
    """Log service shutdown when a setup logger is configured."""
    service, _ = _service_with_mock_repository()
    service._setup_logger = MagicMock()
    service.create_log_message = MagicMock(return_value="stopping")

    BaseService.__del__(service)

    service.create_log_message.assert_called_once_with("d84f9d21", "STOPPING_SERVICE")
    service._setup_logger.info.assert_called_once_with("stopping")
