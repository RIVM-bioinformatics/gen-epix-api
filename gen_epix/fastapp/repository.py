import abc
import uuid
from itertools import chain
from typing import Any, Callable, Hashable, Iterable, Type

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import Filter


class BaseRepository(abc.ABC):
    def __init__(self, **kwargs: Any):
        self._id: str = kwargs.get("id", str(uuid.uuid4()))  # type: ignore[attr-defined]
        self._name: str = kwargs.get("name", self._id)  # type: ignore[attr-defined]

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @abc.abstractmethod
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
        """
        Perform CRUD operations on the repository within a unit of work context. The
        user_id corresponds to the user that executes the operation and can e.g. be
        used to determine permissions of the user or to store the executing user as
        metadata.
        The filter can be used to filter the results of the operation, and is only
        applied to read and delete all operations. The filter must have keys that
        correspond to the row class fields and must be convertable into a where clause,
        and can e.g. be created by the split_filter method.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def split_filter(
        self, model_class: Type, filter: Filter | None
    ) -> tuple[Filter | None, Filter | None]:
        """
        Splits a filter into two parts: a repository filter that can can be applied by
        this repository directly and presumably efficiently (e.g. as a where clause on
        an SQL database) and a service filter with the remainder that cannot and would
        have to be applied by the service after retrieving results filtered by the
        first part. The input filter must have keys that correspond to the model class
        fields.
        The filters are returned as a tuple[repository_filter, service_filter]. In
        case the filter cannot be split, the first element of the tuple will be None.
        In case the entire filter can be converted into a repository_filter, the second
        element of the tuple will be None.
        """
        raise NotImplementedError()

    def update_association(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: Type[Model],
        link_field_name1: str,
        link_field_name2: str,
        obj_id1: Hashable | None,
        obj_id2: Hashable | None,
        association_objs: Iterable[Model],
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        return_id = kwargs.pop("return_id", False)
        excluded_association_objs: Iterable[Model] = kwargs.pop(
            "excluded_association_objs", []
        )

        # Parse input and create some general functions and values
        association_objs = list(association_objs)
        assert model_class.ENTITY is not None
        id_field_name = model_class.ENTITY.id_field_name
        if not isinstance(id_field_name, str):
            raise exc.RepositoryServiceError(
                f"Model {model_class.__name__}: id_field_name other than string not implemented"
            )
        get_association_id: Callable[[Model], Hashable] = lambda x: getattr(
            x, id_field_name
        )
        excluded_obj_ids = {get_association_id(x) for x in excluded_association_objs}
        excluded_id_pairs = {get_id_pair(x) for x in excluded_association_objs}

        def get_id_pair(obj: Model) -> tuple[Hashable, Hashable]:
            return (getattr(obj, link_field_name1), getattr(obj, link_field_name2))

        # Special case: no association objects, i.e. delete all associations of either obj1 or obj2
        if not association_objs:
            # Go over obj_id1 and obj_id2, only one of both should be provided
            for obj_id, link_field_name in zip(
                [obj_id1, obj_id2], [link_field_name1, link_field_name2]
            ):
                if obj_id is None:
                    continue
                to_delete_obj_ids = [
                    get_association_id(x)  # type: ignore
                    for x in self.crud(  # type: ignore
                        uow,
                        user_id,
                        model_class,
                        None,
                        None,
                        CrudOperation.READ_ALL,
                    )
                    if getattr(x, link_field_name) == obj_id
                    and get_association_id(x) not in excluded_obj_ids  # type: ignore
                ]
                self.crud(
                    uow,
                    user_id,
                    model_class,
                    None,
                    to_delete_obj_ids,
                    CrudOperation.DELETE_SOME,
                )
            return []

        # Get obj_id_pairs and verify uniqueness
        obj_id_pairs = [get_id_pair(x) for x in association_objs]
        obj_dict = dict(zip(obj_id_pairs, association_objs))
        if len(obj_id_pairs) != len(frozenset(obj_id_pairs)):
            invalid_ids = list(
                chain.from_iterable(
                    [x for x in obj_id_pairs if obj_id_pairs.count(x) > 1]
                )
            )
            raise exc.DuplicateIdsError(
                f"Model {model_class.__name__}: object id pairs are not unique",
                ids=invalid_ids,
            )

        # Verify if any excluded ids or id pairs are present
        if excluded_obj_ids:
            invalid_association_obj_ids = [
                get_association_id(x)
                for x in association_objs
                if get_association_id(x) in excluded_obj_ids
            ]
            if invalid_association_obj_ids:
                raise exc.InvalidModelIdsError(
                    f"Model {model_class.__name__}: association objects contains some excluded ids",
                    ids=invalid_association_obj_ids,
                )
        if excluded_id_pairs:
            invalid_id_pairs = [x for x in obj_id_pairs if x in excluded_id_pairs]
            if invalid_id_pairs:
                raise exc.InvalidModelIdsError(
                    f"Model {model_class.__name__}: association object id pairs contains some excluded pairs",
                )

        # Retrieve non-excluded existing objects
        # TODO: replace retrieval of existing objects with a more efficient method
        existing_objs: list[Model] = [
            x  # type: ignore
            for x in self.crud(  # type: ignore
                uow, user_id, model_class, None, None, CrudOperation.READ_ALL
            )
            if get_id_pair(x) in obj_dict  # type: ignore
        ]
        existing_obj_dict: dict[Hashable, Model] = {
            get_id_pair(x): x
            for x in existing_objs
            if get_id_pair(x) not in excluded_id_pairs
        }

        # Determine association objects to create, update or delete
        to_create_objs = [y for x, y in obj_dict.items() if x not in existing_obj_dict]
        to_update_objs = [y for x, y in obj_dict.items() if x in existing_obj_dict]
        to_delete_objs = [y for x, y in existing_obj_dict.items() if x not in obj_dict]

        # Verify that objects to create have an id
        if any([get_association_id(x) is None for x in to_create_objs]):
            raise exc.InvalidModelIdsError(
                f"Model {model_class.__name__}: object(s) to create have no id",
                ids=[
                    get_association_id(x)
                    for x in to_create_objs
                    if get_association_id(x) is None
                ],
            )

        # Create association objects
        if to_create_objs:
            self.crud(
                uow,
                user_id,
                model_class,
                to_create_objs,
                None,
                CrudOperation.CREATE_SOME,
            )

        # Update association objects
        to_update_obj_ids = [
            get_association_id(existing_obj_dict[get_id_pair(x)])
            for x in to_update_objs
        ]
        if to_update_obj_ids:
            for obj, obj_id in zip(to_update_objs, to_update_obj_ids):
                # Set actual ids of objects to update, so that this is also corrected in the caller
                setattr(obj, id_field_name, obj_id)
            self.crud(
                uow,
                user_id,
                model_class,
                to_update_objs,
                None,
                CrudOperation.UPDATE_SOME,
            )

        # Delete association objects
        if to_delete_objs:
            self.crud(
                uow,
                user_id,
                model_class,
                None,
                [get_association_id(x) for x in to_delete_objs],
                CrudOperation.DELETE_SOME,
            )

        return (
            [get_association_id(x) for x in association_objs]
            if return_id
            else association_objs
        )

    @abc.abstractmethod
    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: Type[Model],
        obj_ids: Iterable[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def uow(self, **kwargs: Any) -> BaseUnitOfWork:
        raise NotImplementedError()

    @staticmethod
    def raise_on_duplicate_ids(obj_ids: Iterable[Hashable]) -> None:
        set_ = set()
        duplicate_ids = [x for x in obj_ids if x in set_ or set_.add(x)]  # type: ignore
        if duplicate_ids:
            duplicate_ids_str = ", ".join([f'"{x}"' for x in duplicate_ids])
            raise exc.DuplicateIdsError(
                f"Object ids are not unique: {duplicate_ids_str}",
                ids=duplicate_ids,
            )

    @staticmethod
    def verify_crud_args(
        model_class: Type[Model],
        objs: Model | Iterable[Model] | None,
        obj_ids: Hashable | Iterable[Hashable] | None,
        operation: CrudOperation,
    ) -> None:

        def _verify_no_objs() -> None:
            if objs is not None:
                raise exc.InvalidArgumentsError(
                    "Invalid objs: expected None, " f"got {type(objs)}"
                )

        def _verify_no_obj_ids() -> None:
            if obj_ids is not None:
                raise exc.InvalidArgumentsError(
                    "Invalid obj_ids: expected None, " f"got {type(obj_ids)}"
                )

        def _verify_no_data() -> None:
            _verify_no_objs()
            _verify_no_obj_ids()

        def _verify_one_obj() -> None:
            if not isinstance(objs, model_class):
                raise exc.InvalidArgumentsError(
                    "Invalid objs: expected single object, " f"got {type(objs)}"
                )
            _verify_no_obj_ids()

        def _verify_one_id() -> None:
            _verify_no_objs()
            if not isinstance(obj_ids, Hashable):
                raise exc.InvalidArgumentsError(
                    "Invalid obj_ids: expected single obj_id, " f"got {type(obj_ids)}"
                )

        def _verify_some_objs() -> None:
            if not isinstance(objs, Iterable) or isinstance(objs, model_class):
                raise exc.InvalidArgumentsError(
                    "Invalid objs: expected iterable of objs, " f"got {type(objs)}"
                )
            _verify_no_obj_ids()

        def _verify_some_ids() -> None:
            _verify_no_objs()
            if not isinstance(obj_ids, Iterable):
                raise exc.InvalidArgumentsError(
                    "Invalid obj_ids: expected iterable of obj_ids, "
                    f"got {type(obj_ids)}"
                )

        match operation:
            case CrudOperation.CREATE_ONE:
                _verify_one_obj()
            case CrudOperation.CREATE_SOME:
                _verify_some_objs()
            case CrudOperation.READ_ONE:
                _verify_one_id()
            case CrudOperation.READ_SOME:
                _verify_some_ids()
            case CrudOperation.READ_ALL:
                _verify_no_data()
            case CrudOperation.UPDATE_ONE:
                _verify_one_obj()
            case CrudOperation.UPDATE_SOME:
                _verify_some_objs()
            case CrudOperation.UPSERT_ONE:
                _verify_one_obj()
            case CrudOperation.UPSERT_SOME:
                _verify_some_objs()
            case CrudOperation.DELETE_ONE:
                _verify_one_id()
            case CrudOperation.DELETE_SOME:
                _verify_some_ids()
            case CrudOperation.DELETE_ALL:
                _verify_no_data()
            case CrudOperation.UNDELETE_ONE:
                _verify_one_id()
            case CrudOperation.UNDELETE_SOME:
                _verify_some_ids()
            case CrudOperation.UNDELETE_ALL:
                _verify_no_data()
            case CrudOperation.RESTORE_ONE:
                _verify_one_id()
            case CrudOperation.RESTORE_SOME:
                _verify_some_ids()
            case CrudOperation.EXISTS_ONE:
                _verify_one_id()
            case CrudOperation.EXISTS_SOME:
                _verify_some_ids()
            case _:
                raise NotImplementedError(f"Operation {operation} not implemented")
