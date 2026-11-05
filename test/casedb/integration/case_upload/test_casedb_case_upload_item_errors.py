"""Integration test: one bad case in an upload no longer keeps the others out.

Runs UploadCasesCommand against DICT and SQLite CASEDB apps, so the whole upload path
is exercised: verification, merged-content validation, upsert and storage. With
fail_batch_on_item_error=False the cases that pass verification are stored even
when another case in the same batch fails. A case fails here by
carrying a value for a column that does not exist.
"""

import copy
import logging
from dataclasses import dataclass
from test.casedb.casedb_test_client import CasedbTestClient as Env
from test.test_client.enum import EnumTestType
from test.test_client.pytest_params import BuildDbParams
from uuid import UUID, uuid4

import pytest

from gen_epix.casedb.domain import command, enum, model
from gen_epix.commondb.domain.enum import (
    AppType,
    DevRepositoryConfig,
    UploadAction,
)
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp import CrudOperation
from gen_epix.seqdb.domain import enum as seqdb_enum

TEST_TYPE = EnumTestType.CASEDB_INTEGRATION_CASE_UPLOAD_ITEM_ERRORS

SEQDB_APP_CFGS = get_app_cfgs(
    AppType.SEQDB,
    seqdb_enum.ServiceType,
    seqdb_enum.RepositoryType,
    TEST_TYPE,
)
CASEDB_APP_CFGS = get_app_cfgs(
    AppType.CASEDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    seqdb_app_cfgs=SEQDB_APP_CFGS,
)


@dataclass(frozen=True)
class RefData:
    """The reference data the tests upload cases against."""

    root_user: model.User
    case_type_id: UUID
    col_id: UUID
    data_collection_id: UUID


_PARAMS = [
    BuildDbParams(True, DevRepositoryConfig.SA_SQLITE_EMPTY),
    BuildDbParams(True, DevRepositoryConfig.DICT_EMPTY),
]


@pytest.fixture(scope="module", name="env", params=_PARAMS, ids=[p.id for p in _PARAMS])
def get_test_client(request: pytest.FixtureRequest) -> Env:
    params: BuildDbParams = request.param
    cfg_key = f"{TEST_TYPE.value}__{params.dev_repository_config.value}"
    app_cfg = copy.copy(CASEDB_APP_CFGS[cfg_key])
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    app_cfg.cfg["service"]["seqdb"]["props"]["local_client"]["app_cfg"] = (
        SEQDB_APP_CFGS[cfg_key]
    )
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=app_cfg.name,
        app_cfg=app_cfg,
        log_level=logging.ERROR,
        use_endpoints=not params.skip_endpoints,
    )


@pytest.fixture(scope="module", name="ref_data")
def create_ref_data(env: Env) -> RefData:
    """Create one CaseType with a single TEXT Col, and a data collection."""
    root_user = env.get_root_user()
    env.set_obj(root_user)
    env.create_disease(root_user, "disease_1")
    env.create_etiological_agent(root_user, "etiological_agent_1")
    case_type = env.create_case_type(
        root_user, "case_type1", "disease_1", "etiological_agent_1"
    )
    env.create_ref_dim(root_user, "ref_dim1", enum.DimType.TEXT)
    env.create_ref_col(root_user, "ref_col1_1", enum.ColType.TEXT)
    env.create_dim(root_user, "dim1_1_1")
    col = env.create_col(root_user, "col1_1_1_1")
    data_collection = env.create_data_collection(root_user, "data_collection1")
    assert case_type.id and col.id and data_collection.id
    return RefData(root_user, case_type.id, col.id, data_collection.id)


def _case_for_upload(
    ref_data: RefData, value: str, case_id: UUID | None = None, is_bad: bool = False
) -> model.CaseForUpload:
    """A case with ``value`` in the Col; a bad case also has a value for an unknown Col."""
    content: dict[UUID, str | None] = {ref_data.col_id: value}
    if is_bad:
        content[uuid4()] = "value for a column that does not exist"
    return model.CaseForUpload(
        case=model.Case(
            id=case_id,
            case_type_id=ref_data.case_type_id,
            created_in_data_collection_id=ref_data.data_collection_id,
            content=content,
        )
    )


