"""
Unit tests for omopdb person upload services.

The tests use the Person, Measurement, Observation, Specimen, and MeasurementRelation
OMOP domain models and their ForUpload derivatives, and focus on verifying the
PersonBatchUploader.

The tests mirror the generic upload scenarios from test_commondb_upload.py, adapted to
the OMOP person domain:

1 Existence of parent (Person) objects in the repository
1.1 ID not provided or NULL_ID: person does not exist and needs to be created
1.2 ID provided and is_new_id=True
1.2.1 Object with this ID does not exist: succeeds (create with that ID)
1.2.2 Object with this ID exists: error
2 Provision of child objects
2.1 Person without any child objects (no measurements, observations, specimens,
    measurement relations)
2.2 Person with measurements only
2.3 Person with observations only
2.4 Person with specimens only
2.5 Person with measurement relations only
2.6 Person with multiple child types
3 Concept ID resolution in child objects (via concept UUID or integer ID)
3.1 MeasurementForUpload with concept integer IDs resolving to existing concepts
3.2 ObservationForUpload with concept integer IDs
3.3 SpecimenForUpload with concept integer IDs
4 Parent link (person_id) in child objects
4.1 NULL_ID: person_id filled in during upload
4.2 Actual person_id matching the parent
4.2.1 Mismatch: error
4.2.2 Match: succeeds
5 External identifiers for persons
5.1 No external identifiers: succeeds
5.2 Existing external identifier resolves person ID
5.3 New external identifier created on upload
6 Upload command on_exists value
6.1 ERROR: error if any existing person
6.2 SKIP: skip existing person
6.3 UPDATE: update existing person
7 Parametrized batch sizes
7.1 Single person
7.2 Multiple persons
8 External identifiers for Specimen objects (use IdentifierType=SAMPLE for testing purposes)
8.1 No external identifiers: succeeds
8.2 One external identifier provided
8.2.1 Existing external identifier i.e. (identifier_issuer, external_id) combination exists already
8.2.1.1 Specimen ID None or NULL_ID: set specimen ID in upload result
8.2.1.2 Specimen ID provided
8.2.1.2.1 Same as existing external identifiers' specimen ID: no issue
8.2.1.2.2 Different from existing external identifiers' specimen ID: error
8.2.2 New external identifier i.e. (identifier_issuer, external_id) combination does not exist yet for this specimen: create new external identifier once specimen ID is known
8.3 Identifier issuer invalid
8.3.1 Identifier issuer ID (any except NULL_ID) provided and not found: error
8.3.2 Identifier issuer code provided and not found: error
8.3.3 Both identifier issuer ID (any except NULL_ID) and code provided and do not match: error
"""

from datetime import date, datetime, timezone
from unittest import TestCase
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from gen_epix.commondb.domain.enum import (
    IdentifierType,
    OnExistsUploadAction,
    Role,
    UploadStatus,
    UploadStatusSet,
)
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.organization import (
    ExternalIdentifier,
    ExternalIdentifierForUpload,
    IdentifierIssuer,
    User,
)
from gen_epix.commondb.domain.model.upload import UploadResult
from gen_epix.fastapp.app import App
from gen_epix.fastapp.model import ModelFieldProps
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain.command import UploadPersonsCommand
from gen_epix.omopdb.domain.model import (
    MeasurementForUpload,
    MeasurementRelationForUpload,
    ObservationForUpload,
    Person,
    PersonBatchForUpload,
    PersonBatchUploadResult,
    PersonForUpload,
    Specimen,
    SpecimenForUpload,
)
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.upload import PersonBatchUploader

# ---------------------------------------------------------------------------
# Base test case
# ---------------------------------------------------------------------------


