"""Integration test: one bad person in an upload no longer keeps the others out.

Runs UploadPersonsCommand through DICT HTTP and directly against SQLite, exercising
verification, upsert and storage. With fail_batch_on_item_error=False the persons
that pass verification are stored even when another person in the same batch
fails. A person fails here because its specimen carries an identifier that already
belongs to another specimen.
"""

import copy
import logging
from datetime import date
from test.omopdb.integration.person_upload.ref_data import RefData
from test.omopdb.omopdb_test_client import OmopdbTestClient as Env
from test.test_client.enum import EnumTestType
from test.test_client.pytest_params import BuildDbParams
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.omopdb.domain import command, enum, model

TEST_TYPE = EnumTestType.OMOPDB_INTEGRATION_PERSON_UPLOAD_ITEM_ERRORS
OMOPDB_APP_CFGS = get_app_cfgs(
    AppType.OMOPDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


_PARAMS = [
    BuildDbParams(True, DevRepositoryConfig.SA_SQLITE_EMPTY),
    BuildDbParams(False, DevRepositoryConfig.DICT_EMPTY),
]


@pytest.fixture(scope="module", name="env", params=_PARAMS, ids=[p.id for p in _PARAMS])
def get_test_client(request: pytest.FixtureRequest) -> Env:
    params: BuildDbParams = request.param
    app_cfg = copy.copy(
        OMOPDB_APP_CFGS[f"{TEST_TYPE.value}__{params.dev_repository_config.value}"]
    )
    app_cfg._name = f"{TEST_TYPE.value}__{params.id}"
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=app_cfg.name,
        app_cfg=app_cfg,
        log_level=logging.ERROR,
        use_endpoints=not params.skip_endpoints,
    )


def _person_for_upload(
    ref_data: RefData, specimen_external_id: str | None = None
) -> model.PersonForUpload:
    """A new person with a given id, optionally with one identified specimen."""
    specimens = None
    if specimen_external_id is not None:
        specimens = [
            model.SpecimenForUpload(  # type: ignore[call-arg]
                specimen_id=uuid4(),
                specimen_concept_id=ref_data.concept_id,
                specimen_type_concept_id=ref_data.concept_id,
                specimen_date=date(2026, 10, 1),
                identifiers=[
                    IdentifierForUpload(
                        identifier_issuer_id=ref_data.identifier_issuer_id,
                        external_id=specimen_external_id,
                    )
                ],
            )
        ]
    return model.PersonForUpload(
        id=uuid4(),
        person=model.Person(
            year_of_birth=1990,
            gender_concept_id=ref_data.concept_id,
            race_concept_id=ref_data.concept_id,
            ethnicity_concept_id=ref_data.concept_id,
            person_type_concept_id=ref_data.concept_id,
        ),
        specimens=specimens,
    )


def _upload(
    env: Env,
    ref_data: RefData,
    persons: list[model.PersonForUpload],
    fail_batch_on_item_error: bool,
) -> model.PersonBatchUploadResult:
    return env.handle(  # type: ignore[no-any-return]
        command.UploadPersonsCommand(
            user=ref_data.root_user,
            person_batch=model.PersonBatchForUpload(persons=persons),
            fail_batch_on_item_error=fail_batch_on_item_error,  # type: ignore[call-arg]
        )
    )


def _stored_person_ids(env: Env, ref_data: RefData) -> set[UUID]:
    persons: list[model.Person] = env.app.handle(
        command.PersonCrudCommand(
            user=ref_data.root_user,
            operation=CrudOperation.READ_ALL,
        )
    )
    return {x.person_id for x in persons}  # type: ignore[misc]


def _batch_with_one_taken_specimen_identifier(
    env: Env, ref_data: RefData
) -> list[model.PersonForUpload]:
    """Three new persons; the middle one's specimen reuses a stored specimen identifier."""
    taken_external_id = f"specimen_{uuid4().hex[:8]}"
    create_result = _upload(
        env,
        ref_data,
        [_person_for_upload(ref_data, taken_external_id)],
        fail_batch_on_item_error=True,
    )
    assert create_result.persons[0].status == EtlStatus.CREATED
    return [
        _person_for_upload(ref_data, f"specimen_{uuid4().hex[:8]}"),
        _person_for_upload(ref_data, taken_external_id),
        _person_for_upload(ref_data),
    ]


class TestOneBadPersonFailsOnItsOwn:
    """A person that fails verification is left out; the other persons are stored."""

    def test_good_persons_are_stored(self, env: Env, ref_data: RefData) -> None:
        persons = _batch_with_one_taken_specimen_identifier(env, ref_data)

        batch_result = _upload(env, ref_data, persons, fail_batch_on_item_error=False)

        assert [x.status for x in batch_result.persons] == [
            EtlStatus.CREATED,
            EtlStatus.FAILED,
            EtlStatus.CREATED,
        ]
        # The identifier error itself is nested under the specimen result, which the
        # endpoint response does not include, so check the failed specimen instead
        assert [x.status for x in batch_result.persons[1].specimens or []] == [
            EtlStatus.FAILED
        ]
        stored_person_ids = _stored_person_ids(env, ref_data)
        assert persons[0].id in stored_person_ids
        assert persons[1].id not in stored_person_ids
        assert persons[2].id in stored_person_ids
        assert batch_result.status == EtlStatus.FAILED
        assert batch_result.has_log_code("c0f70912")

    def test_default_stores_nothing(self, env: Env, ref_data: RefData) -> None:
        persons = _batch_with_one_taken_specimen_identifier(env, ref_data)

        batch_result = _upload(env, ref_data, persons, fail_batch_on_item_error=True)

        stored_person_ids = _stored_person_ids(env, ref_data)
        assert not stored_person_ids.intersection(x.id for x in persons)
        assert batch_result.has_log_code("02095f22")