def _upload(
    env: Env,
    ref_data: RefData,
    cases: list[model.CaseForUpload],
    fail_batch_on_item_error: bool,
) -> model.CaseBatchUploadResult:
    return env.handle(  # type: ignore[no-any-return]
        command.UploadCasesCommand(
            user=ref_data.root_user,
            case_type_id=ref_data.case_type_id,
            on_exists=UploadAction.UPDATE.value,  # type: ignore[call-arg]
            case_batch=model.CaseBatchForUpload(cases=cases),
            fail_batch_on_item_error=fail_batch_on_item_error,  # type: ignore[call-arg]
        )
    )


def _stored_values(env: Env, ref_data: RefData) -> dict[UUID, str | None]:
    """Map each stored case's id to its value in the Col."""
    cases: list[model.Case] = env.app.handle(
        command.CaseCrudCommand(
            user=ref_data.root_user,
            operation=CrudOperation.READ_ALL,
        )
    )
    return {x.id: x.content.get(ref_data.col_id) for x in cases}  # type: ignore[misc]


def _new_values(run_id: str) -> list[str]:
    return [f"item_error_{run_id}_{i}" for i in range(3)]


class TestOneBadCaseFailsOnItsOwn:
    """A case that fails verification is left out; the other cases are stored."""

    def test_good_new_cases_are_stored(self, env: Env, ref_data: RefData) -> None:
        values = _new_values(uuid4().hex[:8])
        cases = [
            _case_for_upload(ref_data, value, is_bad=i == 1)
            for i, value in enumerate(values)
        ]

        batch_result = _upload(env, ref_data, cases, fail_batch_on_item_error=False)

        assert [x.status for x in batch_result.cases] == [
            EtlStatus.CREATED,
            EtlStatus.FAILED,
            EtlStatus.CREATED,
        ]
        stored_values = set(_stored_values(env, ref_data).values())
        assert values[0] in stored_values
        assert values[1] not in stored_values
        assert values[2] in stored_values
        assert batch_result.status == EtlStatus.FAILED
        assert batch_result.has_log_code("c0f70912")

    def test_default_stores_nothing(self, env: Env, ref_data: RefData) -> None:
        values = _new_values(uuid4().hex[:8])
        cases = [
            _case_for_upload(ref_data, value, is_bad=i == 1)
            for i, value in enumerate(values)
        ]

        batch_result = _upload(env, ref_data, cases, fail_batch_on_item_error=True)

        stored_values = set(_stored_values(env, ref_data).values())
        assert not stored_values.intersection(values)
        assert batch_result.has_log_code("02095f22")

    def test_failed_existing_case_keeps_its_stored_content(
        self, env: Env, ref_data: RefData
    ) -> None:
        """An update to a good existing case is stored; a bad one changes nothing."""
        old_values = _new_values(uuid4().hex[:8])[:2]
        create_result = _upload(
            env,
            ref_data,
            [_case_for_upload(ref_data, value) for value in old_values],
            fail_batch_on_item_error=True,
        )
        case_ids = [x.id for x in create_result.cases]
        assert all(x is not None for x in case_ids)
        new_values = _new_values(uuid4().hex[:8])[:2]

        batch_result = _upload(
            env,
            ref_data,
            [
                _case_for_upload(ref_data, new_values[0], case_id=case_ids[0]),
                _case_for_upload(
                    ref_data, new_values[1], case_id=case_ids[1], is_bad=True
                ),
            ],
            fail_batch_on_item_error=False,
        )

        assert [x.status for x in batch_result.cases] == [
            EtlStatus.UPDATED,
            EtlStatus.FAILED,
        ]
        stored_values = _stored_values(env, ref_data)
        assert stored_values[case_ids[0]] == new_values[0]  # type: ignore[index]
        assert stored_values[case_ids[1]] == old_values[1]  # type: ignore[index]
