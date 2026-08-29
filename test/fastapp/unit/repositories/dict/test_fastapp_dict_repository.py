import datetime
import io
from test.util.mock_compat import MagicMock, Mock
from typing import Any, Iterable, Literal, Optional, cast
from uuid import UUID, uuid4

import pytest

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.dict.unit_of_work import DictUnitOfWork
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import Filter


class ParentModel(Model):
    id: UUID
    value: str


class ChildModel(Model):
    id: UUID
    value: str
    parent_id: Optional[UUID] = None
    parent: Optional[ParentModel] = None


def make_parent_entity(keys: bool = True) -> Entity:
    entity: Entity = MagicMock(spec=Entity)
    entity.persistable = True
    entity.name = "Parent"  # type: ignore[misc]
    entity.table_name = "parent"
    entity.model_class = ParentModel  # type: ignore[misc]
    entity.id_field_name = "id"
    entity.get_link_field_names.return_value = []  # type: ignore[attr-defined]
    # Return only data field(s)
    entity.get_field_names.return_value = ["value"]  # type: ignore[attr-defined]
    # Keys generator for unique constraint tests
    if keys:

        def _keys(obj: ParentModel) -> dict[str, Any]:
            return {"value": obj.value}

        entity.get_keys_generator.return_value = _keys  # type: ignore[attr-defined]
    else:

        def _empty_keys(obj: ParentModel) -> dict[str, Any]:
            return {}

        entity.get_keys_generator.return_value = _empty_keys  # type: ignore[attr-defined]
    return entity


def make_child_entity(keys: bool = True) -> Entity:
    entity: Entity = MagicMock(spec=Entity)
    entity.persistable = True
    entity.name = "Child"  # type: ignore[misc]
    entity.table_name = "child"
    entity.model_class = ChildModel  # type: ignore[misc]
    entity.id_field_name = "id"
    entity.get_link_field_names.return_value = ["parent_id"]  # type: ignore[attr-defined]
    # Link properties
    entity.get_link_properties_by_field_name.return_value = (1, ParentModel, "parent")  # type: ignore[attr-defined]
    # Data fields
    entity.get_field_names.return_value = ["value"]  # type: ignore[attr-defined]
    # Keys generator
    if keys:

        def _keys(obj: ChildModel) -> dict[str, Any]:
            return {"value": obj.value}

        entity.get_keys_generator.return_value = _keys  # type: ignore[attr-defined]
    else:

        def _empty_keys(obj: ChildModel) -> dict[str, Any]:
            return {}

        entity.get_keys_generator.return_value = _empty_keys  # type: ignore[attr-defined]
    return entity


def make_repo(
    entities: Iterable[Entity],
    db: dict[type[Model], dict[Any, Model]],
    extra_data: Literal["ignore", "raise", "drop"] = "ignore",
    missing_data: Literal["raise", "ignore"] = "ignore",
) -> DictRepository:
    return DictRepository(
        entities=entities,
        db=db,
        extra_data=extra_data,
        missing_data=missing_data,
        timestamp_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
    )


# Fixtures


@pytest.fixture
def parent_id() -> UUID:
    return uuid4()


@pytest.fixture
def child_id() -> UUID:
    return uuid4()


@pytest.fixture
def parent_repo(parent_id: UUID) -> DictRepository:
    parent = ParentModel(id=parent_id, value="p1")
    db: dict[type[Model], dict[Any, Model]] = {ParentModel: {parent_id: parent}}
    repo = make_repo([make_parent_entity(keys=True)], db)
    return repo


@pytest.fixture
def pc_repo(parent_id: UUID, child_id: UUID) -> DictRepository:
    parent = ParentModel(id=parent_id, value="p1")
    child = ChildModel(id=child_id, value="c1", parent_id=parent_id, parent=None)
    db: dict[type[Model], dict[Any, Model]] = {
        ParentModel: {parent_id: parent},
        ChildModel: {child_id: child},
    }
    repo = make_repo([make_parent_entity(keys=True), make_child_entity(keys=True)], db)
    return repo