class BasePersonUploadTestCase(TestCase):
    """Base test case with common fixtures and utilities for person upload tests."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Test user
        self.user = User(
            id=uuid4(),
            key="test@example.com",
            email="test@example.com",
            roles={Role.APP_ADMIN.value},
            organization_id=uuid4(),
            is_active=True,
        )

        # Deterministic test IDs
        self.person_id = UUID("550e8400-e29b-41d4-a716-446655440001")
        self.measurement_id = UUID("550e8400-e29b-41d4-a716-446655440002")
        self.observation_id = UUID("550e8400-e29b-41d4-a716-446655440003")
        self.specimen_id = UUID("550e8400-e29b-41d4-a716-446655440004")
        self.concept_id = UUID("550e8400-e29b-41d4-a716-446655440005")
        self.identifier_issuer_id = UUID("550e8400-e29b-41d4-a716-446655440006")
        self.identifier_issuer_id2 = UUID("550e8400-e29b-41d4-a716-446655440007")
        self.identifier_issuer_code = "test_issuer"
        self.identifier_issuer_code2 = "test_issuer2"
        self.identifier_issuer = IdentifierIssuer(
            id=self.identifier_issuer_id,
            code=self.identifier_issuer_code,
            name="Test Issuer",
        )
        self.identifier_issuer2 = IdentifierIssuer(
            id=self.identifier_issuer_id2,
            code=self.identifier_issuer_code2,
            name="Test Issuer 2",
        )
        self.random_ids = [
            UUID(f"550e8400-e29b-41d4-a716-4466554400{i:02x}")
            for i in range(0x10, 0x30)
        ]

        # Mock service (must look like BaseOmopService)
        self.service = Mock(spec=BaseOmopService)
        self.service.generate_id = Mock(side_effect=uuid4)
        self.service.repository = Mock()

        # Mock UOW context manager
        self.uow = Mock(spec=BaseUnitOfWork)
        self.uow.__enter__ = Mock(return_value=self.uow)
        self.uow.__exit__ = Mock(return_value=None)
        self.service.repository.uow.return_value = self.uow

        # Default mock return values
        self.service.repository.crud.return_value = []
        self.service.repository.read_fields.return_value = []

        # Mock app for cross-service calls
        self.service.app = Mock(spec=App)
        self.service.app.handle.return_value = []

        self.batch_uploader = PersonBatchUploader(self.service)

        # Make Person fields mutable for testing update scenarios.
        # Default ModelFieldProps(is_mutable_always=False) would reject any
        # update to fields that already have values, which is not what we want
        # to test here (upload flow, not field mutability).
        self.batch_uploader.stored_model_field_props[Person] = {
            field_name: ModelFieldProps(is_mutable_always=True)
            for field_name in Person.model_fields
        }
        self.batch_uploader.stored_model_field_props[Specimen] = {
            field_name: ModelFieldProps(is_mutable_always=True)
            for field_name in Specimen.model_fields
        }

    # -- Factory helpers -----------------------------------------------------

    def create_person(
        self,
        person_id: UUID | None = None,
        year_of_birth: int | None = 1990,
        gender_concept_id: UUID | None = None,
        race_concept_id: UUID | None = None,
        ethnicity_concept_id: UUID | None = None,
        person_type_concept_id: UUID | None = None,
        person_source_value: str | None = "src_person",
    ) -> Person:
        """Create a test Person domain model."""
        return Person(
            person_id=person_id,
            year_of_birth=year_of_birth or 0,
            gender_concept_id=gender_concept_id or uuid4(),
            race_concept_id=race_concept_id or uuid4(),
            ethnicity_concept_id=ethnicity_concept_id or uuid4(),
            person_type_concept_id=person_type_concept_id or uuid4(),
            person_source_value=person_source_value,
        )

    def create_person_for_upload(
        self,
        person_id: UUID | None = None,
        person: Person | None | object = "_DEFAULT",
        external_identifiers: list[ExternalIdentifierForUpload] | None = None,
        measurements: list[MeasurementForUpload] | None = None,
        observations: list[ObservationForUpload] | None = None,
        specimens: list[SpecimenForUpload] | None = None,
        measurement_relations: list[MeasurementRelationForUpload] | None = None,
    ) -> PersonForUpload:
        """Create a test PersonForUpload. A default Person is created unless person=None."""
        if person == "_DEFAULT":
            person = self.create_person(person_id=person_id or None)
        return PersonForUpload(
            id=person_id or NULL_ID,
            person=person,  # type: ignore[arg-type]
            external_identifiers=external_identifiers,
            measurements=measurements,
            observations=observations,
            specimens=specimens,
            measurement_relations=measurement_relations,
        )

    def get_person_from_for_upload(
        self,
        person_for_upload: PersonForUpload,
        person_id: UUID | None = None,
        year_of_birth: int | None = None,
        gender_concept_id: UUID | None = None,
        race_concept_id: UUID | None = None,
        ethnicity_concept_id: UUID | None = None,
        person_type_concept_id: UUID | None = None,
        person_source_value: str | None = "src_person",
    ) -> Person:
        """Get the Person model contained in a PersonForUpload model, with optional overrides."""
        person = person_for_upload.person
        return Person(
            person_id=person_id or person.person_id if person else None,
            year_of_birth=year_of_birth or person.year_of_birth if person else 0,
            gender_concept_id=(
                gender_concept_id or person.gender_concept_id if person else uuid4()
            ),
            race_concept_id=(
                race_concept_id or person.race_concept_id if person else uuid4()
            ),
            ethnicity_concept_id=(
                ethnicity_concept_id or person.ethnicity_concept_id
                if person
                else uuid4()
            ),
            person_type_concept_id=(
                person_type_concept_id or person.person_type_concept_id
                if person
                else uuid4()
            ),
            person_source_value=(
                person_source_value or person.person_source_value if person else None
            ),
        )

    def create_measurement_for_upload(
        self,
        measurement_id: UUID = NULL_ID,
        person_id: UUID = NULL_ID,
        measurement_concept_int_id: int = 3004249,
        measurement_type_concept_int_id: int = 32817,
        measurement_date: date | None = None,
    ) -> MeasurementForUpload:
        """Create a test MeasurementForUpload with integer concept IDs.

        Required concept UUID fields are set to valid UUIDs so that
        create_children can convert ForUpload → base model via model_dump().
        """
        return MeasurementForUpload(
            measurement_id=measurement_id,
            person_id=person_id,
            measurement_concept_id=uuid4(),
            measurement_concept_int_id=measurement_concept_int_id,
            measurement_type_concept_id=uuid4(),
            measurement_type_concept_int_id=measurement_type_concept_int_id,
            measurement_date=measurement_date or date(2024, 1, 15),
            measurement_source_concept_id=uuid4(),
            measurement_source_concept_int_id=0,
            operator_concept_int_id=0,
            value_as_concept_int_id=0,
            unit_concept_int_id=0,
        )

    def create_observation_for_upload(
        self,
        observation_id: UUID = NULL_ID,
        person_id: UUID = NULL_ID,
        observation_concept_int_id: int = 4083587,
        observation_type_concept_int_id: int = 32817,
        observation_date: date | None = None,
        observation_datetime: datetime | None = None,
    ) -> ObservationForUpload:
        """Create a test ObservationForUpload with integer concept IDs.

        Required concept UUID fields are set to valid UUIDs so that
        create_children can convert ForUpload → base model via model_dump().
        """
        return ObservationForUpload(  # type: ignore[call-arg]
            observation_id=observation_id,
            person_id=person_id,
            observation_concept_id=uuid4(),
            observation_concept_int_id=observation_concept_int_id,
            observation_type_concept_id=uuid4(),
            observation_type_concept_int_id=observation_type_concept_int_id,
            observation_date=observation_date or date(2024, 1, 15),
            observation_datetime=observation_datetime
            or datetime(2024, 1, 15, tzinfo=timezone.utc),
            observation_source_concept_id=uuid4(),
            observation_source_concept_int_id=0,
            value_as_concept_int_id=0,
            qualifier_concept_int_id=0,
            unit_concept_int_id=0,
            obs_event_field_concept_int_id=0,
        )

    def create_specimen_for_upload(
        self,
        specimen_id: UUID = NULL_ID,
        person_id: UUID = NULL_ID,
        specimen_concept_int_id: int = 4001225,
        specimen_type_concept_int_id: int = 32817,
        specimen_date: date | None = None,
        external_identifiers: list[ExternalIdentifierForUpload] | None = None,
    ) -> SpecimenForUpload:
        """Create a test SpecimenForUpload with integer concept IDs.

        Required concept UUID fields are set to valid UUIDs so that
        create_children can convert ForUpload → base model via model_dump().
        """
        return SpecimenForUpload(
            specimen_id=specimen_id,
            person_id=person_id,
            specimen_concept_id=uuid4(),
            specimen_concept_int_id=specimen_concept_int_id,
            specimen_type_concept_id=uuid4(),
            specimen_type_concept_int_id=specimen_type_concept_int_id,
            specimen_date=specimen_date or date(2024, 1, 15),
            unit_concept_int_id=0,
            anatomic_site_concept_int_id=0,
            disease_status_concept_int_id=0,
            derived_from_specimen_concept_int_id=0,
            external_identifiers=external_identifiers,  # type: ignore[call-arg]
        )

    def create_measurement_relation_for_upload(
        self,
        measurement_relation_id: UUID = NULL_ID,
        person_id: UUID = NULL_ID,
        from_measurement_id: UUID = NULL_ID,
        to_measurement_id: UUID = NULL_ID,
        measurement_relation_concept_id: UUID | None = None,
    ) -> MeasurementRelationForUpload:
        """Create a test MeasurementRelationForUpload."""
        return MeasurementRelationForUpload(
            measurement_relation_id=measurement_relation_id,
            person_id=person_id,
            from_measurement_id=from_measurement_id,
            to_measurement_id=to_measurement_id,
            measurement_relation_concept_id=(
                measurement_relation_concept_id or uuid4()
            ),
        )

    def create_command_for_persons(
        self,
        persons: list[PersonForUpload] | PersonForUpload,
        on_exists: OnExistsUploadAction = OnExistsUploadAction.UPDATE,
        validate_command: bool = True,
    ) -> UploadPersonsCommand:
        """Create a test UploadPersonsCommand."""
        if not isinstance(persons, list):
            persons = [persons]
        if validate_command:
            person_batch = PersonBatchForUpload(batch_id=uuid4(), persons=persons)  # type: ignore[call-arg]
        else:
            person_batch = PersonBatchForUpload.model_construct(
                batch_id=uuid4(), persons=persons
            )
        cmd = UploadPersonsCommand(
            user=self.user,
            person_batch=person_batch,
            on_exists=on_exists,  # type: ignore[call-arg]
        )
        return cmd

    def create_external_identifier_for_upload(
        self,
        identifier_issuer_id: UUID | None = None,
        identifier_issuer_code: str = "test_issuer",
        external_id: str = "test_external_id",
    ) -> ExternalIdentifierForUpload:
        """Create a test external identifier for upload."""
        return ExternalIdentifierForUpload(
            identifier_issuer_id=identifier_issuer_id or NULL_ID,
            identifier_issuer_code=identifier_issuer_code,
            external_id=external_id,
        )

    def get_external_identifier_from_for_upload(
        self,
        external_identifier_for_upload: ExternalIdentifierForUpload,
        internal_id: UUID,
        id: UUID | None = None,
        identifier_issuer_id: UUID | None = None,
        external_id: str | None = None,
    ) -> ExternalIdentifier:
        """Get an ExternalIdentifier from an ExternalIdentifierForUpload, with optional overrides."""
        return ExternalIdentifier(
            id=id or uuid4(),
            identifier_issuer_id=identifier_issuer_id
            or external_identifier_for_upload.identifier_issuer_id,  # type: ignore[arg-type]
            external_id=external_id or external_identifier_for_upload.external_id,
            internal_id=internal_id,
            identifier_type=IdentifierType.PERSON,
        )

    def get_specimen_external_identifier_from_for_upload(
        self,
        external_identifier_for_upload: ExternalIdentifierForUpload,
        internal_id: UUID,
        id: UUID | None = None,
        identifier_issuer_id: UUID | None = None,
        external_id: str | None = None,
    ) -> ExternalIdentifier:
        """Get the ExternalIdentifier model for Specimen, corresponding to an ExternalIdentifierForUpload model, with optional overrides."""
        return ExternalIdentifier(
            id=id or uuid4(),
            identifier_issuer_id=identifier_issuer_id
            or external_identifier_for_upload.identifier_issuer_id,  # type: ignore[arg-type]
            external_id=external_id or external_identifier_for_upload.external_id,
            internal_id=internal_id,
            identifier_type=IdentifierType.SAMPLE,
        )

    # -- Upload helper -------------------------------------------------------

    def upload_batch(
        self,
        cmd: UploadPersonsCommand | list[PersonForUpload] | PersonForUpload,
        on_exists: OnExistsUploadAction = OnExistsUploadAction.UPDATE,
        validate_command: bool = True,
    ) -> PersonBatchUploadResult:
        """Upload a batch of persons and return the upload result."""
        if isinstance(cmd, UploadPersonsCommand):
            pass
        else:
            cmd = self.create_command_for_persons(
                cmd, on_exists, validate_command=validate_command
            )
        batch_result = self.batch_uploader.upload_batch(cmd)
        return batch_result  # type: ignore[return-value]

    # -- Assertion helpers ---------------------------------------------------

    def assertBatchProcessed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.PROCESSED.value:
            self.fail(
                f"Upload was not processed, status: {upload_result.status.value}",
            )

    def assertBatchFailed(self, upload_result: UploadResult) -> None:
        if upload_result.status not in UploadStatusSet.FAILED.value:
            self.fail(
                f"Upload did not fail, status: {upload_result.status.value}",
            )

    def assertStatusCount(
        self,
        upload_result: UploadResult,
        n_skipped: int = 0,
        n_created: int = 0,
        n_updated: int = 0,
        n_failed: int = 0,
        n_pending: int = 0,
        n_processed: int = 0,
        include_self: bool = False,
    ) -> None:
        expected_status_count = {
            UploadStatus.SKIPPED: n_skipped,
            UploadStatus.CREATED: n_created,
            UploadStatus.UPDATED: n_updated,
            UploadStatus.FAILED: n_failed,
            UploadStatus.PENDING: n_pending,
            UploadStatus.PROCESSED: n_processed,
        }
        actual_status_count = upload_result.get_status_count(include_self=include_self)  # type: ignore[attr-defined]
        different_status_count = {
            (x, expected_status_count[x], actual_status_count[x])
            for x in UploadStatus
            if actual_status_count[x] != expected_status_count[x]
        }
        if different_status_count:
            different_status_count_str = ", ".join(
                f"{x[0].value} ({x[1]}/{x[2]})" for x in different_status_count
            )
            self.fail(
                f"Status count mismatch (expected/actual): {different_status_count_str}"
            )


# ---------------------------------------------------------------------------
# Test Scenario 1: Existence of person objects in the repository
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test1PersonExistence(BasePersonUploadTestCase):
    """Test scenarios related to person existence in repository."""

    def test_1_1_person_id_not_provided_creates_new_person(self) -> None:
        """Test 1.1: ID not provided or NULL_ID - person does not exist and needs to be created."""
        person_for_upload = self.create_person_for_upload()
        created_person_id = self.random_ids[0]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)
        self.assertEqual(batch_result.persons[0].id, created_person_id)

    def test_1_2_1_person_id_provided_new_id_not_exists_succeeds(self) -> None:
        """Test 1.2.1: Person with is_new_id=True and ID does not exist - should succeed."""
        person_for_upload = self.create_person_for_upload(
            person_id=self.person_id, is_new_id=True
        )
        self.service.repository.crud.side_effect = [
            [False],  # Person does not exist
            [person_for_upload.id],  # Create persons returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)
        self.assertEqual(batch_result.persons[0].id, person_for_upload.id)

    def test_1_2_2_person_id_provided_new_id_exists_fails(self) -> None:
        """Test 1.2.2: Person with is_new_id=True and ID exists - should fail."""
        person_for_upload = self.create_person_for_upload(
            person_id=self.person_id, is_new_id=True
        )
        self.service.repository.crud.side_effect = [
            [True],  # Person already exists
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1)


# ---------------------------------------------------------------------------
# Test Scenario 2: Provision of child objects
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test2ChildObjectProvision(BasePersonUploadTestCase):
    """Test scenarios related to providing different combinations of child objects."""

    def test_2_1_person_without_children(self) -> None:
        """Test 2.1: Person without any child objects."""
        person_for_upload = self.create_person_for_upload()
        created_person_id = self.random_ids[0]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)
        self.assertEqual(batch_result.persons[0].id, created_person_id)

    def test_2_2_person_with_measurements_only(self) -> None:
        """Test 2.2: Person with measurements only."""
        measurement = self.create_measurement_for_upload()
        person_for_upload = self.create_person_for_upload(measurements=[measurement])
        created_person_id = self.random_ids[0]
        created_measurement_id = self.random_ids[1]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
            [created_measurement_id],  # Create measurements returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.persons[0].id, created_person_id)
        self.assertEqual(batch_result.persons[0].measurements[0].id, created_measurement_id)  # type: ignore[index]

    def test_2_3_person_with_observations_only(self) -> None:
        """Test 2.3: Person with observations only."""
        observation = self.create_observation_for_upload()
        person_for_upload = self.create_person_for_upload(observations=[observation])
        created_person_id = self.random_ids[0]
        created_observation_id = self.random_ids[1]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
            [created_observation_id],  # Create observations returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.persons[0].id, created_person_id)
        self.assertEqual(batch_result.persons[0].observations[0].id, created_observation_id)  # type: ignore[index]

    def test_2_4_person_with_specimens_only(self) -> None:
        """Test 2.4: Person with specimens only."""
        specimen = self.create_specimen_for_upload()
        person_for_upload = self.create_person_for_upload(specimens=[specimen])
        created_person_id = self.random_ids[0]
        created_specimen_id = self.random_ids[1]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
            [created_specimen_id],  # Create specimens returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.persons[0].id, created_person_id)
        self.assertEqual(batch_result.persons[0].specimens[0].id, created_specimen_id)  # type: ignore[index]

    def test_2_5_person_with_all_child_types(self) -> None:
        """Test 2.5: Person with measurement relations only."""
        measurement_relation = self.create_measurement_relation_for_upload()
        person_for_upload = self.create_person_for_upload(
            measurement_relations=[measurement_relation],
        )
        created_person_id = self.random_ids[0]
        created_measurement_relation_id = self.random_ids[1]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
            [created_measurement_relation_id],  # Create measurement relations IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.persons[0].id, created_person_id)
        self.assertEqual(
            batch_result.persons[0].measurement_relations[0].id,  # type: ignore[index]
            created_measurement_relation_id,
        )

    def test_2_6_person_with_all_child_types(self) -> None:
        """Test 2.6: Person with measurements, observations, specimens, relations."""
        measurement = self.create_measurement_for_upload()
        observation = self.create_observation_for_upload()
        specimen = self.create_specimen_for_upload()
        measurement_relation = self.create_measurement_relation_for_upload()
        person_for_upload = self.create_person_for_upload(
            measurements=[measurement],
            observations=[observation],
            specimens=[specimen],
            measurement_relations=[measurement_relation],
        )
        created_person_id = self.random_ids[0]
        created_measurement_id = self.random_ids[1]
        created_observation_id = self.random_ids[2]
        created_specimen_id = self.random_ids[3]
        created_measurement_relation_id = self.random_ids[4]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
            [created_measurement_id],  # Create measurements returned IDs
            [created_observation_id],  # Create observations returned IDs
            [created_specimen_id],  # Create specimens returned IDs
            [created_measurement_relation_id],  # Create measurement relations IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=5)
        self.assertEqual(batch_result.persons[0].id, created_person_id)
        self.assertEqual(batch_result.persons[0].measurements[0].id, created_measurement_id)  # type: ignore[index]
        self.assertEqual(batch_result.persons[0].observations[0].id, created_observation_id)  # type: ignore[index]
        self.assertEqual(batch_result.persons[0].specimens[0].id, created_specimen_id)  # type: ignore[index]
        self.assertEqual(
            batch_result.persons[0].measurement_relations[0].id,  # type: ignore[index]
            created_measurement_relation_id,
        )


# ---------------------------------------------------------------------------
# Test Scenario 4: Parent link (person_id) in child objects
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test4PersonLinks(BasePersonUploadTestCase):
    """Test scenarios related to person_id links in child objects."""

    def test_4_1_child_null_person_id_set_during_upload(self) -> None:
        """Test 4.1: NULL_ID person_id in child - should be set during upload."""
        measurement = self.create_measurement_for_upload(person_id=NULL_ID)
        measurement_relation = self.create_measurement_relation_for_upload(
            person_id=NULL_ID
        )
        person_for_upload = self.create_person_for_upload(
            measurements=[measurement],
            measurement_relations=[measurement_relation],
        )
        created_person_id = self.random_ids[0]
        created_measurement_id = self.random_ids[1]
        created_measurement_relation_id = self.random_ids[2]
        # generate_id must return the same ID that crud will return for the
        # parent, so that the child's person_id link is set consistently.
        self.service.generate_id.side_effect = [
            created_person_id,
            created_measurement_id,
            created_measurement_relation_id,
        ]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
            [created_measurement_id],  # Create measurements returned IDs
            [created_measurement_relation_id],  # Create measurement relations IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=3)
        self.assertEqual(measurement.person_id, created_person_id)
        self.assertEqual(measurement_relation.person_id, created_person_id)

    def test_4_2_1_child_person_id_mismatch_fails(self) -> None:
        """Test 4.2.1: Child person_id does not match parent - should fail."""
        measurement = self.create_measurement_for_upload(person_id=self.person_id)
        person_for_upload = self.create_person_for_upload(
            person_id=self.person_id,
            is_new_id=True,
            measurements=[measurement],
        )
        # Override ID to be different from child's person_id
        person_for_upload.id = self.random_ids[1]
        self.service.repository.crud.side_effect = [
            [False],  # Person does not exist
        ]
        batch_result = self.upload_batch(person_for_upload, validate_command=False)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_pending=1, n_failed=1)

    def test_4_2_2_child_person_id_matches_succeeds(self) -> None:
        """Test 4.2.2: Child person_id matches parent - should succeed."""
        measurement = self.create_measurement_for_upload(person_id=self.person_id)
        person_for_upload = self.create_person_for_upload(
            person_id=self.person_id,
            measurements=[measurement],
        )
        existing_person = self.get_person_from_for_upload(person_for_upload)
        created_measurement_id = self.random_ids[0]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_person],  # Existing persons
            [created_measurement_id],  # Create measurements returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1, n_created=1)
        self.assertEqual(batch_result.persons[0].measurements[0].id, created_measurement_id)  # type: ignore[index]


# ---------------------------------------------------------------------------
# Test Scenario 5: External identifiers for persons
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test5ExternalIdentifiers(BasePersonUploadTestCase):
    """Test scenarios related to external identifiers for persons."""

    def test_5_1_no_external_ids_provided(self) -> None:
        """Test 5.1: No external identifiers provided - should succeed."""
        person_for_upload = self.create_person_for_upload(external_identifiers=None)
        created_person_id = self.random_ids[0]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1)

    def test_5_2_existing_external_id_resolves_person(self) -> None:
        """Test 5.2: Existing external identifier resolves person ID."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        existing_person_id = self.random_ids[0]
        existing_external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier, internal_id=existing_person_id
        )
        # Create upload person whose person_id matches the existing person so
        # that update_objects finds identical content and skips the update.
        person = self.create_person(person_id=existing_person_id)
        person.person_id = None  # Will be resolved from the external identifier
        person_for_upload = self.create_person_for_upload(
            person=person,
            external_identifiers=[external_identifier],
        )
        existing_person = self.get_person_from_for_upload(
            person_for_upload, person_id=existing_person_id
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # Identifier issuers
            [existing_external_identifier],  # Existing external identifiers
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_person],  # Existing persons
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=2)
        self.assertEqual(batch_result.persons[0].id, existing_person_id)

    def test_5_3_new_external_id_created_on_upload(self) -> None:
        """Test 5.3: New external identifier created on upload."""
        external_identifier_for_upload = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        created_external_identifier_id = self.random_ids[0]
        created_person_id = self.random_ids[1]
        person_for_upload = self.create_person_for_upload(
            external_identifiers=[external_identifier_for_upload],
        )
        external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier_for_upload,
            id=created_external_identifier_id,
            internal_id=created_person_id,
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # Identifier issuers
            [],  # No existing external identifiers
            [created_external_identifier_id],  # Created external identifier ID
        ]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create persons returned IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2)
        self.assertEqual(batch_result.persons[0].id, created_person_id)
        self.assertEqual(
            batch_result.persons[0].external_identifiers[0].id,  # type: ignore[index]
            created_external_identifier_id,
        )


