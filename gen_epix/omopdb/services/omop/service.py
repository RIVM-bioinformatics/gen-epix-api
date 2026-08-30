"""Concrete OmopDB command service delegating to upload and retrieval workflows."""

from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.retrieve_person import (
    omop_service_retrieve_persons_by_id,
    omop_service_retrieve_persons_by_query,
)
from gen_epix.omopdb.services.omop.upload import omop_service_upload_persons


class OmopService(BaseOmopService):
    """Handle OMOP person-upload and person-retrieval commands."""

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
