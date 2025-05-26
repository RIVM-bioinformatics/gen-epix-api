from test.fastapp.command import (
    Model1_1CrudCommand,
    Model1_2CrudCommand,
    Model2_1CrudCommand,
    Model2_2CrudCommand,
)
from test.fastapp.enum import TestType as EnumTestType  # to avoid PyTest warning
from test.fastapp.model import Model1_1, Model1_2, Model2_1, Model2_2
from test.fastapp.service_test_client import ServiceTestClient as Env

import pytest

from gen_epix.fastapp.enum import CrudOperation
from gen_epix.fastapp.repositories.dict.repository import DictRepository
from gen_epix.fastapp.repositories.sa.repository import SARepository


def get_test_clients() -> list[Env]:
    envs = [
        Env.get_test_client(
            DictRepository, test_type=EnumTestType.SERVICE_SERVICE_UNIT_REPOSITORY
        ),
        Env.get_test_client(
            SARepository, test_type=EnumTestType.SERVICE_SERVICE_UNIT_REPOSITORY
        ),
    ]
    return envs


@pytest.mark.parametrize(
    "env",
    get_test_clients(),
)
class TestRepository:

    def test_to_from_sql(self, env: Env) -> None:
        props = [
            (Model1_1, env.repository1),
            (Model1_2, env.repository1),
            (Model2_1, env.repository2),
            (Model2_2, env.repository2),
        ]
        for model_class, repository in props:
            model_instance = env.get_model_instance_for_class(model_class)
            if isinstance(repository, SARepository):
                row = repository.to_sql(env.user_ids[0], model_class, model_instance)
                model_converted = repository.from_sql(model_class, row)
            elif isinstance(repository, DictRepository):
                # Not applicable
                model_converted = model_instance
            else:
                raise NotImplementedError
            assert model_instance == model_converted

    def test_create_one(self, env: Env) -> None:
        model1_1 = env.get_model_instance_for_class(Model1_1, set_id=False)
        model1_1_created = env.app.handle(
            Model1_1CrudCommand(objs=model1_1, operation=CrudOperation.CREATE_ONE)
        )
        assert model1_1 == model1_1_created

        model1_2 = env.get_model_instance_for_class(Model1_2, set_id=False)
        model1_2.model1_1_id = model1_1_created.id
        model1_2_created = env.app.handle(
            Model1_2CrudCommand(objs=model1_2, operation=CrudOperation.CREATE_ONE)
        )
        assert model1_2 == model1_2_created

        model2_1 = env.get_model_instance_for_class(Model2_1, set_id=False)
        model2_1.model1_2_id = model1_2_created.id
        model2_1_created = env.app.handle(
            Model2_1CrudCommand(objs=model2_1, operation=CrudOperation.CREATE_ONE)
        )
        assert model2_1 == model2_1_created

        model2_2 = env.get_model_instance_for_class(Model2_2, set_id=False)
        model2_2.model2_1_id = model2_1_created.id
        model2_2_created = env.app.handle(
            Model2_2CrudCommand(objs=model2_2, operation=CrudOperation.CREATE_ONE)
        )
        assert model2_2 == model2_2_created

    def test_create_some(self, env: Env) -> None:
        env.create_all_model_instances()

    def test_read(self, env: Env) -> None:
        models1_1, models1_2, models2_1, models2_2 = env.create_all_model_instances()
        # Read one, read some and read all without cascade
        # 1_1
        model1_1_read = env.app.handle(
            Model1_1CrudCommand(
                obj_ids=models1_1[0].id, operation=CrudOperation.READ_ONE
            )
        )
        assert models1_1[0] == model1_1_read
        models1_1_read = env.app.handle(
            Model1_1CrudCommand(
                obj_ids=[x.id for x in models1_1], operation=CrudOperation.READ_SOME
            )
        )
        assert all([x == y for x, y in zip(models1_1, models1_1_read)])
        models1_1_read_all = env.app.handle(
            Model1_1CrudCommand(operation=CrudOperation.READ_ALL)
        )
        models1_1_read_all = {x.id: x for x in models1_1_read_all}
        assert all([x == models1_1_read_all[x.id] for x in models1_1])
        # 1_2
        model1_2_read = env.app.handle(
            Model1_2CrudCommand(
                obj_ids=models1_2[0].id, operation=CrudOperation.READ_ONE
            )
        )
        assert models1_2[0] == model1_2_read
        models1_2_read = env.app.handle(
            Model1_2CrudCommand(
                obj_ids=[x.id for x in models1_2], operation=CrudOperation.READ_SOME
            )
        )
        assert all([x == y for x, y in zip(models1_2, models1_2_read)])
        model1_2_read_all = env.app.handle(
            Model1_2CrudCommand(operation=CrudOperation.READ_ALL)
        )
        model1_2_read_all = {x.id: x for x in model1_2_read_all}
        assert all([x == model1_2_read_all[x.id] for x in models1_2])
        # 2_1
        model2_1_read = env.app.handle(
            Model2_1CrudCommand(
                obj_ids=models2_1[0].id, operation=CrudOperation.READ_ONE
            )
        )
        assert models2_1[0] == model2_1_read
        models2_1_read = env.app.handle(
            Model2_1CrudCommand(
                obj_ids=[x.id for x in models2_1], operation=CrudOperation.READ_SOME
            )
        )
        assert all([x == y for x, y in zip(models2_1, models2_1_read)])
        model2_1_read_all = env.app.handle(
            Model2_1CrudCommand(operation=CrudOperation.READ_ALL)
        )
        model2_1_read_all = {x.id: x for x in model2_1_read_all}
        assert all([x == model2_1_read_all[x.id] for x in models2_1])
        # 2_2
        model2_2_read = env.app.handle(
            Model2_2CrudCommand(
                obj_ids=models2_2[0].id, operation=CrudOperation.READ_ONE
            )
        )
        assert models2_2[0] == model2_2_read
        models2_2_read = env.app.handle(
            Model2_2CrudCommand(
                obj_ids=[x.id for x in models2_2], operation=CrudOperation.READ_SOME
            )
        )
        assert all([x == y for x, y in zip(models2_2, models2_2_read)])
        model2_2_read_all = env.app.handle(
            Model2_2CrudCommand(operation=CrudOperation.READ_ALL)
        )
        model2_2_read_all = {x.id: x for x in model2_2_read_all}
        assert all([x == model2_2_read_all[x.id] for x in models2_2])

    def test_read_cascade(self, env: Env) -> None:
        models1_1, models1_2, models2_1, models2_2 = env.create_all_model_instances(
            cascade=True
        )
        # Read with cascade
        props = {"cascade_read": True}
        # 1_1
        model1_1_read = env.app.handle(
            Model1_1CrudCommand(
                obj_ids=models1_1[0].id, operation=CrudOperation.READ_ONE, props=props
            )
        )
        assert models1_1[0] == model1_1_read
        models1_1_read = env.app.handle(
            Model1_1CrudCommand(
                obj_ids=[x.id for x in models1_1],
                operation=CrudOperation.READ_SOME,
                props=props,
            )
        )
        assert all([x == y for x, y in zip(models1_1, models1_1_read)])
        models1_1_read_all = env.app.handle(
            Model1_1CrudCommand(operation=CrudOperation.READ_ALL, props=props)
        )
        models1_1_read_all = {x.id: x for x in models1_1_read_all}
        assert all([x == models1_1_read_all[x.id] for x in models1_1])
        # 1_2
        model1_2_read = env.app.handle(
            Model1_2CrudCommand(
                obj_ids=models1_2[0].id, operation=CrudOperation.READ_ONE, props=props
            )
        )
        assert models1_2[0] == model1_2_read
        models1_2_read = env.app.handle(
            Model1_2CrudCommand(
                obj_ids=[x.id for x in models1_2],
                operation=CrudOperation.READ_SOME,
                props=props,
            )
        )
        assert all([x == y for x, y in zip(models1_2, models1_2_read)])
        model1_2_read_all = env.app.handle(
            Model1_2CrudCommand(operation=CrudOperation.READ_ALL, props=props)
        )
        model1_2_read_all = {x.id: x for x in model1_2_read_all}
        assert all([x == model1_2_read_all[x.id] for x in models1_2])
        # 2_1
        model2_1_read = env.app.handle(
            Model2_1CrudCommand(
                obj_ids=models2_1[0].id, operation=CrudOperation.READ_ONE, props=props
            )
        )
        assert models2_1[0] == model2_1_read
        models2_1_read = env.app.handle(
            Model2_1CrudCommand(
                obj_ids=[x.id for x in models2_1],
                operation=CrudOperation.READ_SOME,
                props=props,
            )
        )
        assert all([x == y for x, y in zip(models2_1, models2_1_read)])
        model2_1_read_all = env.app.handle(
            Model2_1CrudCommand(operation=CrudOperation.READ_ALL, props=props)
        )
        model2_1_read_all = {x.id: x for x in model2_1_read_all}
        assert all([x == model2_1_read_all[x.id] for x in models2_1])
        # 2_2
        model2_2_read = env.app.handle(
            Model2_2CrudCommand(
                obj_ids=models2_2[0].id, operation=CrudOperation.READ_ONE, props=props
            )
        )
        assert models2_2[0] == model2_2_read
        models2_2_read = env.app.handle(
            Model2_2CrudCommand(
                obj_ids=[x.id for x in models2_2],
                operation=CrudOperation.READ_SOME,
                props=props,
            )
        )
        assert all([x == y for x, y in zip(models2_2, models2_2_read)])
        model2_2_read_all = env.app.handle(
            Model2_2CrudCommand(operation=CrudOperation.READ_ALL, props=props)
        )
        model2_2_read_all = {x.id: x for x in model2_2_read_all}
        assert all([x == model2_2_read_all[x.id] for x in models2_2])
