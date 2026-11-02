"""Integration test: nothing is written for a new object that on_new=SKIP leaves out.

A person or specimen that does not exist yet and is uploaded with on_new=SKIP is not
created. Its identifiers must then not be created either: they would point to an
object that is not there, which fails the link check and with it the whole request.

Runs against SQLite rather than DICT, so that the data the uploader writes also has
to satisfy the database's foreign keys, as in production. The endpoints are not
used, since they do not work with SQLite (multi-threading).
"""

import logging
from dataclasses import dataclass
from datetime import date
from test.omopdb.omopdb_test_client import OmopdbTestClient as Env
from test.test_client.enum import EnumTestType
from typing import Any
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import AppType, DevRepositoryConfig, UploadAction
from gen_epix.commondb.domain.model.organization import IdentifierForUpload
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.etl.enum import EtlStatus
from gen_epix.fastapp.enum import CrudOperation
from gen_epix.omopdb.domain import command, enum, model

TEST_TYPE = EnumTestType.OMOPDB_INTEGRATION_PERSON_UPLOAD_SKIPPED_NEW
DEV_REPOSITORY_CONFIG = DevRepositoryConfig.SA_SQLITE_EMPTY

OMOPDB_APP_CFGS = get_app_cfgs(
    AppType.OMOPDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
    log_any=False,
)


@dataclass(frozen=True)
class RefData:
    """The user, concept and identifier issuer the tests upload persons with."""

    root_user: model.User
    concept_id: UUID
    identifier_issuer_id: UUID


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    """Return a test client on an empty SQLite repository."""
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=OMOPDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        log_level=logging.ERROR,
        use_endpoints=False,
    )


def _create(env: Env, root_user: model.User, crud_command_class: type, obj: Any) -> Any:
    return env.app.handle(
        crud_command_class(user=root_user, operation=CrudOperation.CREATE_ONE, objs=obj)
    )


@pytest.fixture(scope="module", name="ref_data")
def create_ref_data(env: Env) -> RefData:
    """Create one concept, used for every concept field, and an identifier issuer.

    The concept's domain, vocabulary and class point to concepts by id only, which
    are not checked, so they need not exist.
    """
    root_user = env.get_root_user()
    domain: model.Domain = _create(
        env,
        root_user,
        command.DomainCrudCommand,
        model.Domain(
            domain_str_id="test", domain_name="Test", domain_concept_id=uuid4()
        ),
    )
    vocabulary: model.Vocabulary = _create(
        env,
        root_user,
        command.VocabularyCrudCommand,
        model.Vocabulary(
            vocabulary_str_id="test",
            vocabulary_name="Test",
            vocabulary_concept_id=uuid4(),
        ),
    )
    concept_class: model.ConceptClass = _create(
        env,
        root_user,
        command.ConceptClassCrudCommand,
        model.ConceptClass(
            concept_class_str_id="test",
            concept_class_name="Test",
            concept_class_concept_id=uuid4(),
        ),
    )
    assert domain.domain_id is not None
    assert vocabulary.vocabulary_id is not None
    assert concept_class.concept_class_id is not None
    concept: model.Concept = _create(
        env,
        root_user,
        command.ConceptCrudCommand,
        model.Concept(
            concept_int_id=1,
            concept_name="Test",
            domain_id=domain.domain_id,
            vocabulary_id=vocabulary.vocabulary_id,
            concept_class_id=concept_class.concept_class_id,
            concept_code="test",
            valid_start_date=date(2000, 1, 1),
            valid_end_date=date(2099, 12, 31),
        ),
    )
    identifier_issuer: model.IdentifierIssuer = _create(
        env,
        root_user,
        command.IdentifierIssuerCrudCommand,
        model.IdentifierIssuer(code="test_issuer", name="Test"),
    )
    assert concept.concept_id is not None
    assert identifier_issuer.id is not None
    return RefData(root_user, concept.concept_id, identifier_issuer.id)


def _identifiers(
    ref_data: RefData, external_id: str | None
) -> list[IdentifierForUpload] | None:
    if external_id is None:
        return None
    return [
        IdentifierForUpload(
            identifier_issuer_id=ref_data.identifier_issuer_id,
            external_id=external_id,
        )
    ]


def _specimen(ref_data: RefData, external_id: str) -> model.SpecimenForUpload:
    """A specimen with a given id that does not exist yet, with one identifier."""
    return model.SpecimenForUpload(  # type: ignore[call-arg]
        specimen_id=uuid4(),
        specimen_concept_id=ref_data.concept_id,
        specimen_type_concept_id=ref_data.concept_id,
        specimen_date=date(2026, 10, 1),
        identifiers=_identifiers(ref_data, external_id),
    )


def _person_for_upload(
    ref_data: RefData,
    person_id: UUID,
    external_id: str | None = None,
    month_of_birth: int | None = None,
    specimens: list[model.SpecimenForUpload] | None = None,
) -> model.PersonForUpload:
    return model.PersonForUpload(  # type: ignore[call-arg]
        id=person_id,
        person=model.Person(
            year_of_birth=1990,
            month_of_birth=month_of_birth,
            gender_concept_id=ref_data.concept_id,
            race_concept_id=ref_data.concept_id,
            ethnicity_concept_id=ref_data.concept_id,
            person_type_concept_id=ref_data.concept_id,
        ),
        identifiers=_identifiers(ref_data, external_id),
        specimens=specimens,
    )


