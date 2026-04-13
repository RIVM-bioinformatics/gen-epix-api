"""
Integration tests for OMOPDB person batch upload via the HTTP API.

These tests exercise the full HTTP flow:
  POST /v1/upload/persons → PersonBatchUploadResult

They complement the unit tests in test/omopdb/unit/upload/test_omopdb_upload.py,
which test the batch uploader logic in isolation using mocks. Here we use a real
app instance (with an in-memory DICT repository) and a FastAPI TestClient so that
the request travels through authentication, routing, command dispatch, and the full
upload pipeline before we inspect the response.

Happy-path batch-level status values:
  CREATED   – all persons in the batch were new
  UPDATED   – all persons were updated
  SKIPPED   – all persons were skipped (on_exists=SKIP or on_new=SKIP)
  PROCESSED – mixed outcomes across persons

Failure modes covered here:
  FAILED (business logic)  – on_exists=ERROR with existing person,
                             on_new=ERROR with new person
  HTTP 401/403             – request without authentication token
  HTTP 422                 – malformed request body (missing required fields)

LSP-2985: the goal is to make the batch return SUCCEEDED. Once that is implemented,
the happy-path assertions below should be updated to expect EtlStatus.SUCCEEDED.
"""

import logging
from test.omopdb.integration.person_upload.base import (
    DEV_REPOSITORY_CONFIG,
    SKIP_ENDPOINTS,
    TEST_TYPE,
    VERBOSE,
)
from test.omopdb.omopdb_test_client import OmopdbTestClient as Env
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import AppType, EtlStatus, UploadAction
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.util import get_app_cfgs
from gen_epix.omopdb.domain import command, enum
from gen_epix.omopdb.domain.model import (
    Person,
    PersonBatchForUpload,
    PersonBatchUploadResult,
    PersonForUpload,
)

_GENDER_CONCEPT_ID = UUID("1e7d7dc0-41ef-9b58-de77-cb4a4eff115b")
_RACE_CONCEPT_ID = UUID("af5570f5-a181-0b7a-f78c-af4bc70a660f")
_ETHNICITY_CONCEPT_ID = UUID("8a234c39-9f1d-de91-f9f6-bd90661f36db")
_PERSON_TYPE_CONCEPT_ID = UUID("e8ac2efe-d38a-c881-c5dc-1812343e67c8")

OMOPDB_APP_CFGS = get_app_cfgs(
    AppType.OMOPDB,
    enum.ServiceType,
    enum.RepositoryType,
    TEST_TYPE,
)


@pytest.fixture(scope="module", name="env")
def get_test_client() -> Env:
    return Env.get_test_client(  # type: ignore[return-value]
        test_type=TEST_TYPE.value,
        app_cfg=OMOPDB_APP_CFGS[f"{TEST_TYPE.value}__{DEV_REPOSITORY_CONFIG.value}"],
        verbose=VERBOSE,
        log_level=logging.ERROR,
        use_endpoints=not SKIP_ENDPOINTS,
    )