# Tests for create_repository


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_no_file_initializes_empty_db() -> None:
    """Repository creation without a file should initialize empty model stores."""
    parent_entity = make_parent_entity()
    child_entity = make_child_entity()

    repository = DictRepository.create_repository(
        entities=[parent_entity, child_entity],
        file=None,
    )
    assert isinstance(repository, DictRepository)
    parent_model_class = cast(type[Model], parent_entity.model_class)
    child_model_class = cast(type[Model], child_entity.model_class)
    assert repository.db[parent_model_class] == {}
    assert repository.db[child_model_class] == {}


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_detect_pkl_calls_from_pkl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, bool] = {"pkl": False}

    def fake_from_pkl(
        repository_class: type, entities: Iterable[Entity], pkl_file: str, **kwargs: Any
    ) -> DictRepository:
        called["pkl"] = True
        # Return a minimal repository
        db: dict[type[Model], dict[Any, Model]] = {}
        return make_repo([], db)

    monkeypatch.setattr(
        DictRepository, "create_repository_from_pkl", staticmethod(fake_from_pkl)
    )
    repo = DictRepository.create_repository(file="/tmp/db.pkl")
    assert isinstance(repo, DictRepository)
    assert called["pkl"] is True


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_detect_zip_calls_from_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called: dict[str, bool] = {"zip": False}

    def fake_from_json(
        repository_class: type, entities: Iterable[Entity], zip_file: str, **kwargs: Any
    ) -> DictRepository:
        called["zip"] = True
        db: dict[type[Model], dict[Any, Model]] = {}
        return make_repo([], db)

    monkeypatch.setattr(
        DictRepository, "create_repository_from_json", staticmethod(fake_from_json)
    )
    repo = DictRepository.create_repository(file="/tmp/db.zip")
    assert isinstance(repo, DictRepository)
    assert called["zip"] is True


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_json_unsupported() -> None:
    with pytest.raises(NotImplementedError):
        DictRepository.create_repository(file="/tmp/db.json")


# Tests for create_repository_from_pkl


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_from_pkl_plain(monkeypatch: pytest.MonkeyPatch) -> None:
    db: dict[type[Model], dict[Any, Model]] = {ParentModel: {}}
    # Mock pickle.load to return db
    monkeypatch.setattr("pickle.load", lambda handle: db)
    # Mock open to avoid filesystem
    monkeypatch.setattr("builtins.open", lambda f, mode: io.BytesIO(b"dummy"))
    repo = DictRepository.create_repository_from_pkl(
        DictRepository, [make_parent_entity()], "/tmp/db.pkl"
    )
    assert isinstance(repo, DictRepository)
    assert repo.db == db


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_from_pkl_gz(monkeypatch: pytest.MonkeyPatch) -> None:
    db: dict[type[Model], dict[Any, Model]] = {ParentModel: {}}
    monkeypatch.setattr("pickle.load", lambda handle: db)
    monkeypatch.setattr("gzip.open", lambda f, mode: io.BytesIO(b"dummy"))
    repo = DictRepository.create_repository_from_pkl(
        DictRepository, [make_parent_entity()], "/tmp/db.pkl.gz"
    )
    assert isinstance(repo, DictRepository)
    assert repo.db == db


# Tests for create_repository_from_json


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_from_json_invalid_format() -> None:
    with pytest.raises(exc.RepositoryServiceError):
        DictRepository.create_repository_from_json(
            DictRepository, [make_parent_entity()], "/tmp/db.txt"
        )


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_create_repository_from_json_happy(
    monkeypatch: pytest.MonkeyPatch, parent_id: UUID
) -> None:
    parent_entity = make_parent_entity()

    # Fake zipfile.ZipFile
    class FakeZip:
        def __init__(self, *_: Any, **__: Any) -> None:
            pass

        def __enter__(self) -> "FakeZip":
            return self

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

        def namelist(self) -> list[str]:
            return ["parent.json"]

        def open(self, name: str) -> io.BytesIO:
            return io.BytesIO(b"[]")

    monkeypatch.setattr("zipfile.ZipFile", FakeZip)
    # Mock json.load to return one parent row
    monkeypatch.setattr(
        "json.load", lambda handle: [{"id": str(parent_id), "value": "p1"}]
    )

    repo = DictRepository.create_repository_from_json(
        DictRepository, [parent_entity], "/tmp/db.zip"
    )
    # db gets populated with model instances keyed by UUID (but json creates str -> ParentModel(**x) casts types)
    assert isinstance(repo, DictRepository)
    assert ParentModel in repo.db
    assert len(repo.db[ParentModel]) == 1


