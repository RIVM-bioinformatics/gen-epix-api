"""Shared app and reference-data fixtures for SEQDB sample upload tests."""

import copy
import logging
from test.seqdb.integration.upload_samples.ref_data import (
    SeqUploadRefData,
    create_ref_data,
)
from test.seqdb.seqdb_test_client import SeqdbTestClient
from test.test_client.enum import EnumTestType
from test.test_client.pytest_params import BuildDbParams
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.seqdb.domain import command, enum, model

TEST_TYPE = EnumTestType.SEQDB_INTEGRATION_UPLOAD_SAMPLES
APP_CFGS = get_app_cfgs(
    AppType.SEQDB, enum.ServiceType, enum.RepositoryType, TEST_TYPE, log_any=False
)
PARAMS = [
    BuildDbParams(True, DevRepositoryConfig.SA_SQLITE_EMPTY),
    BuildDbParams(False, DevRepositoryConfig.SA_SQLITE_EMPTY),
    BuildDbParams(True, DevRepositoryConfig.DICT_EMPTY),
    BuildDbParams(False, DevRepositoryConfig.DICT_EMPTY),
]


@pytest.fixture(scope="package", params=PARAMS, ids=[p.id for p in PARAMS])
def env(request: pytest.FixtureRequest) -> SeqdbTestClient:
    params: BuildDbParams = request.param
    # Repository file paths are changed in place when each test client is created.
    app_cfg = copy.deepcopy(
        APP_CFGS[f"{TEST_TYPE.value}__{params.dev_repository_config.value}"]
    )
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    return SeqdbTestClient.get_test_client(  # type: ignore[return-value]
        test_type=app_cfg.name,
        app_cfg=app_cfg,
        log_level=logging.ERROR,
        use_endpoints=not params.skip_endpoints,
    )


@pytest.fixture(scope="package")
def ref_data(env: SeqdbTestClient) -> SeqUploadRefData:
    return create_ref_data(env)


@pytest.fixture(scope="package")
def allele_ref_data(env: SeqdbTestClient) -> tuple[UUID, UUID]:
    user = env.get_root_user()
    locus: model.Locus = env.app.handle(
        command.LocusCrudCommand(
            user=user,
            operation=CrudOperation.CREATE_ONE,
            objs=model.Locus(code=f"locus_{uuid4().hex}"),
        )
    )
    assert locus.id is not None
    locus_set: model.LocusSet = env.app.handle(
        command.LocusSetCrudCommand(
            user=user,
            operation=CrudOperation.CREATE_ONE,
            objs=model.LocusSet(
                code=f"locus_set_{uuid4().hex}",
                name=f"Test locus set {uuid4().hex}",
                locus_ids=[locus.id],
            ),
        )
    )
    assert locus_set.id is not None
    protocol: model.Protocol = env.app.handle(
        command.ProtocolCrudCommand(
            user=user,
            operation=CrudOperation.CREATE_ONE,
            objs=model.Protocol(
                code=f"allele_protocol_{uuid4().hex}",
                protocol_type=enum.ProtocolType.SEQ_PROFILE,
                seq_profile_type=enum.SeqProfileType.ALLELE,
                locus_set_id=locus_set.id,
            ),
        )
    )
    assert protocol.id is not None
    return locus.id, protocol.id
