"""Upload person-centered OMOP batches through the shared batch-upload workflow."""

from uuid import UUID

import gen_epix.omopdb.domain.command as command
import gen_epix.omopdb.domain.model as model
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.commondb.domain.enum import EtlStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import BaseBatchUploadResult
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import exc
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.person_validator import PersonValidator


class PersonBatchUploader(BatchUploader):
    """Encapsulates validation and persistence of person batches and associated data."""

    def __init__(self, service: BaseService) -> None:
        """Initialize the uploader for an OMOP service.

        Args:
            service: Service that owns person upload persistence and validation.

        Raises:
            InvalidArgumentsError: If `service` is not an OmopDB service.
        """
        super().__init__(
            command.UploadPersonsCommand,
            model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
            service,
        )
        if not isinstance(service, BaseOmopService):
            raise exc.InvalidArgumentsError("38bd57d4", "Invalid service type")
        self.service: BaseOmopService = service

    def verify_user_rights(self, cmd: UploadBatchCommandMixin) -> None:
        """Verify rights for a person-upload command.

        Args:
            cmd: Batch command whose user permissions are being checked.

        Raises:
            InvalidArgumentsError: If `cmd` is not an upload-persons command.
        """
        # Verify command type
        if not isinstance(cmd, command.UploadPersonsCommand):
            raise exc.InvalidArgumentsError("f8dbeb8d", "Invalid command type")
        # TODO: implement additional user rights verifications as necessary

    def verify_batch(
        self,
        cmd: UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """Verify generic batch requirements and person content.

        Args:
            cmd: Upload-persons command containing the batch.
            batch_result: Mutable result that receives validation issues.
            uow: Unit of work used for generic batch verification.

        Returns:
            `True` when generic and person-content verification succeed.

        Raises:
            InvalidArgumentsError: If the command or batch result has an invalid type.
        """
        if not isinstance(cmd, command.UploadPersonsCommand):
            raise exc.InvalidArgumentsError("7b3446fe", "Invalid command type")
        if not isinstance(batch_result, model.PersonBatchUploadResult):
            raise exc.InvalidArgumentsError("1a93de93", "Invalid return value type")
        success = True

        # Verify generic aspects. This will fill in any person IDs based on external
        # identifiers. The person IDs are needed for person content validation when the
        # person is being updated, since the merged content is validated and the IDs
        # are needed to retrieve the persons.
        success &= super().verify_batch(cmd, batch_result, uow)

        # Verify person content. Derived values and data issues are also added in the
        # form of ValidatedPersonForUpload objects in the result.
        success &= self.verify_person_content(cmd, batch_result, uow)

        return success

    def upsert_batch(
        self,
        cmd: UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """Upsert the persons in a validated upload batch.

        Args:
            cmd: Upload-persons command containing the batch.
            batch_result: Mutable result that records persisted entities.
            uow: Unit of work used for batch persistence.

        Returns:
            `True` when the generic batch upsert succeeds.

        Raises:
            InvalidArgumentsError: If the command or batch result has an invalid type.
        """
        if not isinstance(cmd, command.UploadPersonsCommand):
            raise exc.InvalidArgumentsError("94c3402c", "Invalid command type")
        if not isinstance(batch_result, model.PersonBatchUploadResult):
            raise exc.InvalidArgumentsError("aba133d4", "Invalid return value type")
        success = True

        # Use the general parent method for upserting the persons
        success &= super().upsert_batch(cmd, batch_result, uow)

        return success

    def verify_person_content(
        self,
        cmd: command.UploadPersonsCommand,
        batch_result: model.PersonBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Verify the person content and add any derived values.
        """
        success = True
        # Initialize some
        status_count_before = batch_result.get_status_count()
        person_validator = self._get_person_validator(
            cmd.user.id if cmd.user and cmd.user.id else NULL_ID
        )

        # Validate and transform each person
        person_validator.validate_and_transform(cmd, batch_result)

        # Update status of each result with data issues found
        for person_result in batch_result.persons:
            person_result.update_status_with_data_issues()

        # Update batch status if necessary
        status_count_after = batch_result.get_status_count()
        if status_count_after[EtlStatus.FAILED] > status_count_before[EtlStatus.FAILED]:
            success = False
        return success

    def _get_person_validator(self, user_id: UUID) -> PersonValidator:
        """Get person validator for the given complete person type"""
        return PersonValidator(self.service, user_id)


def omop_service_upload_persons(
    self: BaseOmopService, cmd: command.UploadPersonsCommand
) -> model.PersonBatchUploadResult:
    """Upload a person batch through an OmopDB service instance."""
    batch_uploader = PersonBatchUploader(self)

    batch_result: model.PersonBatchUploadResult = batch_uploader.upload_batch(cmd)  # type: ignore[assignment]
    return batch_result