# __init__ validation tests


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_init_invalid_extra_data_raises(parent_id: UUID) -> None:
    parent_entity = make_parent_entity()
    db: dict[type[Model], dict[Any, Model]] = {
        ParentModel: {parent_id: ParentModel(id=parent_id, value="p")}
    }
    with pytest.raises(ValueError):
        DictRepository(
            [parent_entity],
            db,
            extra_data=cast(Any, "bad"),
            missing_data="ignore",
        )


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_init_invalid_missing_data_raises(parent_id: UUID) -> None:
    parent_entity = make_parent_entity()
    db: dict[type[Model], dict[Any, Model]] = {
        ParentModel: {parent_id: ParentModel(id=parent_id, value="p")}
    }
    with pytest.raises(ValueError):
        DictRepository(
            [parent_entity],
            db,
            extra_data="ignore",
            missing_data=cast(Any, "bad"),
        )


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_init_missing_data_raise(parent_id: UUID) -> None:
    parent_entity = make_parent_entity()
    with pytest.raises(ValueError):
        DictRepository([parent_entity], {}, extra_data="ignore", missing_data="raise")


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_init_composite_id_field_raises(parent_id: UUID) -> None:
    entity: Entity = make_parent_entity()
    entity.id_field_name = ["id1", "id2"]  # type: ignore[assignment]
    db: dict[type[Model], dict[Any, Model]] = {
        ParentModel: {parent_id: ParentModel(id=parent_id, value="p")}
    }
    with pytest.raises(NotImplementedError):
        DictRepository([entity], db, extra_data="ignore", missing_data="ignore")


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_db_property(parent_repo: DictRepository, parent_id: UUID) -> None:
    assert ParentModel in parent_repo.db
    assert parent_id in parent_repo.db[ParentModel]


# split_filter


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_split_filter_returns_filter_and_none(parent_repo: DictRepository) -> None:
    filter_: Filter = Mock(spec=Filter)
    f, where = parent_repo.split_filter(ParentModel, filter_)
    assert f is filter_
    assert where is None


# read_fields


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_read_fields_no_filter(parent_repo: DictRepository) -> None:
    uow: BaseUnitOfWork = parent_repo.uow()
    tuples = list(parent_repo.read_fields(uow, None, ParentModel, ["id", "value"]))
    assert len(tuples) == 1
    assert isinstance(tuples[0][0], UUID)
    assert isinstance(tuples[0][1], str)


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_read_fields_with_filter(parent_repo: DictRepository) -> None:
    uow: BaseUnitOfWork = parent_repo.uow()
    filter_: Filter = Mock(spec=Filter)
    # Return iterable matching zero rows
    filter_.filter_rows.return_value = []  # type: ignore[attr-defined]
    tuples = list(
        parent_repo.read_fields(uow, None, ParentModel, ["id", "value"], filter=filter_)
    )
    assert tuples == []
    filter_.filter_rows.assert_called()  # type: ignore[attr-defined]


# verify_valid_ids


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_verify_valid_ids_exists_and_duplicate(
    parent_repo: DictRepository, parent_id: UUID
) -> None:
    uow: BaseUnitOfWork = parent_repo.uow()
    # Invalid id triggers InvalidIdsError
    with pytest.raises(exc.InvalidIdsError):
        parent_repo.verify_valid_ids(
            uow,
            None,
            ParentModel,
            [parent_id, uuid4()],
            verify_exists=True,
            verify_duplicate=False,
        )
    # Duplicate triggers DuplicateIdsError
    with pytest.raises(exc.DuplicateIdsError):
        parent_repo.verify_valid_ids(
            uow,
            None,
            ParentModel,
            [parent_id, parent_id],
            verify_exists=False,
            verify_duplicate=True,
        )