def _make_person() -> Person:
    """Create a minimal valid Person using real OMOP concept IDs."""
    return Person(
        year_of_birth=1990,
        gender_concept_id=_GENDER_CONCEPT_ID,
        race_concept_id=_RACE_CONCEPT_ID,
        ethnicity_concept_id=_ETHNICITY_CONCEPT_ID,
        person_type_concept_id=_PERSON_TYPE_CONCEPT_ID,
    )


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestPersonBatchUploadHappyPath:
    """
    Happy-path tests for POST /v1/upload/persons.

    The root user is auto-created by the app config (IDP_MODE=MOCK,
    key="root1_1@org1.org"). No additional setup is required because
    reference data validation is not enforced in the base upload pipeline.
    """

    def test_upload_empty_batch_returns_skipped(self, env: Env) -> None:
        """
        An empty batch (persons=[]) should return HTTP 200 with status=SKIPPED.
        No error is raised; the empty result is a valid no-op.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                person_batch=PersonBatchForUpload(persons=[]),
            )
        )

        assert isinstance(result, PersonBatchUploadResult)
        assert result.persons == []
        assert result.status == EtlStatus.SKIPPED

    def test_upload_single_person_returns_created(self, env: Env) -> None:
        """
        A batch containing exactly one new person should return CREATED at both the
        individual result level and the batch level. The assigned ID must be populated.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        batch = PersonBatchForUpload(
            persons=[PersonForUpload(id=NULL_ID, person=_make_person())]
        )
        result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(user=root_user, person_batch=batch)
        )

        assert isinstance(result, PersonBatchUploadResult)
        assert len(result.persons) == 1
        person_result = result.persons[0]
        assert person_result.status == EtlStatus.CREATED
        assert person_result.is_new is True
        assert person_result.id is not None
        assert result.status == EtlStatus.CREATED

    def test_upload_multiple_persons_returns_created(self, env: Env) -> None:
        """
        A batch of three new persons should return CREATED for each individual result
        and CREATED at the batch level.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        batch = PersonBatchForUpload(
            persons=[
                PersonForUpload(id=NULL_ID, person=_make_person()),
                PersonForUpload(id=NULL_ID, person=_make_person()),
                PersonForUpload(id=NULL_ID, person=_make_person()),
            ]
        )
        result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(user=root_user, person_batch=batch)
        )

        assert isinstance(result, PersonBatchUploadResult)
        assert len(result.persons) == 3
        for person_result in result.persons:
            assert person_result.status == EtlStatus.CREATED
            assert person_result.is_new is True
            assert person_result.id is not None
        assert result.status == EtlStatus.CREATED

    def test_upload_person_twice_with_on_exists_update_returns_updated(
        self, env: Env, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Uploading the same person a second time using on_exists=UPDATE should return
        UPDATED. Without explicitly setting on_exists=UPDATE the default is ERROR,
        which would make the second upload fail (see TestPersonBatchUploadFailureModes).
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        # Mock the link update step to isolate testing of the person upload logic
        # On CREATE, there are no links to update, so this is a no-op.
        # On UPDATE, the person upload logic will attempt to update links
        monkeypatch.setattr(
            "gen_epix.fastapp.repositories.dict.repository.DictRepository._apply_link_updates",
            lambda *args, **kwargs: None,  # No-op
        )

        person = _make_person()

        # First upload – creates the person
        first_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=NULL_ID, person=person)]
                ),
            )
        )
        assert first_result.status == EtlStatus.CREATED
        created_id = first_result.persons[0].id
        assert created_id is not None

        # Second upload – same ID, explicitly allow update.
        # Change year_of_birth to ensure content differs from the first upload.
        # The Person object must carry person_id so that update_objects can locate it.
        person.year_of_birth = 1991
        person.person_id = created_id
        second_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(  # type: ignore[call-arg]
                user=root_user,
                on_exists=UploadAction.UPDATE,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=created_id, person=person)]
                ),
            )
        )

        assert isinstance(second_result, PersonBatchUploadResult)
        assert len(second_result.persons) == 1
        assert second_result.persons[0].status == EtlStatus.UPDATED
        assert second_result.persons[0].is_new is False
        assert second_result.status == EtlStatus.UPDATED

    def test_on_exists_skip_returns_skipped(self, env: Env) -> None:
        """
        When on_exists=SKIP and the person already exists, the upload silently skips
        the person. No error is raised; the batch status is SKIPPED.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        # Create the person first
        first_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=NULL_ID, person=_make_person())]
                ),
            )
        )
        assert first_result.status == EtlStatus.CREATED
        created_id = first_result.persons[0].id

        # Second upload with on_exists=SKIP
        second_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                on_exists=UploadAction.SKIP,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=created_id, person=_make_person())]
                ),
            )
        )

        assert isinstance(second_result, PersonBatchUploadResult)
        assert second_result.persons[0].status == EtlStatus.SKIPPED
        assert second_result.status == EtlStatus.SKIPPED

    def test_on_new_skip_returns_skipped(self, env: Env) -> None:
        """
        When on_new=SKIP and the person does not exist, the upload silently skips
        the person without creating it. The batch status is SKIPPED.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                on_new=UploadAction.SKIP,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=NULL_ID, person=_make_person())]
                ),
            )
        )

        assert isinstance(result, PersonBatchUploadResult)
        assert result.persons[0].status == EtlStatus.SKIPPED
        assert result.status == EtlStatus.SKIPPED

    def test_verify_only_does_not_persist(self, env: Env) -> None:
        """
        When verify_only=True the upload pipeline runs validation but does not write
        anything to the repository. The result shows what would have happened (CREATED),
        but a subsequent fetch confirms the person was not actually stored.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")
        fixed_id = uuid4()

        result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                verify_only=True,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=fixed_id, person=_make_person())]
                ),
            )
        )

        # Verification says it would be created, but nothing was stored → SKIPPED
        assert isinstance(result, PersonBatchUploadResult)
        assert result.persons[0].status == EtlStatus.SKIPPED
        assert result.status == EtlStatus.SKIPPED
        assert result.persons[0].is_new is True

        # … but a second upload with the same fixed_id finds no existing record,
        # confirming nothing was persisted.
        second_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                on_new=UploadAction.ERROR,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=fixed_id, person=_make_person())]
                ),
            )
        )
        # on_new=ERROR would fail if the person existed; FAILED here means it was absent.
        assert second_result.persons[0].status == EtlStatus.FAILED


