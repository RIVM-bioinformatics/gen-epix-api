from uuid import UUID

import gen_epix.omopdb.domain.command as command
import gen_epix.omopdb.domain.model as model
from gen_epix.commondb.domain.command.base import UploadBatchCommandMixin
from gen_epix.commondb.domain.enum import UploadStatus
from gen_epix.commondb.domain.literal import NULL_ID
from gen_epix.commondb.domain.model.upload import BaseBatchUploadResult
from gen_epix.commondb.services.upload import BatchUploader
from gen_epix.fastapp.service import BaseService
from gen_epix.fastapp.unit_of_work import BaseUnitOfWork
from gen_epix.omopdb.domain import exc
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.person_validator import PersonValidator


class PersonBatchUploader(BatchUploader):
    def __init__(self, service: BaseService) -> None:
        super().__init__(
            command.UploadPersonsCommand,
            model.STORED_MODEL_FIELD_PROPS,  # type: ignore[arg-type]
            service,
        )
        if not isinstance(service, BaseOmopService):
            raise exc.InvalidArgumentsError("Invalid service type")
        self.service: BaseOmopService = service

    def verify_user_rights(self, cmd: UploadBatchCommandMixin) -> None:
        """
        Implements user rights verification for uploading cases. Only ABAC rights are
        verified: the user must have write access to all case type columns contained in
        the uploaded cases for the created in data collection.
        """
        # Verify command type
        if not isinstance(cmd, command.UploadPersonsCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        # TODO: implement additional user rights verifications as necessary

    def verify_batch(
        self,
        cmd: UploadBatchCommandMixin,
        batch_result: BaseBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Extends batch verification to the person content.
        """
        if not isinstance(cmd, command.UploadPersonsCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        if not isinstance(batch_result, model.PersonBatchUploadResult):
            raise exc.InvalidArgumentsError("Invalid return value type")
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
        """
        Extends batch upload to uploading the persons with this service.
        """
        if not isinstance(cmd, command.UploadPersonsCommand):
            raise exc.InvalidArgumentsError("Invalid command type")
        if not isinstance(batch_result, model.PersonBatchUploadResult):
            raise exc.InvalidArgumentsError("Invalid return value type")
        success = True

        # Use the general parent method for upserting the persons
        success &= super().upsert_batch(cmd, batch_result, uow)

        # Upsert child external identifiers. This needs to be done after the main
        # upsert to ensure that any new person IDs are available for the external
        # identifiers.
        success &= self.upsert_person_children_external_identifiers(
            cmd, batch_result, uow
        )

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

        # Verify child external identifiers
        success &= self.verify_person_children_external_identifiers(
            cmd, batch_result, uow
        )

        # Validate and transform each person
        person_validator.validate_and_transform(cmd, batch_result)

        # Update status of each result with data issues found
        for person_result in batch_result.persons:
            person_result.update_status_with_data_issues()

        # Update batch status if necessary
        status_count_after = batch_result.get_status_count()
        if (
            status_count_after[UploadStatus.FAILED]
            > status_count_before[UploadStatus.FAILED]
        ):
            success = False
        return success

    def _get_person_validator(self, user_id: UUID) -> PersonValidator:
        """Get person validator for the given complete person type"""
        return PersonValidator(self.service, user_id)

    def verify_person_children_external_identifiers(
        self,
        cmd: command.UploadPersonsCommand,
        batch_result: model.PersonBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Verify external identifiers in any of the person child objects. This includes
        verifying that any provided external identifier IDs exist and are accessible
        by the user, and filling in any missing IDs based on provided codes.
        """
        success = True
        success &= self.verify_children_external_identifiers(
            cmd,
            batch_result,
            uow,
            "specimens",
            model.SpecimenForUpload.EXTERNAL_IDENTIFIER_TYPE,
        )

        return success

    def upsert_person_children_external_identifiers(
        self,
        cmd: command.UploadPersonsCommand,
        batch_result: model.PersonBatchUploadResult,
        uow: BaseUnitOfWork,
    ) -> bool:
        """
        Upsert external identifiers in any of the person child objects. This includes
        upserting any provided external identifiers that are not marked as failed.
        """
        success = True
        # TODO: implement

        return success


def omop_service_upload_persons(
    self: BaseOmopService, cmd: command.UploadPersonsCommand
) -> model.PersonBatchUploadResult:
    batch_uploader = PersonBatchUploader(self)

    batch_result: model.PersonBatchUploadResult = batch_uploader.upload_batch(cmd)  # type: ignore[assignment]
    return batch_result