# ---------------------------------------------------------------------------
# Test Scenario 6: Upload command on_exists value
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test6OnExistsActions(BasePersonUploadTestCase):
    """Test scenarios related to the on_exists command parameter."""

    def test_6_1_on_exists_error_with_existing_person_fails(self) -> None:
        """Test 6.1: on_exists=ERROR with existing person - should fail."""
        person_for_upload = self.create_person_for_upload(person_id=self.person_id)
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: person exists
        ]
        batch_result = self.upload_batch(
            person_for_upload, on_exists=OnExistsUploadAction.ERROR
        )
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1)

    def test_6_2_on_exists_skip_with_existing_person_skips(self) -> None:
        """Test 6.2: on_exists=SKIP with existing person - should skip."""
        person_for_upload = self.create_person_for_upload(person_id=self.person_id)
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: person exists
        ]
        batch_result = self.upload_batch(
            person_for_upload, on_exists=OnExistsUploadAction.SKIP
        )
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_skipped=1)

    def test_6_3_on_exists_update_with_existing_person_updates(self) -> None:
        """Test 6.3: on_exists=UPDATE with existing person - should update."""
        person_for_upload = self.create_person_for_upload(
            person_id=self.person_id,
            person=self.create_person(
                person_id=self.person_id, person_source_value="new_value"
            ),
        )
        existing_person = self.create_person(
            person_id=self.person_id, person_source_value="old_value"
        )
        self.service.repository.crud.side_effect = [
            [True],  # EXISTS_SOME: person exists
            [existing_person],  # READ_SOME: retrieve existing person for comparison
            [self.person_id],  # UPDATE_SOME: update returns ID
        ]
        batch_result = self.upload_batch(
            person_for_upload, on_exists=OnExistsUploadAction.UPDATE
        )
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_updated=1)


