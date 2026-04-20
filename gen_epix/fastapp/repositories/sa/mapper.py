import abc
from collections.abc import Callable, Hashable, Iterable
from typing import Any

from sqlalchemy import Row
from sqlalchemy.orm import MappedColumn

from gen_epix.fastapp import exc
from gen_epix.fastapp.enum import FieldType, FieldTypeSet
from gen_epix.fastapp.model import Model


class BaseSAMapper(abc.ABC):
    """
    BaseSAMapper is an abstract base class for mappers between SQLAlchemy models
    (rows) and Pydantic models. It defines the interface and common functionality
    for mappers, but does not implement the actual mapping logic.
    """

    def __init__(
        self,
        model_class: type[Model],
        row_class: type[Row],
        **kwargs: Any,
    ):
        if model_class.ENTITY is None:
            raise exc.RepositoryServiceError(
                "e0c83ad7",
                f"Model {model_class.__name__} does not have an ENTITY class attribute",
            )
        self._model_class = model_class
        self._row_class = row_class
        self._table_name: str = row_class.__tablename__  # type: ignore[attr-defined]
        self._schema_name: str | None = self._get_schema_name(row_class)

    @property
    def model_class(self) -> type[Model]:
        return self._model_class

    @property
    def row_class(self) -> type:
        return self._row_class

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def schema_name(self) -> str | None:
        return self._schema_name

    @abc.abstractmethod
    def get_field_names_by_type(self, field_type: FieldType) -> tuple:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_field_names_by_set(self, field_type_set: FieldTypeSet) -> tuple:
        raise NotImplementedError()

    def get_field_name_map(self, reverse: bool = False) -> dict[str, str]:
        """
        Get a field name map between model and row fields. If one of the fields does
        not exist or there is no one-to-one mapping, it is excluded from the map.
        This is a naive implementation that can be overridden for performance.
        """
        return {
            field_name if not reverse else row_field_name: (
                row_field_name if not reverse else field_name
            )
            for field_type in FieldType
            for field_name, row_field_name in zip(
                self.get_field_names_by_type(field_type),
                self.get_row_field_names_by_type(field_type),
            )
            if field_name and row_field_name
        }

    @abc.abstractmethod
    def get_mapped_field_name(
        self, field_name: str, reverse: bool = False
    ) -> str | None:
        """
        Get the mapped field name between model and row fields. If there is no
        equivalent or no one-to-one mapping, return None.
        This is a naive implementation that can be overridden for performance.
        """
        return self.get_field_name_map(reverse).get(field_name)

    @abc.abstractmethod
    def get_row_field_names_by_type(self, field_type: FieldType) -> tuple:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_row_field_names_by_set(self, field_type_set: FieldTypeSet) -> tuple:
        raise NotImplementedError()

    def get_id(self, obj: Model) -> Hashable | MappedColumn:
        return obj.get_id()

    @abc.abstractmethod
    def get_row_id(self, row: Row | type[Row]) -> Hashable:
        raise NotImplementedError()

    @abc.abstractmethod
    def dump(self, user_id: Hashable | None, obj: Model, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def update(
        self, user_id: Hashable | None, obj: Model, row: Row, **kwargs: Any
    ) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def load(self, row: Row, **kwargs: Any) -> Model:
        raise NotImplementedError

    @staticmethod
    def _get_schema_name(row: Row | type[Row]) -> str | None:
        for arg in row.__table_args__:  # type: ignore[union-attr]
            if isinstance(arg, dict) and "schema" in arg:
                return arg["schema"]  # type: ignore[no-any-return]
        return None


class BaseSAMapperFactory(abc.ABC):
    """
    Abstract factory for creating SAMapper instances.

    Subclass this in each db layer (casedb, seqdb, etc.) to provide mappers with
    db-specific update logic. The factory is injected into SARepository at construction
    time so that fastapp has no knowledge of process- or metadata-specific field rules.
    """

    @abc.abstractmethod
    def create_mapper(
        self,
        model_class: type[Model],
        row_class: type,
        field_name_map: dict[str, str] | None = None,
    ) -> BaseSAMapper:
        raise NotImplementedError()


class SAMapperFactory(BaseSAMapperFactory):
    """Default factory that creates standard SAMapper instances with no special update logic."""

    def create_mapper(
        self,
        model_class: type[Model],
        row_class: type,
        field_name_map: dict[str, str] | None = None,
    ) -> "SAMapper":
        return SAMapper(model_class, row_class, field_name_map=field_name_map)


class SAMapper(BaseSAMapper):

    def __init__(
        self,
        model_class: type[Model],
        row_class: type,
        field_name_map: dict[str, str] | None = None,
        generate_service_metadata: (
            Callable[[Model, Hashable], dict[str, Any]] | None
        ) = None,
        **kwargs: Any,
    ):
        super().__init__(model_class, row_class, **kwargs)
        self.field_name_map = field_name_map or {}
        self.rev_field_name_map = {y: x for x, y in self.field_name_map.items()}
        self._field_names_by_type: dict[FieldType, tuple] = {}
        self._row_field_names_by_type: dict[FieldType, tuple] = {}
        self._field_names_by_set: dict[FieldTypeSet, tuple] = {}
        self._row_field_names_by_set: dict[FieldTypeSet, tuple] = {}
        self._relationship_field_name_map: dict[str, str] = {}
        self._relationship_field_name_reverse_map: dict[str, str] = {}
        self._init_field_names(model_class, row_class, self.field_name_map)
        self._init_relationship_field_names(model_class, row_class, self.field_name_map)
        self._init_extract_primary_key(model_class)
        self._generate_service_metadata = (
            generate_service_metadata if generate_service_metadata else lambda x, y: {}
        )
        self._is_identical_common_field_names = (
            self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON]
            == self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON]
        )
        self.field_name_map = {
            x: y
            for x, y in zip(
                self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
            )
        }
        self.rev_field_name_map = {y: x for x, y in self.field_name_map.items()}

    def get_field_names_by_type(self, field_type: FieldType) -> tuple:
        """
        The order of field names is guaranteed to be the same as the order of the row
        field names returned by the corresponding function.
        """
        return self._field_names_by_type[field_type]

    def get_field_names_by_set(self, field_type_set: FieldTypeSet) -> tuple:
        """
        The order of field names is guaranteed to be the same as the order of the row
        field names returned by the corresponding function.
        """
        return self._field_names_by_set[field_type_set]

    def get_field_name_map(self, reverse: bool = False) -> dict[str, str]:
        if reverse:
            return self.rev_field_name_map
        return self.field_name_map

    def get_mapped_field_name(
        self, field_name: str, reverse: bool = False
    ) -> str | None:
        if self._is_identical_common_field_names:
            return field_name
        if reverse:
            return self.rev_field_name_map.get(field_name)
        return self.field_name_map.get(field_name)

    def get_row_field_names_by_type(self, field_type: FieldType) -> tuple:
        return self._row_field_names_by_type[field_type]

    def get_row_field_names_by_set(self, field_type_set: FieldTypeSet) -> tuple:
        return self._row_field_names_by_set[field_type_set]

    def get_id(self, obj: Model) -> Hashable:
        return self._get_id(obj)

    def get_row_id(self, row: Row | type[Row]) -> Hashable | MappedColumn:
        return self._get_row_id(row)

    def dump(self, user_id: Hashable | None, obj: Model, **kwargs: Any) -> Any:
        if self._is_identical_common_field_names:
            mapped_dict = obj.model_dump(exclude_none=True)
        else:
            obj_dict = obj.model_dump(exclude_none=False)
            mapped_dict = {
                y: obj_dict[x]
                for x, y in zip(
                    self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                    self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                )
                if obj_dict[x] is not None
            }
        if kwargs:
            return self.row_class(**(mapped_dict | kwargs))
        return self.row_class(**mapped_dict)

    def update(
        self, user_id: Hashable | None, obj: Model, row: Row, **kwargs: Any
    ) -> bool:
        """
        Update the given row with the values from the given object. Only fields that are
        not None in the object are updated, preserving existing DB values for omitted
        fields. Override in subclasses to add db-specific rules (e.g. never touch
        created_at, stamp modified_by from user_id).

        Returns True if any fields were updated, False otherwise.
        """
        if self._is_identical_common_field_names:
            mapped_dict = obj.model_dump(exclude_none=True)
        else:
            obj_dict = obj.model_dump(exclude_none=False)
            mapped_dict = {
                y: obj_dict[x]
                for x, y in zip(
                    self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                    self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                )
                if obj_dict[x] is not None
            }
        if kwargs:
            mapped_dict.update(kwargs)
        is_updated = False
        for key, value in mapped_dict.items():
            if value is None:
                continue
            curr_value = getattr(row, key)
            if curr_value != value:
                setattr(row, key, value)
                is_updated = True
        return is_updated

    def load(self, row: Row, **kwargs: Any) -> Model:
        if self._is_identical_common_field_names:
            mapped_dict = {
                x: getattr(row, x)
                for x in self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON]
            }
        else:
            mapped_dict = {
                x: getattr(row, y)
                for x, y in zip(
                    self._field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                    self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON],
                )
            }
        if kwargs:
            return self.model_class(**(mapped_dict | kwargs))
        return self.model_class(**mapped_dict)

    def _init_field_names(
        self, model_class: type[Model], row_class: type, field_name_map: dict[str, str]
    ) -> None:
        # Set model and row field names by field type
        valid_row_field_names = set(row_class.__table__.columns.keys())
        entity = model_class.ENTITY
        if entity is None:
            raise exc.RepositoryInitializationServiceError(
                "4e09aa9b", f"Model {model_class.__name__} does not ENTITY set"
            )
        common_field_names_set = set.union(
            *[
                set(entity.get_field_names(field_type=x))
                for x in FieldTypeSet.MODEL_DB_COMMON.value
            ],
        )
        for field_type in FieldType:
            field_names = entity.get_field_names(field_type=field_type)
            row_field_names = [
                field_name_map.get(x, x)
                for x in field_names
                if x in common_field_names_set
            ]
            invalid_row_field_names = set(row_field_names) - valid_row_field_names
            if invalid_row_field_names:
                invalid_row_field_names_str = ", ".join(invalid_row_field_names)
                raise exc.RepositoryServiceError(
                    "ec4fcec5",
                    f"Row {row_class.__name__} field(s) {invalid_row_field_names_str} do not exist",
                )
            self._field_names_by_type[field_type] = tuple(field_names)
            self._row_field_names_by_type[field_type] = tuple(row_field_names)

        # Set model and row field names by field type set
        for field_type_set in FieldTypeSet:
            field_names = []
            row_field_names = []
            for field_type in field_type_set.value:
                field_names.extend(self._field_names_by_type[field_type])
                row_field_names.extend(self._row_field_names_by_type[field_type])
            self._field_names_by_set[field_type_set] = tuple(field_names)
            self._row_field_names_by_set[field_type_set] = tuple(row_field_names)

    def _retrieve_field_names(
        self,
        row_class: type,
        service_metadata_field_names: Iterable[str] | None = None,
        db_metadata_field_names: Iterable[str] | None = None,
    ) -> tuple[tuple[str, ...] | None, tuple[str, ...] | None, list[str], set[str]]:
        row_field_names = set(
            self._row_field_names_by_set[FieldTypeSet.MODEL_DB_COMMON]
        )
        actual_row_only_field_names = [
            x for x in row_class.__table__.columns.keys() if x not in row_field_names
        ]
        actual_row_only_field_names_set = set(actual_row_only_field_names)
        service_metadata_field_names = self._check_field_names(
            row_class,
            service_metadata_field_names,
            "service_metadata_field_names",
            actual_row_only_field_names_set,
        )
        db_metadata_field_names = self._check_field_names(
            row_class,
            db_metadata_field_names,
            "db_metadata_field_names",
            actual_row_only_field_names_set,
        )

        return (
            service_metadata_field_names,
            db_metadata_field_names,
            actual_row_only_field_names,
            actual_row_only_field_names_set,
        )

    def _check_field_names(
        self,
        row_class: type,
        field_names: Iterable[str] | None,
        name: str,
        valid_field_names: Iterable[str],
    ) -> tuple[str, ...] | None:
        if field_names is None:
            return None
        if isinstance(field_names, Iterable):
            out_field_names: tuple[str, ...] = tuple(field_names)
        else:
            raise exc.RepositoryServiceError(
                "132ee6ed", f"Row {row_class.__name__} {name} must be a tuple"
            )
        invalid_field_names = set(out_field_names) - set(valid_field_names)
        if invalid_field_names:
            invalid_field_names_str = ", ".join(invalid_field_names)
            raise exc.RepositoryServiceError(
                "19753fac",
                f"Row {row_class.__name__} {name} provided field(s) {invalid_field_names_str} are not in the db model",
            )
        return out_field_names

    def _init_relationship_field_names(
        self, model_class: type[Model], row_class: type, field_name_map: dict[str, str]
    ) -> None:
        # Check that all link fields in the model have corresponding relationship fields in the row
        entity = model_class.ENTITY
        if entity is None:
            raise exc.RepositoryInitializationServiceError(
                "1fd34005", f"Model {model_class.__name__} does not have an ENTITY set"
            )
        relationship_field_names = entity.get_field_names(
            field_type=FieldType.RELATIONSHIP
        )
        row_relationship_field_names = [
            field_name_map.get(x, x) for x in relationship_field_names
        ]
        for field_name, row_field_name in zip(
            relationship_field_names, row_relationship_field_names
        ):
            if not hasattr(row_class, row_field_name):
                continue
            self._relationship_field_name_map[field_name] = row_field_name
            self._relationship_field_name_reverse_map[row_field_name] = field_name

    def _init_extract_primary_key(self, model_class: type[Model]) -> None:
        id_field_names = self._field_names_by_type[FieldType.ID]
        row_id_field_names = self._row_field_names_by_type[FieldType.ID]
        if len(id_field_names) != 1 or len(row_id_field_names) != 1:
            raise NotImplementedError(
                f"Model {model_class.__name__} has more than one ID field"
            )
        id_field_name = id_field_names[0]
        row_id_field_name = row_id_field_names[0]
        self._get_id: Callable[[Model], Hashable] = lambda x: getattr(x, id_field_name)
        self._get_row_id: Callable[[Row | type[Row]], Hashable | MappedColumn] = (
            lambda x: getattr(x, row_id_field_name)
        )
