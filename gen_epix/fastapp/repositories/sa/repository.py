import re
import uuid
import warnings
from pathlib import Path
from typing import Any, Callable, Hashable, Iterable, Self, Sequence, Type

import sqlalchemy as sa
from sqlalchemy import Engine, delete, select
from sqlalchemy.orm import Session, sessionmaker

import gen_epix.fastapp.exc as exc
from gen_epix.fastapp import CrudOperation, Link
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.enum import CrudOperation, FieldTypeSet, IsolationLevel
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.engine_factory import EngineFactory
from gen_epix.fastapp.repositories.sa.mapper import BaseSAMapper, SAMapper
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import (
    BooleanOperator,
    ComparisonOperator,
    CompositeFilter,
    DateRangeFilter,
    DatetimeRangeFilter,
    EqualsBooleanFilter,
    EqualsFilter,
    EqualsNumberFilter,
    EqualsStringFilter,
    EqualsUuidFilter,
    ExistsFilter,
    Filter,
    NumberRangeFilter,
    NumberSetFilter,
    RangeFilter,
    StringSetFilter,
    UuidSetFilter,
)


class SARepository(BaseRepository):
    DEFAULT_MAX_INSERT_BATCH_SIZE = 2000

    def __init__(self, engine: Engine, **kwargs: Any):
        register_mappers = kwargs.pop("register_mappers", True)
        # Add properties
        self._id: str = kwargs.get("id", str(uuid.uuid4()))  # type: ignore[assignment]
        self._name: str = kwargs.get("name", self._id)  # type: ignore[assignment]
        self._engine = engine

        # Create a session maker per isolation level
        self._default_isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE
        self._session_maker_by_isolation_level: dict[IsolationLevel, sessionmaker] = {
            x: sessionmaker(engine.execution_options(isolation_level=x.value))
            for x in IsolationLevel
        }

        # Initialize remaining properties
        self._mapper_by_model: dict[Type[Any], BaseSAMapper] = {}
        self._mapper_by_row: dict[Type[Any], BaseSAMapper] = {}
        self._uow_context_stack: list[BaseUnitOfWork] = []

        # Register mappers if necessary
        if register_mappers:
            self.register_mappers(**kwargs)

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_isolation_level(self) -> IsolationLevel:
        return self._default_isolation_level

    @default_isolation_level.setter
    def default_isolation_level(self, value: IsolationLevel) -> None:
        self._default_isolation_level = value

    def uow(
        self,
        **kwargs: Any,
    ) -> BaseUnitOfWork:
        if self._uow_context_stack:
            # Nested within another context -> reuse the session of that context
            if kwargs:
                raise exc.RepositoryServiceError(
                    "Cannot pass arguments when creating a nested UnitOfWork"
                )
            return SAUnitOfWork(
                self._uow_context_stack[-1].session,
                context_stack=self._uow_context_stack,
            )
        isolation_level: IsolationLevel = kwargs.pop(
            "isolation_level", self._default_isolation_level
        )  # type: ignore[assignment]
        expire_on_commit: bool = kwargs.pop("expire_on_commit", True)  # type: ignore[assignment]
        return SAUnitOfWork(
            self.get_session(
                isolation_level=isolation_level,
                expire_on_commit=expire_on_commit,
                **kwargs,
            ),
            context_stack=self._uow_context_stack,
        )

    def get_session(
        self,
        isolation_level: IsolationLevel | None = None,
        expire_on_commit: bool = False,
        **kwargs: Any,
    ) -> Session:
        isolation_level = isolation_level or self._default_isolation_level
        session: Session = self._session_maker_by_isolation_level[isolation_level](
            expire_on_commit=expire_on_commit
        )
        return session

    def register_mappers(self, **kwargs: Any) -> None:
        """
        Default implementation to register standard mappers for a list of entities.
        """
        # Parse arguments
        entities: list[Entity] = kwargs.pop("entities", [])  # type: ignore[assignment]
        field_name_map: dict[Type[Model], dict[str, str]] = kwargs.pop(
            "field_name_map", {}
        )
        service_metadata_field_names: dict[Type[Model], tuple] = kwargs.pop(
            "service_metadata_field_names", {}
        )
        db_metadata_field_names: dict[Type[Model], tuple] = kwargs.pop(
            "db_metadata_field_names", {}
        )
        generate_service_metadata: dict[
            Type[Model], Callable[[Model, Hashable], dict[str, Any]]
        ] = kwargs.pop("get_row_metadata", {})

        # Create and register mapper for each entity
        for entity in entities:
            if not entity.persistable:
                continue
            model_class = entity.model_class
            db_model_class = entity.db_model_class
            if not db_model_class:
                raise exc.RepositoryInitializationServiceError(
                    f"Entity {entity.name} has no db_model_class set"
                )
            assert issubclass(model_class, Model)
            mapper = SAMapper(
                model_class,
                db_model_class,
                field_name_map=field_name_map.get(model_class),
                service_metadata_field_names=service_metadata_field_names.get(
                    model_class
                ),
                db_metadata_field_names=db_metadata_field_names.get(model_class),
                generate_service_metadata=generate_service_metadata.get(model_class),
            )
            self.register_mapper(mapper)

    def get_mapper(self, model_class: Type) -> BaseSAMapper:
        mapper = self._mapper_by_model.get(model_class)
        if not mapper:
            raise exc.RepositoryInitializationServiceError(
                f"No mapper set for Model {model_class}"
            )
        return mapper

    def register_mapper(self, mapper: BaseSAMapper) -> Self:
        for current_mapper in self._mapper_by_model.values():
            if current_mapper.row_class == mapper.row_class:
                raise exc.RepositoryInitializationServiceError(
                    f"Mapper for {current_mapper.model_class} already set"
                )
            if (
                current_mapper.schema_name == mapper.schema_name
                and current_mapper.table_name == mapper.table_name
            ):
                raise exc.RepositoryInitializationServiceError(
                    f"Mapper for {current_mapper.model_class} already set"
                )
        model_class = mapper.model_class
        self._mapper_by_model[model_class] = mapper
        return self

    def to_sql(
        self,
        user_id: Hashable | None,
        model_class: Type,
        obj: Any | Iterable[Any],
        **kwargs: Any,
    ) -> Any | list[Any]:
        mapper = self._mapper_by_model[model_class]
        if isinstance(obj, model_class):
            return mapper.dump(user_id, obj, **kwargs)
        return [mapper.dump(user_id, x, **kwargs) for x in obj]

    def from_sql(
        self, model_class: Type, row: Any | Iterable[Any], **kwargs: Any
    ) -> Any | list[Any]:
        mapper = self._mapper_by_model[model_class]
        if isinstance(row, Iterable):
            return [mapper.load(x, **kwargs) for x in row]
        return mapper.load(row, **kwargs)

    def crud(  # type: ignore
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: Type[Model],
        objs: Model | Iterable[Model] | None,
        obj_ids: Hashable | Iterable[Hashable] | None,
        operation: CrudOperation,
        filter: Filter | None = None,
        **kwargs,
    ) -> Model | list[Model] | Hashable | list[Hashable] | bool | list[bool] | None:
        if not isinstance(uow, SAUnitOfWork):
            raise exc.RepositoryServiceError(f"Invalid UnitOfWork: {uow}")
        session = uow.session
        BaseRepository.verify_crud_args(model_class, objs, obj_ids, operation)
        match operation:
            case CrudOperation.CREATE_ONE:
                return self.create_one(
                    model_class, user_id, objs, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.CREATE_SOME:
                return self.create_some(
                    model_class, user_id, objs, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.READ_ONE:
                return self.read_one(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.READ_SOME:
                return self.read_some(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.READ_ALL:
                return self.read_all(model_class, filter, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.UPDATE_ONE:
                return self.update_one(
                    model_class, user_id, objs, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.UPDATE_SOME:
                return self.update_some(
                    model_class, user_id, objs, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.UPSERT_ONE:
                return self.upsert_one(
                    model_class, user_id, objs, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.UPSERT_SOME:
                return self.upsert_some(
                    model_class, user_id, objs, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.DELETE_ONE:
                return self.delete_one(
                    model_class, user_id, obj_ids, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.DELETE_SOME:
                return self.delete_some(
                    model_class, user_id, obj_ids, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.DELETE_ALL:
                return self.delete_all(
                    model_class, user_id, filter, session=session, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.EXISTS_ONE:
                return self.exists_one(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.EXISTS_SOME:
                return self.exists_some(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case _:
                raise NotImplementedError(f"Operation {operation} not implemented")

    def create_one(
        self, model_class: Type, user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        return self.create_some(model_class, user_id, [obj], **kwargs)[0]

    def create_some(
        self,
        model_class: Type,
        user_id: Hashable,
        objs: Iterable[Model],
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        return_id: bool = kwargs.get("return_id", False)  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        max_batch_size = int(
            kwargs.get("max_batch_size", self.DEFAULT_MAX_INSERT_BATCH_SIZE)
        )
        objs = objs if isinstance(objs, list) else list(objs)
        if not objs:
            return []

        # Check objs
        if not all(isinstance(x, model_class) for x in objs):
            raise ValueError("Not all objs are of the correct Model")

        # Create rows

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            rows = self.to_sql(user_id, model_class, objs)
            n_rows = len(rows)
            n_batches = int(n_rows / max_batch_size) + (n_rows / max_batch_size > 0)
            if not flush and n_batches > 1:
                raise exc.RepositoryServiceError(
                    f"Creation of {n_rows} objects requires more than one (n={n_batches}) batche while flush={flush}"
                )
            for i in range(n_batches):
                slice_ = slice(
                    i * max_batch_size,
                    min((i + 1) * max_batch_size, n_rows),
                )
                rows_slice = rows[slice_]
                session.add_all(rows_slice)
                if flush:
                    session.flush()
            if return_id:
                mapper = self.get_mapper(model_class)
                get_row_id = mapper.get_row_id
                return [get_row_id(x) for x in rows]
            return self.from_sql(model_class, rows)

        created_objs = self._execute_sa(session, _execute, kwargs)
        return created_objs  # type: ignore[return-value]

    def read_one(self, model_class: Type, obj_id: Hashable, **kwargs: Any) -> Model:
        return self.read_some(model_class, [obj_id], **kwargs)[0]

    def read_some(
        self, model_class: Type, obj_ids: Iterable[Hashable], **kwargs: Any
    ) -> list[Model]:
        """
        :param optimize_parameter_handling, optional kwarg:
           if True, avoid parameterized query that using SQL's IN that is
           more many parameters nonperformant by creating and joining with a temporary table instead
           default = False, but possibly recommend to set dynamically based on number of parameters
        """
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        obj_ids = obj_ids if isinstance(obj_ids, list) else list(obj_ids)
        SARepository._verify_duplicate_ids(model_class, obj_ids)
        # Retrieve rows and verify result
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        cascade_read = kwargs.get("cascade_read", False)
        optimize_parameter_handling = kwargs.get("optimize_parameter_handling", False)

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            rows, row_ids = SARepository._in_session_read_some(
                mapper, session, row_class, obj_ids, optimize_parameter_handling
            )

            # Reorder objs to guarantee same order as obj_ids and at the
            # same time detect missing objs
            map_to_index = {x: i for i, x in enumerate(row_ids)}
            objs = self.from_sql(
                model_class,
                [rows[map_to_index[x]] if x in map_to_index else None for x in obj_ids],
            )
            if any(x is None for x in objs):
                invalids_ids = [x for x, y in zip(obj_ids, objs) if y is None]
                invalids_ids_str = ", ".join([str(x) for x in invalids_ids])
                raise exc.InvalidIdsError(
                    f"{model_class} object(s) do not exist: {invalids_ids_str}",
                    ids=obj_ids,
                )
            # Read links if requested and known
            # If links were not passed explicitly, retrieve them from model
            if cascade_read:
                links = kwargs.get("links", model_class.ENTITY.links)
                self._in_session_add_cascade_read(session, links, objs)

            return objs

        objs = self._execute_sa(session, _execute, kwargs)
        return objs

    def read_all(
        self, model_class: Type, filter: Filter | None, **kwargs: Any
    ) -> list[Model]:
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        # Retrieve rows and generate objs
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        get_row_id = mapper.get_row_id
        cascade_read: bool = kwargs.get("cascade_read", False)  # type: ignore[assignment]
        return_id: bool = kwargs.get("return_id", False)  # type: ignore[assignment]
        obj_filter: Filter | None = kwargs.get("obj_filter", None)  # type: ignore[assignment]

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            # Get either rows or row_ids
            if return_id:
                # Select only row_ids
                stmt = select(get_row_id(row_class))
            else:
                # Select entire row
                stmt = select(row_class)
            if filter:
                # Convert filter to where clause and add to statement
                stmt = stmt.where(self.get_where_clause_from_filter(row_class, filter))
            if return_id:
                row_ids = [x[0] for x in session.execute(stmt).all()]
                if obj_filter:
                    # Retrieve entire rows and filter them with obj_filter, then get
                    # remaining IDs
                    stmt2 = select(row_class).where(get_row_id(row_class).in_(row_ids))
                    rows = [x[0] for x in session.execute(stmt2).all()]
                    objs = self.from_sql(model_class, rows)
                    objs = list(obj_filter.filter_rows(objs, is_model=True))
                    if len(objs) < len(row_ids):
                        row_ids = [mapper.get_id(x) for x in objs]
                objs = row_ids
            else:
                rows = [x[0] for x in session.execute(stmt).all()]
                objs = self.from_sql(model_class, rows)
                if obj_filter:
                    objs = list(obj_filter.filter_rows(objs, is_model=True))
                # Read links if needed
                if cascade_read:
                    links = kwargs.get("links", {})
                    self._in_session_add_cascade_read(session, links, objs)
            return objs

        objs = self._execute_sa(session, _execute, kwargs)
        return objs

    def update_one(
        self, model_class: Type, user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        return self.update_some(model_class, user_id, [obj], **kwargs)[0]

    def update_some(
        self,
        model_class: Type,
        user_id: Hashable,
        objs: Iterable[Model],
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        # Check arguments
        objs = objs if isinstance(objs, list) else list(objs)
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        # Retrieve row
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        row_field_names = mapper.get_row_field_names_by_set(FieldTypeSet.DATA)
        get_row_id = mapper.get_row_id
        get_metadata = mapper.generate_service_metadata

        def _execute(session: Session) -> list[Model]:
            updated_rows = self.to_sql(user_id, model_class, objs)
            obj_ids = [get_row_id(x) for x in updated_rows]
            rows, row_ids = SARepository._in_session_read_some(
                mapper, session, row_class, obj_ids
            )
            map_rows = dict(zip(row_ids, rows))
            for updated_row in updated_rows:
                is_update = False
                row = map_rows[get_row_id(updated_row)]
                # Update content
                for row_field_name in row_field_names:
                    updated_value = getattr(updated_row, row_field_name)
                    if getattr(row, row_field_name) != updated_value:
                        is_update = True
                        setattr(row, row_field_name, updated_value)
                if is_update:
                    # TODO: avoid calling get_metadata twice, once here and once as
                    # part of to_sql above. This could be done by having a property
                    # in the mapper for those metadata fields that are not generated
                    # by the database, as only those need to be set here.
                    for row_field_name, value in get_metadata(updated_row, user_id):
                        setattr(row, row_field_name, value)
            if flush:
                session.flush()
            # Generate objs
            return self.from_sql(model_class, rows)

        updated_objs = self._execute_sa(session, _execute, kwargs)
        return updated_objs

    def upsert_one(
        self, model_class: Type, user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        return self.upsert_some(model_class, user_id, [obj], **kwargs)[0]

    def upsert_some(
        self,
        model_class: Type,
        _user_id: Hashable,
        _objs: Iterable[Model],
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        raise NotImplementedError

    def delete_one(
        self, model_class: Type, user_id: Hashable, row_id: Hashable, **kwargs: Any
    ) -> Hashable:
        return self.delete_some(model_class, user_id, [row_id], **kwargs)[0]

    def delete_some(
        self,
        model_class: Type,
        user_id: Hashable,
        row_ids: Iterable[Hashable],
        **kwargs: Any,
    ) -> list[Hashable]:
        # Check arguments
        row_ids = row_ids if isinstance(row_ids, list) else list(row_ids)
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        # Delete rows
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        get_row_id = mapper.get_row_id

        def _execute(session: Session) -> None:
            is_existing = self.exists_some(model_class, row_ids)
            if not all(is_existing):
                invalid_ids = [x for x, y in zip(row_ids, is_existing) if not y]
                invalid_ids_str = ", ".join([str(x) for x in invalid_ids])
                raise exc.InvalidIdsError(
                    f"{model_class} object(s) do not exist: {invalid_ids_str}",
                    ids=invalid_ids,
                )
            session.execute(delete(row_class).where(get_row_id(row_class).in_(row_ids)))
            if flush:
                session.flush()

        self._execute_sa(session, _execute, kwargs)
        return row_ids

    def delete_all(
        self,
        model_class: Type,
        user_id: Hashable,
        filter: Filter | None,
        **kwargs: Any,
    ) -> list[Hashable] | None:
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        # Delete rows
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        get_row_id = mapper.get_row_id
        return_id: bool = kwargs.get("return_id", False)  # type: ignore[assignment]
        obj_filter: Filter | None = kwargs.get("obj_filter", None)

        def _execute(session: Session) -> list[Hashable] | None:

            if filter or obj_filter:
                raise NotImplementedError("Filter not implemented for delete_all")
            row_ids = None
            if return_id:
                # Get ids
                row_ids = session.execute(select(get_row_id(row_class))).all()
                row_ids = [x[0] for x in row_ids]
            session.execute(delete(row_class))
            return row_ids

        deleted_row_ids = self._execute_sa(session, _execute, kwargs)
        return deleted_row_ids if return_id else None

    def exists_one(self, model_class: Type, obj_id: Hashable, **kwargs: Any) -> bool:
        return self.exists_some(model_class, [obj_id], **kwargs)[0]

    def exists_some(
        self, model_class: Type, obj_ids: Iterable[Hashable], **kwargs: Any
    ) -> list[bool]:
        session: Session = kwargs.get("session")  # type: ignore[assignment]

        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        SARepository._verify_duplicate_ids(model_class, obj_ids)

        def _execute(session: Session) -> list[bool]:
            # select(mapper.get_row_id(row_class)) works because mapper.get_row_id returns the attribute of the row class
            # that functions as the primary key and this attribute is an SQLalchemy Column object that is aware of which table it is in
            rows: Sequence = session.execute(
                select(mapper.get_row_id(row_class)).where(
                    mapper.get_row_id(row_class).in_(obj_ids)
                )
            ).all()
            found_obj_ids = {x[0] for x in rows}
            is_existing_obj = [x in found_obj_ids for x in obj_ids]
            return is_existing_obj

        return self._execute_sa(session, _execute, kwargs)

    def split_filter(
        self, model_class: Type, filter: Filter | None
    ) -> tuple[Filter | None, Filter | None]:
        if not filter:
            return None, None
        field_name_map = self.get_mapper(model_class).get_field_name_map()
        return self._split_filter_recursion(field_name_map, filter)

    def get_where_clause_from_filter(self, row_class: Type, filter: Filter) -> Any:
        invert = filter.invert
        if isinstance(filter, CompositeFilter):
            args = []
            for sub_filter in filter.filters:
                args.append(self.get_where_clause_from_filter(row_class, sub_filter))
            if filter.operator == BooleanOperator.AND:
                return sa.and_(*args) if not invert else sa.not_(sa.and_(*args))
            if filter.operator == BooleanOperator.OR:
                return sa.or_(*args) if not invert else sa.not_(sa.or_(*args))
            raise exc.InvalidArgumentsError(
                f"Unsupported filter operator: {filter.operator.value}"
            )
        column = getattr(row_class, filter.get_key())
        if (
            isinstance(filter, StringSetFilter)
            or isinstance(filter, NumberSetFilter)
            or isinstance(filter, UuidSetFilter)
        ):
            return (
                column.in_(filter.members)
                if not invert
                else sa.not_(column.in_(filter.members))
            )
        elif isinstance(filter, ExistsFilter):
            return column != None if not invert else column == None
        elif isinstance(filter, EqualsFilter):
            return column == filter.value if not invert else column != filter.value
        elif isinstance(filter, RangeFilter):
            args = []
            if filter.lower_bound:
                if filter.lower_bound_censor == ComparisonOperator.GT:
                    args.append(column > filter.lower_bound)
                elif filter.lower_bound_censor == ComparisonOperator.GTE:
                    args.append(column >= filter.lower_bound)
            if filter.upper_bound:
                if filter.upper_bound_censor == ComparisonOperator.ST:
                    args.append(column < filter.upper_bound)
                elif filter.upper_bound_censor == ComparisonOperator.STE:
                    args.append(column <= filter.upper_bound)
            if len(args) == 1:
                return args[0] if not invert else sa.not_(args[0])
            return sa.and_(*args) if not invert else sa.not_(sa.and_(*args))
        raise exc.InvalidArgumentsError(
            f"Unsupported filter type: {filter.__class__.__name__}"
        )

    def _split_filter_recursion(
        self, field_name_map: dict[str, str], filter: Filter
    ) -> tuple[Filter | None, Filter | None]:
        map_key_only_classes = [
            ExistsFilter,
            EqualsBooleanFilter,
            EqualsNumberFilter,
            EqualsStringFilter,
            EqualsUuidFilter,
            StringSetFilter,
            NumberSetFilter,
            UuidSetFilter,
            DateRangeFilter,
            DatetimeRangeFilter,
            NumberRangeFilter,
        ]
        # Convert composite filter if possible
        if isinstance(filter, CompositeFilter):
            where_clause_filters = []
            remainder_filters = []
            if filter.operator == BooleanOperator.OR:
                # Split only when all sub-filters can fully be converted into a where
                # clause
                for sub_filter in filter.filters:
                    where_clause_filter, remainder_filter = (
                        self._split_filter_recursion(field_name_map, sub_filter)
                    )
                    if remainder_filter is not None:
                        # Subfilter could not be converted completely -> filter cannot
                        # be converted
                        return None, filter
                    where_clause_filters.append(where_clause_filter)
                return (
                    CompositeFilter(
                        filters=where_clause_filters, operator=BooleanOperator.OR
                    ),
                    None,
                )
            if filter.operator == BooleanOperator.AND:
                # Split all sub-filters
                for sub_filter in filter.filters:
                    where_clause_filter, remainder_filter = (
                        self._split_filter_recursion(field_name_map, sub_filter)
                    )
                    if where_clause_filter:
                        where_clause_filters.append(where_clause_filter)
                    if remainder_filter:
                        remainder_filters.append(remainder_filter)
                # Combine where clause and remainder filters each into a single filter
                if len(where_clause_filters) == 0:
                    where_clause_filter = None
                elif len(where_clause_filters) == 1:
                    where_clause_filter = where_clause_filters[0]
                else:
                    where_clause_filter = CompositeFilter(
                        filters=where_clause_filters, operator=BooleanOperator.AND
                    )
                if len(remainder_filters) == 0:
                    remainder_filter = None
                elif len(remainder_filters) == 1:
                    remainder_filter = remainder_filters[0]
                else:
                    remainder_filter = CompositeFilter(
                        filters=remainder_filters, operator=BooleanOperator.AND
                    )
                return where_clause_filter, remainder_filter
            # Filter cannot be converted due to unsupported operator
            return None, filter
        # Convert non-composite filter if possible
        mapped_key = field_name_map.get(filter.get_key())
        if not mapped_key:
            # Field name cannot be mapped
            return None, filter
        for filter_class in map_key_only_classes:
            if isinstance(filter, filter_class):
                values = filter.model_dump()
                values["key"] = mapped_key
                return filter_class(**values), None
        # Filter cannot be converted
        return None, filter

    def print_db_content(self, model_class: Type[Model], **kwargs: Any) -> None:
        """Helper method for debugging"""
        header = kwargs.get("header", "")
        mapper = self.get_mapper(model_class)
        tables_classes = [
            mapper.row_class,
        ]
        row_sets = []
        with self.get_session() as session:
            for table_class in tables_classes:
                row_sets.append(list(session.query(table_class)) if table_class else [])
            session.commit()
            for table_class, row_set in zip(tables_classes, row_sets):
                if not table_class:
                    continue
                if not row_set:
                    print(f"{header}empty {table_class}")
                for row in row_set:
                    print(f"{header}{row}")

    def _in_session_add_cascade_read(
        self,
        session: Session,
        links: dict[int, Link],
        objs: list[Model],
        optimize_parameter_handling: bool = False,
    ) -> None:
        # Go over each link
        for link in links.values():
            # Get unique link ids to retrieve
            link_mapper = self.get_mapper(link.link_model_class)
            link_ids = [getattr(x, link.link_field_name) for x in objs]
            uq_link_ids = set(link_ids)
            uq_link_ids.discard(None)
            # Retrieve unique link objs
            uq_link_rows, uq_link_ids = SARepository._in_session_read_some(
                link_mapper,
                session,
                link_mapper.row_class,
                list(uq_link_ids),
                optimize_parameter_handling,
            )
            uq_link_objs = self.from_sql(link.link_model_class, uq_link_rows)
            # Map link objs to ids and set in objs
            uq_link_objs = dict(zip(uq_link_ids, uq_link_objs))
            uq_link_objs[None] = None
            for obj, link_id in zip(objs, link_ids):
                setattr(
                    obj,
                    link.relationship_field_name,
                    uq_link_objs[link_id],
                )

    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: Type[Model],
        obj_ids: Iterable[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        # Check arguments
        if not verify_exists and not verify_duplicate:
            return
        if not isinstance(obj_ids, list):
            obj_ids = list(obj_ids)
        obj_ids_set = set(obj_ids)
        if verify_duplicate and len(obj_ids) != len(obj_ids_set):
            seen = set()
            uq_obj_ids = set(
                x for x in obj_ids if x not in seen and not seen.add(x)  # type: ignore[func-returns-value]
            )
            duplicate_obj_ids = obj_ids_set - uq_obj_ids
            raise exc.DuplicateIdsError("obj_ids is not unique", ids=duplicate_obj_ids)
        # Verify existence of objs
        if verify_exists:
            try:
                self.crud(
                    uow,
                    user_id,
                    model_class,
                    None,
                    list(obj_ids_set),
                    CrudOperation.READ_SOME,
                )
            except exc.InvalidIdsError as e:
                # TODO: determine invalid obj_ids and pass them to the exception
                raise exc.InvalidIdsError("Invalid obj_ids", ids=None) from e

    @staticmethod
    def _select_with_id_join(
        session: sa.orm.Session,
        get_row_id: Callable[[Type], sa.Column],
        row_class: Type,
        obj_ids: list[Hashable],
    ) -> sa.sql.Select:
        """
        Implement a SELECT statement with an INNER JOIN to restrict to the obj_ids passed
        using dialect-specific temporary table creation. Concept is generic and can
        be implemented with essentially any SQL dialect but implementation specifics
        vary; at present, only MS SQL Server is supported.
        """

        dialect = session.get_bind().dialect
        if dialect.name == "mssql":
            # TODO: check if temp table exists and take a different name in that case
            temp_table_name = f"#temp_{str(uuid.uuid4()).replace('-','_')}"
            id_col_name = get_row_id(row_class).name
            id_datatype = row_class.__table__.c[id_col_name].type
            id_datatype_sql = id_datatype.compile(dialect=dialect)
            # TODO: finalize this part
            # Create the temp table
            # we might think to introspect after CREATE TABLE, but that opens us up to session/database sync and lock issues...
            # which we did experience in testing
            temp_table_obj = sa.Table(
                temp_table_name, row_class.metadata, sa.Column(id_col_name, id_datatype)
            )
            session.execute(
                sa.text(
                    f"CREATE TABLE {temp_table_name} ({id_col_name} {id_datatype_sql})"
                )
            )
            # session.flush()  # need to be able to introspect!
            # temp_table_obj = sa.Table(temp_table_name, row_class.metadata, autoload_with=session.get_bind().engine)
            # hard-coded batch size; MS SQL Server limit is 2,100; we just use something reasonable
            # no urgent need to turn hard-coding into a parameter as this is dialect-specific issues
            # handled in dialect-specific code
            batch_size = 1000
            for i in range(0, len(obj_ids), batch_size):
                oid_batch = obj_ids[i : i + batch_size]
                values = [{id_col_name: v} for v in oid_batch]
                session.execute(sa.insert(temp_table_obj), values)
                session.flush()
        else:
            raise NotImplementedError(
                "Only MS SQL Server is supported by _select_with_id_join"
            )

        # Select with join to restrict to ids passed
        sql_select = select(row_class).join(
            temp_table_obj,
            row_class.__table__.c[id_col_name] == temp_table_obj.c[id_col_name],
        )
        return sql_select

    @staticmethod
    def _in_session_read_some(
        mapper: BaseSAMapper,
        session: Session,
        row_class: Type,
        obj_ids: list[Hashable],
        optimize_parameter_handling: bool = False,
    ) -> tuple[list[Any], list[Hashable]]:
        """
        :param optimize_parameter_handling: if True, avoid parameterized query that using SQL's IN that is
           more many parameters nonperformant by creating and joining with a temporary table instead
           default = False, but possibly recommend to set dynamically based on number of parameters
        """
        # n = len(obj_ids)
        # Get rows as list[(Row,)], convert to list[Row]
        get_row_id = mapper.get_row_id
        if obj_ids and optimize_parameter_handling:
            # TODO: finalize this part, remove the example
            # One approach to optmization relative to parameterized query with many params
            # is to create CTE and join with it; this improves performance relative to
            # parameterized query with many params and avoids dialect issues and works with
            # arbitrarily many parameters, but is less performant than temporary table
            # method.
            # Testing on IlesSampleContext:
            #   parameterized query on IlesResult: approx 20 rows per second
            #   CTE method: approx 1,400 rows per second (10k rows)
            #   temporary table method: approx 7,000 rows per second (10k rows)
            # Leaving here in case anyone wants to revisit
            # create a SQLAlchemy CTE from the obj_ids passed as parameters
            # union_stmt = sa.union_all(*[select(sa.literal(oid).label("obj_ids")) for oid in obj_ids])
            # cte = union_stmt.cte("cte_parms")
            # id_col_name = get_row_id(row_class).name
            # sql_select = select(row_class).join(cte, row_class.__table__.c[id_col_name] == cte.c.obj_ids)

            # Or.... the temporary table method
            sql_select = SARepository._select_with_id_join(
                session, get_row_id, row_class, obj_ids
            )
        else:
            sql_select = select(row_class).where(get_row_id(row_class).in_(obj_ids))

        rows = session.execute(sql_select).all()
        rows = [x[0] for x in rows]
        # Further process rows
        row_ids = [get_row_id(x) for x in rows]
        SARepository._in_session_verify_retrieved_ids(mapper, obj_ids, row_ids)
        return rows, row_ids

    def _execute_sa(
        self, session: Session, execute_fun: Callable, kwargs: dict
    ) -> list[Model] | Model | list[Hashable] | Hashable | list[bool] | bool | None:
        if session:
            retval = execute_fun(session)
        else:
            with self.uow(**kwargs) as uow:
                retval = execute_fun(uow.session)
        return retval

    @staticmethod
    def _in_session_verify_retrieved_ids(
        mapper: BaseSAMapper,
        obj_ids: list[Hashable],
        row_ids: list[Hashable],
        table_name: str | None = None,
    ) -> None:
        n = len(obj_ids)
        if len(row_ids) < n:
            not_found_obj_ids = [x for x in obj_ids if x not in row_ids]
            not_found_obj_ids_str = ", ".join([f"{x}" for x in not_found_obj_ids])
            table_name = table_name or mapper.table_name
            if n == 1:
                raise exc.InvalidIdsError(
                    f"Table {table_name}: no row found for id {not_found_obj_ids_str}"
                )
            raise exc.InvalidIdsError(
                f"Table {table_name}: no rows found for ids {not_found_obj_ids_str}"
            )

    @staticmethod
    def _verify_duplicate_ids(model_class: Type, obj_ids: Iterable[Hashable]) -> None:
        if not isinstance(obj_ids, list) and not isinstance(obj_ids, set):
            obj_ids = [obj_ids]
        seen = set()
        uq_obj_ids = set(
            x for x in obj_ids if x not in seen and not seen.add(x)  # type: ignore
        )
        if len(uq_obj_ids) == len(obj_ids):
            return
        duplicate_ids = set(obj_ids) - uq_obj_ids
        duplicate_ids_str = ", ".join([str(x) for x in duplicate_ids])
        raise exc.DuplicateIdsError(
            f"Model {model_class}: object ids are not unique: {duplicate_ids_str}",
            ids=duplicate_ids_str,
        )

    @classmethod
    def create_sa_repository(
        cls,
        entities: list[Entity],
        connection_string: str,
        **kwargs: Any,
    ) -> "SARepository":
        # Parse arguments
        echo = kwargs.pop("echo", False)
        register_mappers = kwargs.pop("register_mappers", True)
        recreate_sqlite_file = kwargs.pop("recreate_sqlite_file", False)
        schema_names = {x.schema_name for x in entities if x.persistable}

        is_sqlite = str(connection_string).lower().startswith("sqlite:///")
        if is_sqlite:
            sqlite_file = Path(
                re.sub(".*sqlite:///", "", connection_string, flags=re.IGNORECASE)
            )
            if recreate_sqlite_file:
                # Remove existing file
                if sqlite_file.is_file():
                    sqlite_file.unlink()
                # Create the file by creating a connection
                engine = sa.create_engine(
                    f"sqlite:///{sqlite_file.as_posix()}", echo=echo
                )
                conn = engine.connect()
                conn.close()
            elif not sqlite_file.is_file():
                raise ValueError("Unable to derive file from connection string")

            # Filter some warnings
            warnings.filterwarnings(
                "ignore",
                r"^Dialect sqlite\+pysqlite does not support updated rowcount.*",
                sa.exc.SAWarning,
            )

            # Create engine, creating the sqlite file(s) if needed
            engine = sa.create_engine("sqlite:///:memory:", echo=echo)

            # Make sure foreign key constraints are enforced,
            # which is not the default for sqlite
            @sa.event.listens_for(engine, "connect")
            def set_sqlite_pragma(
                dbapi_connection: Any, connection_record: Any
            ) -> None:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")

                cursor.close()

            # Add each schema as a separate database, as sqlite does not support schemas
            with engine.connect() as conn:
                if len(schema_names) > 1:
                    raise NotImplementedError(
                        "Multiple schemas: " + ", ".join(schema_names)
                    )
                for schema_name in schema_names:
                    conn.execute(
                        sa.text(f"attach database '{sqlite_file}' as '{schema_name}';")
                    )
        else:
            engine = EngineFactory.create_engine(connection_string, echo)

            # Create schemas if not exists
            for schema_name in schema_names:
                if not schema_name:
                    continue
                with engine.connect() as conn:
                    print(conn)
                    result = conn.execute(sa.text("SELECT name FROM sys.schemas"))
                    schemas = [row[0] for row in result]
                    print(schemas)
                    conn.dialect
                    if not conn.dialect.has_schema(conn, schema_name):
                        conn.execute(sa.schema.CreateSchema(schema_name))
                        conn.commit()

        # Create all tables if necessary
        metadata_set = set()
        for entity in entities:
            if not entity.persistable:
                continue
            db_model_class = entity.db_model_class
            metadata_set.add(db_model_class.metadata)
        for metadata in metadata_set:
            metadata.create_all(engine)

        # Create repository
        repository = cls(
            engine, entities=entities, register_mappers=register_mappers, **kwargs
        )

        return repository

    @classmethod
    def test_connection(
        cls,
        connection_string: str,
        **kwargs: Any,
    ) -> BaseException | None:
        try:
            connection = sa.create_engine(
                connection_string,
                connect_args=kwargs,
            ).connect()
            connection.close()
            return None
        except BaseException as exception:
            # Connection failed, skip loading
            return exception
