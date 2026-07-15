"""
Unit tests for BaseRepository utilities and association updates.

Tests follow the repository's public API and cover all branches:
- update_association
- raise_on_duplicate_ids
- verify_crud_args

Abstract methods are exercised via a minimal concrete subclass or by
invoking the base definitions when appropriate to ensure coverage.
"""

from collections.abc import Hashable, Iterable
from test.util.mock_compat import Mock
from typing import Any, Callable, ClassVar, cast
from uuid import uuid4

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork


class AssocModel(Model):
    """Simple association model for testing update_association."""

    id: Hashable | None = None
    src: Hashable
    dst: Hashable

    # Persistable entity with id field name "id"
    ENTITY: ClassVar[Entity | None] = Entity(persistable=True, id_field_name="id")


def make_assoc(
    src: Hashable,
    dst: Hashable,
    id: Hashable | None = None,
) -> AssocModel:
    """Helper to create association objects."""
    return AssocModel(id=id, src=src, dst=dst)


class DummyRepository(BaseRepository):
    """Concrete repository for testing that delegates to mocks."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._crud_mock: Mock = Mock()
        self._read_fields_mock: Mock = Mock()

    @classmethod
    def create_repository(cls, **kwargs: Any) -> "DummyRepository":
        return cls(**kwargs)

    def crud(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        operation: CrudOperation,
        objs: Model | Iterable[Model] | None = None,
        obj_ids: Hashable | Iterable[Hashable] | None = None,
        filter: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        return self._crud_mock(
            uow, user_id, model_class, operation, filter, objs, obj_ids, **kwargs
        )

    def read_fields(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        field_names: list[str],
        filter: Any | None = None,
        **kwargs: Any,
    ) -> Iterable[tuple]:
        return cast(
            Iterable[tuple],
            self._read_fields_mock(
                uow, user_id, model_class, field_names, filter, **kwargs
            ),
        )

    def split_filter(
        self, model_class: type, filter: Any | None
    ) -> tuple[Any | None, Any | None]:
        return None, filter

    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: type[Model],
        obj_ids: Iterable[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        return None

    def uow(self, **kwargs: Any) -> BaseUnitOfWork:
        return cast(BaseUnitOfWork, Mock(spec=BaseUnitOfWork))


class BaseRepositoryTestCase:
    """Base test case with common fixtures and utilities."""

    def setup_method(self) -> None:
        self.repo = DummyRepository()
        self.uow: BaseUnitOfWork = cast(BaseUnitOfWork, Mock(spec=BaseUnitOfWork))

    def expectCrudCalled(
        self,
        operation: CrudOperation,
        call_index: int | None = None,
        assert_args: Callable[..., None] | None = None,
    ) -> None:
        calls = [
            c for c in self.repo._crud_mock.call_args_list if c.args[3] == operation
        ]
        if call_index is None:
            assert calls, f"Expected at least one {operation} call"
            call = calls[-1]
        else:
            assert (
                len(calls) > call_index
            ), f"Expected {operation} call at index {call_index}"
            call = calls[call_index]
        if assert_args:
            assert_args(*call.args, **call.kwargs)


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestUpdateAssociation(BaseRepositoryTestCase):
    """Tests for update_association covering all branches."""

    def test_delete_all_by_obj_id1_with_exclusions(self) -> None:
        # 1. Input
        obj_id1 = "P1"
        existing: list[AssocModel] = [
            make_assoc("P1", "C1", id="A1"),
            make_assoc("P1", "C2", id="A2"),
            make_assoc("P2", "C1", id="A3"),
        ]
        excluded = [make_assoc("P1", "C2", id="A2")]

        # 2. Mocks
        self.repo._crud_mock.return_value = existing

        # 3. Execute
        retval = self.repo.update_association(
            self.uow,
            user_id=None,
            model_class=AssocModel,
            link_field_name1="src",
            link_field_name2="dst",
            obj_id1=obj_id1,
            obj_id2=None,
            association_objs=[],
            excluded_association_objs=excluded,
        )

        # 4. Verify
        assert retval == []
        self.expectCrudCalled(CrudOperation.READ_ALL)

        def _assert_delete(
            _uow: Any,
            _user_id: Any,
            _model_class: Any,
            _op: Any,
            _filter: Any,
            _objs: Any,
            obj_ids: Any,
            *_: Any,
            **__: Any,
        ) -> None:
            assert sorted(obj_ids) == ["A1"]

        self.expectCrudCalled(CrudOperation.DELETE_SOME, assert_args=_assert_delete)

    def test_delete_all_by_obj_id2_with_exclusions(self) -> None:
        # 1. Input
        obj_id2 = "C1"
        existing: list[AssocModel] = [
            make_assoc("P1", "C1", id="A1"),
            make_assoc("P2", "C1", id="A2"),
            make_assoc("P2", "C2", id="A3"),
        ]
        excluded = [make_assoc("P2", "C1", id="A2")]

        # 2. Mocks
        self.repo._crud_mock.return_value = existing

        # 3. Execute
        _ = self.repo.update_association(
            self.uow,
            user_id=None,
            model_class=AssocModel,
            link_field_name1="src",
            link_field_name2="dst",
            obj_id1=None,
            obj_id2=obj_id2,
            association_objs=[],
            excluded_association_objs=excluded,
        )

        # 4. Verify
        self.expectCrudCalled(CrudOperation.READ_ALL)

        def _assert_delete(
            _uow: Any,
            _user_id: Any,
            _model_class: Any,
            _op: Any,
            _filter: Any,
            _objs: Any,
            obj_ids: Any,
            *_: Any,
            **__: Any,
        ) -> None:
            assert sorted(obj_ids) == ["A1"]

        self.expectCrudCalled(CrudOperation.DELETE_SOME, assert_args=_assert_delete)

    def test_duplicate_pairs_raise(self) -> None:
        # 1. Input
        a1 = make_assoc("P1", "C1", id="A1")
        a2 = make_assoc("P1", "C1", id="A2")
        objs = [a1, a2]

        # 2. Mocks
        self.repo._crud_mock.return_value = []

        # 3. Execute / 4. Verify
        with pytest.raises(exc.DuplicateIdsError) as ei:
            self.repo.update_association(
                self.uow,
                None,
                AssocModel,
                "src",
                "dst",
                None,
                None,
                objs,
            )
        assert set(ei.value.ids).issubset(["P1", "C1"])  # type: ignore[arg-type]

    def test_excluded_ids_present_raise(self) -> None:
        # 1. Input
        objs = [make_assoc("P1", "C1", id="A1")]
        excluded = [make_assoc("P1", "C1", id="A1")]

        # 2. Mocks
        self.repo._crud_mock.return_value = []

        # 3. Execute / 4. Verify
        with pytest.raises(exc.InvalidModelIdsError) as ei:
            self.repo.update_association(
                self.uow,
                None,
                AssocModel,
                "src",
                "dst",
                None,
                None,
                objs,
                excluded_association_objs=excluded,
            )
        assert set(ei.value.ids).issubset(["A1"])  # type: ignore[arg-type]

    def test_excluded_pairs_present_raise(self) -> None:
        # 1. Input
        objs = [make_assoc("P1", "C1", id="A1")]
        excluded = [make_assoc("P1", "C1", id="A9")]

        # 2. Mocks
        self.repo._crud_mock.return_value = []

        # 3. Execute / 4. Verify
        with pytest.raises(exc.InvalidModelIdsError):
            self.repo.update_association(
                self.uow,
                None,
                AssocModel,
                "src",
                "dst",
                None,
                None,
                objs,
                excluded_association_objs=excluded,
            )

    def test_invalid_entity_id_field_type_raises(self) -> None:
        # 1. Input
        bad_entity = Entity(persistable=True, id_field_name="123")
        AssocModel.ENTITY = bad_entity
        AssocModel.ENTITY.id_field_name = 123  # type: ignore[assignment]
        objs = [make_assoc("P1", "C1", id="A1")]

        # 2. Mocks
        self.repo._crud_mock.return_value = []

        # 3. Execute / 4. Verify
        with pytest.raises(exc.RepositoryServiceError):
            self.repo.update_association(
                self.uow,
                None,
                AssocModel,
                "src",
                "dst",
                None,
                None,
                objs,
            )
        # Reset entity to valid state for subsequent tests
        AssocModel.ENTITY = Entity(persistable=True, id_field_name="id")

    def test_create_update_delete_and_return_ids(self) -> None:
        # 1. Input (scoped by obj_id1="P1")
        existing: list[AssocModel] = [
            make_assoc("P1", "C1", id="E11"),
            make_assoc("P1", "C2", id="E12"),
            make_assoc("P2", "C2", id="E13"),
        ]
        # For P1: to_update: (P1,C1); to_create: (P1,C3); to_delete: (P1,C2)
        u1 = make_assoc("P1", "C1")
        c1 = make_assoc("P1", "C3", id="NEW1")
        objs = [u1, c1]

        # 2. Mocks
        self.repo._crud_mock.return_value = existing

        # 3. Execute
        retval = self.repo.update_association(
            self.uow,
            None,
            AssocModel,
            "src",
            "dst",
            obj_id1="P1",
            obj_id2=None,
            association_objs=objs,
            return_id=True,
        )

        # 4. Verify
        # IDs are set on update objs
        assert u1.id == "E11"
        # Calls
        self.expectCrudCalled(CrudOperation.CREATE_SOME)
        self.expectCrudCalled(CrudOperation.UPDATE_SOME)
        self.expectCrudCalled(CrudOperation.DELETE_SOME)
        # Return order corresponds to objs after mutation
        assert retval == ["E11", "NEW1"]

    def test_create_with_missing_id_raises(self) -> None:
        # 1. Input (scoped by obj_id1="P1")
        existing: list[AssocModel] = [make_assoc("P1", "C1", id="E11")]
        objs = [make_assoc("P1", "C2", id=None)]

        # 2. Mocks
        self.repo._crud_mock.return_value = existing

        # 3. Execute / 4. Verify
        with pytest.raises(exc.InvalidModelIdsError):
            self.repo.update_association(
                self.uow,
                None,
                AssocModel,
                "src",
                "dst",
                obj_id1="P1",
                obj_id2=None,
                association_objs=objs,
            )


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestRaiseOnDuplicateIds(BaseRepositoryTestCase):
    """Tests for static helper raise_on_duplicate_ids."""

    def test_no_duplicates(self) -> None:
        # 1. Input
        ids = ["a", "b", "c"]

        # 2. Mocks: N/A

        # 3. Execute
        BaseRepository.raise_on_duplicate_ids(ids)

        # 4. Verify: no exception
        assert True

    def test_duplicates_raise(self) -> None:
        # 1. Input
        ids = ["a", "b", "a", "c", "b"]

        # 2. Mocks: N/A

        # 3. Execute / 4. Verify
        with pytest.raises(exc.DuplicateIdsError) as ei:
            BaseRepository.raise_on_duplicate_ids(ids)
        assert set(cast(list, ei.value.ids)) == {"a", "b"}


@pytest.mark.scenario_ids("TC-SEC-28-03")
class TestInitAndAbstracts(BaseRepositoryTestCase):
    """Tests for __init__, properties, and abstract methods coverage."""

    def test_id_and_name_defaults_and_overrides(self) -> None:
        # 1. Input
        repo1 = DummyRepository()
        repo2 = DummyRepository(id="RID", name="RNAME")

        # 2. Mocks: N/A

        # 3. Execute: accessors
        _id1 = repo1.id
        _name1 = repo1.name
        _id2 = repo2.id
        _name2 = repo2.name

        # 4. Verify
        assert isinstance(_id1, str) and isinstance(_name1, str)
        assert _id2 == "RID" and _name2 == "RNAME"

    def test_class_abstract_create_repository_raises(self) -> None:
        # 1-4. Directly call on base class to cover NotImplementedError
        with pytest.raises(NotImplementedError):
            BaseRepository.create_repository()

    def test_instance_abstract_methods_raise_when_called_unbound(self) -> None:
        # 1. Input: dummy self object
        class Dummy:  # Minimal self placeholder
            pass

        dummy = Dummy()

        # 2-4. Call unbound functions directly to cover base raises
        with pytest.raises(NotImplementedError):
            BaseRepository.__dict__["crud"](
                dummy, None, None, Model, None, None, CrudOperation.READ_ALL, None
            )
        with pytest.raises(NotImplementedError):
            BaseRepository.__dict__["read_fields"](
                dummy, None, None, Model, ["id"], None
            )
        with pytest.raises(NotImplementedError):
            BaseRepository.__dict__["split_filter"](dummy, Model, None)
        with pytest.raises(NotImplementedError):
            BaseRepository.__dict__["verify_valid_ids"](
                dummy, None, uuid4(), Model, ["a"]
            )
        with pytest.raises(NotImplementedError):
            BaseRepository.__dict__["uow"](dummy)


# Parametrized tests for verify_crud_args


def _valid_args_for_operation(op: CrudOperation) -> tuple[type[Model], Any, Any]:
    """Return (model_class, objs, obj_ids) with valid shapes for given op."""
    model_class: type[Model] = AssocModel
    obj = make_assoc("S", "D", id="X")
    if op == CrudOperation.CREATE_ONE:
        return model_class, obj, None
    if op == CrudOperation.CREATE_SOME:
        return model_class, [obj], None
    if op == CrudOperation.READ_ONE:
        return model_class, None, "ID1"
    if op == CrudOperation.READ_SOME:
        return model_class, None, ["ID1", "ID2"]
    if op == CrudOperation.READ_ALL:
        return model_class, None, None
    if op == CrudOperation.UPDATE_ONE:
        return model_class, obj, None
    if op == CrudOperation.UPDATE_SOME:
        return model_class, [obj], None
    if op == CrudOperation.UPSERT_ONE:
        return model_class, obj, None
    if op == CrudOperation.UPSERT_SOME:
        return model_class, [obj], None
    if op == CrudOperation.DELETE_ONE:
        return model_class, None, "ID1"
    if op == CrudOperation.DELETE_SOME:
        return model_class, None, ["ID1", "ID2"]
    if op == CrudOperation.DELETE_ALL:
        return model_class, None, None
    if op == CrudOperation.UNDELETE_ONE:
        return model_class, None, "ID1"
    if op == CrudOperation.UNDELETE_SOME:
        return model_class, None, ["ID1", "ID2"]
    if op == CrudOperation.UNDELETE_ALL:
        return model_class, None, None
    if op == CrudOperation.EXISTS_ONE:
        return model_class, None, "ID1"
    if op == CrudOperation.EXISTS_SOME:
        return model_class, None, ["ID1", "ID2"]
    raise AssertionError(f"Unhandled operation: {op}")


@pytest.mark.scenario_ids("TC-SEC-28-03")
@pytest.mark.parametrize("operation", list(CrudOperation))
def test_verify_crud_args_valid(operation: CrudOperation) -> None:
    # 1. Input
    model_class, objs, obj_ids = _valid_args_for_operation(operation)

    # 2. Mocks: N/A

    # 3. Execute
    BaseRepository.verify_crud_args(model_class, objs, obj_ids, operation)

    # 4. Verify: no exception
    assert True


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_verify_crud_args_errors() -> None:
    # 1. Input: various invalid shapes to hit all error branches
    model_class: type[Model] = AssocModel
    valid_obj: AssocModel = make_assoc("S", "D", id="X")

    # 2. Mocks: N/A

    # 3. Execute / 4. Verify
    # _verify_no_objs via READ_ALL with objs provided
    with pytest.raises(exc.InvalidArgumentsError):
        BaseRepository.verify_crud_args(
            model_class, valid_obj, None, CrudOperation.READ_ALL
        )
    # _verify_no_obj_ids via CREATE_ONE with obj_ids provided
    with pytest.raises(exc.InvalidArgumentsError):
        BaseRepository.verify_crud_args(
            model_class, valid_obj, "ID", CrudOperation.CREATE_ONE
        )
    # _verify_one_obj wrong type
    with pytest.raises(exc.InvalidArgumentsError):
        BaseRepository.verify_crud_args(
            model_class, object(), None, CrudOperation.CREATE_ONE  # type: ignore[arg-type]
        )
    # _verify_one_id wrong shape (non-iterable hashable expected)
    with pytest.raises(exc.InvalidArgumentsError):
        BaseRepository.verify_crud_args(
            model_class, None, ["A", "B"], CrudOperation.READ_ONE
        )
    # _verify_some_objs wrong shape (single object passed)
    with pytest.raises(exc.InvalidArgumentsError):
        BaseRepository.verify_crud_args(
            model_class, valid_obj, None, CrudOperation.CREATE_SOME
        )
    # _verify_some_ids wrong type (non-iterable)
    with pytest.raises(exc.InvalidArgumentsError):
        BaseRepository.verify_crud_args(model_class, None, 123, CrudOperation.READ_SOME)