# read_all, read_one, read_some


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_read_all_variants(pc_repo: DictRepository, parent_id: UUID) -> None:
    # Return copies by default
    parents = pc_repo.read_all(ParentModel, filter=None)
    assert len(parents) == 1
    assert parents[0].value == "p1"  # type: ignore[attr-defined]
    # Return IDs
    ids = pc_repo.read_all(ParentModel, filter=None, return_id=True)
    assert ids == [parent_id]
    # No copy
    children_no_copy = pc_repo.read_all(
        ChildModel, filter=None, return_id=False, return_copy=False
    )
    assert children_no_copy[0] is pc_repo.db[ChildModel][children_no_copy[0].id]  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_read_all_with_filter(parent_repo: DictRepository, parent_id: UUID) -> None:
    filter_: Filter = Mock(spec=Filter)
    # When return_id=True, match_rows is used
    filter_.match_rows.return_value = [True]  # type: ignore[attr-defined]
    ids = parent_repo.read_all(ParentModel, filter=filter_, return_id=True)
    assert ids == [parent_id]
    filter_.match_rows.assert_called()  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_read_one_and_some(parent_repo: DictRepository, parent_id: UUID) -> None:
    obj = parent_repo.read_one(ParentModel, parent_id)
    assert isinstance(obj, ParentModel)
    objs = parent_repo.read_some(ParentModel, [parent_id])
    assert len(objs) == 1
    # invalid id
    with pytest.raises(exc.InvalidIdsError):
        parent_repo.read_some(ParentModel, [uuid4()])
    # duplicate ids not allowed
    with pytest.raises(exc.DuplicateIdsError):
        parent_repo.read_some(
            ParentModel,
            [parent_id, parent_id],
            return_id=True,
            allow_duplicate_ids=False,
        )
    # allow duplicates
    objs_dup = parent_repo.read_some(
        ParentModel, [parent_id, parent_id], allow_duplicate_ids=True
    )
    assert len(objs_dup) == 2
    assert all(cast(ParentModel, x).id == parent_id for x in objs_dup)
    # No copy
    objs_nc = parent_repo.read_some(
        ParentModel,
        [parent_id],
        return_id=False,
        allow_duplicate_ids=False,
        return_copy=False,
    )
    assert objs_nc[0] is parent_repo.db[ParentModel][parent_id]


