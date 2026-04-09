from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.retrieve_person import (
    omop_service_retrieve_persons_by_id,
    omop_service_retrieve_persons_by_query,
)
from gen_epix.omopdb.services.omop.upload import omop_service_upload_persons


class OmopService(BaseOmopService):
    def upload_persons(
        self, cmd: command.UploadPersonsCommand
    ) -> model.PersonBatchUploadResult:
        return omop_service_upload_persons(self, cmd)

    def retrieve_persons_by_id(
        self, cmd: command.RetrievePersonsByIdCommand
    ) -> list[model.FullPerson]:
        return omop_service_retrieve_persons_by_id(self, cmd)

    def retrieve_persons_by_query(
        self, cmd: command.RetrievePersonsByQueryCommand
    ) -> model.PersonQueryResult:
        return omop_service_retrieve_persons_by_query(self, cmd)
