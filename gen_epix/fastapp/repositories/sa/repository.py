import re
import threading
import uuid
import warnings
from collections.abc import Callable, Hashable, Iterable, Sequence
from pathlib import Path
from typing import Any, Self

import sqlalchemy as sa
from sqlalchemy import Engine, delete, inspect, select
from sqlalchemy.orm import Session, sessionmaker

import gen_epix.fastapp.exc as exc
from gen_epix.fastapp import CrudOperation, Link
from gen_epix.fastapp.domain.entity import Entity
from gen_epix.fastapp.domain.link import Link
from gen_epix.fastapp.enum import CrudOperation, IsolationLevel
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories.sa.engine_factory import EngineFactory
from gen_epix.fastapp.repositories.sa.mapper import (
    BaseSAMapper,
    BaseSAMapperFactory,
    SAMapper,
)
from gen_epix.fastapp.repositories.sa.unit_of_work import SAUnitOfWork
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.filter import (
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
    LogicalOperator,
    NumberRangeFilter,
    NumberSetFilter,
    RangeFilter,
    StringSetFilter,
    UuidSetFilter,
)


class SARepository(BaseRepository):
    DEFAULT_MAX_INSERT_BATCH_SIZE = 2000

    @classmethod
    def _process_repository_params(
        cls, kwargs: dict[str, Any]
    ) -> tuple[list[Entity], str, dict[str, Any]]:
        """Helper method to process common repository parameters and handle connection string/file logic."""
        entities = kwargs.pop("entities", [])
        connection_string = kwargs.pop("connection_string", None)
        file = kwargs.pop("file", None)

        if connection_string is None:
            if file is None:
                raise exc.RepositoryInitializationServiceError(
                    "978e1ed3", "Either connection_string or file must be provided"
                )
            connection_string = f"sqlite:///{Path(file).resolve().as_posix()}"

        return entities, connection_string, kwargs

    @classmethod
    def create_repository(cls, **kwargs: Any) -> BaseRepository:
        entities, connection_string, remaining_kwargs = cls._process_repository_params(
            kwargs
        )
        return cls.create_sa_repository(
            entities=entities,
            connection_string=connection_string,
            **remaining_kwargs,
        )

    @classmethod
    def clear_repository_content(cls, **kwargs: Any) -> None:
        """
        Delete all database objects associated with the repository.
        """
        entities, connection_string, remaining_kwargs = cls._process_repository_params(
            kwargs
        )
        # Get engine
        engine = EngineFactory.create_engine(connection_string, echo=False)

        # Get all actual table names from the database using schema names
        inspector = inspect(engine)
        actual_tables = set()
        schema_names = {x.schema_name for x in entities if x.persistable}
        for schema_name in schema_names:
            if not schema_name:
                continue
            try:
                # Get all table names in this schema from the database
                table_names = inspector.get_table_names(schema=schema_name)
                for table_name in table_names:
                    actual_tables.add((schema_name, table_name))
            except Exception:  # pylint: disable=broad-except
                # Schema might not exist, continue
                continue

        # Drop all foreign key constraints from actual tables
        constraints = []
        for schema_name, table_name in actual_tables:
            try:
                for foreign_key in inspector.get_foreign_keys(
                    table_name, schema=schema_name
                ):
                    if foreign_key.get("name"):
                        constraints.append(
                            (schema_name, table_name, foreign_key["name"])
                        )
            except Exception:  # pylint: disable=broad-except
                # Skip tables that can't be inspected
                continue

        # Drop all foreign key constraints using raw SQL
        if constraints:
            with engine.connect() as conn:
                # Detect database dialect for proper syntax
                dialect_name = conn.dialect.name.lower()
                transaction = conn.begin()
                try:
                    for (
                        schema_name,
                        table_name,
                        constraint_name,
                    ) in constraints:
                        try:
                            # NOTE: Only tested with MS SQL Server
                            if dialect_name == "mssql":
                                # SQL Server syntax with square brackets
                                sql = f"ALTER TABLE [{schema_name}].[{table_name}] DROP CONSTRAINT [{constraint_name}]"
                            elif dialect_name in (
                                "postgresql",
                                "postgres",
                                "redshift",
                            ):
                                # PostgreSQL/Redshift syntax with double quotes
                                sql = f'ALTER TABLE "{schema_name}"."{table_name}" DROP CONSTRAINT "{constraint_name}"'
                            elif dialect_name in ("mysql", "mariadb"):
                                # MySQL/MariaDB syntax with backticks and DROP FOREIGN KEY
                                sql = f"ALTER TABLE `{schema_name}`.`{table_name}` DROP FOREIGN KEY `{constraint_name}`"
                            elif dialect_name in ("oracle", "db2"):
                                # Oracle and DB2 syntax
                                sql = f"ALTER TABLE {schema_name}.{table_name} DROP CONSTRAINT {constraint_name}"
                            else:
                                # Generic SQL syntax (fallback for other databases)
                                sql = f"ALTER TABLE {schema_name}.{table_name} DROP CONSTRAINT {constraint_name}"

                            conn.execute(sa.text(sql))
                        except Exception:  # pylint: disable=broad-except
                            # Some constraints might not exist, continue with others
                            continue
                    transaction.commit()
                except Exception:  # pylint: disable=broad-except
                    transaction.rollback()
                    raise

        # Drop all actual tables
        with engine.connect() as conn:
            for schema_name, table_name in actual_tables:
                try:
                    conn.execute(sa.text(f"DROP TABLE [{schema_name}].[{table_name}]"))
                except Exception:  # pylint: disable=broad-except
                    # Table might already be dropped, continue
                    continue
            conn.commit()

        # Drop schemas if they exist
        for schema_name in schema_names:
            if not schema_name:
                continue
            with engine.connect() as conn:
                try:
                    if conn.dialect.has_schema(conn, schema_name):
                        conn.execute(sa.schema.DropSchema(schema_name))
                        conn.commit()
                except Exception:  # pylint: disable=broad-except
                    # Schema might not exist or have other issues
                    continue

    def __init__(self, engine: Engine, **kwargs: Any):
        # TODO: 2953 remove register_mappers argument
        register_mappers = kwargs.pop("register_mappers", True)
        sa_mapper_factory: BaseSAMapperFactory | None = kwargs.pop(
            "sa_mapper_factory", None
        )
        # Add properties
        self._id: str = kwargs.get("id", str(uuid.uuid4()))
        self._name: str = kwargs.get("name", self._id)
        self._engine = engine

        # Create a session maker per isolation level
        self._default_isolation_level: IsolationLevel = IsolationLevel.SERIALIZABLE
        self._session_maker_by_isolation_level: dict[IsolationLevel, sessionmaker] = {
            x: sessionmaker(engine.execution_options(isolation_level=x.value))
            for x in IsolationLevel
        }

        # Initialize remaining properties
        self._mapper_by_model: dict[type[Any], BaseSAMapper] = {}
        self._mapper_by_row: dict[type[Any], BaseSAMapper] = {}
        self._uow_context_stack_local = threading.local()

        # Register mappers if necessary
        if register_mappers:
            if sa_mapper_factory is not None:
                entities: list[Entity] = kwargs.get("entities", [])
                field_name_map: dict[type[Model], dict[str, str]] = kwargs.get(
                    "field_name_map", {}
                )
                self._init_mappers(entities, field_name_map, sa_mapper_factory)
            else:
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
        context_stack = getattr(self._uow_context_stack_local, "value", None)
        if context_stack is None:
            context_stack = []
            self._uow_context_stack_local.value = context_stack
        if context_stack:
            # Nested within another context -> reuse the session of that context
            if kwargs:
                raise exc.RepositoryServiceError(
                    "b78b8c87",
                    "Cannot pass arguments when creating a nested UnitOfWork",
                )
            return SAUnitOfWork(
                context_stack[-1].session,
                context_stack=context_stack,
            )
        isolation_level: IsolationLevel = kwargs.pop(
            "isolation_level", self._default_isolation_level
        )
        expire_on_commit: bool = kwargs.pop("expire_on_commit", True)
        return SAUnitOfWork(
            self.get_session(
                isolation_level=isolation_level,
                expire_on_commit=expire_on_commit,
                **kwargs,
            ),
            context_stack=context_stack,
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

    def _init_mappers(
        self,
        entities: list[Entity],
        field_name_map: dict[type[Model], dict[str, str]],
        sa_mapper_factory: BaseSAMapperFactory,
    ) -> None:
        """
        Create and register mappers for a list of entities using the given factory.
        The factory encapsulates all db-specific mapper construction, so SARepository
        has no knowledge of process fields or metadata field rules.
        """
        for entity in entities:
            if not entity.persistable:
                continue
            model_class = entity.model_class
            db_model_class = entity.db_model_class
            if not db_model_class:
                raise exc.RepositoryInitializationServiceError(
                    "d135c11c", f"Entity {entity.name} has no db_model_class set"
                )
            assert issubclass(model_class, Model)
            mapper = sa_mapper_factory.create_mapper(
                model_class,
                db_model_class,
                field_name_map=field_name_map.get(model_class),
            )
            self.register_mapper(mapper)

    # TODO: 2953 this can become a static "create_default_mappers" utility method that can be moved to BaseSAMapperFactory, producing a dict[type[Model], BaseSAMapper] that can be passed to the constructor as mentioned in the TODO in the __init__ method
    def register_mappers(
        self,
        entities: list[Entity] | None = None,
        field_name_map: dict[type[Model], dict[str, str]] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Default implementation to register standard mappers for a list of entities.
        """
        # Parse arguments
        entities = entities or []
        field_name_map = field_name_map or {}

        # Create and register mapper for each entity
        for entity in entities:
            if not entity.persistable:
                continue
            model_class = entity.model_class
            db_model_class = entity.db_model_class
            if not db_model_class:
                raise exc.RepositoryInitializationServiceError(
                    "5f725f7a", f"Entity {entity.name} has no db_model_class set"
                )
            assert issubclass(model_class, Model)
            mapper = SAMapper(
                model_class,
                db_model_class,
                field_name_map=field_name_map.get(model_class),
            )
            # TODO: 2953 skip this, instead add to output dict in the proposed static "create_default_mappers" utility method and pass to constructor as mentioned in the TODO in the __init__ method
            self.register_mapper(mapper)

    def get_mapper(self, model_class: type[Model]) -> BaseSAMapper:
        mapper = self._mapper_by_model.get(model_class)
        if not mapper:
            raise exc.RepositoryInitializationServiceError(
                "b8bd9844", f"No mapper set for Model {model_class}"
            )
        return mapper

    def register_mapper(self, mapper: BaseSAMapper) -> Self:
        for current_mapper in self._mapper_by_model.values():
            if current_mapper.row_class == mapper.row_class:
                raise exc.RepositoryInitializationServiceError(
                    "bd89986f", f"Mapper for {current_mapper.model_class} already set"
                )
            if (
                current_mapper.schema_name == mapper.schema_name
                and current_mapper.table_name == mapper.table_name
            ):
                raise exc.RepositoryInitializationServiceError(
                    "90c9edd0", f"Mapper for {current_mapper.model_class} already set"
                )
        model_class = mapper.model_class
        self._mapper_by_model[model_class] = mapper
        return self

    def to_sql(
        self,
        user_id: Hashable | None,
        model_class: type[Model],
        obj: Any | Iterable[Any],
        **kwargs: Any,
    ) -> Any | list[Any]:
        mapper = self._mapper_by_model[model_class]
        if isinstance(obj, model_class):
            return mapper.dump(user_id, obj, **kwargs)
        return [mapper.dump(user_id, x, **kwargs) for x in obj]

    def from_sql(
        self, model_class: type[Model], row: Any | Iterable[Any], **kwargs: Any
    ) -> Any | list[Any]:
        mapper = self._mapper_by_model[model_class]
        if isinstance(row, Iterable):
            return [mapper.load(x, **kwargs) for x in row]
        return mapper.load(row, **kwargs)

    def crud(  # type: ignore
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        operation: CrudOperation,
        objs: Model | Iterable[Model] | None = None,
        obj_ids: Hashable | Iterable[Hashable] | None = None,
        filter: Filter | None = None,
        **kwargs: Any,
    ) -> Model | list[Model] | Hashable | list[Hashable] | bool | list[bool] | None:
        if not isinstance(uow, SAUnitOfWork):
            raise exc.RepositoryServiceError("ff17823b", f"Invalid UnitOfWork: {uow}")
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
        self, model_class: type[Model], user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        return self.create_some(model_class, user_id, [obj], **kwargs)[0]

    def create_some(
        self,
        model_class: type[Model],
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
            raise ValueError(f"Not all objs are of type {model_class.__name__}")

        # Create rows

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            rows = self.to_sql(user_id, model_class, objs)
            n_rows = len(rows)
            n_batches = int(n_rows / max_batch_size) + (n_rows / max_batch_size > 0)
            if not flush and n_batches > 1:
                raise exc.RepositoryServiceError(
                    "fa00ce85",
                    f"Creation of {n_rows} objects requires more than one (n={n_batches}) batches while flush={flush}",
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

    def read_one(
        self, model_class: type[Model], obj_id: Hashable, **kwargs: Any
    ) -> Model:
        return self.read_some(model_class, [obj_id], **kwargs)[0]

    def read_some(
        self, model_class: type[Model], obj_ids: Iterable[Hashable], **kwargs: Any
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
                    "b7efa0d3",
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
        self, model_class: type[Model], filter: Filter | None, **kwargs: Any
    ) -> list[Model]:
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        # Retrieve rows and generate objs
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        get_row_id = mapper.get_row_id
        cascade_read: bool = kwargs.get("cascade_read", False)
        return_id: bool = kwargs.get("return_id", False)
        obj_filter: Filter | None = kwargs.get("obj_filter", None)

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
                stmt = stmt.where(
                    self.get_where_clause_from_filter(row_class, mapper, filter)
                )
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
        self, model_class: type[Model], user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        return self.update_some(model_class, user_id, [obj], **kwargs)[0]

    def update_some(
        self,
        model_class: type[Model],
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

        def _execute(session: Session) -> list[Model]:
            obj_ids = [mapper.get_id(x) for x in objs]
            rows, row_ids = SARepository._in_session_read_some(
                mapper, session, row_class, obj_ids
            )
            map_rows = dict(zip(row_ids, rows))
            for obj in objs:
                row = map_rows[mapper.get_id(obj)]
                mapper.update(user_id, obj, row)
            if flush:
                session.flush()
            return self.from_sql(model_class, rows)

        updated_objs = self._execute_sa(session, _execute, kwargs)
        return updated_objs

    def upsert_one(
        self, model_class: type[Model], user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        return self.upsert_some(model_class, user_id, [obj], **kwargs)[0]

    def upsert_some(
        self,
        model_class: type[Model],
        _user_id: Hashable,
        _objs: Iterable[Model],
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        raise NotImplementedError

    def delete_one(
        self,
        model_class: type[Model],
        user_id: Hashable,
        row_id: Hashable,
        **kwargs: Any,
    ) -> Hashable:
        return self.delete_some(model_class, user_id, [row_id], **kwargs)[0]

    def delete_some(
        self,
        model_class: type[Model],
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
                    "8e431d94",
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
        model_class: type[Model],
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

            row_ids: list[Hashable] | None = None

            # filter and/or obj_filter provided
            if filter or obj_filter:
                # Read all row ids matching filter and obj_filter, then delete those
                row_ids = self.read_all(  # type: ignore[assignment]
                    model_class,
                    filter,
                    session=session,
                    return_id=True,
                    obj_filter=obj_filter,
                )
                stmt = delete(row_class).where(get_row_id(row_class).in_(row_ids))
                session.execute(stmt)
                return row_ids if return_id else None

            # Delete all rows
            if return_id:
                # Get ids
                row_ids = [
                    x[0] for x in session.execute(select(get_row_id(row_class))).all()
                ]

            # # TODO: workaround for SQLite foreign key constraint issues. Remove ASAP.
            # # Check if this is SQLite and if we need to handle foreign key constraints
            # is_sqlite = "sqlite" in str(session.get_bind().url).lower()
            # needs_fk_workaround = False
            # # For SQLite with schemas (using ATTACH DATABASE), foreign key constraints
            # # can cause issues when referencing tables across schemas. Check if this table
            # # has foreign keys that might need special handling.
            # if is_sqlite and hasattr(row_class, "__table__"):
            #     table = row_class.__table__
            #     for fk in table.foreign_keys:
            #         # If foreign key references a table in the same schema, it should work
            #         # If it references a different schema or has schema prefix issues, we might need workaround
            #         referenced_table = fk.column.table
            #         if referenced_table.schema != table.schema or table.name in [
            #             "measurement_relation"
            #         ]:  # Known problematic tables
            #             needs_fk_workaround = True
            #             break
            # # Temporarily disable foreign key constraints if needed
            # if needs_fk_workaround:
            #     session.execute(sa.text("PRAGMA foreign_keys=OFF"))
            #     session.flush()
            # Delete rows
            session.execute(delete(row_class))
            # # Re-enable foreign keys if we disabled them
            # if needs_fk_workaround:
            #     session.execute(sa.text("PRAGMA foreign_keys=ON"))
            #     session.flush()
            # # TODO: end of workaround for SQLite foreign key constraint issues. Remove ASAP.

            return row_ids

        deleted_row_ids = self._execute_sa(session, _execute, kwargs)
        return deleted_row_ids if return_id else None

    def exists_one(
        self, model_class: type[Model], obj_id: Hashable, **kwargs: Any
    ) -> bool:
        return self.exists_some(model_class, [obj_id], **kwargs)[0]

    def exists_some(
        self, model_class: type[Model], obj_ids: Iterable[Hashable], **kwargs: Any
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

    def read_fields(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        field_names: list[str],
        filter: Filter | None = None,
        **kwargs: Any,
    ) -> Iterable[tuple]:
        if not isinstance(uow, SAUnitOfWork):
            raise exc.RepositoryServiceError("4afb32de", f"Invalid UnitOfWork: {uow}")
        mapper = self.get_mapper(model_class)
        field_name_map = mapper.get_field_name_map()
        row_field_names = [field_name_map[x] for x in field_names]
        row_class = mapper.row_class

        def _execute(session: Session) -> Iterable[tuple]:
            stmt = select(*[getattr(row_class, x) for x in row_field_names])
            if filter:
                # Convert filter to where clause and add to statement
                stmt = stmt.where(
                    self.get_where_clause_from_filter(row_class, mapper, filter)
                )
            for row in session.execute(stmt):
                yield row

        return self._execute_sa(uow.session, _execute, kwargs)

    def split_filter(
        self, model_class: type[Model], filter: Filter | None
    ) -> tuple[Filter | None, Filter | None]:
        if not filter:
            return None, None
        field_name_map = self.get_mapper(model_class).get_field_name_map()
        return self._split_filter_recursion(field_name_map, filter)

    def get_where_clause_from_filter(
        self, row_class: type, mapper: BaseSAMapper, filter: Filter
    ) -> Any:
        invert = filter.invert
        if isinstance(filter, CompositeFilter):
            args = []
            for sub_filter in filter.filters:
                args.append(
                    self.get_where_clause_from_filter(row_class, mapper, sub_filter)
                )
            if filter.operator == LogicalOperator.AND:
                return sa.and_(*args) if not invert else sa.not_(sa.and_(*args))
            if filter.operator == LogicalOperator.OR:
                return sa.or_(*args) if not invert else sa.not_(sa.or_(*args))
            raise exc.InvalidArgumentsError(
                "8f411a53", f"Unsupported filter operator: {filter.operator.value}"
            )
        row_field_name = mapper.get_mapped_field_name(str(filter.get_key()))
        if row_field_name is None:
            raise exc.InvalidArgumentsError(
                "320f2bf7",
                f"Filter key '{filter.get_key()}' cannot be mapped to a row field name",
            )
        column = getattr(row_class, row_field_name)
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
            "880a6446", f"Unsupported filter type: {filter.__class__.__name__}"
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
            if filter.operator == LogicalOperator.OR:
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
                        filters=where_clause_filters, operator=LogicalOperator.OR
                    ),
                    None,
                )
            if filter.operator == LogicalOperator.AND:
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
                        filters=where_clause_filters, operator=LogicalOperator.AND
                    )
                if len(remainder_filters) == 0:
                    remainder_filter = None
                elif len(remainder_filters) == 1:
                    remainder_filter = remainder_filters[0]
                else:
                    remainder_filter = CompositeFilter(
                        filters=remainder_filters, operator=LogicalOperator.AND
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

    def print_db_content(self, model_class: type[Model], **kwargs: Any) -> None:
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
        model_class: type[Model],
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
            raise exc.DuplicateIdsError(
                "aac3e2af", "obj_ids is not unique", ids=duplicate_obj_ids
            )
        # Verify existence of objs
        if verify_exists:
            try:
                self.crud(
                    uow,
                    user_id,
                    model_class,
                    CrudOperation.READ_SOME,
                    obj_ids=list(obj_ids_set),
                )
            except exc.InvalidIdsError as e:
                # TODO: determine invalid obj_ids and pass them to the exception
                raise exc.InvalidIdsError(
                    "e1eb6e15", "Invalid obj_ids", ids=None
                ) from e

    @staticmethod
    def _select_with_id_join(
        session: Session,
        get_row_id: Callable[[type], sa.Column],
        row_class: type,
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
                values = [{id_col_name: x} for x in oid_batch]
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
        row_class: type,
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

    def _execute_sa(self, session: Session, execute_fn: Callable, kwargs: dict) -> Any:
        if session:
            retval = execute_fn(session)
        else:
            with self.uow(**kwargs) as uow:
                retval = execute_fn(uow.session)
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
                    "3132db4e",
                    f"Table {table_name}: no row found for id {not_found_obj_ids_str}",
                )
            raise exc.InvalidIdsError(
                "35de72de",
                f"Table {table_name}: no rows found for ids {not_found_obj_ids_str}",
            )

    @staticmethod
    def _verify_duplicate_ids(
        model_class: type[Model], obj_ids: Iterable[Hashable]
    ) -> None:
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
            "bba17339",
            f"Model {model_class.__name__}: object ids are not unique: {duplicate_ids_str}",
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
                    # print(conn)
                    result = conn.execute(sa.text("SELECT name FROM sys.schemas"))
                    schemas = [x[0] for x in result]
                    # print(schemas)
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
            return None
        except BaseException as exception:
            # Connection failed, skip loading
            return exception
