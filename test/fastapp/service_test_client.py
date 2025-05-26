import os
from test.fastapp.command import (
    Model1_1CrudCommand,
    Model1_2CrudCommand,
    Model2_1CrudCommand,
    Model2_2CrudCommand,
)
from test.fastapp.enum import ServiceType
from test.fastapp.model import Base1, Base2, Model1_1, Model1_2, Model2_1, Model2_2
from test.fastapp.service import Service1, Service2
from test.fastapp.user_manager import UserManager
from test.fastapp.util import get_test_name, get_test_root_output_dir
from typing import Hashable, Type
from uuid import UUID

from gen_epix.fastapp import Entity, model
from gen_epix.fastapp.app import App
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.model import Model
from gen_epix.fastapp.repositories import SARepository
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repository import BaseRepository
from gen_epix.fastapp.service import BaseService


class ServiceTestClient:

    TEST_CLIENTS = {}

    @classmethod
    def get_test_client(cls, repository_class: Type[BaseRepository], **kwargs: dict):
        key = (kwargs.get("test_type", repository_class.__name__), repository_class)
        if key not in cls.TEST_CLIENTS:
            cls.TEST_CLIENTS[key] = cls(repository_class, **kwargs)
        return cls.TEST_CLIENTS[key]

    def __init__(self, repository_class: Type[BaseRepository], **kwargs: dict) -> None:
        self.test_type = kwargs.get("test_type", repository_class.__name__)
        self.test_name = kwargs.get("test_name", get_test_name(self.test_type))
        self.test_dir = os.path.join(get_test_root_output_dir(), self.test_name)
        os.makedirs(self.test_dir, exist_ok=True)
        self.repository_type = kwargs.get("repository_type", repository_class.__name__)
        self.user_manager = kwargs.pop("user_manager", UserManager())
        self.app = App(user_manager=self.user_manager, **kwargs)
        for model_class in [Model1_1, Model1_2, Model2_1, Model2_2]:
            entity: Entity = model_class.ENTITY
            if entity.has_model():
                if entity.model_class is not model_class:
                    raise ValueError("Model class mismatch")
            else:
                entity.set_model_class(model_class)
            self.app.domain.register_entity(entity)
        self.service1 = Service1(self.app, service_type=ServiceType.SERVICE1)
        self.service2 = Service2(self.app, service_type=ServiceType.SERVICE2)
        self.repository1 = self.create_repository(
            repository_class, self.service1, base=Base1
        )
        self.repository2 = self.create_repository(
            repository_class, self.service2, base=Base2
        )
        self.service1.repository = self.repository1
        self.service2.repository = self.repository2

        model_ids = {
            Model1_1: [
                UUID("a0dd3426-2f90-413f-b675-679006ff922e"),
                UUID("21f0d84b-f7d8-42d5-89f7-a41c8c755e5a"),
                UUID("0082d0dd-7e96-49f1-985c-d008a450ccd8"),
            ],
            Model1_2: [
                UUID("0f979e3d-66e1-45ba-bf8c-53338e42ed8a"),
                UUID("a03c7ab3-bbe8-47e7-b364-234852e60f83"),
                UUID("73df7ed1-6168-4466-ace7-ec0add6693eb"),
            ],
            Model2_1: [
                UUID("1d0d1b15-9c4a-4701-ad1e-a471828b77b5"),
                UUID("644b49be-4e31-4189-a74e-5886b8c5b84e"),
                UUID("51c6d96e-154e-4d50-9467-0ce148969097"),
            ],
            Model2_2: [
                UUID("6e9e0b7a-46bf-4ecb-a1c1-095730a56232"),
                UUID("a2f860fc-4bbd-43ed-82ef-cb6e16e85b31"),
                UUID("ff9b7532-5e90-42a8-ba5c-9b413bb5d513"),
            ],
        }
        self.df: dict[Type[Model], dict[Hashable, Model]] = {}
        self.df[Model1_1] = {
            x: Model1_1(id=x, var1=i, var2=f"{i}")
            for i, x in enumerate(model_ids[Model1_1])
        }
        self.df[Model1_2] = {
            x: Model1_2(id=x, var1=i, var2=f"{i}", model1_1_id=model_ids[Model1_1][i])
            for i, x in enumerate(model_ids[Model1_2])
        }
        self.df[Model2_1] = {
            x: Model2_1(id=x, var1=i, var2=f"{i}", model1_2_id=model_ids[Model1_2][i])
            for i, x in enumerate(model_ids[Model2_1])
        }
        self.df[Model2_2] = {
            x: Model2_2(
                id=x,
                var1=i,
                var2=f"{i}",
                var3={
                    "e1678e61-526e-4262-b048-17b8ae7f9bb3": "1566b7b4-d686-4492-ad93-61da58b5fe4f",
                    "84b0d379-fae2-44b3-99cc-cb446218116e": i,
                },
                model2_1_id=model_ids[Model2_1][i],
            )
            for i, x in enumerate(model_ids[Model2_2])
        }
        self.user_ids = [
            UUID("f6d0d5d3-5f4f-4b7e-9f7c-1f5c7b5e4d6f"),
            UUID("b3c1e4c6-1b7b-4b2e-8e6e-7c0c7f7b2d8c"),
            UUID("b7e8f4f1-4b1b-4b7e-9f7c-1f5c7b5e4d6f"),
            UUID("b7805518-7a2a-4cef-a299-0bce03d55fb0"),
            UUID("46882e93-a78c-43cc-b6db-a0d292783ba2"),
            UUID("77833e2f-0961-4846-888f-533867c1e03b"),
        ]

    def create_repository(
        self,
        repository_class: Type[BaseRepository],
        service: BaseService,
        **kwargs: dict,
    ) -> BaseRepository:
        name = service.name
        entities = service.app.domain.get_dag_sorted_entities(
            service_type=service.service_type
        )
        model_classes = [x.model_class for x in entities]
        if issubclass(repository_class, DictRepository):
            repository = DictRepository(entities, {}, missing_data="ignore")
        elif issubclass(repository_class, SARepository):
            sqlite_file = os.path.join(self.test_dir, f"{name}.sqlite")
            connection_string = f"sqlite:///{sqlite_file}"
            repository = repository_class.create_sa_repository(
                entities,
                connection_string,
                create_all=True,
                recreate_sqlite_file=True,
                **kwargs,
            )
            # TODO: remove when code above is sufficiently tested
            # base = kwargs["base"]
            # schema_names = {x.ENTITY.schema_name for x in model_classes}
            # if len(schema_names) > 1:
            #     raise ValueError("Multiple schemas are not supported")
            # schema_name = schema_names.pop()

            # sqlite_file = os.path.join(self.test_dir, f"{name}.sqlite")
            # if os.path.exists(sqlite_file):
            #     os.remove(sqlite_file)

            # @sa.event.listens_for(sa.Engine, "connect")
            # def set_sqlite_pragma(dbapi_connection, _) -> None:
            #     cursor = dbapi_connection.cursor()
            #     cursor.execute("PRAGMA foreign_keys=ON")
            #     cursor.close()

            # engine = sa.create_engine("sqlite:///:memory:", echo=False)
            # # Add schema as a separate database, as sqlite does not support schemas
            # with engine.connect() as conn:
            #     conn.execute(
            #         sa.text(f"attach database '{sqlite_file}' as '{schema_name}';")
            #     )
            # repository = SARepository(engine)

            # for model_class in model_classes:
            #     mapper2 = SAMapper(model_class, MODEL_MAP[model_class])
            #     repository.register_mapper(mapper2)
            # base.metadata.create_all(engine)
        else:
            raise NotImplementedError(
                f"Repository type {repository_class.__name__} not implemented"
            )
        return repository

    def get_model_instances_for_class(
        self,
        model_class: Type[Model],
        as_dict: bool = False,
        set_id: bool = True,
    ) -> Model | dict:
        objs = list(self.df[model_class].values())
        if as_dict:
            objs = [x.model_dump(exclude=None if set_id else "id") for x in objs]
        else:
            objs = [x.model_copy() for x in objs]
            if not set_id:
                for obj in objs:
                    obj.id = None
        return objs

    def get_model_instance_for_class(
        self,
        model_class: Type[Model],
        as_dict: bool = False,
        idx: int = 0,
        set_id: bool = True,
    ) -> Model | dict:
        objs: list[Model] = list(self.df[model_class].values())
        obj = objs[idx]
        if as_dict:
            obj = obj.model_dump(exclude=None if set_id else "id")
        else:
            obj = obj.model_copy()
            if not set_id:
                obj.id = None
        return obj

    def create_all_fixture_model_instances(self, user_id: Hashable) -> None:
        models1_1 = self.df[Model1_1].values()
        with self.service1.repository.uow() as uow:
            models1_1_created = self.service1.repository.crud(
                uow, user_id, Model1_1, models1_1, None, CrudOperation.CREATE_SOME
            )
        models1_2 = self.df[Model1_2].values()
        with self.service1.repository.uow() as uow:
            models1_2_created = self.service1.repository.crud(
                uow, user_id, Model1_2, models1_2, None, CrudOperation.CREATE_SOME
            )
        models2_1 = self.df[Model2_1].values()
        with self.service2.repository.uow() as uow:
            models2_1_created = self.service2.repository.crud(
                uow, user_id, Model2_1, models2_1, None, CrudOperation.CREATE_SOME
            )
        models2_2 = self.df[Model2_2].values()
        with self.service2.repository.uow() as uow:
            models2_2_created = self.service2.repository.crud(
                uow, user_id, Model2_2, models2_2, None, CrudOperation.CREATE_SOME
            )
        return (
            models1_1_created,
            models1_2_created,
            models2_1_created,
            models2_2_created,
        )

    def create_all_model_instances(
        self, cascade: bool = False, user: model.User = None
    ) -> None:
        models1_1 = self.get_model_instances_for_class(Model1_1, set_id=False)
        models1_1_created = self.app.handle(
            Model1_1CrudCommand(
                user=user, objs=models1_1, operation=CrudOperation.CREATE_SOME
            )
        )
        assert all([x == y for x, y in zip(models1_1, models1_1_created)])

        models1_2 = self.get_model_instances_for_class(Model1_2, set_id=False)
        for i, model1_2 in enumerate(models1_2):
            model1_2.model1_1_id = models1_1_created[i].id
        models1_2_created = self.app.handle(
            Model1_2CrudCommand(
                user=user, objs=models1_2, operation=CrudOperation.CREATE_SOME
            )
        )
        assert all([x == y for x, y in zip(models1_2, models1_2_created)])

        models2_1 = self.get_model_instances_for_class(Model2_1, set_id=False)
        for i, model2_1 in enumerate(models2_1):
            model2_1.model1_2_id = models1_2_created[i].id
        models2_1_created = self.app.handle(
            Model2_1CrudCommand(
                user=user, objs=models2_1, operation=CrudOperation.CREATE_SOME
            )
        )
        assert all([x == y for x, y in zip(models2_1, models2_1_created)])

        models2_2 = self.get_model_instances_for_class(Model2_2, set_id=False)
        for i, model2_2 in enumerate(models2_2):
            model2_2.model2_1_id = models2_1_created[i].id
        models2_2_created = self.app.handle(
            Model2_2CrudCommand(
                user=user, objs=models2_2, operation=CrudOperation.CREATE_SOME
            )
        )
        assert all([x == y for x, y in zip(models2_2, models2_2_created)])
        # Fill in the back populate fields in case of cascade, to a depth of one
        if cascade:
            models1_1_dict = {x.id: x for x in models1_1}
            models1_2_dict = {x.id: x for x in models1_2}
            models2_1_dict = {x.id: x for x in models2_1}
            for model2_2 in models2_2_created:
                model2_2.model2_1 = models2_1_dict[model2_2.model2_1_id].model_copy()
            for model2_1 in models2_1_created:
                model2_1.model1_2 = models1_2_dict[model2_1.model1_2_id].model_copy()
            for model1_2 in models1_2_created:
                model1_2.model1_1 = models1_1_dict[model1_2.model1_1_id].model_copy()
        return (
            models1_1_created,
            models1_2_created,
            models2_1_created,
            models2_2_created,
        )
