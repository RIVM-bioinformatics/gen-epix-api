"""Reusable repository and service contract tests for operational-data resets."""

from datetime import date, datetime
from functools import partial
from importlib import import_module
from test.util.mock_compat import Mock
from types import SimpleNamespace
from typing import Annotated, Any
from uuid import UUID

import pytest
import sqlalchemy as sa
from fastapi import APIRouter, Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy_utils import UUIDType

from gen_epix.commondb.api.exc import handle_exception
from gen_epix.commondb.domain.command import DeleteOperationalDataCommand
from gen_epix.commondb.domain.enum import FeatureFlag
from gen_epix.commondb.domain.model import User
from gen_epix.fastapp import App, exc

ROW_ID = UUID(int=1)
FLAG = FeatureFlag.ALLOW_DELETE_OPERATIONAL_DATA.value


def _column_value(column: sa.Column) -> Any:
    """Supply valid storage values without invoking unrelated upload validation."""
    if isinstance(column.type, UUIDType):
        return ROW_ID
    if isinstance(column.type, sa.Enum):
        return (
            list(column.type.enum_class)[0]
            if column.type.enum_class
            else column.type.enums[0]
        )
    if isinstance(column.type, sa.JSON):
        return {}
    if isinstance(column.type, sa.DateTime):
        return datetime(2024, 1, 1)
    if isinstance(column.type, sa.Date):
        return date(2024, 1, 1)
    if isinstance(column.type, sa.Boolean):
        return True
    if isinstance(column.type, (sa.Integer, sa.Numeric, sa.Float)):
        return 1
    if isinstance(column.type, sa.LargeBinary):
        return b"test"
    return "test"


