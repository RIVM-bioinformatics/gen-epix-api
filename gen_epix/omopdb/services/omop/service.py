"""Concrete OmopDB command service delegating to upload and retrieval workflows."""

from gen_epix.commondb.domain.enum import FeatureFlag
from gen_epix.fastapp.exc import FeatureDisabledServiceError
from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.retrieve_person import (
    omop_service_retrieve_persons_by_id,
    omop_service_retrieve_persons_by_query,
)
from gen_epix.omopdb.services.omop.upload import omop_service_upload_persons


class OmopService(BaseOmopService):
    """Encapsulates handling of OMOP person-upload and person-retrieval commands."""

    def delete_operational_data(
        self, cmd: command.DeleteOperationalDataCommand
    ) -> None:
        """Delete OMOP operational data in one repository unit of work.

        Args:
            cmd: Reset command authorized by the BEFORE RBAC policy.

        Raises:
            FeatureDisabledServiceError: If the reset flag is false or missing.
        """
        if not self.app.get_feature_flag(
            FeatureFlag.ALLOW_DELETE_OPERATIONAL_DATA.value
        ):
            raise FeatureDisabledServiceError("cc713243")
        with self.repository.uow() as uow:
            self.repository.delete_operational_data(uow)

    def upload_persons(
        self, cmd: command.UploadPersonsCommand
    ) -> model.PersonBatchUploadResult:
        """Upload the person batch carried by the command."""
        return omop_service_upload_persons(self, cmd)

    def retrieve_persons_by_id(
        self, cmd: command.RetrievePersonsByIdCommand
    ) -> list[model.FullPerson]:
        """Retrieve full persons identified by the command."""
        return omop_service_retrieve_persons_by_id(self, cmd)

    def retrieve_persons_by_query(
        self, cmd: command.RetrievePersonsByQueryCommand
    ) -> model.PersonQueryResult:
        """Retrieve persons matching the command query."""
        return omop_service_retrieve_persons_by_query(self, cmd)