# upsert_some


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_upsert_create_and_update(parent_repo: DictRepository, parent_id: UUID) -> None:
    # Create new
    new_obj = ParentModel(id=uuid4(), value="new")
    created = parent_repo.upsert_one(
        None, ParentModel, new_obj, raise_on_present=True, raise_on_missing=False
    )
    assert isinstance(created, ParentModel)
    assert created.value == "new"
    # Update existing
    upd_obj = ParentModel(id=parent_id, value="updated")
    updated = parent_repo.upsert_one(
        None, ParentModel, upd_obj, raise_on_present=False, raise_on_missing=True
    )
    assert isinstance(updated, ParentModel)
    assert parent_repo.db[ParentModel][parent_id].value == "updated"  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_upsert_errors(parent_repo: DictRepository, parent_id: UUID) -> None:
    # Duplicate IDs among objs
    same_id = uuid4()
    a = ParentModel(id=same_id, value="a")
    b = ParentModel(id=same_id, value="b")
    with pytest.raises(exc.DuplicateIdsError):
        parent_repo.upsert_some(
            None, ParentModel, [a, b], raise_on_present=False, raise_on_missing=False
        )
    # Invalid type ids
    wrong = ChildModel(id=uuid4(), value="x")
    with pytest.raises(exc.InvalidModelIdsError):
        parent_repo.upsert_one(
            None, ParentModel, wrong, raise_on_present=False, raise_on_missing=False
        )
    # raise_on_present True on existing
    obj_existing = ParentModel(id=parent_id, value="v")
    with pytest.raises(exc.AlreadyExistingIdsError):
        parent_repo.upsert_one(
            None,
            ParentModel,
            obj_existing,
            raise_on_present=True,
            raise_on_missing=False,
        )
    # raise_on_missing True on missing
    missing_obj = ParentModel(id=uuid4(), value="m")
    with pytest.raises(exc.InvalidIdsError):
        parent_repo.upsert_one(
            None,
            ParentModel,
            missing_obj,
            raise_on_present=False,
            raise_on_missing=True,
        )


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_upsert_unique_keys_among_objs(parent_repo: DictRepository) -> None:
    # Duplicate keys among objs are not detected by the current implementation; both should be inserted
    obj1 = ParentModel(id=uuid4(), value="dup")
    obj2 = ParentModel(id=uuid4(), value="dup")
    res = parent_repo.upsert_some(
        None,
        ParentModel,
        [obj1, obj2],
        raise_on_present=False,
        raise_on_missing=False,
    )  # type: ignore[assignment]
    assert isinstance(res, list)
    stored_ids = set(parent_repo.db[ParentModel].keys())
    assert obj1.id in stored_ids and obj2.id in stored_ids


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_upsert_unique_keys_against_df(
    parent_repo: DictRepository, parent_id: UUID
) -> None:
    # Existing parent has value "p1", new obj with same key should fail
    obj = ParentModel(id=uuid4(), value="p1")
    with pytest.raises(exc.UniqueConstraintViolationError):
        parent_repo.upsert_one(
            None, ParentModel, obj, raise_on_present=False, raise_on_missing=False
        )


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_upsert_links(pc_repo: DictRepository, parent_id: UUID) -> None:
    # Insert a valid child first
    ch_id = uuid4()
    initial_child = ChildModel(
        id=ch_id,
        value="v",
        parent_id=parent_id,
        parent=ParentModel(id=parent_id, value="p1"),
    )
    pc_repo.upsert_one(
        None, ChildModel, initial_child, raise_on_present=False, raise_on_missing=False
    )

    # Update with invalid linked id -> should raise InvalidIdsError (validation happens on update)
    bad_parent_id = uuid4()
    update_bad_link_child = ChildModel(
        id=ch_id, value="v2", parent_id=bad_parent_id, parent=None
    )
    with pytest.raises(exc.InvalidIdsError):
        pc_repo.upsert_one(
            None,
            ChildModel,
            update_bad_link_child,
            raise_on_present=False,
            raise_on_missing=True,
        )

    # Update with mismatched linked object id -> should raise InvalidLinkIdsError
    mismatch_child_update = ChildModel(
        id=ch_id,
        value="v3",
        parent_id=parent_id,
        parent=ParentModel(id=uuid4(), value="px"),
    )
    with pytest.raises(exc.InvalidLinkIdsError):
        pc_repo.upsert_one(
            None,
            ChildModel,
            mismatch_child_update,
            raise_on_present=False,
            raise_on_missing=True,
        )

    # Null link sets both fields to None on update
    null_link_child = ChildModel(id=ch_id, value="v4", parent_id=None, parent=None)
    pc_repo.upsert_one(
        None, ChildModel, null_link_child, raise_on_present=False, raise_on_missing=True
    )
    stored = pc_repo.db[ChildModel][ch_id]
    assert stored.parent_id is None  # type: ignore[attr-defined]
    assert stored.parent is None  # type: ignore[attr-defined]


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_upsert_return_id_and_no_copy(parent_repo: DictRepository) -> None:
    obj = ParentModel(id=uuid4(), value="x")
    ids = parent_repo.upsert_one(
        None,
        ParentModel,
        obj,
        raise_on_present=False,
        raise_on_missing=False,
        return_id=True,
    )
    assert ids == obj.id
    objs = parent_repo.upsert_one(
        None,
        ParentModel,
        obj,
        raise_on_present=False,
        raise_on_missing=False,
        return_id=False,
        return_copy=False,
    )
    assert isinstance(objs, ParentModel)


# delete_some


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_delete_some_link_conflict(pc_repo: DictRepository, parent_id: UUID) -> None:
    # Child references parent_id; deleting parent should fail
    with pytest.raises(exc.LinkConstraintViolationError):
        pc_repo.delete_one(ParentModel, parent_id)


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_delete_some_success(pc_repo: DictRepository, parent_id: UUID) -> None:
    # Delete child (no backlink from other models)
    child_ids = list(pc_repo.db[ChildModel].keys())
    deleted = pc_repo.delete_some(ChildModel, child_ids)
    assert deleted == child_ids
    assert pc_repo.db[ChildModel] == {}


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_delete_some_duplicate_ids(pc_repo: DictRepository, parent_id: UUID) -> None:
    with pytest.raises(exc.DuplicateIdsError):
        pc_repo.delete_some(ParentModel, [parent_id, parent_id])


# delete_all


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_delete_all_with_filter(parent_repo: DictRepository, parent_id: UUID) -> None:
    filter_: Filter = Mock(spec=Filter)
    # One item True, rest False
    filter_.match_rows.return_value = [True]  # type: ignore[attr-defined]
    deleted = parent_repo.delete_all(ParentModel, return_id=True, filter=filter_)
    assert deleted == [parent_id]
    assert parent_repo.db[ParentModel] == {}


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_delete_all_no_filter(pc_repo: DictRepository) -> None:
    # Delete all children
    deleted = pc_repo.delete_all(ChildModel, return_id=True, filter=None)
    # All ids removed
    assert isinstance(deleted, list)
    assert len(deleted) == 1
    assert pc_repo.db[ChildModel] == {}