class BaseOperationalDataTests:
    """Encapsulates backend parity, rollback, dependency, and HTTP reset tests.

    Subclasses declare the app and independent expected operational model names.
    Storage fixtures populate every mapped table, including preserved tables.
    """

    APP_NAME: str
    SERVICE_NAME: str
    EXPECTED_MODELS: set[str]

    @pytest.fixture
    def modules(self):
        """Load the app's real models, repositories, service, and router factory."""
        base = f"gen_epix.{self.APP_NAME}"
        return SimpleNamespace(
            domain=import_module(f"{base}.domain").DOMAIN,
            model=import_module(f"{base}.domain.model"),
            enum=import_module(f"{base}.domain.enum"),
            sa_model=import_module(f"{base}.repositories.sa_model"),
            dict_class=getattr(
                import_module(f"{base}.repositories.{self.SERVICE_NAME}_dict"),
                f"{self.SERVICE_NAME.title()}DictRepository",
            ),
            sa_class=getattr(
                import_module(f"{base}.repositories.{self.SERVICE_NAME}_sa"),
                f"{self.SERVICE_NAME.title()}SARepository",
            ),
            service_class=getattr(
                import_module(f"{base}.services.{self.SERVICE_NAME}.service"),
                f"{self.SERVICE_NAME.title()}Service",
            ),
            role_generator=import_module(
                f"{base}.domain.policy.permission"
            ).RoleGenerator,
            rbac_class=import_module(f"{base}.services.rbac").RbacService,
            create_endpoints=getattr(
                import_module(f"{base}.api.{self.SERVICE_NAME}"),
                f"create_{self.SERVICE_NAME}_endpoints",
            ),
        )

    @pytest.fixture(params=["dict", "sqlite"])
    def repository(self, modules, request):
        """Create an isolated populated backend and enable SQLite FK enforcement."""
        entities = [x for x in modules.domain.entities if x.persistable]
        if request.param == "dict":
            db = {
                x.model_class: {ROW_ID: x.model_class.model_construct()}
                for x in entities
            }
            yield modules.dict_class(entities, db)
            return
        repository = modules.sa_class.create_sa_repository(entities)
        engine = repository._engine
        tables = [
            repository.get_mapper(x.model_class).row_class.__table__ for x in entities
        ]
        # Seed all tables before enabling FKs: metadata contains cross-schema and
        # optional cycles unrelated to reset ordering. Every referenced ID is 1.
        with engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
            for table in tables:
                values = {
                    column.name: _column_value(column)
                    for column in table.columns
                    if column.primary_key
                    or column.foreign_keys
                    or (not column.nullable and column.server_default is None)
                }
                connection.execute(table.insert().values(**values))
        with engine.connect() as connection:
            connection.exec_driver_sql("PRAGMA foreign_keys=ON")
            assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
        try:
            yield repository
        finally:
            engine.dispose()

    @staticmethod
    def snapshot(repository, modules):
        """Capture contents of every table to detect unintended deletions."""
        if isinstance(repository, modules.dict_class):
            return {key: dict(value) for key, value in repository.db.items()}
        with repository.uow() as uow:
            return {
                entity.model_class: list(
                    uow.session.execute(
                        sa.select(
                            repository.get_mapper(
                                entity.model_class
                            ).row_class.__table__
                        )
                    )
                )
                for entity in modules.domain.entities
                if entity.persistable
            }

    def test_delete_and_repeat(self, repository, modules):
        """Empty every operational table while retaining every other stored row."""
        before = self.snapshot(repository, modules)
        shared_tables = (
            dict(repository.db) if isinstance(repository, modules.dict_class) else None
        )
        for _ in range(2):
            with repository.uow() as uow:
                repository.delete_operational_data(uow)
            after = self.snapshot(repository, modules)
            for model_class, rows in before.items():
                if model_class.__name__ in self.EXPECTED_MODELS:
                    assert not after[model_class], model_class.__name__
                else:
                    assert after[model_class] == rows, model_class.__name__
        if shared_tables is not None:
            for model_class, table in shared_tables.items():
                assert repository.db[model_class] is table
            for model_class in modules.model.OPERATIONAL_MODELS:
                repository.db[model_class].update(before[model_class])
        else:
            with repository.uow() as uow:
                for model_class in reversed(modules.model.OPERATIONAL_MODELS):
                    table = repository.get_mapper(model_class).row_class.__table__
                    uow.session.execute(
                        table.insert(),
                        [dict(row._mapping) for row in before[model_class]],
                    )
        assert self.snapshot(repository, modules) == before

    def test_failure_restores_tables(self, repository, modules, monkeypatch):
        """A failure after the first deletion restores all operational records."""
        before = self.snapshot(repository, modules)
        if isinstance(repository, modules.dict_class):

            class FailingTable(dict):
                """Inject a clearing failure after another table was emptied."""

                def clear(self):
                    """Fail during deletion to exercise snapshot restoration."""
                    raise exc.RepositoryServiceError(
                        "test", "injected deletion failure"
                    )

            second = modules.model.OPERATIONAL_MODELS[1]
            repository.db[second] = FailingTable(repository.db[second])
            with pytest.raises(exc.RepositoryServiceError):
                with repository.uow() as uow:
                    repository.delete_operational_data(uow)
        else:
            with pytest.raises(exc.RepositoryServiceError):
                with repository.uow() as uow:
                    execute = uow.session.execute
                    calls = 0

                    def fail_second(*args, **kwargs):
                        """Fail after the first statement has reached the database."""
                        nonlocal calls
                        calls += 1
                        if calls == 2:
                            raise exc.RepositoryServiceError(
                                "test", "injected deletion failure"
                            )
                        return execute(*args, **kwargs)

                    monkeypatch.setattr(uow.session, "execute", fail_second)
                    repository.delete_operational_data(uow)
        assert self.snapshot(repository, modules) == before

    def test_model_scope_and_dependency_order(self, modules):
        """Explicit deletion scope covers inbound domain and mapped SQL links."""
        models = modules.model.OPERATIONAL_MODELS
        assert {x.__name__ for x in models} == self.EXPECTED_MODELS
        assert len(models) == len(self.EXPECTED_MODELS)
        positions = {model: index for index, model in enumerate(models)}
        for entity in modules.domain.entities:
            if not entity.persistable:
                continue
            for link in entity.links.values():
                if link.link_model_class not in positions:
                    continue
                assert entity.model_class in positions, entity.model_class.__name__
                if entity.model_class != link.link_model_class:
                    assert (
                        positions[entity.model_class] < positions[link.link_model_class]
                    )
        mappings = {
            model: row
            for group in modules.sa_model.SA_MODELS_BY_SERVICE_TYPE.values()
            for model, row in group.items()
        }
        table_positions = {
            mappings[model].__table__: pos for model, pos in positions.items()
        }
        for row in mappings.values():
            table = row.__table__
            for fk in table.foreign_keys:
                parent = fk.column.table
                if parent in table_positions and parent != table:
                    assert table in table_positions, table.name
                    assert table_positions[table] < table_positions[parent]

    @pytest.mark.parametrize("enabled", [None, False, True])
    def test_service_and_endpoint(self, modules, enabled):
        """The real service enforces the flag even for authorized direct calls."""
        generator = modules.role_generator
        user = User(
            id=ROW_ID,
            key="reset@example.org",
            email="reset@example.org",
            organization_id=ROW_ID,
            is_active=True,
            roles={modules.enum.Role.ROOT.value},
        )

        def get_user():
            """Return the authenticated root user."""
            return user

        app = App(
            domain=modules.domain,
            impl=SimpleNamespace(
                role_map=generator.get_role_map(),
                role_set_map=generator.get_role_set_map(),
                registered_user_dependency=Annotated[User, Depends(get_user)],
            ),
        )
        repository = Mock()
        repository.uow.return_value.__enter__ = Mock(return_value=Mock())
        repository.uow.return_value.__exit__ = Mock(return_value=False)
        service_type = modules.enum.ServiceType[self.SERVICE_NAME.upper()]
        modules.service_class(app, service_type=service_type, repository=repository)
        assert (
            modules.domain.get_service_type_for_command(DeleteOperationalDataCommand)
            == service_type
        )
        rbac = modules.rbac_class(app, service_type=modules.enum.ServiceType.RBAC)
        rbac.register_roles(
            generator.get_role_permissions_map(), modules.enum.Role.ROOT.value
        )
        rbac.register_policies()
        if enabled is not None:
            app.set_feature_flag(FLAG, enabled)
        cmd = DeleteOperationalDataCommand(user=user)
        if enabled:
            assert app.handle(cmd) is None
        else:
            with pytest.raises(exc.FeatureDisabledServiceError):
                app.handle(cmd)
            repository.delete_operational_data.assert_not_called()
        api = FastAPI()
        router = APIRouter()
        modules.create_endpoints(
            router, app, handle_exception=partial(handle_exception, app, None)
        )
        api.include_router(router, prefix="/v1")
        assert ("/v1/operational_data" in api.openapi()["paths"]) == bool(enabled)
        with TestClient(api) as client:
            assert client.delete("/v1/operational_data").status_code == (
                204 if enabled else 404
            )
            if enabled:
                repository.delete_operational_data.reset_mock()
                app.set_feature_flag(FLAG, False)
                assert client.delete("/v1/operational_data").status_code == 503
                repository.delete_operational_data.assert_not_called()