def _upload(
    env: Env,
    ref_data: RefData,
    persons: list[model.PersonForUpload],
    on_new: UploadAction = UploadAction.SKIP,
    fail_batch_on_item_error: bool = True,
) -> model.PersonBatchUploadResult:
    return env.handle(  # type: ignore[no-any-return]
        command.UploadPersonsCommand(
            user=ref_data.root_user,
            person_batch=model.PersonBatchForUpload(persons=persons),
            on_new=on_new,
            on_exists=UploadAction.UPDATE,
            fail_batch_on_item_error=fail_batch_on_item_error,  # type: ignore[call-arg]
        )
    )


def _create_person(env: Env, ref_data: RefData, external_id: str | None = None) -> UUID:
    """Store a new person and return its id."""
    person_id = uuid4()
    batch_result = _upload(
        env,
        ref_data,
        [_person_for_upload(ref_data, person_id, external_id)],
        on_new=UploadAction.CREATE,
    )
    assert batch_result.persons[0].status == EtlStatus.CREATED
    return person_id


def _read_all(env: Env, ref_data: RefData, crud_command_class: type) -> list:
    return env.app.handle(  # type: ignore[no-any-return]
        crud_command_class(user=ref_data.root_user, operation=CrudOperation.READ_ALL)
    )


def _stored_external_ids(
    env: Env, ref_data: RefData, crud_command_class: type
) -> set[str]:
    return {x.external_id for x in _read_all(env, ref_data, crud_command_class)}


def _external_id() -> str:
    return f"skipped_new_{uuid4().hex[:8]}"


class TestNothingIsWrittenForASkippedNewObject:
    """A new object left out by on_new=SKIP gets no identifiers written."""

    def test_identifier_of_a_skipped_new_person_is_not_stored(
        self, env: Env, ref_data: RefData
    ) -> None:
        existing_person_id = _create_person(env, ref_data)
        new_person_id = uuid4()
        new_person_external_id = _external_id()

        batch_result = _upload(
            env,
            ref_data,
            [
                _person_for_upload(ref_data, existing_person_id, month_of_birth=5),
                _person_for_upload(ref_data, new_person_id, new_person_external_id),
            ],
        )

        existing_result, new_result = batch_result.persons
        assert existing_result.status == EtlStatus.UPDATED
        assert new_result.status == EtlStatus.SKIPPED
        assert [x.status for x in new_result.identifiers or []] == [EtlStatus.SKIPPED]
        assert not batch_result.has_errors()
        persons = {
            x.person_id: x for x in _read_all(env, ref_data, command.PersonCrudCommand)
        }
        assert persons[existing_person_id].month_of_birth == 5
        assert new_person_id not in persons
        assert new_person_external_id not in _stored_external_ids(
            env, ref_data, command.PersonIdentifierCrudCommand
        )

    def test_identifier_of_a_skipped_new_specimen_is_not_stored(
        self, env: Env, ref_data: RefData
    ) -> None:
        existing_person_id = _create_person(env, ref_data)
        specimen_external_id = _external_id()

        batch_result = _upload(
            env,
            ref_data,
            [
                _person_for_upload(
                    ref_data,
                    existing_person_id,
                    specimens=[_specimen(ref_data, specimen_external_id)],
                )
            ],
        )

        specimen_results = batch_result.persons[0].specimens or []
        assert [x.status for x in specimen_results] == [EtlStatus.SKIPPED]
        assert [x.status for x in specimen_results[0].identifiers or []] == [
            EtlStatus.SKIPPED
        ]
        assert not batch_result.has_errors()
        assert specimen_external_id not in _stored_external_ids(
            env, ref_data, command.SpecimenIdentifierCrudCommand
        )

    def test_batch_stops_when_only_skipped_new_persons_are_left(
        self, env: Env, ref_data: RefData
    ) -> None:
        """A skipped new person is not work left, so one failed person stops the batch."""
        taken_external_id = _external_id()
        _create_person(env, ref_data, taken_external_id)
        new_person_id = uuid4()
        new_person_external_id = _external_id()

        batch_result = _upload(
            env,
            ref_data,
            [
                # Fails: its identifier belongs to another person
                _person_for_upload(ref_data, uuid4(), taken_external_id),
                _person_for_upload(ref_data, new_person_id, new_person_external_id),
            ],
            fail_batch_on_item_error=False,
        )

        assert [x.status for x in batch_result.persons] == [
            EtlStatus.FAILED,
            EtlStatus.SKIPPED,
        ]
        assert batch_result.has_log_code("02095f22")
        assert not batch_result.has_log_code("c0f70912")
        assert new_person_external_id not in _stored_external_ids(
            env, ref_data, command.PersonIdentifierCrudCommand
        )
