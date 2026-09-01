"""In-memory dictionary-backed repository implementation."""

import datetime
import gzip
import json
import pickle
import zipfile
from collections.abc import Callable, Hashable, Iterable
from functools import partial
from pathlib import Path
from typing import Any, Literal, cast

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation, FieldTypeSet, FileExtension
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.modifier import BaseDictModelModifier
from gen_epix.fastapp.repositories.dict.unit_of_work import DictUnitOfWork
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import CompositeFilter, Filter, LogicalOperator


class DictRepository(BaseRepository):
    """Repository that stores models in an in-memory dict, keyed by model class."""

    @staticmethod
    def _create_empty_db_for_entities(
        entities: Iterable[Entity],
    ) -> dict[type[Model], dict[Hashable, Model]]:
        """Create an empty db map with one entry per persistable model class."""
        db: dict[type[Model], dict[Hashable, Model]] = {}
        for entity in entities:
            if not entity.persistable:
                continue
            model_class = entity.model_class
            assert issubclass(model_class, Model)
            db[model_class] = {}
        return db

    @staticmethod
    def _create_empty_db_for_entities(
        entities: Iterable[Entity],
    ) -> dict[type[Model], dict[Hashable, Model]]:
        """Create an empty db map with one entry per persistable model class."""
        db: dict[type[Model], dict[Hashable, Model]] = {}
        for entity in entities:
            if not entity.persistable:
                continue
            model_class = entity.model_class
            assert issubclass(model_class, Model)
            db[model_class] = {}
        return db

    @classmethod
    def create_repository(cls, **kwargs: Any) -> BaseRepository:
        """Instantiate a DictRepository, optionally loading data from a pkl/zip file."""
        entities = kwargs.pop("entities", [])
        file = kwargs.pop("file", None)
        file_type = kwargs.pop("file_type", None)
        if file is None:
            db = DictRepository._create_empty_db_for_entities(entities)
            repository = cls(entities=entities, db=db, missing_data="ignore", **kwargs)
            assert isinstance(repository, DictRepository)
            return repository
        if file_type is None:
            path = Path(file)
            suffixes = [x.lower() for x in path.suffixes]
            if FileExtension.PKL.value in suffixes:
                file_type = FileExtension.PKL.value.lstrip(".")
            elif FileExtension.JSON.value in suffixes:
                file_type = FileExtension.JSON.value.lstrip(".")
            elif FileExtension.ZIP.value in suffixes:
                file_type = FileExtension.ZIP.value.lstrip(".")
        else:
            file_type = file_type.lower()
        if file_type == FileExtension.PKL.value.lstrip("."):
            return DictRepository.create_repository_from_pkl(
                repository_class=cls,
                entities=entities,
                pkl_file=file,
                **kwargs,
            )
        if file_type == FileExtension.ZIP.value.lstrip("."):
            return DictRepository.create_repository_from_json(
                repository_class=cls,
                entities=entities,
                zip_file=file,
                **kwargs,
            )
        raise NotImplementedError(f"Unsupported file type: {file_type}")

    @classmethod
    def clear_repository_content(cls, **kwargs: Any) -> None:
        """No action needed for DictRepository."""
        return None

    @staticmethod
    def create_repository_from_pkl(
        repository_class: type[BaseRepository],
        entities: Iterable[Entity],
        pkl_file: str,
        **kwargs: Any,
    ) -> "DictRepository":
        """Load a DictRepository from a pickle file (plain or gzip-compressed)."""
        if pkl_file.lower().endswith(".gz"):
            with gzip.open(pkl_file, "rb") as handle:
                db = pickle.load(handle)
        else:
            with open(pkl_file, "rb") as handle:
                db = pickle.load(handle)
        # TODO: check validity of db
        repository = repository_class(entities, db, **kwargs)  # type: ignore[call-arg]
        assert isinstance(repository, DictRepository)
        return repository

    @staticmethod
    def create_repository_from_json(
        repository_class: type[BaseRepository],
        entities: Iterable[Entity],
        zip_file: str,
        **kwargs: Any,
    ) -> "DictRepository":
        """Load a DictRepository from a zip archive containing per-entity JSON files."""
        if not zip_file.lower().endswith(".zip"):
            raise exc.RepositoryServiceError(
                "d7de52e2", "Invalid file format. Expected .zip"
            )
        db = {}
        entities = list(entities)
        with zipfile.ZipFile(zip_file, "r") as zip_handle:
            files = set(zip_handle.namelist())
            for entity in entities:
                if not entity.persistable:
                    continue
                json_file = entity.name + FileExtension.JSON.value
                if json_file not in files and entity.table_name:
                    json_file = entity.table_name + FileExtension.JSON.value
                if json_file not in files:
                    raise exc.RepositoryServiceError(
                        "a243e8bf",
                        f"Missing file for entity {entity.name} in archive {zip_file}",
                    )
                model_class = entity.model_class
                with zip_handle.open(json_file) as handle:
                    id_field_name = entity.id_field_name
                    db[model_class] = {
                        getattr(y, id_field_name): y  # type: ignore[arg-type]
                        for y in (model_class(**x) for x in json.load(handle))
                    }
        repository = repository_class(entities, db, **kwargs)  # type: ignore[call-arg]
        assert isinstance(repository, DictRepository)
        return repository

    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[type[Model], dict[Hashable, Model]],
        extra_data: Literal["ignore", "raise", "drop"] = "ignore",
        missing_data: Literal["raise", "ignore"] = "raise",
        timestamp_factory: Callable[[], datetime.datetime] = datetime.datetime.now,
        **kwargs: Any,
    ):
        """
        Initialise the repository.

        extra_data controls behaviour when db contains models not in entities:
        ``ignore`` silently skips them, ``drop`` removes their links, ``raise``
        throws.  missing_data controls behaviour when entities have no db entry:
        ``ignore`` creates an empty dict, ``raise`` throws.
        """
        if extra_data not in {"ignore", "raise", "drop"}:
            raise ValueError(f"Invalid extra_data: {extra_data}")
        if missing_data not in {"raise", "ignore"}:
            raise ValueError(f"Invalid missing_data: {missing_data}")
        # Initialize properties
        self._db = dict(db.items())
        self._timestamp_factory = timestamp_factory
        self._entities = set(entities)
        self._links: dict[
            type[Model],
            list[tuple[str, type[Model], str, int, dict[Hashable, Model] | None]],
        ] = {}
        self._get_id: dict[type[Model], Callable[[Model], Hashable]] = {}
        self._back_links: dict[type[Model], list[tuple[type[Model], str]]] = {}
        self._value_field_names: dict[type[Model], list[str]] = {}
        self._keys_generators: dict[type[Model], dict[int, Callable[[Model], str]]] = {}
        self._model_modifiers: dict[type[Model], BaseDictModelModifier] = {}
        self._init_properties(entities, db, missing_data)

        self._verify_extra_models_and_extract_reverse_links(extra_data)

    def register_model_modifier(
        self, model_class: type[Model], modifier: BaseDictModelModifier
    ) -> None:
        """Register a modifier that is called on create/update for model_class."""
        self._model_modifiers[model_class] = modifier

    @property
    def db(self) -> dict[type[Model], dict[Hashable, Model]]:
        """Db the requested value."""
        return self._db

    def _init_properties(
        self,
        entities: Iterable[Entity],
        db: dict,
        missing_data: Literal["raise", "ignore"],
    ) -> None:
        """Populate links, back-links, value fields, key generators, and ID getters."""
        # Further populate properties
        for entity in entities:
            # Extract entity data
            model_class = entity.model_class
            assert issubclass(model_class, Model)
            self._links[model_class] = self._get_links(entity)
            self._back_links[model_class] = []
            self._value_field_names[model_class] = []
            for field_type in FieldTypeSet.DATA.value:
                self._value_field_names[model_class].extend(
                    entity.get_field_names(field_type=field_type)
                )
            self._keys_generators[model_class] = entity.get_keys_generator()  # type: ignore[assignment]
            if entity.persistable and model_class not in db:
                if missing_data == "ignore":
                    self._db[model_class] = {}
                elif missing_data == "raise":
                    raise ValueError(f"No data for model {model_class}")
                else:
                    raise NotImplementedError()
            # Create ID getter
            id_field_name = entity.id_field_name
            if id_field_name is None:
                # No ID field defined for this model, no getter can be created
                continue
            if not isinstance(id_field_name, str):
                raise NotImplementedError(
                    f"Model {model_class.__name__} has more than one ID field"
                )
            self._get_id[model_class] = partial(
                lambda x, y: getattr(y, x), id_field_name
            )

    def _verify_extra_models_and_extract_reverse_links(self, extra_data: str) -> None:
        """Validate that all linked model classes are known and build back-link index."""
        # Verify extra Models in db and extract reverse links
        for model_class, links in self._links.items():
            to_pop: list[int] = []
            self.validate_links_and_manage_extras(
                extra_data, model_class, links, to_pop
            )
            for i in reversed(to_pop):
                links.pop(i)

    def validate_links_and_manage_extras(
        self,
        extra_data: str,
        model_class: type[Model],
        links: list[tuple[str, type[Model], str, int, dict[Hashable, Model] | None]],
        to_pop: list[int],
    ) -> None:
        """Check each link target; populate back-links or record indices to drop."""
        for i, link in enumerate(links):
            link_field_name, link_model_class, _, _, _ = link
            if link_model_class not in self._links:
                if extra_data == "ignore":
                    continue
                if extra_data == "drop":
                    to_pop.append(i)
                    continue
                if extra_data == "raise":
                    raise ValueError(
                        f"Model {model_class.__name__} links to "
                        f"additional linked model {link_model_class.__name__}"
                    )
                raise NotImplementedError
            self._back_links[link_model_class].append((model_class, link_field_name))

    def crud(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        operation: CrudOperation,
        objs: Model | Iterable[Model] | None = None,
        obj_ids: Hashable | Iterable[Hashable] | None = None,
        return_id: bool = False,
        filter: Filter | None = None,
        limit: int = 0,
        offset: int = 0,
        **kwargs: Any,
    ) -> Any:
        """Dispatch a CRUD operation to the appropriate read/write helper."""
        BaseRepository.verify_crud_args(model_class, objs, obj_ids, operation)
        match operation:
            case CrudOperation.READ_ALL:
                return self.read_all(
                    model_class,
                    return_id=return_id,
                    filter=filter,
                    limit=limit,
                    offset=offset,
                    **kwargs,
                )
            case CrudOperation.READ_ONE:
                return self.read_one(model_class, obj_ids, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.READ_SOME:
                return self.read_some(model_class, obj_ids, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.CREATE_ONE:
                return self.upsert_one(
                    user_id,
                    model_class,
                    objs,  # type: ignore[arg-type]
                    return_id=return_id,
                    raise_on_present=True,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.CREATE_SOME:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,  # type: ignore[arg-type]
                    return_id=return_id,
                    raise_on_present=True,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.UPDATE_ONE:
                return self.upsert_one(
                    user_id,
                    model_class,
                    objs,  # type: ignore[arg-type]
                    return_id=return_id,
                    raise_on_present=False,
                    raise_on_missing=True,
                    **kwargs,
                )
            case CrudOperation.UPDATE_SOME:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,  # type: ignore[arg-type]
                    return_id=return_id,
                    raise_on_present=False,
                    raise_on_missing=True,
                    **kwargs,
                )
            case CrudOperation.UPSERT_ONE:
                return self.upsert_one(
                    user_id,
                    model_class,
                    objs,  # type: ignore[arg-type]
                    return_id=return_id,
                    raise_on_present=False,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.UPSERT_SOME:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,  # type: ignore[arg-type]
                    return_id=return_id,
                    raise_on_present=False,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.DELETE_ONE:
                return self.delete_one(model_class, obj_ids, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.DELETE_SOME:
                return self.delete_some(model_class, obj_ids, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.DELETE_ALL:
                return self.delete_all(
                    model_class, return_id=return_id, filter=filter, **kwargs
                )
            case CrudOperation.EXISTS_ONE:
                return self.exists_one(model_class, obj_ids)  # type: ignore[arg-type]
            case CrudOperation.EXISTS_SOME:
                return self.exists_some(model_class, obj_ids)  # type: ignore[arg-type]
            case _:
                raise NotImplementedError(f"Operation {operation} not implemented")

    def read_fields(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        field_names: list[str],
        filter: Filter | None = None,
        **kwargs: Any,
    ) -> Iterable[tuple]:
        """Yield tuples of the requested field values for each matching object."""
        all_objs_iterable = self._db[model_class].values()
        if filter:
            for obj in filter.filter_rows(all_objs_iterable, is_model=True):
                yield tuple(getattr(obj, x) for x in field_names)
        else:
            for obj in all_objs_iterable:
                yield tuple(getattr(obj, x) for x in field_names)

    def uow(self, **kwargs: Any) -> BaseUnitOfWork:
        """Return a no-op unit-of-work suitable for the in-memory backend."""
        return DictUnitOfWork()

    def split_filter(
        self, model_class: type, filter: Filter | None
    ) -> tuple[Filter | None, Filter | None]:
        """Return (where_filter, None) — the full filter applies in-memory."""
        # Entire filter can be used as where clause since the data are stored as
        # domain models
        return filter, None

    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: type[Model],
        obj_ids: Iterable[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        """Raise if any requested id is missing or duplicated in the store."""
        if verify_exists:
            df = self._db[model_class]
            invalid_obj_ids = [x for x in obj_ids if x not in df]
            if invalid_obj_ids:
                DictRepository._raise_invalid_ids(model_class, invalid_obj_ids)
        if verify_duplicate:
            DictRepository._verify_duplicate_ids(model_class, obj_ids)

    def read_all(
        self,
        model_class: type[Model],
        return_id: bool = False,
        filter: Filter | None = None,
        limit: int = 0,
        offset: int = 0,
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        """Return all objects (or their ids) matching the optional filter/page args."""
        return_copy = kwargs.get("return_copy", True)
        df = self._db[model_class]
        # Get any query filter
        query_filter: Filter | None = None
        obj_filter: Filter | None = kwargs.get("obj_filter")
        if filter and obj_filter:
            query_filter = CompositeFilter(
                filters=[filter, obj_filter], operator=LogicalOperator.AND
            )
        elif filter:
            query_filter = filter
        elif obj_filter:
            query_filter = obj_filter
        else:
            query_filter = None
        # Get matching objects
        objs: list[Model] | list[Hashable]
        if query_filter:
            if return_id:
                objs = [
                    x
                    for x, y in zip(
                        df.keys(), query_filter.match_rows(df.values(), is_model=True)
                    )
                    if y
                ]
            else:
                objs = list(query_filter.filter_rows(df.values(), is_model=True))  # type: ignore[assignment]
        elif return_id:
            objs = list(df.keys())
        else:
            objs = list(df.values())
        # Apply limit and offset
        if limit or offset:
            if offset >= len(objs):
                return []
            if offset + limit >= len(objs):
                return objs[offset:]
            objs = objs[offset : offset + limit]
        # Make copy of objects for returning if necessary
        if not return_id and return_copy:
            objs = [x.model_copy() for x in objs if x]  # type: ignore[attr-defined]
        return objs

    def read_one(
        self,
        model_class: type[Model],
        obj_id: Hashable,
        allow_duplicate_ids: bool = False,
        **kwargs: Any,
    ) -> Model | Hashable:
        """Return the single object with the given id."""
        return self.read_some(
            model_class,
            [obj_id],
            allow_duplicate_ids=allow_duplicate_ids,
            **kwargs,
        )[0]

    def read_some(
        self,
        model_class: type[Model],
        obj_ids: Iterable[Hashable],
        allow_duplicate_ids: bool = False,
        **kwargs: Any,
    ) -> list[Model]:
        """Return the objects with the given ids, preserving input order."""
        return_copy = kwargs.get("return_copy", True)
        df = self._db[model_class]
        # Check input
        invalid_obj_ids = list(set(list(obj_ids)) - set(df.keys()))
        if invalid_obj_ids:
            DictRepository._raise_invalid_ids(model_class, invalid_obj_ids)
        if not allow_duplicate_ids:
            DictRepository._verify_duplicate_ids(model_class, obj_ids)
        # Read some
        objs: list[Model | None] = [df.get(x) for x in obj_ids]
        # Verify input
        DictRepository._verify_valid_ids(model_class, obj_ids, objs)
        if not allow_duplicate_ids:
            DictRepository._verify_duplicate_ids(model_class, obj_ids)

        # Make copy of objects for returning
        if return_copy:
            objs = [x.model_copy() for x in objs if x]
        return cast(list[Model], objs)

    def upsert_one(
        self,
        user_id: Hashable,
        model_class: type[Model],
        obj: Model,
        return_id: bool = False,
        raise_on_present: bool = False,
        raise_on_missing: bool = False,
        **kwargs: Any,
    ) -> Model | Hashable:
        """Insert or update a single object; delegates to upsert_some."""
        return self.upsert_some(
            user_id,
            model_class,
            [obj],
            return_id=return_id,
            raise_on_present=raise_on_present,
            raise_on_missing=raise_on_missing,
            **kwargs,
        )[0]

    def upsert_some(
        self,
        user_id: Hashable,
        model_class: type[Model],
        objs: Iterable[Model],
        return_id: bool = False,
        raise_on_present: bool = False,
        raise_on_missing: bool = False,
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        """Insert or update a batch of objects and return them (or their ids)."""
        objs = objs if isinstance(objs, list) else list(objs)
        return_copy = kwargs.get("return_copy", True)
        df = self._db[model_class]
        get_id = self._get_id[model_class]
        obj_ids: list[Hashable] = [get_id(x) for x in objs]
        df_objs: list[Model | None] = [df.get(x) for x in obj_ids]
        # Verify input
        self._validate_upsert_objects(
            model_class,
            objs,
            raise_on_present,
            raise_on_missing,
            df,
            get_id,
            obj_ids,
            df_objs,
        )

        # Upsert objects
        value_field_names = self._value_field_names[model_class]
        links: list[tuple[str, str | None, dict[Hashable, Model] | None]] = [
            (x[0], x[2], x[4]) for x in self._links[model_class]
        ]
        self.upsert_model_objects(
            user_id, model_class, objs, df, get_id, df_objs, value_field_names, links
        )
        stored_df_objs = cast(list[Model], df_objs)
        if return_id:
            return obj_ids
        if return_copy:
            return [x.model_copy() for x in stored_df_objs]
        return stored_df_objs

    def upsert_model_objects(
        self,
        user_id: Hashable | None,
        model_class: type[Model],
        objs: Iterable[Model],
        df: dict[Hashable, Model],
        get_id: Callable[[Model], Hashable],
        df_objs: list[Model | None],
        value_field_names: list[str],
        links: list[tuple[str, str | None, dict[Hashable, Model] | None]],
    ) -> None:
        """Apply per-object insert-or-update logic, invoking the modifier if set."""
        modifier = self._model_modifiers.get(model_class)
        for i, obj, df_obj in zip(range(len(df_objs)), objs, df_objs):
            if df_obj:
                # Already existing -> let modifier fix obj before values are applied
                if modifier:
                    modifier.on_update(user_id, obj, df_obj)
                self._apply_value_updates(value_field_names, obj, df_obj)
                self._apply_link_updates(model_class, get_id, links, obj, df_obj)
            else:
                # New -> insert copy of obj, then stamp metadata on the stored copy
                df_objs[i] = self._insert_new(df, get_id, obj)
                if modifier:
                    modifier.on_create(user_id, cast(Model, df_objs[i]))

    def _insert_new(
        self,
        df: dict[Hashable, Model],
        get_id: Callable[[Model], Hashable],
        obj: Model,
    ) -> Model:
        """Store a copy of obj in df and return the stored copy."""
        new_df_obj: Model = obj.model_copy()
        df[get_id(new_df_obj)] = new_df_obj
        return new_df_obj

    def _apply_link_updates(
        self,
        model_class: type[Model],
        get_id: Callable[[Model], Hashable],
        links: list[tuple[str, str | None, dict[Hashable, Model] | None]],
        obj: Model,
        df_obj: Model,
    ) -> None:
        """Sync all FK/relationship fields from obj onto the stored df_obj."""
        for link_field_name, relationship_field_name, linked_df in links:
            # Verify and update link
            linked_obj_id = getattr(obj, link_field_name)
            if not linked_obj_id:
                setattr(df_obj, link_field_name, None)
                if relationship_field_name is not None:
                    setattr(df_obj, relationship_field_name, None)
                continue
            if linked_df is not None and linked_obj_id not in linked_df:
                raise exc.InvalidIdsError(
                    "8b5592ee",
                    (
                        f"Model {model_class.__name__}: obj {get_id(obj)} has invalid id"
                        f' in {link_field_name}: "{linked_obj_id}"'
                    ),
                    ids=[linked_obj_id],
                )
            setattr(df_obj, link_field_name, linked_obj_id)
            if relationship_field_name is None:
                continue
            linked_obj = getattr(obj, relationship_field_name)
            if not linked_obj:
                continue
            get_link_id = self._get_id[linked_obj.__class__]
            if get_link_id(linked_obj) != linked_obj_id:
                raise exc.InvalidLinkIdsError(
                    "40205b3a",
                    (
                        f"Model {model_class.__name__}: obj {get_link_id(obj)} has different id "
                        f'in {link_field_name} ("{linked_obj_id}") versus '
                        f'{relationship_field_name} ("{get_link_id(linked_obj)}")'
                    ),
                    ids=[linked_obj_id, get_link_id(linked_obj)],
                )

    def _apply_value_updates(
        self, value_field_names: list[str], obj: Model, df_obj: Model
    ) -> None:
        """Copy every data field value from obj onto the stored df_obj."""
        for field_name in value_field_names:
            # Update value field
            setattr(df_obj, field_name, getattr(obj, field_name))

    def _validate_upsert_objects(
        self,
        model_class: type[Model],
        objs: list[Model],
        raise_on_present: bool,
        raise_on_missing: bool,
        df: dict[Hashable, Model],
        get_id: Callable[[Model], Hashable],
        obj_ids: list[Hashable],
        df_objs: list[Model | None],
    ) -> None:
        """Guard against type mismatches, uniqueness violations, and missing/present ids."""
        DictRepository._verify_duplicate_ids(model_class, obj_ids)
        invalid_type_ids = [get_id(x) for x in objs if not isinstance(x, model_class)]
        self._verify_upsert_objects(
            invalid_type_ids,
            model_class,
            obj_ids,
            df_objs,
            raise_on_present,
            raise_on_missing,
        )
        DictRepository._verify_duplicate_keys(
            get_id, self._keys_generators[model_class], model_class, objs, df.values()  # type: ignore[arg-type]
        )

    def delete_one(
        self,
        model_class: type[Model],
        obj_id: Hashable,
        **kwargs: Any,
    ) -> Hashable:
        """Delete the object with the given id and return its id."""
        return self.delete_some(model_class, [obj_id], **kwargs)[0]

    def delete_some(
        self,
        model_class: type[Model],
        obj_ids: Iterable[Hashable],
        **kwargs: Any,
    ) -> list[Hashable]:
        """Delete the objects with the given ids, enforcing FK constraints."""
        df = self._db[model_class]
        df_objs = [df.get(x) for x in obj_ids]
        back_links = self._back_links[model_class]

        # Verify input
        DictRepository._verify_valid_ids(model_class, obj_ids, df_objs)
        DictRepository._verify_duplicate_ids(model_class, obj_ids)

        # Verify existence of link (foreign key) constraint conflicts
        uq_obj_ids = set(obj_ids)
        for link_model_class, link_field_name in back_links:
            link_df = self._db[link_model_class]
            get_id = self._get_id[link_model_class]
            linked_obj_ids = [
                get_id(x)
                for x in link_df.values()
                if getattr(x, link_field_name) in uq_obj_ids
            ]
            if linked_obj_ids:
                linked_obj_ids_str = ", ".join([f'"{x}"' for x in linked_obj_ids])
                raise exc.LinkConstraintViolationError(
                    "50e3ec82",
                    (
                        f"Model {model_class.__name__}: link constraint conflict in model "
                        f"{link_model_class.__name__}, id(s): {linked_obj_ids_str}"
                    ),
                    list(uq_obj_ids),
                    linked_obj_ids,
                )
        # Delete objects
        for obj_id in uq_obj_ids:
            df.pop(obj_id)
        return list(obj_ids)

    def delete_all(
        self,
        model_class: type[Model],
        return_id: bool = False,
        filter: Filter | None = None,
        **kwargs: Any,
    ) -> list[Hashable] | None:
        """Delete all (or filtered) objects; optionally return the deleted ids."""
        df = self._db[model_class]
        # Get any query filter
        query_filter: Filter | None = None
        obj_filter: Filter | None = kwargs.get("obj_filter")
        if filter and obj_filter:
            query_filter = CompositeFilter(
                filters=[filter, obj_filter], operator=LogicalOperator.AND
            )
        elif filter:
            query_filter = filter
        elif obj_filter:
            query_filter = obj_filter
        else:
            query_filter = None
        # Delete objects
        if query_filter:
            # Delete objects matching the query filter
            obj_ids = [
                x
                for x, y in zip(
                    df.keys(), query_filter.match_rows(df.values(), is_model=True)
                )
                if y
            ]
            for obj_id in obj_ids:
                self._db[model_class].pop(obj_id)
        else:
            # Delete all objects
            obj_ids = list(self._db[model_class].keys())
            self._db[model_class] = {}
        return obj_ids if return_id else None

    def exists_one(self, model_class: type[Model], obj_id: Hashable) -> bool:
        """Return True if an object with obj_id exists in the store."""
        df = self._db[model_class]
        return obj_id in df

    def exists_some(
        self, model_class: type[Model], obj_ids: Iterable[Hashable]
    ) -> list[bool]:
        """Return a list of booleans indicating whether each id exists in the store."""
        df = self._db[model_class]
        return [x in df for x in obj_ids]

    def _get_links(
        self, entity: Entity
    ) -> list[tuple[str, type[Model], str, int, dict[Hashable, Model] | None]]:
        """Build the link descriptors for an entity from its declared FK fields."""
        # Return list[tuple[link_field_name, LinkModel, relationship_field_name, link_type_id, linked_df|None]]
        links: list[tuple[str, type[Model], str, int, dict[Hashable, Model] | None]] = (
            []
        )
        for link_field_name in entity.get_link_field_names():
            (
                link_type_id,
                link_model_class,
                relationship_field_name,
            ) = entity.get_link_properties_by_field_name(link_field_name)
            links.append(
                (
                    link_field_name,
                    link_model_class,
                    relationship_field_name,
                    link_type_id,
                    self._db.get(link_model_class),  # type: ignore[arg-type]
                )
            )
        return links

    def _verify_upsert_objects(
        self,
        invalid_type_ids: list[Hashable],
        model_class: type[Model],
        obj_ids: list[Hashable],
        df_objs: list[Model | None],
        raise_on_present: bool,
        raise_on_missing: bool,
    ) -> None:
        """Raise on wrong-type, already-present, or missing objects per upsert flags."""
        if invalid_type_ids:
            invalid_type_ids_str = ", ".join([f'"{x}"' for x in invalid_type_ids])
            raise exc.InvalidModelIdsError(
                "2e1a28a7",
                f"Model {model_class.__name__}: object(s) are of different type: {invalid_type_ids_str}",
                ids=invalid_type_ids,
            )
        get_id = self._get_id[model_class]
        if raise_on_present:
            present_ids = [get_id(x) for x in df_objs if x is not None]
            if present_ids:
                present_ids_str = ", ".join([f'"{x}"' for x in present_ids])
                raise exc.AlreadyExistingIdsError(
                    "7cef048c",
                    f"{model_class} object(s) already exist: {present_ids_str}",
                    ids=present_ids,
                )
        if raise_on_missing:
            missing_ids = [x for x, y in zip(obj_ids, df_objs) if y is None]
            if missing_ids:
                missing_ids_str = ", ".join([f"{x}" for x in missing_ids])
                raise exc.InvalidIdsError(
                    "18e989a1",
                    f"{model_class} object(s) do not exist: {missing_ids_str}",
                    ids=missing_ids,
                )

    @staticmethod
    def _verify_valid_ids(
        model_class: type[Model],
        obj_ids: Iterable[Hashable],
        objs: Iterable[Model | None],
    ) -> None:
        """Raise InvalidIdsError for any id whose corresponding object is None."""
        invalid_obj_ids = [x for x, y in zip(obj_ids, objs) if y is None]
        if invalid_obj_ids:
            DictRepository._raise_invalid_ids(model_class, invalid_obj_ids)

    @staticmethod
    def _raise_invalid_ids(
        model_class: type[Model], invalid_obj_ids: Iterable[Hashable]
    ) -> None:
        """Raise InvalidIdsError with a formatted list of bad ids."""
        invalid_obj_ids_str = ", ".join(f'"{x}"' for x in invalid_obj_ids)
        raise exc.InvalidIdsError(
            "588b3e46",
            f"Model {model_class.__name__}: invalid object id(s) provided: {invalid_obj_ids_str}",
            ids=invalid_obj_ids,
        )

    @staticmethod
    def _verify_duplicate_ids(
        model_class: type[Model], obj_ids: Iterable[Hashable]
    ) -> None:
        """Raise DuplicateIdsError if any id appears more than once in obj_ids."""
        set_: set[Hashable] = set()
        duplicate_ids = [x for x in obj_ids if x in set_ or set_.add(x)]  # type: ignore[func-returns-value]
        if duplicate_ids:
            DictRepository._raise_duplicate_ids(model_class, duplicate_ids)

    @staticmethod
    def _raise_duplicate_ids(
        model_class: type[Model], duplicate_ids: Iterable[Hashable]
    ) -> None:
        """Raise DuplicateIdsError with a formatted list of duplicated ids."""
        duplicate_ids_str = ", ".join([f'"{x}"' for x in duplicate_ids])
        raise exc.DuplicateIdsError(
            "6666582f",
            f"Model {model_class.__name__}: object ids are not unique: {duplicate_ids_str}",
            ids=duplicate_ids,
        )

    @staticmethod
    def _verify_duplicate_keys(
        get_id: Callable[[Model], Hashable],
        keys_generator: Callable[[Model], dict[int, str]],
        model_class: type[Model],
        objs: list[Model],
        df_objs: list[Model] | None,
    ) -> None:
        """Raise UniqueConstraintViolationError if any unique key is duplicated."""
        if not objs:
            # No objs -> no duplicates
            return
        keys = keys_generator(objs[0])
        if not keys:
            # No keys -> no duplicates
            return
        key_ids = list(keys.keys())

        def get_keys(obj: Any) -> Any:
            """Return keys."""
            keys = keys_generator(obj)
            return tuple(keys[x] for x in key_ids)

        # Check for duplicate keys among objs
        obj_keys_list = [get_keys(x) for x in objs]
        n_keys = len(keys)
        duplicate_objs: list[Model] = []
        for i in range(n_keys):
            curr_obj_keys_list = [x[i] for x in obj_keys_list]
            curr_obj_keys = set(curr_obj_keys_list)
            if len(curr_obj_keys) < len(curr_obj_keys_list):
                seen: set[str] = set()
                uq_obj_keys = {
                    x for x in curr_obj_keys_list if x not in seen and not seen.add(x)  # type: ignore[func-returns-value]
                }
                duplicate_obj_keys = curr_obj_keys - uq_obj_keys
                duplicate_objs += [
                    x
                    for x, y in zip(objs, curr_obj_keys_list)
                    if y in duplicate_obj_keys
                ]
        if duplicate_objs:
            raise exc.UniqueConstraintViolationError(
                "9aaac78c",
                f"Model {model_class.__name__}: object keys are not unique",
                duplicate_key_ids=list(set([get_id(x) for x in duplicate_objs])),
            )
        # Check for duplicate keys between objs and df_objs, excluding those df_objs
        #  that have the same id as an obj
        if not df_objs:
            return
        obj_ids = {get_id(x) for x in objs}
        df_obj_keys = [get_keys(x) for x in df_objs if get_id(x) not in obj_ids]
        duplicate_objs = []
        for i in range(n_keys):
            curr_df_obj_keys = {x[i] for x in df_obj_keys}
            curr_obj_keys_list = [x[i] for x in obj_keys_list]
            curr_obj_keys = set(curr_obj_keys_list)
            duplicate_obj_keys = curr_obj_keys & curr_df_obj_keys
            if duplicate_obj_keys:
                duplicate_objs += [
                    x
                    for x, y in zip(objs, curr_obj_keys_list)
                    if y in duplicate_obj_keys
                ]
        if duplicate_objs:
            raise exc.UniqueConstraintViolationError(
                "ec20ed8b",
                f"Model {model_class.__name__}: object keys are not unique",
                duplicate_key_ids=list({get_id(x) for x in duplicate_objs}),
            )