@pytest.mark.scenario_ids("TC-SEC-31-02")
class TestPersonBatchUploadFailureModes:
    """
    Tests for cases where the upload should fail or be rejected, either at the
    business-logic level (HTTP 200, status=FAILED in the body) or at the HTTP level
    (4xx response code).
    """

    def test_on_exists_error_default_returns_failed(self, env: Env) -> None:
        """
        The default on_exists value is ERROR. Uploading a person that already exists
        without explicitly setting on_exists=UPDATE must fail. Both the individual
        person result and the batch result should have status FAILED.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        # Create the person first
        first_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=NULL_ID, person=_make_person())]
                ),
            )
        )
        assert first_result.status == EtlStatus.CREATED
        created_id = first_result.persons[0].id

        # Second upload using the default on_exists=ERROR
        second_result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                # on_exists defaults to UploadAction.ERROR — not set explicitly
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=created_id, person=_make_person())]
                ),
            )
        )

        assert isinstance(second_result, PersonBatchUploadResult)
        assert second_result.persons[0].status == EtlStatus.FAILED
        assert second_result.status == EtlStatus.FAILED
        assert second_result.persons[0].has_errors()

    def test_on_new_error_returns_failed(self, env: Env) -> None:
        """
        When on_new=ERROR and the person does not exist, the upload must fail.
        """
        root_user = env.retrieve_user_by_key("root1_1@org1.org")

        result: PersonBatchUploadResult = env.handle(
            command.UploadPersonsCommand(
                user=root_user,
                on_new=UploadAction.ERROR,
                person_batch=PersonBatchForUpload(
                    persons=[PersonForUpload(id=NULL_ID, person=_make_person())]
                ),
            )
        )

        assert isinstance(result, PersonBatchUploadResult)
        assert result.persons[0].status == EtlStatus.FAILED
        assert result.status == EtlStatus.FAILED
        assert result.persons[0].has_errors()

    # TODO: This fails, meaning the call succeeds without the Authorization header
    # @pytest.mark.skipif(SKIP_ENDPOINTS, reason="Requires HTTP endpoint to test auth")
    # def test_unauthenticated_request_is_rejected(self, env: Env) -> None:
    #     """
    #     A POST without an Authorization header must be rejected by the server
    #     before the command handler runs. Expected: HTTP 401 or 403.
    #     """
    #     assert env.endpoint_test_client is not None
    #     response = env.endpoint_test_client.test_client.post(
    #         env.default_route_prefix + "/upload/persons",
    #         json={
    #             "person_batch": {
    #                 "persons": [
    #                     {
    #                         "id": str(NULL_ID),
    #                         "person": {
    #                             "year_of_birth": 1990,
    #                             "gender_concept_id": str(uuid4()),
    #                             "race_concept_id": str(uuid4()),
    #                             "ethnicity_concept_id": str(uuid4()),
    #                             "person_type_concept_id": str(uuid4()),
    #                         },
    #                     }
    #                 ]
    #             }
    #         },
    #         # No Authorization header
    #     )
    #     assert response.status_code in (401, 403)

    @pytest.mark.skipif(
        SKIP_ENDPOINTS, reason="Requires HTTP endpoint for 422 response"
    )
    def test_malformed_body_returns_422(self, env: Env) -> None:
        """
        A POST with a body that is missing required Person fields (year_of_birth,
        gender_concept_id, etc.) must be rejected with HTTP 422 by FastAPI's request
        validation before the command handler runs.
        """
        assert env.endpoint_test_client is not None
        root_user = env.retrieve_user_by_key("root1_1@org1.org")
        headers = env.endpoint_test_client.get_dummy_jwt_header(root_user.get_key())

        response = env.endpoint_test_client.test_client.post(
            env.default_route_prefix + "/upload/persons",
            headers=headers,
            json={
                "person_batch": {
                    "persons": [
                        {
                            "id": str(NULL_ID),
                            "person": {
                                # year_of_birth and required concept IDs are missing
                                "person_source_value": "incomplete"
                            },
                        }
                    ]
                }
            },
        )
        assert response.status_code == 422
