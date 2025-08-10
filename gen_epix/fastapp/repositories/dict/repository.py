import datetime
import gzip
import json
import pickle
import zipfile
from functools import partial
from typing import Any, Callable, Hashable, Iterable, Type
from uuid import UUID

from gen_epix.fastapp import exc
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.enum import CrudOperation, FieldTypeSet
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.dict.unit_of_work import DictUnitOfWork
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import BooleanOperator, CompositeFilter, Filter


class DictRepository(BaseRepository):
    @staticmethod
    def from_pkl(
        repository_class: Type[BaseRepository],
        entities: Iterable[Entity],
        pkl_file: str,
        **kwargs: Any,
    ) -> "DictRepository":
        if pkl_file.lower().endswith(".gz"):
            with gzip.open(pkl_file, "rb") as handle:
                db = pickle.load(handle)
        else:
            with open(pkl_file, "rb") as handle:
                db = pickle.load(handle)
        # TODO: check validity of db
        repository = repository_class(entities, db, **kwargs)
        assert isinstance(repository, DictRepository)
        return repository

    @staticmethod
    def from_json(
        repository_class: Type[BaseRepository],
        entities: Iterable[Entity],
        zip_file: str,
        **kwargs: Any,
    ) -> "DictRepository":
        if not zip_file.lower().endswith(".zip"):
            raise exc.RepositoryServiceError("Invalid file format. Expected .zip")
        db = {}
        entities = list(entities)
        with zipfile.ZipFile(zip_file, "r") as zip_handle:
            files = set(zip_handle.namelist())
            for entity in entities:
                if not entity.persistable:
                    continue
                json_file = entity.name + ".json"
                if json_file not in files and entity.table_name:
                    json_file = entity.table_name + ".json"
                if json_file not in files:
                    raise exc.RepositoryServiceError(
                        f"Missing file for entity {entity.name} in archive {zip_file}"
                    )
                model_class = entity.model_class
                with zip_handle.open(json_file) as handle:
                    id_field_name = entity.id_field_name
                    db[model_class] = {
                        getattr(y, id_field_name): y
                        for y in (model_class(**x) for x in json.load(handle))
                    }
        repository = repository_class(entities, db, **kwargs)
        assert isinstance(repository, DictRepository)
        return repository

    def __init__(
        self,
        entities: Iterable[Entity],
        db: dict[Type[Model], dict[Hashable, Model]],
        **kwargs: Any,
    ):
        extra_data = kwargs.pop("extra_data", "ignore")
        missing_data = kwargs.pop("missing_data", "raise")
        timestamp_factory = kwargs.pop("timestamp_factory", datetime.datetime.now)
        if extra_data not in {"ignore", "raise", "drop"}:
            raise ValueError(f"Invalid extra_data: {extra_data}")
        if missing_data not in {"raise", "ignore"}:
            raise ValueError(f"Invalid missing_data: {missing_data}")
        # Initialize properties
        self._db = dict(db.items())
        self._timestamp_factory = timestamp_factory
        self._entities = set(entities)
        self._links = {}
        self._get_id: dict[Type[Model], Callable[[Model], Hashable]] = {}
        self._back_links: dict[Type[Model], list[tuple[Type[Model], str]]] = {}
        self._value_field_names: dict[type[Model], list[str]] = {}
        self._keys_generators: dict[type[Model], dict[int, Callable[[Model], str]]] = {}
        self._init_properties(entities, db, missing_data)

        self._verify_extra_models_and_extract_reverse_links(extra_data)

    def _init_properties(
        self, entities: Iterable[Entity], db: dict, missing_data: str
    ) -> None:
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
            self._keys_generators[model_class] = entity.get_keys_generator()
            if entity.persistable and model_class not in db:
                if missing_data == "ignore":
                    self._db[model_class] = {}
                elif missing_data == "raise":
                    raise ValueError(f"No data for model {model_class}")
                else:
                    raise NotImplementedError
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
        # Verify extra Models in db and extract reverse links
        for model_class, links in self._links.items():
            to_pop = []
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
                            f"Model {model_class} links to "
                            "additional linked model {link_model_class}"
                        )
                    raise NotImplementedError
                self._back_links[link_model_class].append(
                    (model_class, link_field_name)
                )
            for i in reversed(to_pop):
                links.pop(i)

    def crud(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: Type[Model],
        objs: Model | Iterable[Model] | None,
        obj_ids: Hashable | Iterable[Hashable] | None,
        operation: CrudOperation,
        filter: Filter | None = None,
        **kwargs: Any,
    ) -> Hashable | list[Hashable] | Model | list[Model] | bool | list[bool] | None:
        BaseRepository.verify_crud_args(model_class, objs, obj_ids, operation)
        match operation:
            case CrudOperation.READ_ALL:
                return self.read_all(model_class, filter, **kwargs)
            case CrudOperation.READ_ONE:
                return self.read_one(model_class, obj_ids, **kwargs)
            case CrudOperation.READ_SOME:
                return self.read_some(model_class, obj_ids, **kwargs)
            case CrudOperation.CREATE_ONE:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,
                    raise_on_present=True,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.CREATE_SOME:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,
                    raise_on_present=True,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.UPDATE_ONE:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,
                    raise_on_present=False,
                    raise_on_missing=True,
                    **kwargs,
                )
            case CrudOperation.UPDATE_SOME:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,
                    raise_on_present=False,
                    raise_on_missing=True,
                    **kwargs,
                )
            case CrudOperation.UPSERT_ONE:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,
                    raise_on_present=False,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.UPSERT_SOME:
                return self.upsert_some(
                    user_id,
                    model_class,
                    objs,
                    raise_on_present=False,
                    raise_on_missing=False,
                    **kwargs,
                )
            case CrudOperation.DELETE_ONE:
                return self.delete_some(model_class, obj_ids, **kwargs)
            case CrudOperation.DELETE_SOME:
                return self.delete_some(model_class, obj_ids, **kwargs)
            case CrudOperation.DELETE_ALL:
                return self.delete_all(model_class, filter, **kwargs)
            case CrudOperation.EXISTS_ONE:
                return self.exists_one(model_class, obj_ids)
            case CrudOperation.EXISTS_SOME:
                return self.exists_some(model_class, obj_ids)
            case _:
                raise NotImplementedError(f"Operation {operation} not implemented")

    def uow(self, **kwargs: Any) -> BaseUnitOfWork:
        return DictUnitOfWork()

    def split_filter(
        self, model_class: Type, filter: Filter | None
    ) -> tuple[Filter | None, Filter | None]:
        # Entire filter can be used as where clause since the data are stored as
        # domain models
        return filter, None

    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: Type[Model],
        obj_ids: Iterable[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        if verify_exists:
            df = self._db[model_class]
            invalid_obj_ids = [x for x in obj_ids if x not in df]
            if invalid_obj_ids:
                DictRepository._raise_invalid_ids(model_class, invalid_obj_ids)
        if verify_duplicate:
            DictRepository._verify_duplicate_ids(model_class, obj_ids)

    def read_all(
        self,
        model_class: Type[Model],
        filter: Filter | None,
        cascade_read: bool = False,
        return_id: bool = False,
        **kwargs: Any,
    ) -> list[Model]:
        return_copy = kwargs.get("return_copy", True)
        df = self._db[model_class]
        # Get any query filter
        obj_filter = kwargs.get("obj_filter")
        if filter and obj_filter:
            query_filter = CompositeFilter(
                filters=[filter, obj_filter], operator=BooleanOperator.AND
            )
        elif filter:
            query_filter = filter
        elif obj_filter:
            query_filter = obj_filter
        else:
            query_filter = None
        # Get matching objects
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
                objs = list(query_filter.filter_rows(df.values(), is_model=True))
        elif return_id:
            objs: list[Hashable] = list(df.keys())
        else:
            objs: list[Model] = list(df.values())
        # Make copy of objects for returning if necessary
        if not return_id and return_copy:
            objs = [x.model_copy() for x in objs if x]
        # Cascade read linked objects if necessary
        if cascade_read and not return_id:
            self._cascade_read(model_class, objs, return_copy)
        return objs

    def read_one(
        self,
        model_class: Type[Model],
        obj_id: Hashable,
        cascade_read: bool = False,
        return_id: bool = False,
        allow_duplicate_ids: bool = False,
        **kwargs: Any,
    ) -> Model:
        return self.read_some(
            model_class,
            [obj_id],
            cascade_read=cascade_read,
            return_id=return_id,
            allow_duplicate_ids=allow_duplicate_ids,
            **kwargs,
        )[0]

    def read_some(
        self,
        model_class: Type[Model],
        obj_ids: Iterable[Hashable],
        cascade_read: bool = False,
        return_id: bool = False,
        allow_duplicate_ids: bool = False,
        **kwargs: Any,
    ) -> list[Model]:
        return_copy = kwargs.get("return_copy", True)
        df = self._db[model_class]
        # Read some or one
        if return_id:
            objs: list[Hashable] = list(obj_ids)
            invalid_obj_ids = [x for x in objs if x not in df]
            if invalid_obj_ids:
                DictRepository._raise_invalid_ids(model_class, invalid_obj_ids)
            if not allow_duplicate_ids:
                DictRepository._verify_duplicate_ids(model_class, obj_ids)
        else:
            objs: list[Model] = [df.get(x) for x in obj_ids]
            # Verify input
            DictRepository._verify_valid_ids(model_class, obj_ids, objs)
            if not allow_duplicate_ids:
                DictRepository._verify_duplicate_ids(model_class, obj_ids)

        # Make copy of objects for returning
        if not return_id and return_copy:
            objs = [x.model_copy() for x in objs if x]

        # Cascade read linked objects if necessary
        if cascade_read and not return_id:
            self._cascade_read(model_class, objs, return_copy)
        return objs

    def upsert_some(
        self,
        user_id: Hashable,
        model_class: Type[Model],
        objs: Model | Iterable[Model],
        raise_on_present: bool = False,
        raise_on_missing: bool = False,
        return_id: bool = False,
        **kwargs: Any,
    ) -> Hashable | list[Hashable] | Model | list[Model]:
        return_copy = kwargs.get("return_copy", True)
        df = self._db[model_class]
        get_id = self._get_id[model_class]
        is_iterable, objs = DictRepository._to_iterable(objs)
        obj_ids: list[Hashable] = [get_id(x) for x in objs]  # type: ignore
        df_objs: list[Model | None] = [df.get(x) for x in obj_ids]
        # Verify input
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
            get_id, self._keys_generators[model_class], model_class, objs, df.values()
        )

        # Upsert objects
        value_field_names = self._value_field_names[model_class]
        links = self._links[model_class]
        links = [tuple([x[0], x[2], x[4]]) for x in links]
        current_time = self._timestamp_factory()
        for i, obj, df_obj in zip(range(len(df_objs)), objs, df_objs):
            if df_obj:
                # Already existing -> update df_obj with obj data
                for field_name in value_field_names:
                    # Update value field
                    setattr(df_obj, field_name, getattr(obj, field_name))
                for link_field_name, relationship_field_name, linked_df in links:
                    # Verify and update link
                    linked_obj_id = getattr(obj, link_field_name)
                    if not linked_obj_id:
                        setattr(df_obj, link_field_name, None)
                        setattr(df_obj, relationship_field_name, None)
                        continue
                    if linked_df is not None and linked_obj_id not in linked_df:
                        raise exc.InvalidIdsError(
                            (
                                f"Model {model_class}: obj {get_id(obj)} has invalid id"
                                f' in {link_field_name}: "{linked_obj_id}"'
                            ),
                            ids=[linked_obj_id],
                        )
                    setattr(df_obj, link_field_name, linked_obj_id)
                    linked_obj = getattr(obj, relationship_field_name)
                    if not linked_obj:
                        continue
                    get_link_id = self._get_id[linked_obj.__class__]
                    if get_link_id(linked_obj) != linked_obj_id:
                        raise exc.InvalidLinkIdsError(
                            (
                                f"Model {model_class}: obj {get_link_id(obj)} has different id "
                                f'in {link_field_name} ("{linked_obj_id}") versus '
                                f'{relationship_field_name} ("{get_link_id(linked_obj)}")'
                            ),
                            ids=[linked_obj_id, get_link_id(linked_obj)],
                        )
            else:
                # New -> insert copy of obj
                df_obj: Model = obj.model_copy()  # type: ignore
                df[get_id(df_obj)] = df_obj  # type: ignore
                df_objs[i] = df_obj
        if return_id:
            return obj_ids if is_iterable else obj_ids[0]
        if return_copy:
            return (
                [x.model_copy() for x in df_objs]
                if is_iterable
                else df_objs[0].model_copy()
            )
        return df_objs if is_iterable else df_objs[0]

    def delete_some(
        self,
        model_class: Type[Model],
        obj_ids: Hashable | Iterable[Hashable],
        **kwargs: Any,
    ) -> Hashable | list[Hashable] | None:
        df = self._db[model_class]
        is_iterable, obj_ids = DictRepository._to_iterable(obj_ids)
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
                    (
                        f"Model {model_class}: link constraint conflict in model "
                        f"{link_model_class}, id(s): {linked_obj_ids_str}"
                    ),
                    list(uq_obj_ids),
                    linked_obj_ids,
                )
        # Delete objects
        for obj_id in uq_obj_ids:
            df.pop(obj_id)
        return obj_ids if is_iterable else obj_ids[0]

    def delete_all(
        self, model_class: Type[Model], filter: Filter | None, **kwargs: Any
    ) -> list[Hashable]:
        df = self._db[model_class]
        # Get any query filter
        obj_filter = kwargs.get("obj_filter")
        if filter and obj_filter:
            query_filter = CompositeFilter(
                filters=[filter, obj_filter], operator=BooleanOperator.AND
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
        return obj_ids

    def exists_one(self, model_class: Type[Model], obj_id: Hashable) -> bool:
        df = self._db[model_class]
        return obj_id in df

    def exists_some(
        self, model_class: Type[Model], obj_ids: Iterable[Hashable]
    ) -> list[bool]:
        df = self._db[model_class]
        return [x in df for x in obj_ids]

    def _get_links(
        self, entity: Entity
    ) -> list[tuple[str, Type[Model], str, int, dict[Hashable, Model] | None]]:
        # Return list[tuple[link_field_name, LinkModel, relationship_field_name, link_type_id, linked_df|None]]
        links = []
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
                    self._db.get(link_model_class),
                )
            )
        return links

    def _cascade_read(
        self,
        model_class: Type[Model],
        objs: list[Model],
        return_copy: bool,
    ) -> None:
        for (
            link_field_name,
            link_model_class,
            relationship_field_name,
            _,
            linked_df,
        ) in self._links[model_class]:
            if linked_df is None:
                continue
            linked_obj_ids = [
                getattr(x, link_field_name) for x in objs if getattr(x, link_field_name)
            ]
            linked_objs = self.read_some(
                link_model_class,
                linked_obj_ids,
                cascade_read=False,
                allow_duplicate_ids=True,
                return_copy=return_copy,
            )
            for obj, linked_obj in zip(objs, linked_objs):
                setattr(obj, relationship_field_name, linked_obj)

    def _verify_upsert_objects(
        self,
        invalid_type_ids: list[Hashable],
        model_class: Type[Model],
        obj_ids: list[Hashable],
        df_objs: list[Model | None],
        raise_on_present: bool,
        raise_on_missing: bool,
    ) -> None:
        if invalid_type_ids:
            invalid_type_ids_str = ", ".join([f'"{x}"' for x in invalid_type_ids])
            raise exc.InvalidModelIdsError(
                f"Model {model_class}: object(s) are of different type: {invalid_type_ids_str}",
                ids=invalid_type_ids,
            )
        get_id = self._get_id[model_class]
        if raise_on_present:
            present_ids = [get_id(x) for x in df_objs if x is not None]
            if present_ids:
                present_ids_str = ", ".join(['"{x}"' for x in present_ids])
                raise exc.AlreadyExistingIdsError(
                    f"{model_class} object(s) already exist: {present_ids_str}",
                    ids=present_ids,
                )
        if raise_on_missing:
            missing_ids = [x for x, y in zip(obj_ids, df_objs) if y is None]
            if missing_ids:
                missing_ids_str = ", ".join([f"{x}" for x in missing_ids])
                raise exc.InvalidIdsError(
                    f"{model_class} object(s) do not exist: {missing_ids_str}",
                    ids=missing_ids,
                )

    @staticmethod
    def _verify_valid_ids(
        model_class: Type[Model],
        obj_ids: Iterable[Hashable],
        objs: Iterable[Model | None],
    ) -> None:
        invalid_obj_ids = [x for x, y in zip(obj_ids, objs) if y is None]
        if invalid_obj_ids:
            DictRepository._raise_invalid_ids(model_class, invalid_obj_ids)

    @staticmethod
    def _raise_invalid_ids(
        model_class: Type[Model], invalid_obj_ids: Iterable[Hashable]
    ) -> None:
        invalid_obj_ids_str = ", ".join(f'"{x}"' for x in invalid_obj_ids)
        raise exc.InvalidIdsError(
            f"Model {model_class}: invalid object id(s) provided: {invalid_obj_ids_str}",
            ids=invalid_obj_ids,
        )

    @staticmethod
    def _verify_duplicate_ids(
        model_class: Type[Model], obj_ids: Iterable[Hashable]
    ) -> None:
        set_ = set()
        duplicate_ids = [x for x in obj_ids if x in set_ or set_.add(x)]
        if duplicate_ids:
            DictRepository._raise_duplicate_ids(model_class, duplicate_ids)

    @staticmethod
    def _raise_duplicate_ids(
        model_class: Type[Model], duplicate_ids: Iterable[Hashable]
    ) -> None:
        duplicate_ids_str = ", ".join([f'"{x}"' for x in duplicate_ids])
        raise exc.DuplicateIdsError(
            f"Model {model_class}: object ids are not unique: {duplicate_ids_str}",
            ids=duplicate_ids,
        )

    @staticmethod
    def _verify_duplicate_keys(
        get_id: Callable[[Model], Hashable],
        keys_generator: Callable,
        model_class: Type[Model],
        objs: list[Model],
        df_objs: list[Model] | None,
    ) -> None:
        if not objs:
            # No objs -> no duplicates
            return
        keys = keys_generator(objs[0])
        if not keys:
            # No keys -> no duplicates
            return
        key_ids = list(keys.keys())

        def get_keys(obj):
            keys = keys_generator(obj)
            return tuple(keys[x] for x in key_ids)

        # Check for duplicate keys among objs
        obj_keys_list = [get_keys(x) for x in objs]
        n_keys = len(keys)
        duplicate_objs = []
        for i in range(n_keys):
            curr_obj_keys_list = [x[i] for x in obj_keys_list]
            curr_obj_keys = set(curr_obj_keys_list)
            if len(curr_obj_keys) < len(curr_obj_keys_list):
                seen = set()
                uq_obj_keys = set(
                    x for x in curr_obj_keys_list if x not in seen and not seen.add(x)  # type: ignore
                )
                duplicate_obj_keys = curr_obj_keys - uq_obj_keys
                duplicate_objs += [
                    x
                    for x, y in zip(objs, curr_obj_keys_list)
                    if y in duplicate_obj_keys
                ]
        if duplicate_objs:
            raise exc.UniqueConstraintViolationError(
                f"Model {model_class}: object keys are not unique",
                duplicate_key_ids=list(set([get_id(x) for x in duplicate_objs])),
            )
        # Check for duplicate keys between objs and df_objs, excluding those df_objs
        #  that have the same id as an obj
        if not df_objs:
            return
        obj_ids = set([get_id(x) for x in objs])
        df_obj_keys = [get_keys(x) for x in df_objs if get_id(x) not in obj_ids]
        duplicate_objs = []
        for i in range(n_keys):
            curr_df_obj_keys = set(x[i] for x in df_obj_keys)
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
                f"Model {model_class}: object keys are not unique",
                duplicate_key_ids=list(set([get_id(x) for x in duplicate_objs])),
            )

    @staticmethod
    def _to_iterable(
        obj: Any | Iterable[Any],
    ) -> tuple[bool, list[Any]]:
        # TODO: take model_class as argument, and derive id field class from it to use for check
        if isinstance(obj, (list, set, frozenset)):
            return True, obj
        if issubclass(type(obj), Model):
            return False, [obj]
        if isinstance(obj, UUID):
            return False, [obj]
        try:
            list_obj = list(obj)
            if not list_obj:
                return True, list_obj
            if issubclass(type(list_obj[0]), Model):
                return False, list_obj
            return False, [obj]
        except:
            return False, [obj]
