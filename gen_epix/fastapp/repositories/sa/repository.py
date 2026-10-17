"""SQLAlchemy repository implementation."""

import re
import threading
import uuid
import warnings
from collections.abc import Callable, Hashable, Iterable, Sequence
from pathlib import Path
from typing import Any, Self, cast

import sqlalchemy as sa
from sqlalchemy import Engine, delete, event, inspect, select
from sqlalchemy.exc import SAWarning
from sqlalchemy.orm import Session, sessionmaker

import gen_epix.fastapp.exc as exc
from gen_epix.fastapp.domain.entity import Entity
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
    """Encapsulates a SQLAlchemy-backed repository."""

    DEFAULT_MAX_INSERT_BATCH_SIZE = 2000
    DEFAULT_MAX_PARAMETERS_IN_CLAUSE = 1000

    @classmethod
    def _process_repository_params(
        cls, kwargs: dict[str, Any]
    ) -> tuple[list[Entity], str | None, dict[str, Any]]:
        """Helper method to process common repository parameters and handle connection string/file logic."""
        entities = kwargs.pop("entities", [])
        connection_string = kwargs.pop("connection_string", None)
        file = kwargs.pop("file", None)

        if connection_string is None and file:
            connection_string = f"sqlite:///{Path(file).resolve().as_posix()}"

        return entities, connection_string, kwargs

    @classmethod
    def create_repository(cls, **kwargs: Any) -> BaseRepository:
        """
        Create a repository instance from keyword arguments.

        Accepts either ``connection_string`` or ``file`` (SQLite path).
        """
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
        """Delete all database objects associated with the repository.

        If ``alembic_schema`` is given, also drops that schema's
        ``alembic_version`` table and the schema itself, so a subsequent
        ``alembic upgrade head`` starts from a clean slate instead of being
        skipped because a stale version row is still on record.
        """
        alembic_schema: str | None = kwargs.pop("alembic_schema", None)
        entities, connection_string, remaining_kwargs = cls._process_repository_params(
            kwargs
        )
        if connection_string is None:
            raise ValueError("connection_string is required to clear an SARepository")
        # Get engine
        engine = EngineFactory.create_engine(connection_string, echo=False)

        # Get all actual table names from the database using schema names
        inspector = inspect(engine)
        actual_tables: set[tuple[str | None, str]] = set()
        schema_names = {x.schema_name for x in entities if x.persistable}
        for schema_name in schema_names:
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
                            (
                                schema_name,
                                table_name,
                                cast(str, foreign_key["name"]),
                            )
                        )
            except Exception:  # pylint: disable=broad-except
                # Skip tables that can't be inspected
                continue

        # Drop all foreign key constraints using raw SQL
        if constraints:
            with engine.connect() as conn:
                # Detect database dialect for proper syntax
                dialect_name = conn.dialect.name.lower()
                identifier_preparer = conn.dialect.identifier_preparer
                transaction = conn.begin()
                try:
                    for schema_name, table_name, constraint_name in constraints:
                        try:
                            quoted_table_name = identifier_preparer.quote(table_name)
                            if schema_name is None:
                                qualified_table_name = quoted_table_name
                            else:
                                qualified_table_name = (
                                    f"{identifier_preparer.quote(schema_name)}."
                                    f"{quoted_table_name}"
                                )
                            quoted_constraint_name = identifier_preparer.quote(
                                constraint_name
                            )
                            # NOTE: Only tested with MS SQL Server
                            if dialect_name == "mssql":
                                sql = (
                                    f"ALTER TABLE {qualified_table_name} "
                                    f"DROP CONSTRAINT {quoted_constraint_name}"
                                )
                            elif dialect_name in (
                                "postgresql",
                                "postgres",
                                "redshift",
                            ):
                                sql = (
                                    f"ALTER TABLE {qualified_table_name} "
                                    f"DROP CONSTRAINT {quoted_constraint_name}"
                                )
                            elif dialect_name in ("mysql", "mariadb"):
                                sql = (
                                    f"ALTER TABLE {qualified_table_name} "
                                    f"DROP FOREIGN KEY {quoted_constraint_name}"
                                )
                            else:
                                sql = (
                                    f"ALTER TABLE {qualified_table_name} "
                                    f"DROP CONSTRAINT {quoted_constraint_name}"
                                )

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
                    sa.Table(table_name, sa.MetaData(), schema=schema_name).drop(
                        conn, checkfirst=True
                    )
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
            engine.dispose()

        # Drop the Alembic version-tracking table and schema, if requested
        if alembic_schema:
            with engine.connect() as conn:
                try:
                    sa.Table(
                        "alembic_version", sa.MetaData(), schema=alembic_schema
                    ).drop(conn, checkfirst=True)
                    conn.commit()
                except Exception:  # pylint: disable=broad-except
                    pass
                try:
                    if conn.dialect.has_schema(conn, alembic_schema):
                        conn.execute(sa.schema.DropSchema(alembic_schema))
                        conn.commit()
                except Exception:  # pylint: disable=broad-except
                    pass
            engine.dispose()

    @classmethod
    def check_schema_matches(cls, **kwargs: Any) -> list[str]:
        """Compare each entity's expected table/columns against the live database.

        Returns a list of human-readable problems (missing tables, missing
        columns); empty if the schema matches. Does not assume the database
        already matches the entities - that's exactly what this detects.
        """
        entities, connection_string, _ = cls._process_repository_params(kwargs)
        if connection_string is None:
            raise ValueError(
                "connection_string is required to check an SARepository schema"
            )
        engine = EngineFactory.create_engine(connection_string, echo=False)
        inspector = inspect(engine)
        problems: list[str] = []
        for entity in entities:
            if not entity.persistable or not entity.db_model_class:
                continue
            table = entity.db_model_class.__table__
            schema_name = entity.schema_name
            qualified_name = (
                f"{schema_name}.{table.name}" if schema_name else table.name
            )
            try:
                actual_tables = set(inspector.get_table_names(schema=schema_name))
            except Exception as e:  # pylint: disable=broad-except
                problems.append(f"schema {schema_name!r} could not be inspected: {e}")
                continue
            if table.name not in actual_tables:
                problems.append(f"table {qualified_name} does not exist")
                continue
            actual_columns = {
                c["name"] for c in inspector.get_columns(table.name, schema=schema_name)
            }
            missing_columns = {c.name for c in table.columns} - actual_columns
            if missing_columns:
                problems.append(
                    f"table {qualified_name} is missing column(s): "
                    f"{', '.join(sorted(missing_columns))}"
                )
        return problems

    def __init__(self, engine: Engine, **kwargs: Any):
        """
        Initialise the repository with the provided SQLAlchemy engine.

        Registers mappers for each persistable entity and creates per-
        isolation-level session factories.
        """
        # TODO: 2953 remove register_mappers argument
        register_mappers: bool = kwargs.pop("register_mappers", True)
        sa_mapper_factory: BaseSAMapperFactory | None = kwargs.pop(
            "sa_mapper_factory", None
        )
        # Add properties
        self._id: str = kwargs.get("id", str(uuid.uuid4()))
        self._name: str = kwargs.get("name", self._id)
        self._engine = engine
        self._max_insert_batch_size: int = int(
            kwargs.get("max_insert_batch_size", self.DEFAULT_MAX_INSERT_BATCH_SIZE)
        )
        self._max_parameters_in_clause: int = int(
            kwargs.get(
                "max_parameter_batch_size", self.DEFAULT_MAX_PARAMETERS_IN_CLAUSE
            )
        )

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
        """Return the repository's unique identifier."""
        return self._id

    @property
    def name(self) -> str:
        """Return the repository's name."""
        return self._name

    @property
    def default_isolation_level(self) -> IsolationLevel:
        """Return the default isolation level for new sessions."""
        return self._default_isolation_level

    @default_isolation_level.setter
    def default_isolation_level(self, value: IsolationLevel) -> None:
        """Set the default isolation level for new sessions."""
        self._default_isolation_level = value

    def uow(
        self,
        **kwargs: Any,
    ) -> BaseUnitOfWork:
        """
        Return a unit-of-work context manager backed by an SA session.

        Nests within the active UoW when already inside a context.
        """
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
            last_uow: SAUnitOfWork = context_stack[-1]
            return SAUnitOfWork(
                last_uow.session,
                context_stack=self._uow_context_stack_local.value,
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
        """Create and return a new SA session at the given isolation level."""
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
        """Default implementation to register standard mappers for a list of entities."""
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
        """Return the registered mapper for the given model class."""
        mapper = self._mapper_by_model.get(model_class)
        if not mapper:
            raise exc.RepositoryInitializationServiceError(
                "b8bd9844", f"No mapper set for Model {model_class}"
            )
        return mapper

    def register_mapper(self, mapper: BaseSAMapper) -> Self:
        """Register a mapper, enforcing uniqueness by row class and table."""
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
        """Convert one or more model instances to their ORM row equivalents."""
        mapper = self._mapper_by_model[model_class]
        if isinstance(obj, model_class):
            return mapper.dump(user_id, obj, **kwargs)
        return [mapper.dump(user_id, x, **kwargs) for x in obj]

    def from_sql(
        self, model_class: type[Model], row: Any | Iterable[Any], **kwargs: Any
    ) -> Any | list[Any]:
        """Convert one or more ORM rows back to model instances."""
        mapper = self._mapper_by_model[model_class]
        if isinstance(row, Iterable):
            return [mapper.load(x, **kwargs) for x in row]
        return mapper.load(row, **kwargs)

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
        """Dispatch a CRUD operation to the appropriate concrete method."""
        if not isinstance(uow, SAUnitOfWork):
            raise exc.RepositoryServiceError("ff17823b", f"Invalid UnitOfWork: {uow}")
        session = uow.session
        if limit < 0:
            raise exc.RepositoryServiceError("d9c8e5b3", "Limit cannot be negative")
        if offset < 0:
            raise exc.RepositoryServiceError("a4f1c9d2", "Offset cannot be negative")
        BaseRepository.verify_crud_args(model_class, objs, obj_ids, operation)
        match operation:
            case CrudOperation.CREATE_ONE:
                return self.create_one(
                    model_class, user_id, objs, session=session, return_id=return_id, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.CREATE_SOME:
                return self.create_some(
                    model_class, user_id, objs, session=session, return_id=return_id, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.READ_ONE:
                return self.read_one(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.READ_SOME:
                return self.read_some(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.READ_ALL:
                return self.read_all(
                    model_class,
                    filter,
                    session=session,
                    return_id=return_id,
                    limit=limit,
                    offset=offset,
                    **kwargs,
                )
            case CrudOperation.UPDATE_ONE:
                return self.update_one(
                    model_class, user_id, objs, session=session, return_id=return_id, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.UPDATE_SOME:
                return self.update_some(
                    model_class, user_id, objs, session=session, return_id=return_id, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.UPSERT_ONE:
                return self.upsert_one(
                    model_class, user_id, objs, session=session, return_id=return_id, **kwargs  # type: ignore[arg-type]
                )
            case CrudOperation.UPSERT_SOME:
                return self.upsert_some(
                    model_class, user_id, objs, session=session, return_id=return_id, **kwargs  # type: ignore[arg-type]
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
                    model_class,
                    user_id,
                    filter,
                    session=session,
                    return_id=return_id,
                    **kwargs,
                )
            case CrudOperation.EXISTS_ONE:
                return self.exists_one(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case CrudOperation.EXISTS_SOME:
                return self.exists_some(model_class, obj_ids, session=session, **kwargs)  # type: ignore[arg-type]
            case _:
                raise NotImplementedError(f"Operation {operation} not implemented")

    def create_one(
        self,
        model_class: type[Model],
        user_id: Hashable,
        obj: Model,
        return_id: bool = False,
        **kwargs: Any,
    ) -> Model | Hashable:
        """Persist a single model instance and return it (or its id)."""
        return self.create_some(
            model_class, user_id, [obj], return_id=return_id, **kwargs
        )[0]

    def create_some(
        self,
        model_class: type[Model],
        user_id: Hashable,
        objs: Iterable[Model],
        return_id: bool = False,
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        """Persist a batch of model instances, flushing in configurable chunks."""
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        max_batch_size = self._max_insert_batch_size
        objs = objs if isinstance(objs, list) else list(objs)
        if not objs:
            return []

        # Check objs
        if not all(isinstance(x, model_class) for x in objs):
            raise ValueError(f"Not all objs are of type {model_class.__name__}")
        mapper = self.get_mapper(model_class)
        SARepository._verify_duplicate_ids(
            model_class, [mapper.get_id(obj) for obj in objs]
        )

        # Create rows

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            """Execute the requested value."""
            rows = self.to_sql(user_id, model_class, objs)
            n_rows = len(rows)
            n_batches = (n_rows + max_batch_size - 1) // max_batch_size
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
                return [mapper.get_row_id(x) for x in rows]
            return self.from_sql(model_class, rows)

        created_objs: list[Model] | list[Hashable] = self._execute_sa(
            session, _execute, kwargs
        )
        return created_objs

    def read_one(
        self, model_class: type[Model], obj_id: Hashable, **kwargs: Any
    ) -> Model:
        """Fetch a single model by id."""
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
        optimize_parameter_handling = kwargs.get("optimize_parameter_handling", False)

        def _execute(session: Session) -> list[Model]:
            """Execute the requested value."""
            rows, row_ids = SARepository._in_session_read_some(
                mapper,
                session,
                obj_ids,
                optimize_parameter_handling=optimize_parameter_handling,
                max_ids_in_clause=self._max_parameters_in_clause,
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
            return objs

        objs: list[Model] = self._execute_sa(session, _execute, kwargs)
        return objs

    def read_all(
        self,
        model_class: type[Model],
        filter: Filter | None,
        return_id: bool = False,
        limit: int = 0,
        offset: int = 0,
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        """
        Fetch all rows matching an optional filter, with limit/offset support.

        An ``obj_filter`` kwarg may apply additional Python-side filtering.
        """
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        # Retrieve rows and generate objs
        mapper = self.get_mapper(model_class)
        obj_filter: Filter | None = kwargs.get("obj_filter", None)
        limit = limit or -1
        offset = offset or 0
        return self._execute_sa(
            session,
            lambda current_session: self._execute_read_all(
                current_session,
                model_class,
                mapper,
                filter,
                obj_filter,
                return_id,
                limit,
                offset,
            ),
            kwargs,
        )

    @staticmethod
    def _add_read_all_sql_pagination(
        stmt: sa.Select, limit: int, offset: int
    ) -> sa.Select:
        """Apply SQL pagination when filtering is entirely database-side."""
        if limit > 0:
            stmt = stmt.limit(limit)
        if offset > 0:
            stmt = stmt.offset(offset)
        return stmt

    @staticmethod
    def _apply_read_all_obj_pagination(
        objs: list[Model], limit: int, offset: int
    ) -> list[Model]:
        """Apply pagination after Python-side object filtering."""
        if limit <= 0:
            return objs
        if offset > len(objs):
            return []
        if offset + limit > len(objs):
            return objs[offset:]
        return objs[offset : offset + limit]

    def _execute_read_all(
        self,
        session: Session,
        model_class: type[Model],
        mapper: BaseSAMapper,
        filter: Filter | None,
        obj_filter: Filter | None,
        return_id: bool,
        limit: int,
        offset: int,
    ) -> list[Model] | list[Hashable]:
        """Execute a read_all query and apply any Python-side filter."""
        row_class = mapper.row_class
        selected_column = mapper.get_row_id_column() if return_id else row_class
        stmt = select(selected_column)
        if not obj_filter:
            # Apply SQL pagination only when Python-side filtering is not needed.
            stmt = self._add_read_all_sql_pagination(stmt, limit, offset)
        if filter:
            stmt = stmt.where(
                self.get_where_clause_from_filter(row_class, mapper, filter)
            )
        if return_id:
            return self._read_all_ids(
                session, model_class, mapper, stmt, obj_filter, limit, offset
            )
        rows = [row[0] for row in session.execute(stmt).all()]
        objs = cast(list[Model], self.from_sql(model_class, rows))
        if obj_filter:
            objs = cast(list[Model], list(obj_filter.filter_rows(objs, is_model=True)))
            objs = self._apply_read_all_obj_pagination(objs, limit, offset)
        return objs

    def _read_all_ids(
        self,
        session: Session,
        model_class: type[Model],
        mapper: BaseSAMapper,
        stmt: sa.Select,
        obj_filter: Filter | None,
        limit: int,
        offset: int,
    ) -> list[Hashable]:
        """Return IDs, applying object filters through the corresponding domain rows."""
        row_ids: list[Hashable] = [row[0] for row in session.execute(stmt).all()]
        if not obj_filter:
            return row_ids
        # Retrieve entire rows and filter them with obj_filter, then get remaining IDs.
        row_class = mapper.row_class
        stmt = select(row_class).where(mapper.get_row_id_column().in_(row_ids))
        rows = [row[0] for row in session.execute(stmt).all()]
        objs = cast(list[Model], self.from_sql(model_class, rows))
        objs = cast(list[Model], list(obj_filter.filter_rows(objs, is_model=True)))
        objs = self._apply_read_all_obj_pagination(objs, limit, offset)
        if len(objs) < len(row_ids):
            return [mapper.get_id(obj) for obj in objs]
        return row_ids

    def update_one(
        self, model_class: type[Model], user_id: Hashable, obj: Model, **kwargs: Any
    ) -> Model | Hashable:
        """Update a single model instance and return it (or its id)."""
        return self.update_some(model_class, user_id, [obj], **kwargs)[0]

    def update_some(
        self,
        model_class: type[Model],
        user_id: Hashable,
        objs: Iterable[Model],
        return_id: bool = False,
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        """Update existing rows in-place by loading and applying model changes."""
        # Check arguments
        objs = objs if isinstance(objs, list) else list(objs)
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        optimize_parameter_handling: bool = bool(
            kwargs.get("optimize_parameter_handling", False)
        )
        # Retrieve row
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        SARepository._verify_duplicate_ids(
            model_class, [mapper.get_id(obj) for obj in objs]
        )

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            """Execute the requested value."""
            obj_ids = [mapper.get_id(x) for x in objs]
            rows, row_ids = SARepository._in_session_read_some(
                mapper,
                session,
                obj_ids,
                optimize_parameter_handling=optimize_parameter_handling,
                max_ids_in_clause=self._max_parameters_in_clause,
            )
            map_rows = dict(zip(row_ids, rows))
            for obj in objs:
                row = map_rows[mapper.get_id(obj)]
                mapper.update(user_id, obj, row)
            if flush:
                session.flush()
            if return_id:
                return obj_ids
            return self.from_sql(model_class, rows)

        updated_objs: list[Model] | list[Hashable] = self._execute_sa(
            session, _execute, kwargs
        )
        return updated_objs

    def upsert_one(
        self,
        model_class: type[Model],
        user_id: Hashable,
        obj: Model,
        return_id: bool = False,
        **kwargs: Any,
    ) -> Model | Hashable:
        """Insert or update a single model instance."""
        return self.upsert_some(
            model_class, user_id, [obj], return_id=return_id, **kwargs
        )[0]

    def upsert_some(
        self,
        model_class: type[Model],
        user_id: Hashable,
        objs: Iterable[Model],
        return_id: bool = False,
        **kwargs: Any,
    ) -> list[Model] | list[Hashable]:
        """
        Insert new objects and update existing ones in a single call.

        Existence is checked in batches to respect SQL Server's parameter limit.
        """
        objs = objs if isinstance(objs, list) else list(objs)
        if not objs:
            return []
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        optimize_parameter_handling: bool = bool(
            kwargs.get("optimize_parameter_handling", False)
        )
        max_batch_size = self._max_insert_batch_size

        if not all(isinstance(x, model_class) for x in objs):
            raise ValueError(f"Not all objs are of type {model_class.__name__}")

        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        SARepository._verify_duplicate_ids(
            model_class, [mapper.get_id(obj) for obj in objs]
        )

        def _execute(session: Session) -> list[Model] | list[Hashable]:
            """Execute the requested value."""
            obj_ids = [mapper.get_id(x) for x in objs]
            row_id_col = mapper.get_row_id_column()
            existing_ids = self._get_existing_upsert_ids(
                session, obj_ids, row_id_col, max_batch_size
            )

            new_objs = [o for o, oid in zip(objs, obj_ids) if oid not in existing_ids]
            existing_objs = [o for o, oid in zip(objs, obj_ids) if oid in existing_ids]

            new_rows: list[Any] = self.to_sql(user_id, model_class, new_objs)
            self._insert_upsert_rows(session, new_rows, max_batch_size, flush)
            updated_rows = self._update_upsert_rows(
                session,
                mapper,
                user_id,
                existing_objs,
                max_batch_size,
                optimize_parameter_handling,
                flush,
            )

            row_by_id = {mapper.get_row_id(row): row for row in new_rows + updated_rows}
            all_rows = [row_by_id[obj_id] for obj_id in obj_ids]
            if return_id:
                return [mapper.get_row_id(x) for x in all_rows]
            return self.from_sql(model_class, all_rows)

        retval: list[Model] | list[Hashable] = self._execute_sa(
            session, _execute, kwargs
        )
        return retval

    @staticmethod
    def _get_existing_upsert_ids(
        session: Session,
        obj_ids: list[Hashable],
        row_id_column: Any,
        max_batch_size: int,
    ) -> set[Hashable]:
        """Query existing IDs in chunks within database parameter limits."""
        # Chunk the existence check to avoid SQL Server's 2100-parameter limit.
        existing_ids: set[Hashable] = set()
        for chunk_start in range(0, len(obj_ids), max_batch_size):
            chunk = obj_ids[chunk_start : chunk_start + max_batch_size]
            chunk_rows = session.execute(
                select(row_id_column).where(row_id_column.in_(chunk))
            ).all()
            existing_ids.update(row[0] for row in chunk_rows)
        return existing_ids

    @staticmethod
    def _insert_upsert_rows(
        session: Session, new_rows: list[Any], max_batch_size: int, flush: bool
    ) -> None:
        """Insert new SQL rows in batches."""
        n_rows = len(new_rows)
        n_batches = max(1, -(-n_rows // max_batch_size))  # ceiling division
        for batch_index in range(n_batches):
            row_slice = slice(
                batch_index * max_batch_size,
                min((batch_index + 1) * max_batch_size, n_rows),
            )
            session.add_all(new_rows[row_slice])
            if flush:
                session.flush()

    def _update_upsert_rows(
        self,
        session: Session,
        mapper: BaseSAMapper,
        user_id: Hashable,
        existing_objs: list[Model],
        max_batch_size: int,
        optimize_parameter_handling: bool,
        flush: bool,
    ) -> list[Any]:
        """Update existing SQL rows in parameter-safe chunks."""
        if not existing_objs:
            return []
        existing_obj_ids = [mapper.get_id(obj) for obj in existing_objs]
        all_rows: list[Any] = []
        all_row_ids: list[Hashable] = []
        # Update existing objects in chunks to avoid SQL Server's 2100-parameter limit.
        for chunk_start in range(0, len(existing_obj_ids), max_batch_size):
            chunk_ids = existing_obj_ids[chunk_start : chunk_start + max_batch_size]
            chunk_rows, chunk_row_ids = SARepository._in_session_read_some(
                mapper,
                session,
                chunk_ids,
                optimize_parameter_handling=optimize_parameter_handling,
                max_ids_in_clause=self._max_parameters_in_clause,
            )
            all_rows.extend(chunk_rows)
            all_row_ids.extend(chunk_row_ids)
        map_rows = dict(zip(all_row_ids, all_rows))
        for obj in existing_objs:
            row = map_rows[mapper.get_id(obj)]
            mapper.update(user_id, obj, row)
        if flush:
            session.flush()
        return all_rows

    def delete_one(
        self,
        model_class: type[Model],
        user_id: Hashable,
        row_id: Hashable,
        **kwargs: Any,
    ) -> Hashable:
        """Delete a single row by id and return that id."""
        return self.delete_some(model_class, user_id, [row_id], **kwargs)[0]

    def delete_some(
        self,
        model_class: type[Model],
        user_id: Hashable,
        row_ids: Iterable[Hashable],
        **kwargs: Any,
    ) -> list[Hashable]:
        """Delete the specified rows after confirming they exist."""
        # Check arguments
        row_ids = row_ids if isinstance(row_ids, list) else list(row_ids)
        SARepository._verify_duplicate_ids(model_class, row_ids)
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        flush = kwargs.get("flush", True)
        # Delete rows
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class

        def _execute(session: Session) -> None:
            """Execute the requested value."""
            is_existing = self.exists_some(model_class, row_ids)
            if not all(is_existing):
                invalid_ids = [x for x, y in zip(row_ids, is_existing) if not y]
                invalid_ids_str = ", ".join([str(x) for x in invalid_ids])
                raise exc.InvalidIdsError(
                    "8e431d94",
                    f"{model_class} object(s) do not exist: {invalid_ids_str}",
                    ids=invalid_ids,
                )
            session.execute(
                delete(row_class).where(mapper.get_row_id_column().in_(row_ids))
            )
            if flush:
                session.flush()

        self._execute_sa(session, _execute, kwargs)
        return row_ids

    def delete_all(
        self,
        model_class: type[Model],
        user_id: Hashable,
        filter: Filter | None,
        return_id: bool = False,
        **kwargs: Any,
    ) -> list[Hashable] | None:
        """Delete all rows, optionally filtered, returning ids when requested."""
        # Check arguments
        session: Session = kwargs.get("session")  # type: ignore[assignment]
        # Delete rows
        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        obj_filter: Filter | None = kwargs.get("obj_filter", None)

        def _execute(session: Session) -> list[Hashable] | None:
            """Execute the requested value."""
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
                assert row_ids is not None
                stmt = delete(row_class).where(mapper.get_row_id_column().in_(row_ids))
                session.execute(stmt)
                return row_ids if return_id else None

            # Delete all rows
            if return_id:
                # Get ids
                row_ids = [
                    x[0]
                    for x in session.execute(select(mapper.get_row_id_column())).all()
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
        """Return True if the row for the given id exists."""
        return self.exists_some(model_class, [obj_id], **kwargs)[0]

    def exists_some(
        self, model_class: type[Model], obj_ids: Iterable[Hashable], **kwargs: Any
    ) -> list[bool]:
        """Return a per-id existence flag list in the same order as obj_ids."""
        session: Session = kwargs.get("session")  # type: ignore[assignment]

        mapper = self.get_mapper(model_class)
        row_class = mapper.row_class
        SARepository._verify_duplicate_ids(model_class, obj_ids)

        def _execute(session: Session) -> list[bool]:
            """Execute the requested value."""
            row_id_col = mapper.get_row_id_column()
            rows: Sequence = session.execute(
                select(row_id_col).where(row_id_col.in_(obj_ids))
            ).all()
            found_obj_ids = {x[0] for x in rows}
            is_existing_obj = [x in found_obj_ids for x in obj_ids]
            return is_existing_obj

        retval: list[bool] = self._execute_sa(session, _execute, kwargs)
        return retval

    def read_fields(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable | None,
        model_class: type[Model],
        field_names: list[str],
        filter: Filter | None = None,
        **kwargs: Any,
    ) -> Iterable[tuple[Any, ...]]:
        """Read a projection of specific fields, optionally filtered."""
        if not isinstance(uow, SAUnitOfWork):
            raise exc.RepositoryServiceError("4afb32de", f"Invalid UnitOfWork: {uow}")
        mapper = self.get_mapper(model_class)
        field_name_map = mapper.get_field_name_map()
        row_field_names = [field_name_map[x] for x in field_names]
        row_class = mapper.row_class

        def _execute(session: Session) -> Iterable[tuple[Any, ...]]:
            """Execute the requested value."""
            stmt = select(*[getattr(row_class, x) for x in row_field_names])
            if filter:
                # Convert filter to where clause and add to statement
                stmt = stmt.where(
                    self.get_where_clause_from_filter(row_class, mapper, filter)
                )
            for row in session.execute(stmt):
                yield tuple(row)

        retval: Iterable[tuple[Any, ...]] = self._execute_sa(
            uow.session, _execute, kwargs
        )
        return retval

    def split_filter(
        self, model_class: type[Model], filter: Filter | None
    ) -> tuple[Filter | None, Filter | None]:
        """Split a filter into a SQL where-clause part and a Python remainder."""
        if not filter:
            return None, None
        field_name_map = self.get_mapper(model_class).get_field_name_map()
        return self._split_filter_recursion(field_name_map, filter)

    def get_where_clause_from_filter(
        self,
        row_class: type,
        mapper: BaseSAMapper | None,
        filter: Filter,
        column_function_map: dict[str, Callable] | None = None,
    ) -> Any:
        """Recursively convert a Filter tree to a SQLAlchemy where-clause."""
        column_function_map = column_function_map or {}
        if isinstance(filter, CompositeFilter):
            return self._get_composite_where_clause(row_class, mapper, filter)
        result_column = self._get_filter_column(
            row_class, mapper, filter, column_function_map
        )
        invert = filter.invert
        if (
            isinstance(filter, StringSetFilter)
            or isinstance(filter, NumberSetFilter)
            or isinstance(filter, UuidSetFilter)
        ):
            return self._get_set_where_clause(filter, result_column, invert)
        if isinstance(filter, ExistsFilter):
            return result_column != None if not invert else result_column == None
        if isinstance(filter, EqualsFilter):
            return (
                result_column == filter.value
                if not invert
                else result_column != filter.value
            )
        if isinstance(filter, RangeFilter):
            return self._get_range_where_clause(filter, result_column, invert)
        raise exc.InvalidArgumentsError(
            "880a6446", f"Unsupported filter type: {filter.__class__.__name__}"
        )

    def _get_composite_where_clause(
        self,
        row_class: type,
        mapper: BaseSAMapper | None,
        filter: CompositeFilter,
    ) -> Any:
        """Convert a composite filter and apply its inversion."""
        args = [
            self.get_where_clause_from_filter(row_class, mapper, sub_filter)
            for sub_filter in filter.filters
        ]
        if filter.operator == LogicalOperator.AND:
            clause = sa.and_(*args)
        elif filter.operator == LogicalOperator.OR:
            clause = sa.or_(*args)
        else:
            raise exc.InvalidArgumentsError(
                "8f411a53", f"Unsupported filter operator: {filter.operator.value}"
            )
        return sa.not_(clause) if filter.invert else clause

    @staticmethod
    def _get_filter_column(
        row_class: type,
        mapper: BaseSAMapper | None,
        filter: Filter,
        column_function_map: dict[str, Callable],
    ) -> Any:
        """Resolve a domain filter key to its SQLAlchemy column or expression."""
        filter_key = str(filter.get_key())
        if mapper is None:
            # Row field name assumed as filter key
            row_field_name = filter_key
        else:
            row_field_name = mapper.get_mapped_field_name(filter_key)
        if row_field_name is None:
            raise exc.InvalidArgumentsError(
                "320f2bf7",
                f"Filter key '{filter.get_key()}' cannot be mapped to a row field name",
            )
        column = getattr(row_class, row_field_name)
        column_function = column_function_map.get(row_field_name)
        return column_function(column) if column_function else column

    @staticmethod
    def _get_set_where_clause(
        filter: StringSetFilter | NumberSetFilter | UuidSetFilter,
        column: Any,
        invert: bool,
    ) -> Any:
        """Build an IN predicate, converting Enum members when needed."""
        members = filter.members
        # Handle Enum types by converting the members to the corresponding Enum values
        enum_class = getattr(column.type, "enum_class", None)
        if enum_class is not None:
            members = frozenset(enum_class(value) for value in members)
        clause = column.in_(members)
        return sa.not_(clause) if invert else clause

    @staticmethod
    def _get_range_where_clause(filter: RangeFilter, column: Any, invert: bool) -> Any:
        """Build lower and upper range predicates, including inversion."""
        args = []
        if filter.lower_bound is not None:
            if filter.lower_bound_censor == ComparisonOperator.GT:
                args.append(column > filter.lower_bound)
            elif filter.lower_bound_censor == ComparisonOperator.GTE:
                args.append(column >= filter.lower_bound)
        if filter.upper_bound is not None:
            if filter.upper_bound_censor == ComparisonOperator.ST:
                args.append(column < filter.upper_bound)
            elif filter.upper_bound_censor == ComparisonOperator.STE:
                args.append(column <= filter.upper_bound)
        if len(args) == 1:
            return sa.not_(args[0]) if invert else args[0]
        clause = sa.and_(*args)
        return sa.not_(clause) if invert else clause

    def _split_filter_recursion(
        self, field_name_map: dict[str, str], filter: Filter
    ) -> tuple[Filter | None, Filter | None]:
        """
        Recursively partition a filter into a SQL-expressible subtree and
        a remainder to be evaluated in Python.

        """
        if not isinstance(filter, CompositeFilter):
            return self._split_leaf_filter(field_name_map, filter)
        if filter.operator == LogicalOperator.OR:
            return self._split_or_filter(field_name_map, filter)
        if filter.operator == LogicalOperator.AND:
            return self._split_and_filter(field_name_map, filter)
        # Filter cannot be converted due to unsupported operator
        return None, filter

    def _split_leaf_filter(
        self, field_name_map: dict[str, str], filter: Filter
    ) -> tuple[Filter | None, Filter | None]:
        """Map a supported leaf filter to its SQL model field."""
        map_key_only_classes = (
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
        )
        mapped_key = field_name_map.get(str(filter.get_key()))
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

    def _split_or_filter(
        self, field_name_map: dict[str, str], filter: CompositeFilter
    ) -> tuple[Filter | None, Filter | None]:
        """Push an OR filter to SQL only when every branch is translatable."""
        where_clause_filters: list[Filter] = []
        for sub_filter in filter.filters:
            where_clause_filter, remainder_filter = self._split_filter_recursion(
                field_name_map, sub_filter
            )
            if remainder_filter is not None or where_clause_filter is None:
                return None, filter
            where_clause_filters.append(where_clause_filter)
        return (
            CompositeFilter(filters=where_clause_filters, operator=LogicalOperator.OR),
            None,
        )

    def _split_and_filter(
        self, field_name_map: dict[str, str], filter: CompositeFilter
    ) -> tuple[Filter | None, Filter | None]:
        """Split SQL-compatible and Python-only branches of an AND filter."""
        where_clause_filters: list[Filter] = []
        remainder_filters: list[Filter] = []
        for sub_filter in filter.filters:
            where_clause_filter, remainder_filter = self._split_filter_recursion(
                field_name_map, sub_filter
            )
            if where_clause_filter:
                where_clause_filters.append(where_clause_filter)
            if remainder_filter:
                remainder_filters.append(remainder_filter)
        return (
            self._combine_and_filters(where_clause_filters),
            self._combine_and_filters(remainder_filters),
        )

    @staticmethod
    def _combine_and_filters(filters: list[Filter]) -> Filter | None:
        """Return no filter, the sole filter, or an AND composite as appropriate."""
        if not filters:
            return None
        if len(filters) == 1:
            return filters[0]
        return CompositeFilter(filters=filters, operator=LogicalOperator.AND)

    def print_db_content(self, model_class: type[Model], **kwargs: Any) -> None:
        """Helper method for debugging."""
        header = kwargs.get("header", "")
        mapper = self.get_mapper(model_class)
        tables_classes = [
            mapper.row_class,
        ]
        row_sets: list[list[Model]] = []
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

    def verify_valid_ids(
        self,
        uow: BaseUnitOfWork,
        user_id: Hashable,
        model_class: type[Model],
        obj_ids: Iterable[Hashable],
        verify_exists: bool = True,
        verify_duplicate: bool = True,
    ) -> None:
        """Verify that obj_ids are unique and/or exist in the database."""
        # Check arguments
        if not verify_exists and not verify_duplicate:
            return
        if not isinstance(obj_ids, list):
            obj_ids = list(obj_ids)
        obj_ids_set = set(obj_ids)
        if verify_duplicate and len(obj_ids) != len(obj_ids_set):
            seen = set()
            duplicate_obj_ids = [
                x for x in obj_ids if x in seen or seen.add(x)  # type: ignore[func-returns-value]
            ]
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
    def create_unique_values_temp_table(
        session: Session,
        metadata: sa.MetaData,
        col_name: str,
        col_type: sa.types.TypeEngine,
        values: list[uuid.UUID],
        max_insert_batch_size: int = DEFAULT_MAX_INSERT_BATCH_SIZE,
        table_name: str | None = None,
    ) -> sa.Table:
        """
        Create an SQL temp table with a single columns with unique values. This can be
        used e.g. to optimize queries with filters on many values or where otherwise a
        size limit would be exceeded.

        IN() on uniqueidentifier FK columns via pyodbc raises ODBC 07002
        regardless of list size; a temp-table JOIN avoids the parameter
        binding entirely.

        The table_name parameter can be used to specify a name for the temp table and
        must not contain a "#" prefix. If not provided, a random name will be generated.
        """
        if not table_name:
            temp_table_name = f"#{uuid.uuid4().hex}"
        elif isinstance(table_name, str):
            if table_name.startswith("#"):
                raise ValueError("table_name must not contain a '#' prefix")
            temp_table_name = f"#{table_name}"
        dialect = session.get_bind().dialect
        col_sql = col_type.compile(dialect=dialect)
        temp_table = sa.Table(
            temp_table_name,
            metadata,
            sa.Column(col_name, col_type),
        )
        session.execute(
            sa.text(f"CREATE TABLE {temp_table_name} ({col_name} {col_sql})")
        )
        batch_size = max_insert_batch_size
        for i in range(0, len(values), batch_size):
            insert_values = [{col_name: x} for x in values[i : i + batch_size]]
            session.execute(sa.insert(temp_table), insert_values)
            session.flush()
        return temp_table

    @staticmethod
    def _select_with_id_join(
        mapper: BaseSAMapper,
        session: Session,
        obj_ids: list[Hashable],
        max_ids_in_clause: int = DEFAULT_MAX_PARAMETERS_IN_CLAUSE,
    ) -> sa.sql.Select:
        """Build a SELECT restricted to the given ids via a temp-table JOIN.

        Avoids ODBC 07002 errors on MSSQL for UNIQUEIDENTIFIER IN() queries.
        Falls back to a plain IN() clause on non-MSSQL dialects.
        """
        row_class = mapper.row_class
        table = cast(sa.Table, row_class.__table__)  # type: ignore[attr-defined]
        id_col = mapper.get_row_id_column()
        dialect = session.get_bind().dialect
        if dialect.name != "mssql":
            # Non-mssql dialects (e.g. SQLite) don't have the ODBC 07002
            # IN() / UNIQUEIDENTIFIER bind issue — fall back to a plain
            # IN() filter so optimize_parameter_handling=True is safe in
            # tests and on other backends.
            return select(row_class).where(id_col.in_(obj_ids))

        # TODO: check if temp table exists and take a different name in that case
        temp_table_name = f"#temp_{str(uuid.uuid4()).replace('-', '_')}"
        id_col_name = id_col.name
        id_datatype = table.c[id_col_name].type
        id_datatype_sql = id_datatype.compile(dialect=dialect)
        # TODO: finalize this part
        # Create the temp table
        # we might think to introspect after CREATE TABLE, but that opens us up to session/database sync and lock issues...
        # which we did experience in testing
        temp_table_obj = sa.Table(
            temp_table_name, row_class.metadata, sa.Column(id_col_name, id_datatype)  # type: ignore[attr-defined]
        )
        session.execute(
            sa.text(f"CREATE TABLE {temp_table_name} ({id_col_name} {id_datatype_sql})")
        )
        # session.flush()  # need to be able to introspect!
        # temp_table_obj = sa.Table(temp_table_name, row_class.metadata, autoload_with=session.get_bind().engine)
        # hard-coded batch size; MS SQL Server limit is 2,100; we just use something reasonable
        # no urgent need to turn hard-coding into a parameter as this is dialect-specific issues
        # handled in dialect-specific code
        batch_size = max_ids_in_clause
        for i in range(0, len(obj_ids), batch_size):
            oid_batch = obj_ids[i : i + batch_size]
            values = [{id_col_name: x} for x in oid_batch]
            session.execute(sa.insert(temp_table_obj), values)
            session.flush()

        # Select with join to restrict to ids passed (mssql temp-table path)
        sql_select: sa.sql.Select = select(row_class).join(
            temp_table_obj,
            table.c[id_col_name] == temp_table_obj.c[id_col_name],
        )
        return sql_select

    @staticmethod
    def _in_session_read_some(
        mapper: BaseSAMapper,
        session: Session,
        obj_ids: list[Hashable],
        optimize_parameter_handling: bool = False,
        max_ids_in_clause: int = DEFAULT_MAX_PARAMETERS_IN_CLAUSE,
    ) -> tuple[list[Any], list[Hashable]]:
        """
        :param optimize_parameter_handling: if True, avoid parameterized query that using SQL's IN that is
           more many parameters nonperformant by creating and joining with a temporary table instead
           default = False, but possibly recommend to set dynamically based on number of parameters
        """
        # n = len(obj_ids)
        # Get rows as list[(Row,)], convert to list[Row]
        row_class = mapper.row_class
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
                mapper, session, obj_ids, max_ids_in_clause=max_ids_in_clause
            )
        else:
            sql_select = select(row_class).where(
                mapper.get_row_id_column().in_(obj_ids)
            )

        rows = session.execute(sql_select).all()
        rows = [x[0] for x in rows]
        # Further process rows
        row_ids = [mapper.get_row_id(x) for x in rows]
        SARepository._in_session_verify_retrieved_ids(mapper, obj_ids, row_ids)
        return rows, row_ids

    def _execute_sa(self, session: Session, execute_fn: Callable, kwargs: dict) -> Any:
        """Run execute_fn in the given session, or open a fresh UoW session."""
        if session:
            retval = execute_fn(session)
        else:
            with self.uow(**kwargs) as uow:
                assert isinstance(uow, SAUnitOfWork)
                retval = execute_fn(uow.session)
        return retval

    @staticmethod
    def _in_session_verify_retrieved_ids(
        mapper: BaseSAMapper,
        obj_ids: list[Hashable],
        row_ids: list[Hashable],
        table_name: str | None = None,
    ) -> None:
        """Raise InvalidIdsError if fewer rows were returned than requested."""
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
        """Raise DuplicateIdsError if obj_ids contains duplicates."""
        if not isinstance(obj_ids, list) and not isinstance(obj_ids, set):
            obj_ids = list(obj_ids)
        seen = set()
        duplicate_ids = [
            x for x in obj_ids if x in seen or seen.add(x)  # type: ignore[func-returns-value]
        ]
        if not duplicate_ids:
            return
        duplicate_ids_str = ", ".join([str(x) for x in duplicate_ids])
        raise exc.DuplicateIdsError(
            "bba17339",
            f"Model {model_class.__name__}: object ids are not unique: {duplicate_ids_str}",
            ids=duplicate_ids,
        )

    @classmethod
    def create_sa_repository(
        cls,
        entities: list[Entity],
        connection_string: str | None = None,
        **kwargs: Any,
    ) -> "SARepository":
        """
        Create an SARepository and its database engine.

        When connection_string is None, an in-memory SQLite database will be created. When
        connection_string is provided, it will be used to create the engine. SQLite
        repositories retain their convenient automatic schema setup. Other databases
        are migration-managed by default; pass ``create_database_objects=True`` only
        for explicit bootstrap tooling.
        """
        # Parse arguments
        echo = kwargs.pop("echo", False)
        register_mappers = kwargs.pop("register_mappers", True)
        recreate_sqlite_file = kwargs.pop("recreate_sqlite_file", False)

        # Handle sqlite separately
        is_sqlite = connection_string is None or str(
            connection_string
        ).lower().startswith("sqlite:///")
        create_database_objects = kwargs.pop("create_database_objects", is_sqlite)
        schema_names = {x.schema_name for x in entities if x.persistable}
        if is_sqlite:
            engine = cls._create_sqlite_engine(
                connection_string, schema_names, echo, recreate_sqlite_file
            )
        else:
            if connection_string is None:
                raise ValueError(
                    "connection_string must be provided for non-sqlite databases"
                )
            connect_args = kwargs.pop("connect_args", None)
            engine = cls._create_non_sqlite_engine(
                connection_string,
                schema_names,
                echo,
                create_database_objects,
                connect_args,
            )

        metadata_set = cls._get_repository_metadata(entities)

        # Create any non-existing database objects except schemas (done earlier), if allowed
        if create_database_objects:
            for metadata in metadata_set:
                metadata.create_all(engine, checkfirst=True)

        # Create repository
        repository = cls(
            engine, entities=entities, register_mappers=register_mappers, **kwargs
        )

        return repository

    @staticmethod
    def _create_sqlite_engine(
        connection_string: str | None,
        schema_names: set[str | None],
        echo: bool,
        recreate_sqlite_file: bool,
    ) -> Engine:
        """Create a SQLite engine and attach its configured schemas."""
        sqlite_target = (
            None
            if connection_string is None
            else re.sub(".*sqlite:///", "", connection_string, flags=re.IGNORECASE)
        )
        if sqlite_target:
            sqlite_target_lower = sqlite_target.lower()
            is_memory_target = sqlite_target_lower == ":memory:" or (
                sqlite_target_lower.startswith("file:")
                and "mode=memory" in sqlite_target_lower
            )
        else:
            is_memory_target = True
            # Create random connection string for shared in-memory sqlite database,
            # so that multiple SARepository instances created in this way will not
            # share the same database. This is important e.g. for testing, where
            # multiple tests may create their own SARepository instances.
            sqlite_target = f"file:{uuid.uuid4()}?mode=memory&cache=shared&uri=true"
            sqlite_target_lower = sqlite_target.lower()
            connection_string = f"sqlite:///{sqlite_target}"

        sqlite_file: Path | None = None
        if is_memory_target:
            if sqlite_target_lower.startswith("file:"):
                # SQLAlchemy forwards URI parameters from the URL to sqlite3.
                if "uri=" not in sqlite_target_lower:
                    sqlite_target = f"{sqlite_target}&uri=true"
                    connection_string = f"sqlite:///{sqlite_target}"
        else:
            sqlite_file = Path(sqlite_target)
            if recreate_sqlite_file:
                # Remove existing file
                if sqlite_file.is_file():
                    sqlite_file.unlink()
            elif not sqlite_file.is_file():
                raise ValueError(
                    "Unable to derive file from connection string or file does not exist"
                )

        warnings.filterwarnings(
            "ignore",
            r"^Dialect sqlite\+pysqlite does not support updated rowcount.*",
            SAWarning,
        )
        assert connection_string is not None
        engine = sa.create_engine(connection_string, echo=echo)

        # Make sure foreign key constraints are enforced, which is not the default.
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
            """Set sqlite pragma."""
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # Unique per repository so schemas in separate repositories do not collide
        # in SQLite's process-wide shared cache.
        memory_schema_namespace = uuid.uuid4().hex
        with engine.connect() as conn:
            for schema_name in schema_names:
                if not schema_name or schema_name == "main":
                    continue
                if is_memory_target:
                    attach_target = (
                        f"file:{schema_name}_{memory_schema_namespace}"
                        "?mode=memory&cache=shared&uri=true"
                    )
                else:
                    if len(schema_names) > 1:
                        valid_schema_names = [
                            name for name in schema_names if name is not None
                        ]
                        raise NotImplementedError(
                            "Multiple schemas: " + ", ".join(sorted(valid_schema_names))
                        )
                    assert sqlite_file is not None
                    attach_target = sqlite_file.as_posix()
                conn.execute(
                    sa.text(f"attach database '{attach_target}' as '{schema_name}';")
                )
        return engine

    @staticmethod
    def _create_non_sqlite_engine(
        connection_string: str,
        schema_names: set[str | None],
        echo: bool,
        create_database_objects: bool,
        connect_args: dict[str, Any] | None,
    ) -> Engine:
        """Create a non-SQLite engine and any requested database schemas."""
        engine = EngineFactory.create_engine(
            connection_string, echo, connect_args=connect_args
        )
        if create_database_objects:
            for schema_name in schema_names:
                if not schema_name:
                    continue
                with engine.connect() as conn:
                    if not conn.dialect.has_schema(conn, schema_name):
                        conn.execute(sa.schema.CreateSchema(schema_name))
                        conn.commit()
        return engine

    @staticmethod
    def _get_repository_metadata(entities: list[Entity]) -> set[sa.MetaData]:
        """Validate persistable entities and collect their SQLAlchemy metadata."""
        metadata_set: set[sa.MetaData] = set()
        for entity in entities:
            # Retrieve metadata
            if not entity.persistable:
                continue
            db_model_class = entity.db_model_class
            if not db_model_class:
                raise ValueError(
                    f"Entity {entity.name} is persistable but does not have a db_model_class"
                )
            metadata_set.add(cast(sa.MetaData, getattr(db_model_class, "metadata")))
        return metadata_set

    @classmethod
    def test_connection(
        cls,
        connection_string: str,
        **kwargs: Any,
    ) -> Exception | None:
        """
        Try to open a database connection; return None on success or the
        exception on failure.

        """
        try:
            connection = sa.create_engine(
                connection_string,
                connect_args=kwargs,
            ).connect()
            connection.close()
            return None
        except Exception as exception:
            # Connection failed, skip loading
            return exception