# exists_one, exists_some


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_exists_one_and_some(parent_repo: DictRepository, parent_id: UUID) -> None:
    assert parent_repo.exists_one(ParentModel, parent_id) is True
    assert parent_repo.exists_one(ParentModel, uuid4()) is False
    res = parent_repo.exists_some(ParentModel, [parent_id, uuid4()])
    assert res == [True, False]


# crud dispatch


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_crud_dispatch_all_ops(parent_repo: DictRepository, parent_id: UUID) -> None:
    uow = parent_repo.uow()
    # READ_ALL
    res_all = parent_repo.crud(uow, None, ParentModel, CrudOperation.READ_ALL)
    assert isinstance(res_all, list)
    # READ_ONE
    res_one = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.READ_ONE, obj_ids=parent_id
    )
    assert isinstance(res_one, ParentModel)
    # READ_SOME
    res_some = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.READ_SOME, obj_ids=[parent_id]
    )
    assert isinstance(res_some, list)
    # CREATE_ONE
    created_obj = ParentModel(id=uuid4(), value="c")
    res_create = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.CREATE_ONE, objs=created_obj
    )
    assert isinstance(res_create, ParentModel)
    # UPDATE_ONE
    upd_obj = ParentModel(id=parent_id, value="u")
    res_update = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.UPDATE_ONE, objs=upd_obj
    )
    assert isinstance(res_update, ParentModel)
    # UPSERT_ONE
    upsert_obj = ParentModel(id=uuid4(), value="x")
    res_upsert = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.UPSERT_ONE, objs=upsert_obj
    )
    assert isinstance(res_upsert, ParentModel)
    # DELETE_ONE
    to_del = upsert_obj.id
    res_del = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.DELETE_ONE, obj_ids=to_del
    )
    assert res_del == to_del

    # CREATE_SOME
    create_some_objs = [
        ParentModel(id=uuid4(), value="c1"),
        ParentModel(id=uuid4(), value="c2"),
    ]
    res_create_some = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.CREATE_SOME, objs=create_some_objs
    )
    assert isinstance(res_create_some, list)
    assert len(res_create_some) == 2

    # UPDATE_SOME
    update_some_objs = [
        ParentModel(id=parent_id, value="u2"),
        ParentModel(id=created_obj.id, value="c2_updated"),
    ]
    res_update_some = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.UPDATE_SOME, objs=update_some_objs
    )
    assert isinstance(res_update_some, list)
    assert parent_repo.db[ParentModel][parent_id].value == "u2"  # type: ignore[attr-defined]
    assert parent_repo.db[ParentModel][created_obj.id].value == "c2_updated"  # type: ignore[attr-defined]

    # UPSERT_SOME
    new_upsert_id = uuid4()
    upsert_some_objs = [
        ParentModel(id=parent_id, value="u3"),
        ParentModel(id=new_upsert_id, value="uxs_new"),
    ]
    res_upsert_some = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.UPSERT_SOME, objs=upsert_some_objs
    )
    assert isinstance(res_upsert_some, list)
    assert parent_repo.db[ParentModel][parent_id].value == "u3"  # type: ignore[attr-defined]

    # DELETE_SOME
    res_delete_some = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.DELETE_SOME, obj_ids=[new_upsert_id]
    )
    assert isinstance(res_delete_some, list)
    assert new_upsert_id not in parent_repo.db[ParentModel]

    # EXISTS_ONE
    res_exists = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.EXISTS_ONE, obj_ids=parent_id
    )
    assert isinstance(res_exists, bool)
    # DELETE_ALL
    res_delete_all = parent_repo.crud(
        uow,
        None,
        ParentModel,
        CrudOperation.DELETE_ALL,
        return_id=True,
    )
    assert isinstance(res_delete_all, list)
    # EXISTS_SOME
    res_exists_some = parent_repo.crud(
        uow, None, ParentModel, CrudOperation.EXISTS_SOME, obj_ids=[uuid4(), uuid4()]
    )
    assert isinstance(res_exists_some, list)


# uow


@pytest.mark.scenario_ids("TC-SEC-28-03")
def test_uow_returns_dict_unit_of_work(parent_repo: DictRepository) -> None:
    uow = parent_repo.uow()
    assert isinstance(uow, DictUnitOfWork)
