"""Integration test: one bad person in an upload no longer keeps the others out.

Runs UploadPersonsCommand through the HTTP endpoint against a real (DICT) OMOPDB
app, so the flag travels over the wire and the whole upload path is exercised:
verification, upsert and storage. With fail_batch_on_item_error=False the persons
that pass verification are stored even when another person in the same batch
fails. A person fails here because its specimen carries an identifier that already
belongs to another specimen, or because it changes an unchangeable field of a
stored observation (LSP-4178).
"""

import logging
from dataclasses import dataclass
from datetime import date
from test.omopdb.omopdb_test_client import OmopdbTestClient as Env
from test.test_client.enum import EnumTestType
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig, UploadAction
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.omopdb.domain import command, enum, model

TEST_TYPE = EnumTestType.OMOPDB_INTEGRATION_PERSON_UPLOAD_ITEM_ERRORS
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.DICT_EMPTY

# Concept ids are not checked against reference data by the upload
_GENDER_CONCEPT_ID = UUID("1e7d7dc0-41ef-9b58-de77-cb4a4eff115b")
_RACE_CONCEPT_ID = UUID("af5570f5-a181-0b7a-f78c-af4bc70a660f")
_ETHNICITY_CONCEPT_ID = UUID("8a234c39-9f1d-de91-f9f6-bd90661f36db")
_PERSON_TYPE_CONCEPT_ID = UUID("e8ac2efe-d38a-c881-c5dc-1812343e67c8")
_OBSERVATION_CONCEPT_ID = UUID("5c8e3a21-7d4b-4f60-8e19-2a6b9d0c4f33")
_OBSERVATION_TYPE_CONCEPT_ID = UUID("c1f09b7a-3e52-4d86-a0b8-6e4d2f9a1c55")
_SPECIMEN_CONCEPT_ID = UUID("4d7a1f0e-6b55-4c1e-9a43-0f3c2a9d8e11")
_SPECIMEN_TYPE_CONCEPT_ID = UUID("9b2e6c3d-1a7f-4e08-b5d4-7c6a2f1e0d22")

OMOPDB_APP_CFGS = get_app_cfgs(
    AppType.OMOPDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


@dataclass(frozen=True)
class RefData:
    """The user and identifier issuer the tests upload persons with."""

    root_user: model.User
    identifier_issuer_id: UUID


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    """Return a test client on an empty DICT repository that uses the endpoints."""
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=OMOPDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        log_level=logging.ERROR,
        use_endpoints=True,
    )


@pytest.fixture(scope="module", name="ref_data")
def create_ref_data(env: Env) -> RefData:
    """Create the identifier issuer for the specimen identifiers."""
    root_user = env.get_root_user()
    identifier_issuer: model.IdentifierIssuer = env.app.handle(
        command.IdentifierIssuerCrudCommand(
            user=root_user,
            operation=CrudOperation.CREATE_ONE,
            objs=model.IdentifierIssuer(code="specimen_issuer", name="Specimens"),
        )
    )
    assert identifier_issuer.id is not None
    return RefData(root_user, identifier_issuer.id)


def _person_for_upload(
    ref_data: RefData,
    specimen_external_id: str | None = None,
    person_id: UUID | None = None,
) -> model.PersonForUpload:
    """A new person with a given id, optionally with one identified specimen."""
    specimens = None
    if specimen_external_id is not None:
        specimens = [
            model.SpecimenForUpload(  # type: ignore[call-arg]
                specimen_id=uuid4(),
                specimen_concept_id=_SPECIMEN_CONCEPT_ID,
                specimen_type_concept_id=_SPECIMEN_TYPE_CONCEPT_ID,
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
        id=person_id or uuid4(),
        person=model.Person(
            year_of_birth=1990,
            gender_concept_id=_GENDER_CONCEPT_ID,
            race_concept_id=_RACE_CONCEPT_ID,
            ethnicity_concept_id=_ETHNICITY_CONCEPT_ID,
            person_type_concept_id=_PERSON_TYPE_CONCEPT_ID,
        ),
        specimens=specimens,
    )


def _upload(
    env: Env,
    ref_data: RefData,
    persons: list[model.PersonForUpload],
    fail_batch_on_item_error: bool,
    on_exists: UploadAction = UploadAction.ERROR,
) -> model.PersonBatchUploadResult:
    return env.handle(  # type: ignore[no-any-return]
        command.UploadPersonsCommand(
            user=ref_data.root_user,
            person_batch=model.PersonBatchForUpload(persons=persons),
            fail_batch_on_item_error=fail_batch_on_item_error,  # type: ignore[call-arg]
            on_exists=on_exists,  # type: ignore[call-arg]
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


def _person_with_observation(
    ref_data: RefData, person_id: UUID, observation_id: UUID, observation_date: date
) -> model.PersonForUpload:
    """A person with fixed ids and one observation on the given date."""
    person = _person_for_upload(ref_data, person_id=person_id)
    person.observations = [
        model.ObservationForUpload(  # type: ignore[call-arg]
            observation_id=observation_id,
            observation_concept_id=_OBSERVATION_CONCEPT_ID,
            observation_date=observation_date,
            observation_type_concept_id=_OBSERVATION_TYPE_CONCEPT_ID,
        )
    ]
    return person


def _batch_with_changed_observation_date(
    env: Env, ref_data: RefData
) -> list[model.PersonForUpload]:
    """A stored person re-uploaded with another observation_date, and a new person."""
    person_id, observation_id = uuid4(), uuid4()
    create_result = _upload(
        env,
        ref_data,
        [
            _person_with_observation(
                ref_data, person_id, observation_id, date(2026, 10, 1)
            )
        ],
        fail_batch_on_item_error=True,
    )
    assert create_result.persons[0].status == EtlStatus.CREATED
    return [
        _person_with_observation(
            ref_data, person_id, observation_id, date(2026, 10, 2)
        ),
        _person_for_upload(ref_data),
    ]


class TestChangedUnchangeableField:
    """Changing an unchangeable field of a stored observation fails only its person."""

    def test_other_person_is_stored(self, env: Env, ref_data: RefData) -> None:
        persons = _batch_with_changed_observation_date(env, ref_data)

        batch_result = _upload(
            env,
            ref_data,
            persons,
            fail_batch_on_item_error=False,
            on_exists=UploadAction.UPDATE,
        )

        assert batch_result.persons[0].status == EtlStatus.FAILED
        assert batch_result.persons[1].status == EtlStatus.CREATED
        assert persons[1].id in _stored_person_ids(env, ref_data)
        assert batch_result.has_log_code("c0f70912")
        assert not batch_result.has_log_code("05358e8a")

    def test_default_stores_nothing(self, env: Env, ref_data: RefData) -> None:
        persons = _batch_with_changed_observation_date(env, ref_data)

        batch_result = _upload(
            env,
            ref_data,
            persons,
            fail_batch_on_item_error=True,
            on_exists=UploadAction.UPDATE,
        )

        assert persons[1].id not in _stored_person_ids(env, ref_data)
        assert batch_result.has_log_code("02095f22")