# ---------------------------------------------------------------------------
# Test Scenario 7: Parametrized batch sizes
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test7ParametrizedBatchSizes(BasePersonUploadTestCase):
    """Test upload with varying batch sizes."""

    def test_7_batch_of_n_new_persons(self) -> None:
        """Test 7: Upload batch of n new persons."""
        for n_persons in [1, 3, 5]:
            with self.subTest(n_persons=n_persons):
                self.setUp()  # Reset mocks for each subtest
                persons_for_upload = [
                    self.create_person_for_upload() for _ in range(n_persons)
                ]
                created_ids = self.random_ids[:n_persons]
                self.service.repository.crud.side_effect = [
                    created_ids,  # Create persons returned IDs
                ]
                batch_result = self.upload_batch(persons_for_upload)
                self.assertBatchProcessed(batch_result)
                self.assertStatusCount(batch_result, n_created=n_persons)
                for i, created_id in enumerate(created_ids):
                    self.assertEqual(batch_result.persons[i].id, created_id)

    def test_7_person_with_n_measurements(self) -> None:
        """Test 7: Upload person with varying number of measurements."""
        for n_children in [0, 1, 3]:
            with self.subTest(n_children=n_children):
                self.setUp()  # Reset mocks for each subtest
                measurements = [
                    self.create_measurement_for_upload() for _ in range(n_children)
                ]
                person_for_upload = self.create_person_for_upload(
                    measurements=measurements if measurements else None,
                )
                created_person_id = self.random_ids[0]
                created_measurement_ids = self.random_ids[1 : 1 + n_children]
                side_effects: list[list[UUID]] = [
                    [created_person_id],  # Create persons returned IDs
                ]
                if n_children > 0:
                    side_effects.append(
                        created_measurement_ids
                    )  # Create measurements returned IDs
                self.service.repository.crud.side_effect = side_effects
                batch_result = self.upload_batch(person_for_upload)
                self.assertBatchProcessed(batch_result)
                self.assertStatusCount(batch_result, n_created=1 + n_children)


