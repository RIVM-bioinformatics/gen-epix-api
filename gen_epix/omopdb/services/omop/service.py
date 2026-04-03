from gen_epix.omopdb.domain import command, model
from gen_epix.omopdb.services.omop.base import BaseOmopService
from gen_epix.omopdb.services.omop.retrieve_full_persons import (
    omop_service_retrieve_full_persons,
)
from gen_epix.omopdb.services.omop.upload import omop_service_upload_persons


class OmopService(BaseOmopService):
    def upload_persons(
        self, cmd: command.UploadPersonsCommand
    ) -> model.PersonBatchUploadResult:
        return omop_service_upload_persons(self, cmd)

    def retrieve_full_persons(
        self, cmd: command.RetrieveFullPersonsCommand
    ) -> list[model.FullPerson]:
        return omop_service_retrieve_full_persons(self, cmd)
