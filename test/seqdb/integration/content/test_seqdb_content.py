"""Integration tests for SeqDB operational content."""

import logging
from test.seqdb.seqdb_test_client import SeqdbTestClient as Env
from test.test_client.enum import EnumTestType

import pytest

from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import command, enum

TEST_TYPE = EnumTestType.SEQDB_INTEGRATION_CONTENT
APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    """Create a SeqDB client backed by the demo dictionary repository."""
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=APP_CFGS[f"{TEST_TYPE.value}__{DevRepositoryConfig.DICT_DEMO.value}"],
        log_level=logging.ERROR,
        use_endpoints=False,
    )


class TestContent:
    """Exercise and clean up SeqDB operational content."""

    def test_content(self, env: Env) -> None:
        """Read demo content, then delete all declared operational models."""
        root_user = env.get_root_user()
        assert env.handle(
            command.SampleCrudCommand(
                user=root_user,
                operation=CrudOperation.READ_ALL,
            )
        )

        result = env.handle(command.DeleteAllOperationalDataCommand(user=root_user))

        assert result.success, {
            key: value[:300]
            for key, value in result.details.items()
            if isinstance(value, str)
        }
        assert set(result.details) == {
            model_class.ENTITY.name
            for model_class in command.DeleteAllOperationalDataCommand.SORTED_OPERATIONAL_DATA_MODEL_CLASSES
        }
        assert (
            env.handle(
                command.SampleCrudCommand(
                    user=root_user,
                    operation=CrudOperation.READ_ALL,
                )
            )
            == []
        )