# ---------------------------------------------------------------------------
# Test Scenario 8: External identifiers for Specimen objects
# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class Test8SpecimenExternalIdentifiers(BasePersonUploadTestCase):
    """Test scenarios related to external identifiers for Specimen objects."""

    def test_8_1_no_external_ids_provided(self) -> None:
        """Test 8.1: Specimen without external identifiers - should succeed."""
        specimen = self.create_specimen_for_upload()
        person_for_upload = self.create_person_for_upload(
            person_id=self.person_id, person=None, specimens=[specimen]
        )
        created_specimen_id = self.random_ids[1]
        self.service.generate_id.side_effect = [created_specimen_id]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [created_specimen_id],  # Created specimen ID
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1, n_skipped=1)

    def test_8_2_1_1_existing_external_id_null_specimen_sets_id(self) -> None:
        """Test 8.2.1.1: Existing external identifier with NULL specimen ID - should set specimen ID."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        existing_external_identifier_id = self.random_ids[0]
        existing_specimen_id = self.random_ids[1]
        existing_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier,
                internal_id=existing_specimen_id,
                id=existing_external_identifier_id,
            )
        )
        existing_specimen = self.create_specimen_for_upload(
            specimen_id=NULL_ID, external_identifiers=[external_identifier]
        )
        existing_person_id = self.person_id
        person_for_upload = self.create_person_for_upload(
            person_id=existing_person_id, person=None, specimens=[existing_specimen]
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],
            [existing_external_identifier],
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_specimen],  # Existing specimen
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_specimen_id, existing_person_id)],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=0, n_updated=0, n_skipped=3)
        self.assertEqual(
            batch_result.persons[0].specimens[0].id, existing_specimen_id  # type: ignore[index]
        )

    def test_8_2_1_2_1_existing_external_id_same_specimen_succeeds(self) -> None:
        """Test 8.2.1.2.1: Existing external identifier with same specimen ID - should succeed."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        existing_external_identifier_id = self.random_ids[0]
        existing_specimen_id = self.random_ids[1]
        existing_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier,
                internal_id=existing_specimen_id,
                id=existing_external_identifier_id,
            )
        )
        existing_specimen = self.create_specimen_for_upload(
            specimen_id=existing_specimen_id, external_identifiers=[external_identifier]
        )
        existing_person_id = self.person_id
        person_for_upload = self.create_person_for_upload(
            person_id=existing_person_id, person=None, specimens=[existing_specimen]
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],
            [existing_external_identifier],
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_specimen],  # Existing specimen
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_specimen_id, existing_person_id)],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=0, n_updated=0, n_skipped=3)
        self.assertEqual(
            batch_result.persons[0].specimens[0].id, existing_specimen_id  # type: ignore[index]
        )

    def test_8_2_1_2_2_existing_external_id_different_specimen_fails(self) -> None:
        """Test 8.2.1.2.2: Existing external identifier with different specimen ID - should fail."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        existing_external_identifier_id = self.random_ids[0]
        existing_specimen_id = self.random_ids[1]
        non_existing_specimen_id = self.random_ids[2]
        existing_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier,
                internal_id=non_existing_specimen_id,
                id=existing_external_identifier_id,
            )
        )
        existing_specimen = self.create_specimen_for_upload(
            specimen_id=existing_specimen_id, external_identifiers=[external_identifier]
        )
        existing_person_id = self.person_id
        person_for_upload = self.create_person_for_upload(
            person_id=existing_person_id, person=None, specimens=[existing_specimen]
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],
            [existing_external_identifier],
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_specimen],  # Existing specimen
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_specimen_id, existing_person_id)],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_pending=1, n_failed=1, n_skipped=1)
        self.assertEqual(
            batch_result.persons[0].specimens[0].id, existing_specimen_id  # type: ignore[index]
        )

    def test_8_2_2_new_external_id_new_specimen(self) -> None:
        """Test 8.2.2: New external identifier for new specimen - should succeed."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        created_external_identifier_id = self.random_ids[0]
        created_specimen_id = self.random_ids[1]
        created_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier,
                internal_id=created_specimen_id,
                id=created_external_identifier_id,
            )
        )
        created_specimen = self.create_specimen_for_upload(
            specimen_id=NULL_ID, external_identifiers=[external_identifier]
        )
        existing_person_id = self.person_id
        person_for_upload = self.create_person_for_upload(
            person_id=existing_person_id, person=None, specimens=[created_specimen]
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],
            [],  # Existing external identifiers
            [created_external_identifier_id],  # Created external identifier IDs
        ]
        self.service.repository.crud.side_effect = [
            # [True],  # Person exists
            [created_specimen_id],  # Created specimen IDs
        ]
        self.service.generate_id.side_effect = [
            created_specimen_id,
            created_external_identifier_id,
        ]
        self.service.repository.read_fields.side_effect = [
            [(created_specimen_id, existing_person_id)],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=2, n_updated=0, n_skipped=1)
        self.assertEqual(
            batch_result.persons[0].specimens[0].id, created_specimen_id  # type: ignore[index]
        )
        self.assertEqual(
            batch_result.persons[0].specimens[0].external_identifiers[0].id, created_external_identifier_id  # type: ignore[index]
        )

    def test_8_2_3_1_multiple_external_ids_some_existing_same_specimen(self) -> None:
        """Test 8.2.3.1: Multiple external IDs, some existing for same specimen - should succeed."""
        external_identifier1 = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        existing_external_identifier_id = self.random_ids[0]
        existing_specimen_id = self.random_ids[1]
        existing_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier1,
                internal_id=existing_specimen_id,
                id=existing_external_identifier_id,
            )
        )
        created_external_identifier_id = self.random_ids[1]
        created_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier2,
                self.specimen_id,
                id=created_external_identifier_id,
            )
        )
        existing_specimen = self.create_specimen_for_upload(
            specimen_id=existing_specimen_id,
            external_identifiers=[external_identifier1, external_identifier2],
        )
        existing_person_id = self.person_id
        person_for_upload = self.create_person_for_upload(
            person_id=existing_person_id, person=None, specimens=[existing_specimen]
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer, self.identifier_issuer2],
            [existing_external_identifier],  # Existing external identifiers
            [created_external_identifier_id],  # Created external identifier IDs
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_specimen],  # Existing specimen
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_specimen_id, existing_person_id)],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=1, n_updated=0, n_skipped=3)
        self.assertEqual(
            batch_result.persons[0].specimens[0].id, existing_specimen_id  # type: ignore[index]
        )
        self.assertEqual(
            batch_result.persons[0].specimens[0].external_identifiers[1].id, created_external_identifier_id  # type: ignore[index]
        )

    def test_8_2_3_1_multiple_external_ids_some_existing_different_specimen(
        self,
    ) -> None:
        """Test 8.2.3.1: Multiple external IDs, some existing for different specimen - should fail."""
        external_identifier1 = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        existing_external_identifier_id = self.random_ids[0]
        non_existing_specimen_id = self.random_ids[2]
        existing_specimen_id = self.random_ids[1]
        existing_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier1,
                internal_id=non_existing_specimen_id,
                id=existing_external_identifier_id,
            )
        )
        created_external_identifier_id = self.random_ids[1]
        created_external_identifier = (
            self.get_specimen_external_identifier_from_for_upload(
                external_identifier2,
                self.specimen_id,
                id=created_external_identifier_id,
            )
        )
        existing_specimen = self.create_specimen_for_upload(
            specimen_id=existing_specimen_id,
            external_identifiers=[external_identifier1, external_identifier2],
        )
        existing_person_id = self.person_id
        person_for_upload = self.create_person_for_upload(
            person_id=existing_person_id, person=None, specimens=[existing_specimen]
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer, self.identifier_issuer2],
            [existing_external_identifier],  # Existing external identifiers
            [created_external_identifier_id],  # Created external identifier IDs
        ]
        self.service.repository.crud.side_effect = [
            [True],  # Person exists
            [existing_specimen],  # Existing specimen
        ]
        self.service.repository.read_fields.side_effect = [
            [(existing_specimen_id, existing_person_id)],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_skipped=1, n_pending=2)
        self.assertEqual(
            batch_result.persons[0].specimens[0].id, existing_specimen_id  # type: ignore[index]
        )
        self.assertEqual(
            batch_result.persons[0].specimens[0].external_identifiers[1].id, None  # type: ignore[index]
        )

    def test_8_2_3_2_multiple_external_ids_all_new_same_issuer(self) -> None:
        """Test 8.2.3.2: Multiple external IDs all new but same issuer - should fail."""
        external_identifier1 = self.create_external_identifier_for_upload(
            external_id="new_ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="new_ext_id_2", identifier_issuer_id=self.identifier_issuer_id
        )
        with pytest.raises(ValueError):
            self.create_specimen_for_upload(
                external_identifiers=[external_identifier1, external_identifier2]
            )

    def test_8_2_3_2_multiple_external_ids_all_new_different_issuer(self) -> None:
        """Test 8.2.3.2: Multiple external IDs all new and different issuer - should succeed."""
        external_identifier1 = self.create_external_identifier_for_upload(
            external_id="new_ext_id_1", identifier_issuer_id=self.identifier_issuer_id
        )
        external_identifier2 = self.create_external_identifier_for_upload(
            external_id="new_ext_id_2",
            identifier_issuer_id=self.identifier_issuer_id2,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        specimen = self.create_specimen_for_upload(
            external_identifiers=[external_identifier1, external_identifier2]
        )
        person_for_upload = self.create_person_for_upload(specimens=[specimen])
        created_person_id = self.random_ids[0]
        created_specimen_id = self.random_ids[1]
        created_external_identifier1_id = self.random_ids[2]
        created_external_identifier2_id = self.random_ids[3]
        self.service.generate_id.side_effect = [
            created_person_id,
            created_specimen_id,
            created_external_identifier1_id,
            created_external_identifier2_id,
        ]
        self.service.repository.crud.side_effect = [
            [created_person_id],
            [created_specimen_id],
            [created_external_identifier1_id, created_external_identifier2_id],
        ]
        self.service.app.handle.side_effect = [
            [self.identifier_issuer, self.identifier_issuer2],
            [],  # Existing external identifiers
            [
                created_external_identifier1_id,
                created_external_identifier2_id,
            ],  # Created external identifier IDs
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=4)

    def test_8_3_1_identifier_issuer_id_not_found(self) -> None:
        """Test 8.3.1: Identifier issuer ID (any except NULL_ID) provided and not found - should fail."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.random_ids[0]
        )
        specimen = self.create_specimen_for_upload(
            external_identifiers=[external_identifier]
        )
        person_for_upload = self.create_person_for_upload(specimens=[specimen])
        created_person_id = self.random_ids[1]
        self.service.generate_id.side_effect = [
            created_person_id,
        ]
        self.service.app.handle.side_effect = [
            [],
            [],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)

    def test_8_3_2_identifier_issuer_code_not_found(self) -> None:
        """Test 8.3.2: Identifier issuer code provided and not found - should fail."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=NULL_ID, identifier_issuer_code="nonexistent_code"
        )
        specimen = self.create_specimen_for_upload(
            external_identifiers=[external_identifier]
        )
        person_for_upload = self.create_person_for_upload(specimens=[specimen])
        created_person_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_person_id,
        ]
        self.service.app.handle.side_effect = [
            [],
            [],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)

    def test_8_3_3_identifier_issuer_id_and_code_mismatch(self) -> None:
        """Test 8.3.3: Both identifier issuer ID and code provided but do not match - should fail."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
            identifier_issuer_code=self.identifier_issuer_code2,
        )
        specimen = self.create_specimen_for_upload(
            external_identifiers=[external_identifier]
        )
        person_for_upload = self.create_person_for_upload(specimens=[specimen])
        created_person_id = self.random_ids[0]
        self.service.generate_id.side_effect = [
            created_person_id,
        ]
        self.service.app.handle.side_effect = [
            [self.identifier_issuer, self.identifier_issuer2],
            [],
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchFailed(batch_result)
        self.assertStatusCount(batch_result, n_failed=1, n_pending=2)


# ---------------------------------------------------------------------------
# Combined scenario tests

# ---------------------------------------------------------------------------


@pytest.mark.scenario_ids("TC-SEC-30-03")
class TestCombinedScenarios(BasePersonUploadTestCase):
    """Test combinations of different scenarios."""

    def test_person_with_all_children_and_external_ids(self) -> None:
        """Test person with all child types and external identifiers."""
        external_identifier = self.create_external_identifier_for_upload(
            identifier_issuer_id=self.identifier_issuer_id,
        )
        measurement = self.create_measurement_for_upload()
        observation = self.create_observation_for_upload()
        specimen = self.create_specimen_for_upload()
        measurement_relation = self.create_measurement_relation_for_upload()
        person_for_upload = self.create_person_for_upload(
            external_identifiers=[external_identifier],
            measurements=[measurement],
            observations=[observation],
            specimens=[specimen],
            measurement_relations=[measurement_relation],
        )
        created_person_id = self.random_ids[0]
        created_measurement_id = self.random_ids[1]
        created_observation_id = self.random_ids[2]
        created_specimen_id = self.random_ids[3]
        created_measurement_relation_id = self.random_ids[4]
        created_external_identifier = self.get_external_identifier_from_for_upload(
            external_identifier,
            internal_id=created_person_id,
            id=self.random_ids[5],
            identifier_issuer_id=self.identifier_issuer_id,
        )
        self.service.app.handle.side_effect = [
            [self.identifier_issuer],  # Resolve IdentifierIssuer
            [],  # No existing ExternalIdentifiers
            [created_external_identifier],  # Created ExternalIdentifier
        ]
        self.service.repository.crud.side_effect = [
            [created_person_id],  # Create person
            [created_measurement_id],  # Create measurement
            [created_observation_id],  # Create observation
            [created_specimen_id],  # Create specimen
            [created_measurement_relation_id],  # Create measurement relation
        ]
        batch_result = self.upload_batch(person_for_upload)
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=6)
        self.assertEqual(batch_result.persons[0].id, created_person_id)

    def test_multiple_persons_mixed_child_types(self) -> None:
        """Test batch with multiple persons having different child type combinations."""
        # Person 1: with measurement
        measurement = self.create_measurement_for_upload()
        person1_for_upload = self.create_person_for_upload(measurements=[measurement])
        # Person 2: no children
        person2_for_upload = self.create_person_for_upload()
        # Person 3: with observation, specimen, and measurement relation
        observation = self.create_observation_for_upload()
        specimen = self.create_specimen_for_upload()
        measurement_relation = self.create_measurement_relation_for_upload()
        person3_for_upload = self.create_person_for_upload(
            observations=[observation],
            specimens=[specimen],
            measurement_relations=[measurement_relation],
        )
        created_person_ids = self.random_ids[0:3]
        created_measurement_id = self.random_ids[3]
        created_observation_id = self.random_ids[4]
        created_specimen_id = self.random_ids[5]
        created_measurement_relation_id = self.random_ids[6]
        self.service.repository.crud.side_effect = [
            created_person_ids,  # Create persons
            [created_measurement_id],  # Create measurements
            [created_observation_id],  # Create observations
            [created_specimen_id],  # Create specimens
            [created_measurement_relation_id],  # Create measurement relations
        ]
        batch_result = self.upload_batch(
            [person1_for_upload, person2_for_upload, person3_for_upload]
        )
        self.assertBatchProcessed(batch_result)
        self.assertStatusCount(batch_result, n_created=7)
        self.assertStatusCount(batch_result, n_created=7)
        self.assertStatusCount(batch_result, n_created=7)
        self.assertStatusCount(batch_result, n_created=7)
        self.assertStatusCount(batch_result, n_created=7)
        self.assertStatusCount(batch_result, n_created=7)
